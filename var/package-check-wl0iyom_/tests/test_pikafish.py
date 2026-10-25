"""Protocol contract tests with a locally authored fake UCI process, not Pikafish."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from app.engine import LocalEngine
from app.pikafish import AnalysisEngine, EngineConfig, EngineUnavailable, _ENGINE_SLOT
from app.rules import Position, START_FEN


FAKE_UCI = r'''
import json
import sys
import time

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mode, log_path = sys.argv[1:3]
position = ''
def emit(line):
    print(line, flush=True)
for raw in sys.stdin:
    line = raw.strip()
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(json.dumps(line) + '\n')
    if line == 'uci':
        if mode == 'handshake_timeout':
            time.sleep(30)
        emit('id name Test UCI only 1.0')
        for name in ['Threads', 'Hash', 'Ponder', 'MultiPV', 'EvalFile']:
            emit('option name ' + name + ' type string default 1')
        emit('uciok')
    elif line == 'isready':
        if mode == 'ready_timeout':
            time.sleep(30)
        emit('readyok')
    elif line.startswith('position '):
        position = line
    elif line.startswith('go '):
        if mode == 'search_timeout':
            time.sleep(30)
        if mode == 'exit':
            sys.exit(0)
        if mode == 'output_limit':
            emit('x' * 20000)
            continue
        turn = position.split()[3]
        history = position.split(' moves ', 1)[1].split() if ' moves ' in position else []
        if len(history) % 2:
            turn = 'b' if turn == 'w' else 'w'
        chosen = line.split('searchmoves ', 1)[1] if 'searchmoves ' in line else None
        first = chosen or ('b0c2' if turn == 'w' else 'b9c7')
        second = 'h0g2' if turn == 'w' else 'h9g7'
        response = 'b9c7' if turn == 'w' else 'b0c2'
        score = '-120' if chosen else '35'
        kind = 'cp'
        if mode == 'mate':
            score, kind = '3', 'mate'
        if mode == 'negative_mate':
            score, kind = '-4', 'mate'
        if mode == 'malformed':
            score = 'NaN'
        if mode == 'illegal_pv':
            response = 'e0e9'
        if mode == 'best_mismatch':
            emit('info depth 7 multipv 1 score cp 20 nodes 100 pv ' + second)
        else:
            bound = ' lowerbound' if mode == 'bound' else ''
            emit('info depth 7 multipv 1 score ' + kind + ' ' + score + bound + ' nodes 100 pv ' + first + ' ' + response)
        if not chosen:
            emit('info depth 7 multipv 2 score cp 10 nodes 100 pv ' + second + ' ' + response)
        if mode == 'partial_iteration':
            emit('info depth 8 multipv 1 score cp 50 nodes 110 pv ' + first + ' ' + response)
        if mode == 'illegal_best':
            first = 'e0e9'
        emit('bestmove ' + first)
    elif line == 'quit':
        break
'''


class PikafishAdapterTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='var/tests')
        self.root = Path(self.temp.name).resolve()
        self.script = self.root / 'fake_uci.py'
        self.script.write_text(FAKE_UCI, encoding='utf-8')
        self.log = self.root / 'commands.jsonl'

    def tearDown(self):
        self.temp.cleanup()

    def engine(self, mode='normal', **options):
        config = EngineConfig(command=(sys.executable, str(self.script), mode, str(self.log)),
                              quick_ms=50, deep_ms=100, handshake_seconds=.4,
                              request_seconds=2.0, **options)
        return AnalysisEngine(config, LocalEngine(max_depth=1, seconds=.1))

    def commands(self):
        return [json.loads(line) for line in self.log.read_text(encoding='utf-8').splitlines()]

    def test_no_binary_is_explicit_limited_fallback(self):
        engine = AnalysisEngine(EngineConfig(), LocalEngine(max_depth=1, seconds=.1))
        result = engine.analyze(START_FEN, selected_move='a0a1')
        self.assertTrue(result['fallback'])
        self.assertEqual(result['fallback_reason'], 'not_configured')
        self.assertEqual(result['confidence'], 'limited')
        self.assertEqual(result['score_type'], 'heuristic_cp')
        self.assertEqual(result['selected']['move'], 'a0a1')
        self.assertFalse(result['search']['exhaustive_root'])
        self.assertTrue(result['warnings'])
        self.assertEqual(engine.status()['last_result'], 'fallback')

    def test_missing_configured_binary_has_no_paths_in_result(self):
        missing = str(self.root / 'private-folder-engine.exe')
        result = AnalysisEngine(EngineConfig(command=(missing,)), LocalEngine(max_depth=0)).analyze(START_FEN)
        self.assertEqual(result['fallback_reason'], 'binary_missing')
        self.assertNotIn(missing, json.dumps(result))

    def test_status_does_not_claim_verified_without_analysis(self):
        status = self.engine().status()
        self.assertEqual(status['status'], 'configured_unverified')
        self.assertTrue(status['configured'])
        self.assertFalse(status['verified'])
        self.assertFalse(self.log.exists())

    def test_handshake_fen_conversion_and_legal_candidates(self):
        result = self.engine().analyze(START_FEN)
        self.assertFalse(result['fallback'])
        self.assertEqual(result['engine_name'], 'Test UCI only 1.0')
        self.assertEqual(result['best_move'], 'b0c2')
        self.assertEqual(result['score'], 35)
        self.assertEqual(result['score_type'], 'cp')
        self.assertEqual(result['turn'], 'w')
        self.assertEqual(result['candidates'][0]['from'], 82)
        self.assertEqual(result['candidates'][0]['to'], 65)
        for candidate in result['candidates']:
            pos = Position.from_fen(START_FEN)
            for move in candidate['pv']:
                pos = pos.play(move)
        commands = self.commands()
        self.assertEqual(commands[0], 'uci')
        self.assertIn('ucinewgame', commands)
        self.assertIn('setoption name Threads value 1', commands)
        self.assertIn('setoption name Hash value 32', commands)
        self.assertIn('setoption name Ponder value false', commands)
        fen_command = next(c for c in commands if c.startswith('position '))
        self.assertIn('rnbakabnr', fen_command)
        self.assertIn('RNBAKABNR w - - 0 1', fen_command)
        self.assertEqual(commands[-1], 'quit')

    def test_selected_move_is_separately_searched_from_same_root(self):
        result = self.engine().analyze(START_FEN, selected_move='a0a1')
        self.assertEqual(result['score'], 35)
        self.assertEqual(result['selected']['score'], -120)
        self.assertEqual(result['selected']['perspective'], 'w')
        self.assertTrue(result['selected']['search']['restricted_root'])
        self.assertNotIn('a0a1', [row['move'] for row in result['candidates']])
        commands = self.commands()
        self.assertIn('go movetime 50 searchmoves a0a1', commands)
        positions = [c for c in commands if c.startswith('position ')]
        self.assertEqual(len(positions), 2)
        self.assertEqual(positions[0], positions[1])

    def test_history_replayed_and_black_score_not_flipped(self):
        result = self.engine().analyze(START_FEN, moves=['a0a1'], selected_move='a9a8')
        self.assertFalse(result['fallback'])
        self.assertEqual(result['turn'], 'b')
        self.assertEqual(result['score'], 35)
        self.assertEqual(result['selected']['score'], -120)
        self.assertEqual(result['selected']['perspective'], 'b')
        self.assertEqual(result['fen'], Position.from_fen(START_FEN).play('a0a1').fen())
        self.assertTrue(result['provenance']['repetition_history'])
        self.assertIn(' moves a0a1', next(c for c in self.commands() if c.startswith('position ')))

    def test_cp_and_mate_units_not_conflated(self):
        for mode, expected in [('mate', 3), ('negative_mate', -4)]:
            with self.subTest(mode=mode):
                result = self.engine(mode).analyze(START_FEN, moves=['a0a1'])
                self.assertFalse(result['fallback'])
                self.assertEqual(result['score_type'], 'mate')
                self.assertEqual(result['score'], expected)
                self.assertEqual(result['candidates'][0]['perspective'], 'b')

    def test_bound_is_preserved_not_exact_evaluation(self):
        result = self.engine('bound').analyze(START_FEN)
        self.assertFalse(result['fallback'])
        self.assertEqual(result['candidates'][0]['bound'], 'lowerbound')

    def test_partial_iteration_does_not_mix_depths(self):
        result = self.engine('partial_iteration').analyze(START_FEN)
        self.assertFalse(result['fallback'])
        self.assertEqual(result['search']['depth'], 8)
        self.assertEqual(len(result['candidates']), 1)
        self.assertEqual(result['score'], 50)

    def test_untrusted_or_incomplete_engine_output_falls_back(self):
        for mode, reason in [('illegal_best', 'illegal_bestmove'), ('illegal_pv', 'illegal_variation'),
                             ('malformed', 'missing_analysis'), ('best_mismatch', 'missing_analysis'),
                             ('exit', 'process_exited'), ('output_limit', 'output_limit')]:
            with self.subTest(mode=mode):
                result = self.engine(mode).analyze(START_FEN)
                self.assertTrue(result['fallback'])
                self.assertEqual(result['fallback_reason'], reason)
                self.assertIn(result['best_move'], Position.from_fen(START_FEN).legal_moves())

    def test_timeout_is_bounded_and_child_reaped(self):
        real_popen = subprocess.Popen
        children = []
        def track(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        for mode in ('handshake_timeout', 'ready_timeout', 'search_timeout'):
            started = time.monotonic()
            with patch('app.pikafish.subprocess.Popen', side_effect=track):
                result = self.engine(mode).analyze(START_FEN)
            self.assertEqual(result['fallback_reason'], 'timeout')
            self.assertLess(time.monotonic() - started, 3.5)
            self.assertIsNotNone(children[-1].poll())

    def test_invalid_fen_history_and_selected_rejected_before_launch(self):
        engine = self.engine()
        for kwargs in [dict(fen='not fen'), dict(fen=START_FEN, moves=['a0a9']),
                       dict(fen=START_FEN, moves='a0a1'), dict(fen=START_FEN, moves=['a0a1'] * 601),
                       dict(fen=START_FEN, selected_move='e0e9'), dict(fen=START_FEN, mode='infinite'),
                       dict(fen=START_FEN + ' - - 0\nquit 1')]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                engine.analyze(**kwargs)
        self.assertFalse(self.log.exists())

    def test_configuration_cannot_inject_uci_commands(self):
        self.assertEqual(EngineConfig(command=('relative.exe',)).availability(), 'invalid_configuration')
        self.assertEqual(EngineConfig(command=(sys.executable + '\nquit',)).availability(), 'invalid_configuration')
        self.assertEqual(EngineConfig(command=(sys.executable,), nnue_path='file\nquit').availability(), 'network_missing')

    def test_nnue_option_and_limit_clamps(self):
        network = self.root / 'test weights.nnue'
        network.write_bytes(b'test protocol only, not a trained network')
        engine = self.engine(nnue_path=str(network), threads=999, hash_mb=999999)
        result = engine.analyze(START_FEN, mode='deep')
        self.assertFalse(result['fallback'])
        self.assertIn(f'setoption name EvalFile value {network}', self.commands())
        self.assertIn('setoption name Threads value 2', self.commands())
        self.assertIn('setoption name Hash value 128', self.commands())
        self.assertIn('go movetime 100', self.commands())

    def test_env_config_limits_no_shell_split(self):
        config = EngineConfig.from_env({'PIKAFISH_PATH': 'C:/Engine Folder/pikafish.exe',
                                        'PIKAFISH_THREADS': '999', 'PIKAFISH_HASH_MB': '-1',
                                        'PIKAFISH_QUICK_MS': 'invalid', 'PIKAFISH_DEEP_MS': '99999'})
        self.assertEqual(config.command, ('C:/Engine Folder/pikafish.exe',))
        self.assertEqual(config.threads, 2)
        self.assertEqual(config.hash_mb, 16)
        self.assertEqual(config.quick_ms, 600)
        self.assertEqual(config.deep_ms, 5000)

    def test_second_concurrent_uci_request_is_busy(self):
        _ENGINE_SLOT.acquire()
        try:
            with self.assertRaisesRegex(EngineUnavailable, 'busy'):
                self.engine().analyze(START_FEN)
        finally:
            _ENGINE_SLOT.release()
        self.assertFalse(self.log.exists())

    def test_terminal_position_uses_rules_not_invented_score(self):
        fen = '4k4/9/9/9/9/9/9/3rpr3/9/4K4 w'
        result = self.engine().analyze(fen)
        self.assertEqual(result['status'], 'terminal')
        self.assertEqual(result['outcome']['winner'], 'b')
        self.assertIsNone(result['score'])
        self.assertIsNone(result['best_move'])
        self.assertFalse(self.log.exists())


if __name__ == '__main__':
    unittest.main()
