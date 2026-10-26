"""Parity check the browser rules/search against the existing Python reference.

No browser, downloaded dependencies, or network required. Fixtures are generated
in memory from the authoritative project rules; no copied third-party games.
Usage: python tools/check_browser_rules.py [--node PATH_TO_MODERN_NODE]
"""
import argparse
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.rules import Position, START_FEN, index
from app.engine import LocalEngine, evaluate
from app.puzzles import PUZZLES


def setup(pieces, turn='w'):
    board = ['.'] * 90
    for sq, piece in {'e0': 'K', 'e9': 'k', 'e4': 'P', **pieces}.items():
        board[index(sq)] = piece
    return Position(tuple(board), turn)


def fixtures():
    cases = [('initial', Position.from_fen(START_FEN))]
    cases.extend((p['id'], Position.from_fen(p['fen'])) for p in PUZZLES)
    edge_cases = [
        ('general-palace', {}),
        ('general-palace-edge', {'e0': '.', 'd0': 'K'}),
        ('advisor', {'d0': 'A'}),
        ('elephant-open-eye', {'c0': 'E'}),
        ('elephant-blocked-eye', {'c0': 'E', 'd1': 'R'}),
        ('elephant-river', {'c4': 'E'}),
        ('rook-blocker', {'a1': 'R', 'a3': 'P', 'd1': 'r'}),
        ('cannon-no-screen', {'a1': 'C', 'a6': 'r'}),
        ('cannon-one-screen', {'a1': 'C', 'a6': 'r', 'a3': 'P'}),
        ('cannon-two-screens', {'a1': 'C', 'a6': 'r', 'a3': 'P', 'a4': 'p'}),
        ('cannon-empty-jump', {'a1': 'C', 'a3': 'p'}),
        ('pawn-before-river', {'a3': 'P'}),
        ('pawn-after-river', {'b5': 'P'}),
        ('pawn-last-rank', {'b9': 'P'}),
        ('flying-general-blocker', {}),
        ('facing-generals-no-capture', {'e4': '.'}),
        ('self-check', {'a0': 'r', 'b0': 'R'}),
        ('check-must-respond', {'a0': 'r', 'b3': 'R'}),
        ('stalemate-loss', {'d2': 'r', 'f2': 'r', 'e2': 'p', 'e4': '.'}),
        ('checkmate-loss', {'d1': 'r', 'f1': 'r', 'e1': 'p', 'e4': '.'}),
    ]
    for dest, leg in [('d5', 'c4'), ('b5', 'c4'), ('e4', 'd3'), ('e2', 'd3'), ('d1', 'c2'), ('b1', 'c2'), ('a2', 'b3'), ('a4', 'b3')]:
        base = {'c3': 'H', 'e4': '.', 'e5': 'P'}
        edge_cases.extend([(f'horse-open-{dest}', base), (f'horse-blocked-{dest}', {**base, leg: 'P'})])
    for name, pieces in edge_cases:
        pos = setup(pieces)
        cases.append((name, pos))
        cases.append((name + '-black', Position(tuple(p.swapcase() for p in reversed(pos.board)), 'b')))
    # Deterministic, generated legal games cover dense positions and both turns.
    for seed in range(4):
        rng = random.Random(seed + 1904)
        pos = Position.from_fen(START_FEN)
        for ply in range(30):
            moves = pos.legal_moves()
            if not moves:
                break
            pos = pos.play(rng.choice(moves))
            cases.append((f'generated-{seed}-{ply + 1}', pos))
    result = []
    for name, pos in cases:
        moves = pos.legal_moves()
        try:
            Position.from_fen(pos.fen())
            fen_valid = True
        except ValueError:
            fen_valid = False
        result.append(dict(name=name, board=pos.board, turn=pos.turn, fen=pos.fen(), fenValid=fen_valid,
                           targets=[pos.targets(i) for i in range(90)], legal=sorted(moves),
                           checks={c: pos.in_check(c) for c in ('w', 'b')}, status=pos.status(),
                           evaluation=evaluate(pos), children={m: pos.play(m).fen() for m in moves}))
    return result


def fen_cases():
    candidates = [
        None, 15, '', '9/9 w', START_FEN + ' ' * 201,
        START_FEN.replace(' w', ' x'), START_FEN.replace('K', 'R'),
        START_FEN.replace('9', '8', 1), START_FEN.replace('9', '0', 1),
        '9/9/9/9/9/9/9/9/9/9 w', setup({'e4': '.'}).fen(),
        setup({'b6': 'p'}).fen(), setup({'c0': '.', 'c2': 'E'}).fen(),
        setup({'e0': '.', 'c0': 'K'}).fen(), setup({'e1': 'A', 'd0': 'A', 'f0': 'A'}).fen(),
        setup({'e2': 'A'}).fen(), setup({'a1': 'P'}).fen(),
        setup({'a2': 'R', 'b2': 'R', 'c2': 'R'}).fen(),
        setup({'a9': 'R'}).fen(),  # The previous side cannot remain in check.
        START_FEN, START_FEN.replace('h', 'n').replace('H', 'N').replace('e', 'b').replace('E', 'B'),
        START_FEN + ' - - 0 1', START_FEN + ' extra', '  ' + START_FEN + '  ',
        START_FEN.replace(' w', '\n w'),
    ]
    result = []
    for fen in candidates:
        try:
            canonical = Position.from_fen(fen).fen()
        except (ValueError, TypeError):
            canonical = None
        result.append(dict(fen=fen, canonical=canonical))
    return result


NODE_CHECK = r"""
const fs = require('fs'), assert = require('assert');
const XQ = require(process.argv[1]), input = JSON.parse(fs.readFileSync(0, 'utf8'));
let positions = 0, childPositions = 0, engineLines = 0;
for (const c of input.positions) {
  const p = new XQ.Position(c.board, c.turn);
  assert.equal(p.fen(), c.fen, c.name + ' FEN');
  assert.equal(XQ.evaluate(p), c.evaluation, c.name + ' evaluation');
  assert.deepStrictEqual(p.legalMoves().sort(), c.legal, c.name + ' legal moves');
  assert.deepStrictEqual(p.status(), c.status, c.name + ' terminal state');
  for (const color of ['w', 'b']) assert.equal(p.inCheck(color), c.checks[color], c.name + ' check ' + color);
  for (let i = 0; i < 90; i++) assert.deepStrictEqual(p.targets(i), c.targets[i], c.name + ' targets ' + i);
  if (c.fenValid) assert.equal(XQ.Position.fromFen(c.fen).fen(), c.fen, c.name + ' accepted FEN');
  else assert.throws(() => XQ.Position.fromFen(c.fen), undefined, c.name + ' rejected FEN');
  for (const [move, fen] of Object.entries(c.children)) {
    assert.equal(p.play(move).fen(), fen, c.name + ' child ' + move);
    assert.equal(p.fen(), c.fen, c.name + ' parent unchanged');
    childPositions++;
  }
  positions++;
}
for (const c of input.fens) {
  if (c.canonical === null) assert.throws(() => XQ.Position.fromFen(c.fen));
  else assert.equal(XQ.Position.fromFen(c.fen).fen(), c.canonical);
}
for (let i = 0; i < 90; i++) assert.equal(XQ.index(XQ.square(i)), i);
for (const sq of ['a10', 'j1', '-1', '', null, '11']) assert.throws(() => XQ.index(sq));
for (const move of ['a0', null, 123, 'a0j9']) assert.throws(() => XQ.parseMove(move));
const start = XQ.Position.fromFen(XQ.START_FEN);
assert.equal(start.legalMoves().length, 44);
const perft2 = start.legalMoves().reduce((total, move) => total + start.play(move).legalMoves().length, 0);
assert.equal(perft2, 1920);
assert.throws(() => start.play('a0a9'));
assert.equal(start.fen(), XQ.START_FEN);
for (const c of input.engines) {
  const p = XQ.Position.fromFen(c.fen), result = XQ.analyze(p, {depth: 2, maxMs: 30000});
  assert.equal(result.depth, 2, c.id + ' completed depth');
  assert.equal(result.complete, true);
  assert.equal(result.score, c.score, c.id + ' engine score');
  assert.deepStrictEqual(result.ranked, c.ranked, c.id + ' all ranked roots and PVs');
  assert.equal(result.bestMove, c.ranked[0].move);
  for (const line of result.ranked) {
    let state = p;
    assert.equal(line.pv[0], line.move);
    for (const move of line.pv) state = state.play(move);
    engineLines++;
  }
}
const timeout = XQ.analyze(start, {depth: 2, maxMs: 0});
assert.equal(timeout.depth, 0);
assert.equal(timeout.complete, false);
assert.equal(timeout.truncated, true);
assert.deepStrictEqual(timeout.ranked.map(l => l.move).sort(), start.legalMoves().sort());
for (const line of timeout.ranked) {
  assert.deepStrictEqual(line.pv, [line.move]);
  assert.equal(line.score, -XQ.evaluate(start.play(line.move)));
}
const depth1 = XQ.analyze(start, {depth: 1, maxMs: 30000});
assert.equal(depth1.depth, 1);
assert.equal(depth1.complete, true);
for (const line of depth1.ranked) assert.equal(line.pv.length, 1);
const terminal = input.positions.find(c => c.name === 'checkmate-loss');
const terminalResult = XQ.analyze(new XQ.Position(terminal.board, terminal.turn));
assert.equal(terminalResult.bestMove, null);
assert.equal(terminalResult.score, -100000);
assert.deepStrictEqual(terminalResult.ranked, []);
const began = performance.now();
const bounded = XQ.analyze(start, {depth: 2, maxMs: 250});
console.log(JSON.stringify({positions, childPositions, fenCases: input.fens.length, perft2,
  enginePositions: input.engines.length, engineLines, invalidInputs: 10,
  initialSearch: {depth: bounded.depth, complete: bounded.complete, elapsedMs: Math.round(performance.now() - began)},
  result: 'PASS'}));
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', help='Node.js 18+ executable')
    args = parser.parse_args()
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    node = args.node or (str(bundled) if bundled.is_file() else shutil.which('node'))
    if not node:
        raise SystemExit('Node.js 18+ required; supply --node PATH.')
    engine = LocalEngine(max_depth=2, seconds=30)
    engines = []
    for puzzle in PUZZLES:
        result = engine.analyze(puzzle['fen'])
        assert result['depth'] == 2, 'Python reference search did not finish.'
        engines.append(dict(id=puzzle['id'], fen=puzzle['fen'], score=result['score'], ranked=result['lines']))
    data = dict(positions=fixtures(), fens=fen_cases(), engines=engines)
    result = subprocess.run([node, '-e', NODE_CHECK, str(ROOT / 'online-preview/xiangqi.js')],
                            input=json.dumps(data, ensure_ascii=False), encoding='utf-8',
                            capture_output=True, timeout=180)
    if result.returncode:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)
    print(result.stdout.strip())


if __name__ == '__main__':
    main()
