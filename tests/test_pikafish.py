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
import threading

import random

from app.pikafish import (AnalysisEngine, BOT_LEVELS, EngineConfig, EngineUnavailable, _EngineQueue,
                         choose_level_move, immediate_mates)
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
        if mode == 'slow':
            time.sleep(0.4)
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


class FakeEngineCase(unittest.TestCase):
    """A temporary folder with the fake UCI engine and its command log."""

    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='var/tests')
        self.root = Path(self.temp.name).resolve()
        self.script = self.root / 'fake_uci.py'
        self.script.write_text(FAKE_UCI, encoding='utf-8')
        self.log = self.root / 'commands.jsonl'

    def tearDown(self):
        self.temp.cleanup()

    def engine(self, mode='normal', queue=None, **options):
        handshake_seconds = options.pop('handshake_seconds', 2.0)
        request_seconds = options.pop('request_seconds', 10.0)
        config = EngineConfig(command=(sys.executable, str(self.script), mode, str(self.log)),
                              quick_ms=50, deep_ms=100, handshake_seconds=handshake_seconds,
                              request_seconds=request_seconds, **options)
        engine = AnalysisEngine(config, LocalEngine(max_depth=1, seconds=.1), queue=queue or _EngineQueue())
        self.addCleanup(engine.close)
        return engine

    def commands(self):
        return [json.loads(line) for line in self.log.read_text(encoding='utf-8').splitlines()]

class PikafishAdapterTests(FakeEngineCase):
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
        engine = self.engine()
        result = engine.analyze(START_FEN)
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
        self.assertNotEqual(commands[-1], 'quit', 'the process stays alive for the next request')
        engine.close()
        self.assertEqual(self.commands()[-1], 'quit')
        self.assertIsNone(engine._process)

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
                result = self.engine(mode, handshake_seconds=.4, request_seconds=2.0).analyze(START_FEN)
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

    def test_queue_refuses_full_duplicate_owner_and_too_late_requests_at_once(self):
        queue = _EngineQueue(limit=1)
        running = queue.enter(2, 'scan-owner', 8.0, time.monotonic() + 9)   # a long search is running
        engine = self.engine(queue=queue, request_seconds=10.0)
        started = time.monotonic()
        with self.assertRaisesRegex(EngineUnavailable, 'busy'):
            engine.analyze(START_FEN, purpose='review-scan', owner='scan-owner')   # same owner
        short = self.engine(queue=queue, request_seconds=2.0)
        with self.assertRaisesRegex(EngineUnavailable, 'busy'):
            short.analyze(START_FEN, purpose='bot', owner='someone')   # cannot finish within 2 s
        self.assertLess(time.monotonic() - started, 1.0, 'refused at once, not after waiting')
        waiter = threading.Thread(target=lambda: engine.analyze(START_FEN, purpose='bot', owner='a'), daemon=True)
        waiter.start()
        time.sleep(.2)
        self.assertEqual(queue.snapshot(), {'waiting': 1, 'running': True, 'limit': 1})
        with self.assertRaisesRegex(EngineUnavailable, 'busy'):
            engine.analyze(START_FEN, purpose='bot', owner='b')   # queue full
        queue.leave(running)
        waiter.join(5)
        self.assertEqual(queue.snapshot(), {'waiting': 0, 'running': False, 'limit': 1})
        self.assertIn('go movetime 50', self.commands(), 'the queued bot request ran after the long search')

    def test_one_long_lived_process_is_reused_then_replaced(self):
        engine = self.engine()
        for _ in range(3):
            self.assertFalse(engine.analyze(START_FEN)['fallback'])
        commands = self.commands()
        self.assertEqual(commands.count('uci'), 1, 'the engine and its network load once')
        self.assertEqual(commands.count('ucinewgame'), 1 + 3, 'one at start-up, then one per request (empty hash)')
        engine.config = EngineConfig(**{**engine.config.__dict__, 'max_searches': 3})
        self.assertFalse(engine.analyze(START_FEN)['fallback'])
        self.assertEqual(self.commands().count('uci'), 2, 'replaced after max_searches')

    def test_a_failed_process_is_not_reused(self):
        engine = self.engine('exit')
        for expected_starts in (1, 2):
            result = engine.analyze(START_FEN)
            self.assertEqual(result['fallback_reason'], 'process_exited')
            self.assertEqual(self.commands().count('uci'), expected_starts)
        self.assertIsNone(engine._process)

    def test_bot_moves_go_before_waiting_scans(self):
        queue = _EngineQueue()
        engine = self.engine('slow', queue=queue)
        finished = []
        def run(purpose, owner):
            engine.analyze(START_FEN, purpose=purpose, owner=owner)
            finished.append(purpose)
        first = threading.Thread(target=run, args=('review-scan', 'a'))
        first.start()
        time.sleep(.2)                      # the first scan is running
        scan = threading.Thread(target=run, args=('review-scan', 'b'))
        scan.start()
        time.sleep(.1)
        bot = threading.Thread(target=run, args=('bot', 'c'))
        bot.start()
        for t in (first, scan, bot):
            t.join(10)
        self.assertEqual(finished, ['review-scan', 'bot', 'review-scan'])

    def test_terminal_position_uses_rules_not_invented_score(self):
        fen = '4k4/9/9/9/9/9/9/3rpr3/9/4K4 w'
        result = self.engine().analyze(fen)
        self.assertEqual(result['status'], 'terminal')
        self.assertEqual(result['outcome']['winner'], 'b')
        self.assertIsNone(result['score'])
        self.assertIsNone(result['best_move'])
        self.assertFalse(self.log.exists())


MATE_IN_ONE = '3k5/2P6/3P5/9/9/9/9/9/9/4K4 w'      # Soldier lesson net: three mates in one
ONLY_MOVE = '5k3/9/9/9/4r4/9/9/9/9/3K5 w'          # the Red General has one legal move


def line(move, score, kind='cp'):
    return {'move': move, 'score': score, 'score_type': kind}


class BotLevelTests(FakeEngineCase):
    """J2 (docs/BOT_LEVELS.md section 3): uncalibrated levels, honest labels, rules first."""

    def test_level_table_grows_monotonically_and_ends_at_full_strength(self):
        nodes = [BOT_LEVELS[n][0] for n in range(1, 7)]
        self.assertEqual(nodes, sorted(nodes))
        caps = [BOT_LEVELS[n][3] for n in range(1, 8)]
        self.assertEqual(caps, sorted(caps, reverse=True))
        self.assertEqual(BOT_LEVELS[7], (None, 1, None, 0))

    def test_choice_respects_the_loss_cap_and_prefers_better_lines(self):
        lines = [line('a', 100), line('b', 40), line('c', -50), line('d', -400)]
        rng = random.Random(7)
        for level in range(1, 8):
            cap = BOT_LEVELS[level][3]
            for _ in range(200):
                chosen, rank, loss = choose_level_move(lines, level, rng)
                self.assertLessEqual(loss, cap, level)
                self.assertEqual(lines[rank - 1]['move'], chosen['move'])
        picks = [choose_level_move(lines, 7, rng)[0]['move'] for _ in range(50)]
        self.assertEqual(set(picks), {'a'}, 'level 7 always plays the best line')
        counts = {m: 0 for m in 'abcd'}
        for _ in range(2000):
            counts[choose_level_move(lines, 5, rng)[0]['move']] += 1
        self.assertGreater(counts['a'], counts['b'])
        self.assertEqual(counts['c'] + counts['d'], 0, 'beyond the 100 cp cap of level 5')
        uniform = {m: 0 for m in 'abcd'}
        for _ in range(3000):
            uniform[choose_level_move(lines, 1, rng)[0]['move']] += 1
        self.assertEqual(uniform['d'], 0, 'level 1 still never loses more than 400 cp')
        self.assertTrue(all(800 < uniform[m] < 1200 for m in 'abc'), uniform)

    def test_mates_are_valued_above_any_score_and_avoid_is_honoured(self):
        lines = [line('m', 2, 'mate'), line('x', 900), line('y', -3, 'mate')]
        self.assertEqual(choose_level_move(lines, 6, random.Random(1))[0]['move'], 'm')
        chosen = choose_level_move([line('m', 1, 'mate'), line('x', 30)], 1, random.Random(1), avoid=('m',))[0]
        self.assertEqual(chosen['move'], 'x')
        alone = choose_level_move([line('m', 1, 'mate')], 1, random.Random(1), avoid=('m',))[0]
        self.assertEqual(alone['move'], 'm', 'avoid never leaves the bot without a move')

    def test_mate_in_one_and_forced_moves_need_no_engine(self):
        state = Position.from_fen(MATE_IN_ONE)
        mates = immediate_mates(state)
        self.assertIn('d7d8', mates)
        for move in mates:
            after = state.play(move)
            self.assertTrue(after.in_check() and not after.legal_moves())
        engine = self.engine()
        for level in range(2, 8):
            result = engine.analyze(MATE_IN_ONE, purpose='bot', level=level)
            self.assertIn(result['best_move'], mates)
            self.assertEqual((result['bot']['reason'], result['fallback']), ('mate_in_one', False))
        forced = engine.analyze(ONLY_MOVE, purpose='bot', level=3)
        self.assertEqual((forced['best_move'], forced['bot']['reason']), ('d0d1', 'only_legal_move'))
        self.assertIn('chưa hiệu chỉnh', forced['warnings'][0])
        self.assertFalse(self.log.exists(), 'the rules answered; the engine was never started')

    def test_level_one_sometimes_passes_over_a_mate_in_one(self):
        engine = self.engine()
        engine.rng = random.Random(0)
        engine.rng.random = lambda: 0.9          # takes the mate
        self.assertEqual(engine.analyze(MATE_IN_ONE, purpose='bot', level=1)['bot']['reason'], 'mate_in_one')
        engine.rng.random = lambda: 0.1          # misses it: the engine is asked instead
        engine.analyze(MATE_IN_ONE, purpose='bot', level=1)
        self.assertIn('go nodes 2000 movetime 3000', self.commands())

    def test_levels_use_node_limits_multipv_and_label_the_result(self):
        engine = self.engine()
        result = engine.analyze(START_FEN, purpose='bot', level=3)
        self.assertFalse(result['fallback'])
        self.assertIn(result['best_move'], {'b0c2', 'h0g2'})
        self.assertEqual({k: result['bot'][k] for k in ('level', 'nodes_limit', 'multipv', 'calibrated')},
                         {'level': 3, 'nodes_limit': 10000, 'multipv': 4, 'calibrated': False})
        self.assertIn('go nodes 10000 movetime 3000', self.commands())
        self.assertIn('setoption name MultiPV value 4', self.commands())
        top = engine.analyze(START_FEN, purpose='bot', level=7)
        self.assertEqual((top['best_move'], top['bot']['rank']), ('b0c2', 1))
        self.assertIn('go movetime 50', self.commands())

    def test_invalid_levels_are_rejected_before_any_search(self):
        engine = self.engine()
        for bad in (0, 8, True, '3', 2.0):
            with self.subTest(level=bad), self.assertRaises(ValueError):
                engine.analyze(START_FEN, purpose='bot', level=bad)
        self.assertFalse(self.log.exists())


if __name__ == '__main__':
    unittest.main()
