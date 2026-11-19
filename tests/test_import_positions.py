"""tools/import_positions.py: rules-only checks and line-v1 drafts."""
from pathlib import Path
from unittest import mock
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import import_positions as imp  # noqa: E402

NODE = shutil.which('node')
ROOKS = '3aka3/5R3/5R3/9/9/9/9/9/9/3K5 w'          # v6-rooks-palace-a root
MAIN = 'f8f9 e9e8 f9f8 e8e9 f7e7 d9e8 e7e8'
ALT = 'f8f9 e9e8 f7f8 e8e7 f9e9 d9e8 e9e8'
CHAPTERS = {'coordination': 'middle', 'rook': 'middle'}


def entry(**overrides):
    value = {'id': 'test-rooks', 'title': {'vi': 'Hai Xe', 'en': 'Two Chariots'}, 'fen': ROOKS, 'sideToMove': 'w',
             'chapterId': 'coordination', 'skill': 'safety', 'difficulty': 'intermediate', 'objective': 'mate',
             'goal': {'vi': 'Chiếu hết.', 'en': 'Checkmate.'}, 'lines': [MAIN, ALT],
             'explanation': {'what': {'vi': 'Hai Xe phối hợp.', 'en': 'Two Chariots coordinate.'}},
             'source': {'name': 'Cờ Chill tự dựng', 'nameEn': 'Created by Cờ Chill'}, 'rights': 'own-work'}
    value.update(overrides)
    return value


class ImportPositionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_file(self, positions, bank=None, write=None, node=None):
        path = self.tmp / 'positions.json'
        path.write_text(json.dumps({'format': imp.FORMAT, 'positions': positions}, ensure_ascii=False, indent=2), encoding='utf-8')
        bank = bank if bank is not None else (set(), {}, CHAPTERS)
        with mock.patch.object(imp, 'existing_bank', return_value=bank):
            return imp.run(path, write, node)

    def messages(self, report, level='error'):
        return ' | '.join(i['message'] for i in report.items if i['level'] == level)

    def test_rebuilds_the_shipped_two_rooks_tree(self):
        report, drafts = self.run_file([entry()])
        self.assertEqual(report.errors, [])
        exercise = drafts[0]['exercise']
        shipped = json.loads(subprocess.run([NODE, '-e', "process.stdout.write(JSON.stringify(require('./web/curriculum.js').findExercise('v6-rooks-palace-a')))"],
                                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True).stdout) if NODE else None
        self.assertEqual(exercise['format'], 'line-v1')
        self.assertEqual(exercise['decisions'], 4)
        self.assertEqual(exercise['exampleLine'], MAIN.split())
        self.assertEqual(exercise['pieceTags'], ['rook'])
        if shipped:
            strip = lambda nodes: {k: {f: v for f, v in n.items() if f != 'rejectedMoves'} for k, n in nodes.items()}
            self.assertEqual(strip(exercise['nodes']), strip(shipped['nodes']))
        self.assertTrue(all(n['rejectedMoves'] == [] for n in exercise['nodes'].values()))
        self.assertIn(imp.REVIEW_ENGINE, exercise['importReview']['pending'])

    @unittest.skipUnless(NODE, 'Node.js needed')
    def test_mate_draft_passes_the_app_validator_and_reads_notation(self):
        report, drafts = self.run_file([entry(lines=['Xt.1 Tg5.1 Xt/1 Tg5/1 Xs-5 S4.5 X5.1', ALT])], node=NODE)
        self.assertEqual(report.errors, [])
        self.assertEqual(drafts[0]['notation'][0], 'Xt.1 Tg5.1 Xt/1 Tg5/1 Xs-5 S4.5 X5.1'.split())
        script = "const L=require('./web/line-practice.js');let s='';process.stdin.on('data',d=>s+=d).on('end',()=>L.validate(JSON.parse(s)))"
        result = subprocess.run([NODE, '-e', script], cwd=ROOT, input=json.dumps(drafts[0]['exercise']), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(NODE, 'Node.js needed')
    def test_bad_notation_names_the_half_move(self):
        report, _ = self.run_file([entry(lines=['Xt.1 Tg5.1 P2-5'])], node=NODE)
        self.assertIn('Nửa nước 3 "P2-5"', self.messages(report))

    def test_illegal_coordinate_move_names_the_half_move(self):
        report, _ = self.run_file([entry(lines=['f8f9 e9e8 f9a0'])])
        self.assertIn('Nửa nước 3', self.messages(report))

    def test_mate_objective_requires_checkmate(self):
        report, _ = self.run_file([entry(lines=['f8f9 e9e8 f9f8'])])
        self.assertIn('chưa chiếu hết', self.messages(report))

    def test_advantage_objective_is_a_marked_draft(self):
        report, drafts = self.run_file([entry(objective='advantage', lines=['f8f9 e9e8 f9f8'], difficulty='intermediate')])
        self.assertEqual(report.errors, [])
        self.assertEqual(drafts[0]['exercise']['format'], 'line-v1-draft')
        self.assertIn(imp.REVIEW_DRAFT, drafts[0]['review'])
        self.assertIn('2 quyết định', self.messages(report, 'warning'))

    def test_line_must_end_with_learner_move(self):
        report, _ = self.run_file([entry(lines=['f8f9 e9e8'])])
        self.assertIn('số nửa nước lẻ', self.messages(report))

    def test_one_reply_per_accepted_move(self):
        start = imp.board_key('rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w')
        report, _ = self.run_file([entry(fen=start, objective='advantage', lines=['h2e2 h9g7 h0g2', 'h2e2 b9c7 h0g2'])])
        self.assertIn('một nước đáp', self.messages(report))

    def test_wrong_field_types_are_reported_not_crashing(self):
        report, _ = self.run_file([entry(chapterId=['rook'], difficulty={'x': 1}, objective=[], phase=[], fen=5, lines='f8f9'), 'text'])
        text = self.messages(report)
        for expected in ('chapterId', 'difficulty', 'objective', 'phase', 'FEN', 'object JSON'):
            self.assertIn(expected, text)

    def test_side_to_move_must_match(self):
        report, _ = self.run_file([entry(sideToMove='b')])
        self.assertIn('sideToMove không khớp', self.messages(report))

    def test_duplicates_exact_mirrored_and_colour_swapped(self):
        key = imp.board_key(ROOKS)
        report, _ = self.run_file([entry()], bank=({'x'}, {key: 'bài A'}, CHAPTERS))
        self.assertIn('Trùng thế với bài A', self.messages(report))
        for variant in (imp.mirrored(key), imp.colour_swapped(key)):
            report, _ = self.run_file([entry()], bank=(set(), {variant: 'bài B'}, CHAPTERS))
            self.assertIn('Gần trùng', self.messages(report, 'warning'))
        report, _ = self.run_file([entry(), entry(id='test-rooks-2')])
        self.assertIn('trong file', self.messages(report))

    def test_colour_swap_is_a_real_position(self):
        swapped = imp.colour_swapped(imp.board_key(ROOKS))
        self.assertEqual(imp.board_key(swapped), swapped)
        self.assertEqual(imp.colour_swapped(swapped), imp.board_key(ROOKS))

    def test_ids_and_rights(self):
        report, _ = self.run_file([entry(id='v6-rooks-palace-a')], bank=({'v6-rooks-palace-a'}, {}, CHAPTERS))
        self.assertIn('id đã có', self.messages(report))
        report, _ = self.run_file([entry(rights='unknown')])
        self.assertIn('rights phải là', self.messages(report))
        report, _ = self.run_file([entry(rights='permission')])
        self.assertIn('rightsNote', self.messages(report))

    def test_missing_english_is_flagged(self):
        report, drafts = self.run_file([entry(title='Hai Xe', goal='Chiếu hết.')])
        self.assertEqual(report.errors, [])
        self.assertIn('goal, title', self.messages(report, 'warning'))
        self.assertEqual(drafts[0]['contentEn']['exercises#test-rooks.goal'], {'vi': 'Chiếu hết.', 'en': ''})

    def test_dry_run_writes_nothing_and_write_needs_no_errors(self):
        out = self.tmp / 'out'
        self.run_file([entry()])
        self.assertFalse(out.exists())
        report, _ = self.run_file([entry(rights='unknown')], write=out)
        self.assertTrue(report.errors)
        self.assertFalse(out.exists())
        self.run_file([entry()], write=out)
        self.assertEqual(sorted(p.name for p in out.iterdir()), ['content-en.json', 'exercises.json', 'report.json'])
        content = json.loads((out / 'content-en.json').read_text(encoding='utf-8'))
        self.assertEqual(content['exercises#test-rooks.what']['en'], 'Two Chariots coordinate.')

    def test_never_writes_into_web(self):
        with self.assertRaises(SystemExit):
            self.run_file([entry()], write=ROOT / 'web' / 'imported')
        self.assertFalse((ROOT / 'web' / 'imported').exists())

    def test_real_bank_flags_the_shipped_exercise(self):
        report, _ = self.run_file([entry()], bank=imp.existing_bank())
        self.assertIn('v6-rooks-palace-a', self.messages(report))
        self.assertIn('coordination', imp.existing_bank()[2])

    def test_cli_exit_codes(self):
        bad = self.tmp / 'bad.json'
        bad.write_text('{not json', encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(imp.main([str(bad)]), 2)
            bad.write_text(json.dumps({'format': 'other'}), encoding='utf-8')
            self.assertEqual(imp.main([str(bad)]), 1)


if __name__ == '__main__':
    unittest.main()
