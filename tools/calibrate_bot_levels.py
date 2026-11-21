"""Calibrate the server bot levels by self-play (J4, docs/BOT_LEVELS.md section 7).

Run on a TEST machine with the real Pikafish binary, never on the production VM
(it keeps one CPU busy for a long time):

    python tools/calibrate_bot_levels.py --confirm-test-machine \
        --engine /opt/pikafish/pikafish --nnue /opt/pikafish/pikafish.nnue
    python tools/calibrate_bot_levels.py --confirm-test-machine --pairs 1-2,2-3 --games 20 --json var/calibration.json

Each pair of levels plays --games games (default 100), alternating colours, from
ten fixed openings. A game ends by checkmate or no legal moves (rules), a position
repeated three times or the ply limit (both counted as a draw by this tool; they
are not tournament rulings). A game in which the engine fell back to the basic
engine is discarded and reported: those moves were not played by the level.
Each move is asked with the current position only, as the web app does.

For each pair the report gives the higher level's score and whether it falls in
the target band (65-85 %, docs/BOT_LEVELS.md), plus time per move per level.
Results describe these engine settings on this machine only; they are not Elo.
Exit code: 0 when every pair is within the target band, 1 otherwise, 2 on setup errors.
"""
from pathlib import Path
import argparse
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.pikafish import AnalysisEngine, EngineConfig, _EngineQueue, BOT_LEVELS  # noqa: E402
from app.rules import Position, START_FEN  # noqa: E402

# Two half-moves each from the start: common first moves and replies, all legal.
OPENINGS = [
    [], ['h2e2', 'h9g7'], ['b2e2', 'b9c7'], ['c3c4', 'g6g5'], ['g3g4', 'c6c5'],
    ['h0g2', 'h9g7'], ['b0c2', 'b9c7'], ['h2f2', 'b7e7'], ['c0e2', 'h7e7'], ['b2d2', 'h9i7'],
]
TARGET = (0.65, 0.85)


def play_game(engine, red_level, black_level, opening, max_plies):
    """Returns ('w'|'b'|None, reason, plies, {level: [seconds per move]}, fell_back)."""
    pos, moves, seen, times = Position.from_fen(START_FEN), [], {}, {red_level: [], black_level: []}
    for move in opening:
        pos = pos.play(move)
        moves.append(move)
    while True:
        status = pos.status()
        if status['over']:
            return status['winner'], 'checkmate' if pos.in_check() else 'no_legal_moves', len(moves), times, False
        key = pos.fen()
        seen[key] = seen.get(key, 0) + 1
        if seen[key] >= 3:
            return None, 'repetition', len(moves), times, False
        if len(moves) >= max_plies:
            return None, 'ply_limit', len(moves), times, False
        level = red_level if pos.turn == 'w' else black_level
        started = time.monotonic()
        # The current position only, exactly as the web app asks for a bot move (no history).
        result = engine.analyze(pos.fen(), purpose='bot', level=level)
        times[level].append(time.monotonic() - started)
        if result.get('fallback') is not False or result.get('best_move') not in pos.legal_moves():
            return None, 'engine_fallback:' + str(result.get('fallback_reason')), len(moves), times, True
        moves.append(result['best_move'])
        pos = pos.play(result['best_move'])


def match(engine, low, high, games, max_plies, progress=print):
    """`games` games between two levels; the higher level plays Red in even games."""
    score, outcome, times, discarded, reasons = 0.0, {'high': 0, 'draw': 0, 'low': 0}, {low: [], high: []}, 0, {}
    for i in range(games):
        opening = OPENINGS[(i // 2) % len(OPENINGS)]
        red, black = (high, low) if i % 2 == 0 else (low, high)
        winner, reason, plies, spent, fell_back = play_game(engine, red, black, opening, max_plies)
        for level, values in spent.items():
            times[level].extend(values)
        reasons[reason] = reasons.get(reason, 0) + 1
        if fell_back:
            discarded += 1
            continue
        high_side = 'w' if red == high else 'b'
        if winner is None:
            outcome['draw'] += 1
            score += 0.5
        elif winner == high_side:
            outcome['high'] += 1
            score += 1
        else:
            outcome['low'] += 1
        if progress and (i + 1) % 10 == 0:
            progress(f'  levels {low}-{high}: {i + 1}/{games} games')
    counted = games - discarded
    share = score / counted if counted else None

    def timing(values):
        values = sorted(values)
        return {'moves': len(values), 'p50s': round(values[len(values) // 2], 3) if values else None,
                'p95s': round(values[min(len(values) - 1, int(0.95 * len(values)))], 3) if values else None}

    return {'low': low, 'high': high, 'games': games, 'counted': counted, 'discarded': discarded,
            'highWins': outcome['high'], 'draws': outcome['draw'], 'lowWins': outcome['low'],
            'highScore': None if share is None else round(share, 3),
            'inTarget': share is not None and TARGET[0] <= share <= TARGET[1],
            'endings': reasons, 'timePerMove': {str(low): timing(times[low]), str(high): timing(times[high])}}


def parse_pairs(text):
    pairs = []
    for item in text.split(','):
        low, high = (int(x) for x in item.split('-'))
        if not (low in BOT_LEVELS and high in BOT_LEVELS and low < high):
            raise ValueError(item)
        pairs.append((low, high))
    return pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--confirm-test-machine', action='store_true',
                        help='Required: this keeps a CPU busy; run it on a test machine, never on production')
    parser.add_argument('--engine', help='Pikafish binary (default: PIKAFISH_PATH)')
    parser.add_argument('--nnue', help='NNUE file (default: PIKAFISH_NNUE_PATH)')
    parser.add_argument('--pairs', default='1-2,2-3,3-4,4-5,5-6,6-7')
    parser.add_argument('--games', type=int, default=100)
    parser.add_argument('--max-plies', type=int, default=200)
    parser.add_argument('--json', help='Also write the results to this file')
    parser.add_argument('--engine-args', nargs='*', default=[], help=argparse.SUPPRESS)  # tests: fake engine arguments
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    if not args.confirm_test_machine:
        parser.error('Add --confirm-test-machine: run this on a test machine with Pikafish, never on the production VM.')
    try:
        pairs = parse_pairs(args.pairs)
    except ValueError as error:
        parser.error(f'Invalid --pairs item {error}; use low-high with levels 1-7, e.g. 1-2,2-3.')
    base = EngineConfig.from_env()
    command = (args.engine,) + tuple(args.engine_args) if args.engine else base.command
    config = EngineConfig(command=command, nnue_path=args.nnue if args.nnue is not None else base.nnue_path,
                          quick_ms=base.quick_ms, threads=1, hash_mb=base.hash_mb, request_seconds=15.0)
    if config.availability() != 'configured_unverified':
        print(f'Engine not usable ({config.availability()}). Set --engine/--nnue or PIKAFISH_PATH.', file=sys.stderr)
        return 2
    engine = AnalysisEngine(config, queue=_EngineQueue())
    results, started = [], time.monotonic()
    try:
        for low, high in pairs:
            print(f'== levels {low} vs {high}, {args.games} games', flush=True)
            result = match(engine, low, high, args.games, args.max_plies, progress=lambda line: print(line, flush=True))
            results.append(result)
            share = '—' if result['highScore'] is None else f"{result['highScore']:.0%}"
            verdict = 'in target' if result['inTarget'] else 'OUTSIDE target 65-85 %'
            print(f"  level {high}: {result['highWins']} won, {result['draws']} drawn, {result['lowWins']} lost"
                  f" ({result['counted']} counted, {result['discarded']} discarded) -> score {share}: {verdict}")
            print(f"  time per move: {result['timePerMove']}")
    finally:
        engine.close()
    report = {'tool': 'calibrate_bot_levels', 'levels': {str(k): list(v) for k, v in BOT_LEVELS.items()},
              'engine': {'nnue': bool(config.nnue_path), 'threads': 1}, 'pairs': results,
              'seconds': round(time.monotonic() - started, 1), 'note': 'Self-play on this machine; not Elo.'}
    if args.json:
        Path(args.json).write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return 0 if all(r['inTarget'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
