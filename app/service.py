"""Application use cases; HTTP and UI do not implement chess or scoring rules."""
from uuid import uuid4
from app.rules import START_FEN, Position, describe, parse_move
from app.engine import LocalEngine, validate_analysis
from app.learning import SKILLS, LESSONS, diagnose, explain_grounded, now_iso, recommend, schedule
from app.puzzles import PUZZLES


def ident():
    return uuid4().hex


def text(value, limit=1500):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'Vui lòng nhập câu trả lời (tối đa {limit} ký tự). Bạn có thể viết “Chưa biết”.')
    return value.strip()


class Service:
    def __init__(self, repository, engine=None, provider=None):
        self.repo = repository
        self.engine = engine or LocalEngine()
        self.provider = provider

    def analysis(self, fen):
        return validate_analysis(Position.from_fen(fen), self.engine.analyze(fen))

    def game_view(self, game):
        pos = Position.from_fen(game['fen'])
        status = pos.status()
        if game.get('closed') and not status['over']:
            status = dict(over=True, winner=None, reason=game.get('end_reason', 'Đã kết thúc để học'))
        return {**game, 'board': list(pos.board), 'turn': pos.turn, 'legal': [] if status['over'] else pos.legal_moves(), 'status': status}

    def new_game(self, db, owner, data):
        mode = data.get('mode', 'bot')
        if mode not in ('bot', 'local', 'demo', 'import'):
            raise ValueError('Chế độ không hợp lệ.')
        fen = START_FEN
        moves = []
        if mode == 'demo':
            fen = PUZZLES[0]['fen']
            moves = ['a2b2', 'a7a2']
        elif mode == 'import':
            fen = data.get('fen', START_FEN)
            raw = data.get('moves', '')
            if not isinstance(raw, str) or len(raw) > 3000:
                raise ValueError('Biên bản quá dài.')
            moves = raw.split()
        if len(moves) > 120:
            raise ValueError('Prototype nhận tối đa 120 nửa nước.')
        pos = Position.from_fen(fen)
        game = dict(id=ident(), initial_fen=pos.fen(), fen=pos.fen(), mode=mode, history=[], closed=False, created_at=now_iso(), source='synthetic-codex-v1' if mode == 'demo' else 'local-user')
        for move in moves:
            self.append_move(game, move)
        if mode in ('demo', 'import'):
            game['closed'] = True
        self.repo.put(db, owner, 'game', game['id'], game)
        return self.game_view(game)

    def append_move(self, game, move):
        if game['closed']:
            raise ValueError('Ván cờ đã kết thúc.')
        pos = Position.from_fen(game['fen'])
        after = pos.play(move)
        game['history'].append(dict(move=move, fen=pos.fen(), after=after.fen(), label=describe(pos, move), turn=pos.turn))
        game['fen'] = after.fen()
        positions = [game['initial_fen']] + [h['after'] for h in game['history']]
        if positions.count(after.fen()) >= 3:
            game.update(closed=True, end_reason='Dừng lặp thế 3 lần — quy ước demo, chưa xử lý luật đuổi/chiếu dai giải đấu')
        elif len(game['history']) >= 120:
            game.update(closed=True, end_reason='Giới hạn demo 120 nửa nước')

    def move(self, db, owner, gid, move):
        game = self.repo.get(db, owner, 'game', gid)
        pos = Position.from_fen(game['fen'])
        if game['mode'] == 'bot' and pos.turn != 'w':
            raise ValueError('Đang là lượt máy. Hãy bấm Máy đi.')
        self.append_move(game, move)
        self.repo.put(db, owner, 'game', gid, game)
        return self.game_view(game)

    def bot(self, db, owner, gid):
        game = self.repo.get(db, owner, 'game', gid)
        pos = Position.from_fen(game['fen'])
        if game['mode'] != 'bot' or pos.turn != 'b' or game['closed']:
            raise ValueError('Không phải lượt máy.')
        analysis = self.analysis(pos.fen())
        if analysis['lines']:
            self.append_move(game, analysis['lines'][0]['move'])
            self.repo.put(db, owner, 'game', gid, game)
        return self.game_view(game)

    def create_exercise(self, db, owner, fen, skill, kind, **extras):
        analysis = self.analysis(fen)
        if not analysis['lines']:
            raise ValueError('Thế cờ này đã hết nước hợp lệ.')
        exercise = dict(id=ident(), fen=fen, skill=skill, kind=kind, analysis=analysis,
                        reflection=None, revealed=False, complete=False, hints=0, created_at=now_iso(), **extras)
        self.repo.put(db, owner, 'exercise', exercise['id'], exercise)
        return exercise

    def exercise_view(self, exercise):
        pos = Position.from_fen(exercise['fen'])
        allowed = ('id', 'fen', 'skill', 'kind', 'reflection', 'draft', 'revealed', 'complete', 'hints', 'title', 'played', 'ply', 'severity', 'unseen', 'source', 'result', 'game_id')
        view = {k: exercise[k] for k in allowed if k in exercise}
        view.update(board=list(pos.board), turn=pos.turn, legal=pos.legal_moves(), skill_name=SKILLS[exercise['skill']])
        if exercise['revealed']:
            view['explanation'] = explain_grounded(exercise, exercise['reflection'], self.provider)
            view['analysis'] = {**exercise['analysis'], 'lines': exercise['analysis']['lines'][:3]}
        return view

    def review(self, db, owner, gid):
        game = self.repo.get(db, owner, 'game', gid)
        if game.get('review_ids'):
            return self.review_view(db, owner, game)
        if not game['history']:
            raise ValueError('Hãy đi ít nhất một nước hoặc tải ván minh họa.')
        game['closed'] = True
        ranked, timeline = [], []
        # Bounded review: the most recent 24 learner moves; disclose coverage.
        learner_moves = [(i, h) for i, h in enumerate(game['history']) if h['turn'] == 'w'][-24:]
        for i, history in learner_moves:
            analysis = self.analysis(history['fen'])
            line = next(x for x in analysis['lines'] if x['move'] == history['move'])
            loss = max(0, analysis['score'] - line['score'])
            diagnostic = diagnose(Position.from_fen(history['fen']), history['move'], loss)
            timeline.append(dict(ply=i + 1, loss=loss, depth=analysis['depth']))
            ranked.append((loss, i, history, diagnostic))
        if not ranked:
            raise ValueError('Biên bản chưa có nước Đỏ để xem lại.')
        ranked.sort(key=lambda x: (-x[0], x[1]))
        selected = [x for x in ranked if x[0] >= 100][:3] or ranked[:1]
        exercises = []
        for loss, i, history, diagnostic in selected:
            exercise = self.create_exercise(db, owner, history['fen'], diagnostic['skill'], 'review',
                                           played=history['move'], ply=i + 1, severity=diagnostic['severity'], game_id=gid,
                                           title=f'Nước {i + 1} · ' + ('Điểm cần xem lại' if loss >= 100 else 'Cùng suy nghĩ lại'),
                                           source=game['source'], family='loose-rook' if game['mode'] == 'demo' else None,
                                           unseen=False)
            exercises.append(exercise)
        game['review_ids'] = [e['id'] for e in exercises]
        game['timeline'] = timeline
        game['review_coverage'] = len(learner_moves)
        self.repo.put(db, owner, 'game', gid, game)
        return self.review_view(db, owner, game)

    def review_view(self, db, owner, game):
        return dict(game_id=game['id'], coverage=game['review_coverage'],
                    moments=[self.exercise_view(self.repo.get(db, owner, 'exercise', eid)) for eid in game['review_ids']])

    def save_draft(self, db, owner, eid, data):
        exercise = self.repo.get(db, owner, 'exercise', eid)
        # A delayed autosave must never replace the submitted reflection.
        if exercise['reflection']:
            return {'saved': False, 'submitted': True}
        draft = {}
        for key in ('evaluation', 'threat', 'plan'):
            value = data.get(key, '')
            if not isinstance(value, str) or len(value) > 1500:
                raise ValueError('Bản nháp cần là văn bản, tối đa 1500 ký tự mỗi câu.')
            draft[key] = value
        draft['confidence'] = data.get('confidence', 'unsure')
        if draft['confidence'] not in ('unsure', 'some', 'sure'):
            raise ValueError('Mức tự tin không hợp lệ.')
        exercise['draft'] = draft
        self.repo.put(db, owner, 'exercise', eid, exercise)
        return {'saved': True, 'submitted': False}

    def reflect(self, db, owner, eid, data):
        exercise = self.repo.get(db, owner, 'exercise', eid)
        if exercise['reflection']:
            return self.exercise_view(exercise)
        reflection = {key: text(data.get(key)) for key in ('evaluation', 'threat', 'plan')}
        reflection['confidence'] = data.get('confidence', 'unsure')
        if reflection['confidence'] not in ('unsure', 'some', 'sure'):
            raise ValueError('Mức tự tin không hợp lệ.')
        exercise['reflection'] = reflection
        exercise.pop('draft', None)
        exercise['revealed'] = exercise['kind'] == 'review'
        self.repo.put(db, owner, 'exercise', eid, exercise)
        return self.exercise_view(exercise)

    def hint(self, db, owner, eid):
        exercise = self.repo.get(db, owner, 'exercise', eid)
        if not exercise['reflection']:
            raise ValueError('Hãy tự suy nghĩ trước khi xem gợi ý.')
        exercise['hints'] = min(2, exercise['hints'] + 1)
        if exercise['hints'] == 2:
            exercise['revealed'] = True
        self.repo.put(db, owner, 'exercise', eid, exercise)
        return {**self.exercise_view(exercise), 'hint': LESSONS[exercise['skill']]}

    def attempt(self, db, owner, eid, move):
        exercise = self.repo.get(db, owner, 'exercise', eid)
        if not exercise['reflection']:
            raise ValueError('Cần trả lời phần tự suy nghĩ trước khi thử nước đi.')
        pos = Position.from_fen(exercise['fen'])
        pos.play(move)  # reject invalid move before any persistence
        if exercise['complete']:
            return self.exercise_view(exercise)
        best = exercise['analysis']['score']
        score = next(x['score'] for x in exercise['analysis']['lines'] if x['move'] == move)
        correct = score == best
        assisted = exercise['revealed'] or exercise['hints'] > 0 or exercise.get('attempted', False)
        first = not exercise.get('attempted')
        exercise['attempted'] = True
        exercise['complete'] = correct
        exercise['revealed'] = True
        if first:
            skill_id = owner + ':' + exercise['skill']
            try:
                previous = self.repo.get(db, owner, 'skill', skill_id)
            except LookupError:
                previous = {}
            updated = schedule(previous, correct, assisted, exercise.get('unseen', False))
            updated.update(skill=exercise['skill'], name=SKILLS[exercise['skill']])
            self.repo.put(db, owner, 'skill', skill_id, updated)
            attempt = dict(id=ident(), exercise_id=eid, skill=exercise['skill'], move=move, correct=correct,
                           assisted=assisted, unseen=exercise.get('unseen', False), kind=exercise['kind'],
                           puzzle_id=exercise.get('puzzle_id'), family=exercise.get('family'), reflection=exercise['reflection'],
                           created_at=now_iso(), next_review_at=updated['next_review_at'], engine=exercise['analysis']['engine'], depth=exercise['analysis']['depth'])
            self.repo.put(db, owner, 'attempt', attempt['id'], attempt)
            exercise['due'] = updated['next_review_at']
        exercise['result'] = dict(correct=correct, move=move, score=score, next_review_at=exercise.get('due'),
                                  first_attempt=first, message=('Đúng với kết quả tìm kiếm cục bộ. Hãy chuyển cách nghĩ sang một thế cờ khác.' if correct else 'Nước này hợp lệ nhưng chưa đạt điểm cao nhất trong tìm kiếm cục bộ. Xem lời giải rồi thử lại; lần sai đầu tiên vẫn được lưu.'))
        self.repo.put(db, owner, 'exercise', eid, exercise)
        return self.exercise_view(exercise)

    def practice(self, db, owner, data):
        skill = data.get('skill', 'material')
        family = None
        if data.get('from_id'):
            source = self.repo.get(db, owner, 'exercise', data['from_id'])
            if not source['complete']:
                raise ValueError('Hãy thử lại đúng thế cờ trước khi chuyển bài.')
            skill, family = source['skill'], source.get('family')
        if skill not in SKILLS:
            raise ValueError('Kỹ năng không hợp lệ.')
        exposures = self.repo.list(db, owner, 'exercise')
        puzzle, unseen = recommend(PUZZLES, skill, exposures, family)
        exercise = self.create_exercise(db, owner, puzzle['fen'], skill, 'practice', title=puzzle['title'],
                                       puzzle_id=puzzle['id'], family=puzzle['family'], unseen=unseen, source=puzzle['source'])
        return self.exercise_view(exercise)

    def dashboard(self, db, owner):
        attempts = self.repo.list(db, owner, 'attempt')
        skills = self.repo.list(db, owner, 'skill')
        exercises = self.repo.list(db, owner, 'exercise')
        independent = [a for a in attempts if a['unseen'] and not a['assisted'] and a['kind'] == 'practice']
        due = sorted([s for s in skills if s['next_review_at'] <= now_iso()], key=lambda x: (x['next_review_at'], x['mastery_score']))[:8]
        return dict(attempts=sorted(attempts, key=lambda x: x['created_at'], reverse=True)[:20], skills=skills, due=due,
                    pending=[dict(id=e['id'], title=e['title'], kind=e['kind'], skill_name=SKILLS[e['skill']],
                                  stage='retry' if e['revealed'] else 'attempt' if e['reflection'] else 'reflection',
                                  has_draft=bool(e.get('draft'))) for e in exercises if not e['complete']][-8:][::-1],
                    total_attempts=len(attempts), transfer_total=len(independent), transfer_success=sum(a['correct'] for a in independent),
                    reviews=[dict(id=e['id'], title=e['title'], skill=e['skill'], complete=e['complete']) for e in exercises if e['kind'] == 'review'][-10:],
                    games=[dict(id=g['id'], moves=len(g['history']), mode=g['mode'], created_at=g['created_at']) for g in self.repo.list(db, owner, 'game')][-10:])

    def export(self, db, owner):
        records = self.repo.export(db, owner)
        for record in records:
            if record['kind'] == 'exercise' and not record['data']['revealed']:
                record['data'].pop('analysis', None)
        return dict(version=1, data=records)

    def dispatch(self, db, owner, path, data):
        requirements = {
            '/api/move': ('id', 'move'), '/api/bot': ('id',), '/api/review': ('id',),
            '/api/draft': ('id',), '/api/reflect': ('id',), '/api/attempt': ('id', 'move'),
            '/api/hint': ('id',), '/api/feedback': ('id',),
        }
        for key in requirements.get(path, ()):
            if not isinstance(data.get(key), str) or not data[key].strip():
                raise ValueError(f'Thiếu hoặc sai trường {key}.')
        if path == '/api/draft':
            return self.save_draft(db, owner, data['id'], data)
        if path == '/api/game':
            return self.new_game(db, owner, data)
        if path == '/api/move':
            return self.move(db, owner, data['id'], data['move'])
        if path == '/api/bot':
            return self.bot(db, owner, data['id'])
        if path == '/api/review':
            return self.review(db, owner, data['id'])
        if path == '/api/reflect':
            return self.reflect(db, owner, data['id'], data)
        if path == '/api/attempt':
            return self.attempt(db, owner, data['id'], data['move'])
        if path == '/api/practice':
            return self.practice(db, owner, data)
        if path == '/api/hint':
            return self.hint(db, owner, data['id'])
        if path == '/api/feedback':
            exercise = self.repo.get(db, owner, 'exercise', data['id'])
            record = dict(id=ident(), exercise_id=exercise['id'], message=text(data.get('message'), 2000), created_at=now_iso())
            self.repo.put(db, owner, 'feedback', record['id'], record)
            return {'saved': True}
        if path == '/api/delete':
            if data.get('confirmation') != 'DELETE':
                raise ValueError('Cần xác nhận xóa.')
            self.repo.delete_owner(db, owner)
            return {'deleted': True}
        raise LookupError('Không tìm thấy chức năng.')
