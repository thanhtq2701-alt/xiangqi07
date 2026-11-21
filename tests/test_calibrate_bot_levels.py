"""tools/calibrate_bot_levels.py with a fake UCI engine that plays legal moves (not Pikafish)."""
from pathlib import Path
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import calibrate_bot_levels as calibrate  # noqa: E402
from app.rules import Position, START_FEN  # noqa: E402

# Answers every search with legal moves from the project's rules. Captures score higher,
# so the lines are ordered like a (very) weak engine's would be. mode "crash" exits on go.
LEGAL_UCI = r'''
import sys
sys.path.insert(0, ROOT)
from app.rules import Position
VALUES = {'r': 900, 'c': 450, 'h': 400, 'a': 200, 'e': 200, 'p': 100, 'k': 0, '.': 0}
mode, multipv, position = sys.argv[1], 1, None
def emit(line):
    print(line, flush=True)
for raw in sys.stdin:
    line = raw.strip()
    if line == 'uci':
        emit('id name Legal test engine')
        emit('option name MultiPV type spin default 1')
        emit('uciok')
    elif line == 'isready':
        emit('readyok')
    elif line.startswith('setoption name MultiPV value '):
        multipv = int(line.split()[-1])
    elif line.startswith('position fen '):
        parts = line.split()
        board = parts[2].translate(str.maketrans('nNbB', 'hHeE'))
        position = Position.from_fen(board + ' ' + parts[3])
        if 'moves' in parts:
            for move in parts[parts.index('moves') + 1:]:
                position = position.play(move)
    elif line.startswith('go '):
        if mode == 'crash':
            sys.exit(0)
        moves = sorted(position.legal_moves(), key=lambda m: (-VALUES[position.board[(9 - int(m[3])) * 9 + ord(m[2]) - 97].lower()], m))
        for rank, move in enumerate(moves[:multipv], 1):
            emit(f'info depth 1 multipv {rank} score cp {100 - 10 * rank} nodes 10 pv {move}')
        emit('bestmove ' + moves[0])
    elif line == 'quit':
        break
'''.replace('ROOT', repr(str(ROOT)))


class CalibrateBotLevelsTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = Path(tempfile.mkdtemp(dir='var/tests'))
        self.addCleanup(shutil.rmtree, self.temp, ignore_errors=True)
        self.script = self.temp / 'legal_uci.py'
        self.script.write_text(LEGAL_UCI, encoding='utf-8')

    def run_tool(self, *args, mode='play'):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = calibrate.main(['--engine', sys.executable, '--engine-args', str(self.script), mode, *args])
            except SystemExit as exit_:
                code = exit_.code
        return code, out.getvalue(), err.getvalue()

    def test_openings_are_legal_and_distinct(self):
        self.assertEqual(len(calibrate.OPENINGS), 10)
        seen = set()
        for opening in calibrate.OPENINGS:
            pos = Position.from_fen(START_FEN)
            for move in opening:
                pos = pos.play(move)
            seen.add(pos.fen())
        self.assertEqual(len(seen), 10)

    def test_refuses_without_confirming_a_test_machine(self):
        code, _out, err = self.run_tool('--pairs', '1-2', '--games', '2')
        self.assertEqual(code, 2)
        self.assertIn('--confirm-test-machine', err)

    def test_refuses_bad_pairs_and_a_missing_engine(self):
        code, _out, err = self.run_tool('--confirm-test-machine', '--pairs', '2-2')
        self.assertEqual(code, 2)
        self.assertIn('Invalid --pairs', err)
        out, errs = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errs):
            code = calibrate.main(['--confirm-test-machine', '--engine', str(self.temp / 'missing-engine')])
        self.assertEqual(code, 2)
        self.assertIn('Engine not usable', errs.getvalue())

    def test_plays_games_alternating_colours_and_reports_the_pair(self):
        report = self.temp / 'report.json'
        code, out, _err = self.run_tool('--confirm-test-machine', '--pairs', '1-2', '--games', '4',
                                        '--max-plies', '14', '--json', str(report))
        self.assertIn(code, (0, 1))
        data = json.loads(report.read_text(encoding='utf-8'))
        pair = data['pairs'][0]
        self.assertEqual((pair['low'], pair['high'], pair['games'], pair['counted'], pair['discarded']), (1, 2, 4, 4, 0))
        self.assertEqual(pair['highWins'] + pair['draws'] + pair['lowWins'], 4)
        self.assertEqual(pair['inTarget'], 0.65 <= pair['highScore'] <= 0.85)
        self.assertGreater(pair['timePerMove']['1']['moves'], 0)
        self.assertGreater(pair['timePerMove']['2']['moves'], 0)
        self.assertEqual(data['note'], 'Self-play on this machine; not Elo.')
        self.assertIn('levels 1 vs 2', out)

    def test_games_where_the_engine_fell_back_are_discarded_not_counted(self):
        code, out, _err = self.run_tool('--confirm-test-machine', '--pairs', '2-3', '--games', '2', '--max-plies', '10',
                                        mode='crash')
        self.assertEqual(code, 1)
        self.assertIn('0 counted, 2 discarded', out)


if __name__ == '__main__':
    unittest.main()
