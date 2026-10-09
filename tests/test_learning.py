import copy
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from app.engine import LocalEngine, validate_analysis
from app.rules import Position, START_FEN
from app.puzzles import PUZZLES
from app.learning import schedule, recommend, explain_grounded
from app.storage import Repository
from app.service import Service

REFLECTION=dict(evaluation='Đỏ có cơ hội ăn quân.',threat='Cần kiểm tra Xe đối phương.',plan='Ăn Xe rồi kiểm tra đường chiếu.',confidence='some')


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.engine=LocalEngine()

    def test_all_twelve_puzzle_solutions(self):
        for puzzle in PUZZLES:
            with self.subTest(puzzle=puzzle['id']):
                pos=Position.from_fen(puzzle['fen'])
                analysis=validate_analysis(pos,self.engine.analyze(pos.fen()))
                self.assertEqual(analysis['depth'],2)
                solution=next(x for x in analysis['lines'] if x['move']==puzzle['solution'])
                self.assertEqual(solution['score'],analysis['score'])
                self.assertLess(next(x['score'] for x in analysis['lines'] if x['move']==puzzle['demo_mistake']),solution['score'])

    def test_twenty_positions_legal_bot_and_pv(self):
        pos=Position.from_fen(START_FEN)
        for _ in range(20):
            result=validate_analysis(pos,self.engine.analyze(pos.fen()))
            self.assertTrue(result['lines'])
            pos=pos.play(result['lines'][0]['move'])

    def test_timeout_still_legal(self):
        pos=Position.from_fen(START_FEN)
        result=LocalEngine(seconds=0).analyze(pos.fen())
        self.assertEqual(result['depth'],0)
        self.assertTrue(result['truncated'])
        self.assertIn(result['lines'][0]['move'],pos.legal_moves())

    def test_cache(self):
        fen=PUZZLES[0]['fen']
        self.engine.analyze(fen)
        before=self.engine.analyze.cache_info().hits
        self.engine.analyze(fen)
        self.assertGreater(self.engine.analyze.cache_info().hits,before)

    def test_reject_invented_engine_line(self):
        pos=Position.from_fen(PUZZLES[0]['fen'])
        data=copy.deepcopy(self.engine.analyze(pos.fen()))
        data['lines'][0]['pv']=['a2a9']
        with self.assertRaises(ValueError):validate_analysis(pos,data)


class ScheduleTests(unittest.TestCase):
    def test_intervals(self):
        now=datetime(2026,10,8,tzinfo=timezone.utc)
        for correct,assisted,unseen,days in [(False,False,True,1),(True,True,True,2),(True,False,False,7),(True,False,True,14)]:
            result=schedule({},correct,assisted,unseen,now)
            self.assertEqual((datetime.fromisoformat(result['next_review_at'])-now).days,days)

    def test_second_transfer(self):
        result=schedule({'transfer_success_count':1},True,False,True)
        self.assertEqual(result['stability'],30)

    def test_scores_bounded(self):
        self.assertEqual(schedule({'mastery_score':0},False,False,True)['mastery_score'],0)
        self.assertEqual(schedule({'mastery_score':100},True,False,True)['mastery_score'],100)

    def test_assisted_not_transfer(self):
        self.assertEqual(schedule({},True,True,True)['transfer_success_count'],0)

    def test_unseen_related_preferred(self):
        p,unseen=recommend(PUZZLES,'material',[{'puzzle_id':'loose-rook','family':'loose-rook'}])
        self.assertEqual(p['skill'],'material')
        self.assertNotEqual(p['id'],'loose-rook')
        self.assertTrue(unseen)

    def test_seen_bank_honest_label(self):
        p,unseen=recommend(PUZZLES,'material',[{'puzzle_id':p['id'],'family':p['family']} for p in PUZZLES])
        self.assertFalse(unseen)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir='var/tests')
        self.path=Path(self.temp.name)/'test.sqlite3'
        self.repo=Repository(self.path)
        self.svc=Service(self.repo)
        self.db=self.repo.connect()
        self.owner='test-owner'

    def tearDown(self):
        self.db.close();self.temp.cleanup()

    def demo_review(self):
        game=self.svc.new_game(self.db,self.owner,{'mode':'demo'})
        return self.svc.review(self.db,self.owner,game['id'])['moments'][0]

    def reflect(self,e):return self.svc.reflect(self.db,self.owner,e['id'],REFLECTION)

    def test_draft_persists_without_revealing_or_scoring(self):
        e=self.demo_review()
        draft={'evaluation':'Đang suy nghĩ', 'threat':'', 'plan':'', 'confidence':'some'}
        self.assertTrue(self.svc.save_draft(self.db,self.owner,e['id'],draft)['saved'])
        self.db.commit()
        with Repository(self.path).connect() as reopened:
            view=self.svc.exercise_view(self.repo.get(reopened,self.owner,'exercise',e['id']))
        self.assertEqual(view['draft'],draft)
        self.assertIsNone(view['reflection'])
        self.assertFalse(view['revealed'])
        self.assertNotIn('analysis',view)
        self.assertNotIn('explanation',view)
        self.assertEqual(self.svc.dashboard(self.db,self.owner)['total_attempts'],0)
        with self.assertRaises(ValueError):self.svc.attempt(self.db,self.owner,e['id'],'a2a7')

    def test_draft_isolation_and_validation(self):
        e=self.demo_review()
        with self.assertRaises(LookupError):self.svc.save_draft(self.db,'another-owner',e['id'],{})
        for draft in ({'plan':7},{'plan':'x'*1501},{'confidence':'invalid'}):
            with self.assertRaises(ValueError):self.svc.save_draft(self.db,self.owner,e['id'],draft)
        self.assertNotIn('draft',self.repo.get(self.db,self.owner,'exercise',e['id']))

    def test_submitted_reflection_wins_over_delayed_draft(self):
        e=self.demo_review()
        self.svc.save_draft(self.db,self.owner,e['id'],{'plan':'Bản nháp'})
        self.reflect(e)
        result=self.svc.save_draft(self.db,self.owner,e['id'],{'plan':'Lưu trễ'})
        self.assertFalse(result['saved'])
        stored=self.repo.get(self.db,self.owner,'exercise',e['id'])
        self.assertNotIn('draft',stored)
        self.assertEqual(stored['reflection']['plan'],REFLECTION['plan'])

    def test_pending_practice_resume_and_completion(self):
        e=self.svc.practice(self.db,self.owner,{'skill':'material'})
        pending=self.svc.dashboard(self.db,self.owner)['pending']
        self.assertEqual(pending[0]['id'],e['id'])
        self.assertEqual(pending[0]['stage'],'reflection')
        self.assertNotIn('analysis',pending[0])
        self.assertEqual(self.svc.dashboard(self.db,'another-owner')['pending'],[])
        self.reflect(e)
        self.assertEqual(self.svc.dashboard(self.db,self.owner)['pending'][0]['stage'],'attempt')
        stored=self.repo.get(self.db,self.owner,'exercise',e['id'])
        self.svc.attempt(self.db,self.owner,e['id'],stored['analysis']['lines'][0]['move'])
        self.assertEqual(self.svc.dashboard(self.db,self.owner)['pending'],[])

    def test_drafts_export_and_delete_with_guest(self):
        e=self.demo_review()
        self.svc.save_draft(self.db,self.owner,e['id'],{'plan':'Ghi chú riêng'})
        records=self.svc.export(self.db,self.owner)['data']
        exercise=next(r['data'] for r in records if r['kind']=='exercise')
        self.assertEqual(exercise['draft']['plan'],'Ghi chú riêng')
        self.assertNotIn('analysis',exercise)
        self.repo.delete_owner(self.db,self.owner)
        self.assertEqual(self.svc.export(self.db,self.owner)['data'],[])

    def test_complete_learning_loop(self):
        e=self.demo_review()
        self.assertNotIn('analysis',e)
        self.assertNotIn('explanation',e)
        e=self.reflect(e)
        self.assertEqual(e['explanation']['move'],'a2a7')
        e=self.svc.attempt(self.db,self.owner,e['id'],'a2a7')
        self.assertTrue(e['complete'])
        practice=self.svc.practice(self.db,self.owner,{'from_id':e['id']})
        self.assertNotEqual(practice['fen'],e['fen'])
        self.assertTrue(practice['unseen'])
        practice=self.reflect(practice)
        self.assertNotIn('explanation',practice)
        answer=self.svc.engine.analyze(practice['fen'])['lines'][0]['move']
        self.svc.attempt(self.db,self.owner,practice['id'],answer)
        d=self.svc.dashboard(self.db,self.owner)
        self.assertEqual(d['total_attempts'],2)
        self.assertEqual(d['transfer_success'],1)
        self.assertEqual(d['skills'][0]['stability'],14)
        self.assertEqual(d['due'],[])

    def test_reflection_cannot_be_bypassed(self):
        e=self.demo_review()
        for action in (lambda:self.svc.attempt(self.db,self.owner,e['id'],'a2a7'),lambda:self.svc.hint(self.db,self.owner,e['id'])):
            with self.assertRaises(ValueError):action()
        self.assertEqual(self.svc.dashboard(self.db,self.owner)['total_attempts'],0)

    def test_reflection_all_fields_required(self):
        e=self.demo_review()
        for field in ('evaluation','threat','plan'):
            with self.assertRaises(ValueError):self.svc.reflect(self.db,self.owner,e['id'],{**REFLECTION,field:' '})

    def test_repeated_attempt_idempotent(self):
        e=self.reflect(self.demo_review())
        self.svc.attempt(self.db,self.owner,e['id'],'a2a7')
        self.svc.attempt(self.db,self.owner,e['id'],'a2a7')
        self.assertEqual(self.svc.dashboard(self.db,self.owner)['total_attempts'],1)

    def test_failure_not_erased_by_retry(self):
        e=self.reflect(self.demo_review())
        failed=self.svc.attempt(self.db,self.owner,e['id'],'a2b2')
        self.assertFalse(failed['complete'])
        self.svc.attempt(self.db,self.owner,e['id'],'a2a7')
        d=self.svc.dashboard(self.db,self.owner)
        self.assertEqual(d['total_attempts'],1)
        self.assertFalse(d['attempts'][0]['correct'])
        self.assertEqual(d['skills'][0]['stability'],1)

    def test_illegal_attempt_no_record(self):
        e=self.reflect(self.demo_review())
        with self.assertRaises(ValueError):self.svc.attempt(self.db,self.owner,e['id'],'a2b3')
        self.assertEqual(self.svc.dashboard(self.db,self.owner)['total_attempts'],0)

    def test_review_idempotent(self):
        game=self.svc.new_game(self.db,self.owner,{'mode':'demo'})
        first=self.svc.review(self.db,self.owner,game['id'])
        second=self.svc.review(self.db,self.owner,game['id'])
        self.assertEqual(first,second)
        self.assertEqual(len(self.repo.list(self.db,self.owner,'exercise')),1)

    def test_guest_isolation(self):
        e=self.demo_review()
        with self.assertRaises(LookupError):self.repo.get(self.db,'someone-else','exercise',e['id'])
        self.assertEqual(self.repo.export(self.db,'someone-else'),[])

    def test_persistence_restart(self):
        e=self.reflect(self.demo_review())
        self.svc.attempt(self.db,self.owner,e['id'],'a2a7')
        self.db.commit()
        reloaded=Repository(self.path)
        with reloaded.connect() as db:
            self.assertEqual(Service(reloaded).dashboard(db,self.owner)['total_attempts'],1)

    def test_hint_marks_assisted(self):
        e=self.svc.practice(self.db,self.owner,{'skill':'horse'})
        self.reflect(e)
        self.svc.hint(self.db,self.owner,e['id'])
        answer=self.svc.engine.analyze(e['fen'])['lines'][0]['move']
        self.svc.attempt(self.db,self.owner,e['id'],answer)
        d=self.svc.dashboard(self.db,self.owner)
        self.assertTrue(d['attempts'][0]['assisted'])
        self.assertEqual(d['transfer_total'],0)

    def test_feedback_persisted(self):
        e=self.demo_review()
        self.svc.dispatch(self.db,self.owner,'/api/feedback',{'id':e['id'],'message':'Please verify this position'})
        self.assertEqual(len(self.repo.list(self.db,self.owner,'feedback')),1)

    def test_export_delete(self):
        self.demo_review()
        self.assertGreater(len(self.repo.export(self.db,self.owner)),0)
        self.svc.dispatch(self.db,self.owner,'/api/delete',{'confirmation':'DELETE'})
        self.assertEqual(self.repo.export(self.db,self.owner),[])

    def test_invalid_import_atomic(self):
        with self.assertRaises(ValueError):self.svc.new_game(self.db,self.owner,{'mode':'import','moves':'a3a4 a9a0'})
        self.assertEqual(self.repo.list(self.db,self.owner,'game'),[])

    def test_illegal_game_move_preserves_history(self):
        g=self.svc.new_game(self.db,self.owner,{'mode':'local'})
        with self.assertRaises(ValueError):self.svc.move(self.db,self.owner,g['id'],'a0a9')
        saved=self.repo.get(self.db,self.owner,'game',g['id'])
        self.assertEqual(saved['history'],[])
        self.assertEqual(saved['fen'],START_FEN)

    def test_bot_and_import(self):
        g=self.svc.new_game(self.db,self.owner,{'mode':'bot'})
        g=self.svc.move(self.db,self.owner,g['id'],'b0c2')
        g=self.svc.bot(self.db,self.owner,g['id'])
        self.assertEqual(g['turn'],'w')
        replay=self.svc.new_game(self.db,self.owner,{'mode':'import','moves':' '.join(h['move'] for h in g['history'])})
        self.assertEqual(replay['fen'],g['fen'])

    def test_provider_failure_and_invention_fall_back(self):
        e=self.demo_review()
        facts=self.repo.get(self.db,self.owner,'exercise',e['id'])
        class Broken:
            def explain(self,*args):raise RuntimeError('offline')
        class Invented:
            def explain(self,*args):return {'move':'a2a9','why':'guaranteed mate'}
        for provider in (Broken(),Invented()):
            result=explain_grounded(facts,REFLECTION,provider)
            self.assertTrue(result['provider_error'])
            self.assertEqual(result['move'],'a2a7')

    def test_no_false_mistake_required(self):
        g=self.svc.new_game(self.db,self.owner,{'mode':'import','fen':PUZZLES[0]['fen'],'moves':'a2a7'})
        moment=self.svc.review(self.db,self.owner,g['id'])['moments'][0]
        self.assertEqual(moment['severity'],'explore')

    def test_due_queue_uses_actual_dates(self):
        self.repo.put(self.db,self.owner,'skill','testskill',dict(skill='horse',name='Mã',mastery_score=40,next_review_at='2020-01-01T00:00:00+00:00'))
        self.assertEqual(len(self.svc.dashboard(self.db,self.owner)['due']),1)


if __name__=='__main__':unittest.main()
