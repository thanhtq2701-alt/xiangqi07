'use strict';
const assert = require('node:assert/strict');
const XQ = require('../online-preview/xiangqi.js');
const CC = require('../online-preview/game-tools.js');
const tests = [];
const test = (name, fn) => tests.push({ name, fn });
function pos(pieces, turn = 'w') {
  const board = Array(90).fill('.');
  for (const [square, piece] of Object.entries(pieces)) board[XQ.index(square)] = piece;
  return XQ.Position.fromFen(new XQ.Position(board, turn).fen());
}
function rotate(p) {
  return new XQ.Position(p.board.slice().reverse().map(piece => piece === '.' ? '.' : XQ.side(piece) === 'w' ? piece.toLowerCase() : piece.toUpperCase()), XQ.other(p.turn));
}
const mirroredMove = move => XQ.square(89 - XQ.index(move.slice(0, 2))) + XQ.square(89 - XQ.index(move.slice(2)));
const start = XQ.Position.fromFen(XQ.START_FEN);

test('Vietnamese notation uses moving-side files and movement directions for all seven pieces', () => {
  const samples = [
    [pos({ d0: 'K', f9: 'k' }), 'd0d1', 'Tg6.1'],
    [pos({ e0: 'K', f9: 'k', d0: 'A' }), 'd0e1', 'S6.5'],
    [pos({ d0: 'K', f9: 'k', c0: 'E' }), 'c0e2', 'T7.5'],
    [pos({ d0: 'K', f9: 'k', a2: 'R' }), 'a2a7', 'X9.5'],
    [pos({ d0: 'K', f9: 'k', b0: 'H' }), 'b0c2', 'M8.7'],
    [start, 'h2e2', 'P2-5'],
    [start, 'a3a4', 'B9.1']
  ];
  for (const [p, move, expected] of samples) {
    assert.equal(CC.notateMove(p, move), expected);
    assert.equal(CC.parseNotation(p, expected), move);
    assert.equal(CC.notateMove(rotate(p), mirroredMove(move)), expected);
    assert.equal(CC.parseNotation(rotate(p), expected), mirroredMove(move));
  }
  const p = start.play('h2e2');
  assert.equal(CC.notateMove(p, 'b9c7'), 'M2.3');
  assert.equal(CC.notateMove(start.play('h2e2').play('b9c7'), 'e2h2'), 'P5-2');
  assert.equal(CC.notateMove(pos({ d0: 'K', f9: 'k', b2: 'H' }), 'b2a0'), 'M8/9');
});

test('every legal move round-trips across deterministic real game positions, both sides and every piece', () => {
  let p = start, random = 1729, count = 0;
  const covered = new Set();
  for (let i = 0; i < 100; i++) {
    const moves = p.legalMoves();
    if (!moves.length) { p = start; continue; }
    const texts = moves.map(move => CC.notateMove(p, move));
    assert.equal(new Set(texts).size, texts.length, 'canonical notation must identify a unique legal move');
    for (let j = 0; j < moves.length; j++) {
      assert.equal(CC.parseNotation(p, texts[j]), moves[j]);
      assert.equal(CC.illegalMoveReason(p, moves[j]), '');
      covered.add(p.board[XQ.index(moves[j].slice(0, 2))]); count++;
    }
    random = (Math.imul(random, 1664525) + 1013904223) >>> 0;
    p = p.play(moves[random % moves.length]);
  }
  assert.equal(covered.size, 14, [...covered].join(''));
  console.log('  round-trip validated ' + count + ' legal moves, all 14 side/piece combinations');
});

test('two pieces on one file use front/back, parsing rejects ambiguous source file', () => {
  const p = pos({ d0: 'K', f9: 'k', a2: 'R', a5: 'R' });
  assert.equal(CC.notateMove(p, 'a5b5'), 'X trước-8');
  assert.equal(CC.notateMove(p, 'a2b2'), 'X sau-8');
  assert.equal(CC.parseNotation(p, 'Xt-8'), 'a5b5');
  assert.equal(CC.parseNotation(p, 'X truoc - 8'), 'a5b5');
  assert.throws(() => CC.parseNotation(p, 'X9-8'), /chưa rõ/);
  assert.equal(CC.notateMove(rotate(p), mirroredMove('a5b5')), 'X trước-8');
});

test('pawn stacks on multiple files and middle pawns remain unambiguous', () => {
  const p = pos({ d0: 'K', f9: 'k', a5: 'P', a6: 'P', c5: 'P', c6: 'P', c7: 'P' });
  assert.equal(CC.notateMove(p, 'a6b6'), 'B9 trước-8');
  assert.equal(CC.notateMove(p, 'c6b6'), 'B7 giữa-8');
  assert.equal(CC.parseNotation(p, 'B7 giữa-8'), 'c6b6');
  for (const move of p.legalMoves()) assert.equal(CC.parseNotation(p, CC.notateMove(p, move)), move);
});

test('notation parser accepts full direction words, exact coordinate moves, and case', () => {
  assert.equal(CC.parseNotation(start, 'P2 bình 5'), 'h2e2');
  assert.equal(CC.parseNotation(start, 'b9 tiến 1'), 'a3a4');
  assert.equal(CC.parseNotation(start, 'A3A4'), 'a3a4');
  assert.throws(() => CC.parseNotation(start, 'P2+5'), /Không có nước/);
  assert.throws(() => CC.parseNotation(start, 'a3a5'), /đúng một ô/);
  assert.throws(() => CC.notateMove(start, 'a3a5'), /đúng một ô/);
});

test('game import parses numbered Vietnamese notation and coordinates atomically', () => {
  const result = CC.parseGameNotation(XQ.START_FEN, '1. P2-5 M2.3\n2) M2.3 a6a5');
  assert.deepEqual(result.moves, ['h2e2', 'b9c7', 'h0g2', 'a6a5']);
  assert.equal(result.positions.length, 5);
  assert.deepEqual(CC.parseGameNotation(XQ.START_FEN, '').moves, []);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 M2.3 a3a5'), /Nửa nước 3/);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 M2.3', 1), /giới hạn 1/);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 garbage'), /Không đọc được/);
  assert.equal(start.fen(), XQ.START_FEN);
});

test('paired move history keeps red left, black right even for black-to-move imports', () => {
  const rows = CC.pairMoveHistory(XQ.START_FEN, ['h2e2', { move: 'b9c7' }, 'h0g2']);
  assert.equal(rows.length, 2); assert.equal(rows[0].red.notation, 'P2-5');
  assert.equal(rows[0].black.notation, 'M2.3'); assert.equal(rows[1].black, null);
  assert.equal(rows[1].number, 2); assert.equal(rows[1].red.ply, 2);
  const blackStart = start.play('h2e2');
  const blackRows = CC.pairMoveHistory(blackStart, ['b9c7', 'h0g2']);
  assert.equal(blackRows[0].red, null); assert.equal(blackRows[0].black.notation, 'M2.3');
  assert.equal(blackRows[1].number, 2); assert.equal(blackRows[1].red.notation, 'M2.3');
});

test('illegal reasons describe only rule violations, including blockers and movement', () => {
  assert.match(CC.illegalMoveReason(start, 'a4a5'), /không có quân/);
  assert.match(CC.illegalMoveReason(start, 'a6a5'), /Chưa đến lượt/);
  assert.match(CC.illegalMoveReason(start, 'a0b0'), /cùng bên/);
  assert.match(CC.illegalMoveReason(start, 'b0d1'), /cản chân/);
  assert.match(CC.illegalMoveReason(start, 'a0a4'), /quân cản/);
  assert.match(CC.illegalMoveReason(start, 'b2b7'), /0 quân ngòi/);
  assert.match(CC.illegalMoveReason(start, 'b2b8'), /không được nhảy/);
  assert.match(CC.illegalMoveReason(start, 'a3a2'), /đi lùi/);
  assert.match(CC.illegalMoveReason(start, 'a3b3'), /chưa qua sông/);
  assert.match(CC.illegalMoveReason(start, 'z0z1'), /Tọa độ/);
  assert.equal(CC.illegalMoveReason(start, 'b2b9'), '');
  const eye = pos({ d0: 'K', f9: 'k', c0: 'E', d1: 'R' });
  assert.match(CC.illegalMoveReason(eye, 'c0e2'), /cản mắt/);
  const river = pos({ d0: 'K', f9: 'k', c4: 'E' });
  assert.match(CC.illegalMoveReason(river, 'c4e6'), /qua sông/);
  assert.match(CC.illegalMoveReason(pos({ d0: 'K', f9: 'k' }), 'd0c0'), /trong cung/);
  assert.match(CC.illegalMoveReason(pos({ e0: 'K', f9: 'k', d0: 'A' }), 'd0d1'), /chéo một ô/);
});

test('moving a blocker cannot expose either facing generals or self-check', () => {
  const facing = pos({ e0: 'K', e9: 'k', e4: 'H' });
  assert.match(CC.illegalMoveReason(facing, 'e4f6'), /hai Tướng đối mặt/);
  const pin = pos({ e0: 'K', d9: 'k', e9: 'r', e4: 'R' });
  assert.match(CC.illegalMoveReason(pin, 'e4f4'), /bị chiếu/);
  assert.equal(CC.illegalMoveReason(pin, 'e4e9'), '');
});

test('four occurrences are required, strict one-sided perpetual check loses for either color', () => {
  const p = pos({ f0: 'K', e9: 'k', d8: 'R' }), cycle = ['d8e8', 'e9d9', 'e8d8', 'd9e9'];
  assert.equal(CC.repetitionStatus(p, cycle).over, false);
  const third = CC.repetitionStatus(p, cycle.concat(cycle));
  assert.equal(third.over, false); assert.equal(third.code, 'repetition-warning');
  const fourth = CC.repetitionStatus(p, cycle.concat(cycle, cycle));
  assert.equal(fourth.occurrences, 4); assert.equal(fourth.code, 'perpetual-check');
  assert.equal(fourth.winner, 'b'); assert.equal(fourth.over, true);
  const mirrored = CC.repetitionStatus(rotate(p), cycle.concat(cycle, cycle).map(mirroredMove));
  assert.equal(mirrored.winner, 'w');
});

test('ordinary quiet repetition is bounded, with board AND turn included', () => {
  const p = pos({ d0: 'K', f9: 'k' }), cycle = ['d0d1', 'f9f8', 'd1d0', 'f8f9'];
  assert.equal(CC.repetitionStatus(p, cycle.concat(cycle)).over, false);
  const result = CC.repetitionStatus(p, cycle.concat(cycle, cycle));
  assert.equal(result.code, 'quiet-repetition'); assert.equal(result.winner, null);
  assert.equal(result.over, true); assert.equal(result.needsVerification, false);
});

test('possible chase is never silently adjudicated as an ordinary repetition draw', () => {
  const cycle = ['b0a2', 'b9a7', 'a2b0', 'a7b9'];
  const result = CC.repetitionStatus(start, cycle.concat(cycle, cycle));
  assert.equal(result.code, 'repetition-review');
  assert.equal(result.over, false); assert.equal(result.needsVerification, true);
});

test('capture resets the natural move count; a pawn advance does not', () => {
  assert.equal(CC.repetitionStatus(start, ['a3a4', 'a6a5']).quietPlies, 2);
  assert.equal(CC.repetitionStatus(start, ['a3a4', 'a6a5', 'a4a5']).quietPlies, 0);
  assert.throws(() => CC.repetitionStatus(start, ['a3a5']), /không hợp lệ/);
});

test('100 quiet plies require verification, without fabricating an automatic draw', () => {
  let p = start, random = 9842;
  const history = [], occurrences = new Map([[p.fen(), 1]]);
  for (let i = 0; i < 100; i++) {
    const options = p.legalMoves().filter(move => {
      if (p.board[XQ.index(move.slice(2))] !== '.') return false;
      const after = p.afterUnchecked(move);
      return !after.inCheck() && (occurrences.get(after.fen()) || 0) < 2;
    });
    assert.ok(options.length, 'deterministic quiet fixture must have a legal continuation');
    random = (Math.imul(random, 1664525) + 1013904223) >>> 0;
    const move = options[random % options.length];
    history.push(move); p = p.play(move); occurrences.set(p.fen(), (occurrences.get(p.fen()) || 0) + 1);
  }
  const before = CC.repetitionStatus(start, history.slice(0, 99));
  assert.equal(before.quietPlies, 99); assert.equal(before.needsVerification, false);
  const result = CC.repetitionStatus(start, history);
  assert.equal(result.quietPlies, 100); assert.equal(result.code, 'natural-movecount-review');
  assert.equal(result.over, false); assert.equal(result.winner, null); assert.equal(result.needsVerification, true);
});

let failures = 0;
for (const { name, fn } of tests) {
  try { fn(); console.log('PASS ' + name); } catch (error) { failures++; console.error('FAIL ' + name + '\n' + error.stack); }
}
console.log((tests.length - failures) + '/' + tests.length + ' game-tools tests passed');
process.exitCode = failures ? 1 : 0;
