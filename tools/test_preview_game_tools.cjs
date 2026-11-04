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
    [pos({ d0: 'K', f9: 'k', c0: 'E' }), 'c0e2', 'V7.5'],
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

test('two pieces on one file use t/s from the moving side, parsing rejects ambiguous source file', () => {
  const p = pos({ d0: 'K', f9: 'k', a2: 'R', a5: 'R' });
  assert.equal(CC.notateMove(p, 'a5b5'), 'Xt-8');
  assert.equal(CC.notateMove(p, 'a2b2'), 'Xs-8');
  assert.equal(CC.notateMove(p, 'a5a6'), 'Xt.1');
  assert.equal(CC.notateMove(p, 'a2a1'), 'Xs/1');
  assert.equal(CC.parseNotation(p, 'Xt-8'), 'a5b5');
  assert.equal(CC.parseNotation(p, 'xs-8'), 'a2b2');
  assert.throws(() => CC.parseNotation(p, 'X9-8'), /chưa rõ/);
  // X9/1 could only be the rear Chariot here, but standard notation still requires t/s.
  assert.throws(() => CC.parseNotation(p, 'X9/1'), /chưa rõ/);
  assert.equal(CC.notateMove(rotate(p), mirroredMove('a5b5')), 'Xt-8');
});

function roundTrips(p) {
  const moves = p.legalMoves(), texts = moves.map(move => CC.notateMove(p, move));
  assert.equal(new Set(texts).size, texts.length, texts.join(' '));
  moves.forEach((move, i) => assert.equal(CC.parseNotation(p, texts[i]), move));
}

test('three pawns on one file are t/g/s; stacks on two files add the file number', () => {
  const three = pos({ d0: 'K', f9: 'k', c5: 'P', c6: 'P', c7: 'P' });
  assert.equal(CC.notateMove(three, 'c7c8'), 'Bt.1');
  assert.equal(CC.notateMove(three, 'c6b6'), 'Bg-8');
  assert.equal(CC.notateMove(three, 'c5b5'), 'Bs-8');
  assert.equal(CC.notateMove(rotate(three), mirroredMove('c7c8')), 'Bt.1');
  const twoFiles = pos({ d0: 'K', f9: 'k', a5: 'P', a6: 'P', c5: 'P', c6: 'P', c7: 'P' });
  assert.equal(CC.notateMove(twoFiles, 'a6b6'), 'B9t-8');
  assert.equal(CC.notateMove(twoFiles, 'a5b5'), 'B9s-8');
  assert.equal(CC.notateMove(twoFiles, 'c6b6'), 'B7g-8');
  assert.equal(CC.parseNotation(twoFiles, 'b7g-8'), 'c6b6');
  for (const p of [three, twoFiles, rotate(three), rotate(twoFiles)]) roundTrips(p);
});

test('four or five pawns on one file are numbered from the front and never collide with a lone pawn', () => {
  const four = pos({ d0: 'K', f9: 'k', c5: 'P', c6: 'P', c7: 'P', c8: 'P', a5: 'P' });
  assert.equal(CC.notateMove(four, 'c8b8'), 'B1-8');
  assert.equal(CC.notateMove(four, 'c6b6'), 'B3-8');
  assert.equal(CC.notateMove(four, 'a5a6'), 'B9.1');
  const five = pos({ d0: 'K', f9: 'k', c5: 'P', c6: 'P', c7: 'P', c8: 'P', c9: 'P' });
  assert.equal(CC.notateMove(five, 'c9b9'), 'B1-8');
  assert.equal(CC.notateMove(five, 'c5b5'), 'B5-8');
  // A lone pawn on file 2 reads B2-3, so the stack keeps its file number instead of B2-8.
  const collision = pos({ d0: 'K', f9: 'k', c5: 'P', c6: 'P', c7: 'P', c8: 'P', h5: 'P' });
  assert.equal(CC.notateMove(collision, 'c7b7'), 'B72-8');
  assert.equal(CC.notateMove(collision, 'h5g5'), 'B2-3');
  assert.deepEqual(CC.parseGameNotation(collision, 'B72-8').moves, ['c7b7']);
  for (const p of [four, five, collision, rotate(four), rotate(collision)]) roundTrips(p);
});

test('only standard notation is accepted: no machine coordinates, words or T for the Elephant', () => {
  const elephant = pos({ d0: 'K', f9: 'k', c0: 'E' });
  assert.equal(CC.parseNotation(elephant, 'v7.5'), 'c0e2');
  assert.equal(CC.parseNotation(start, 'x9.1'), 'a0a1');
  assert.equal(CC.parseNotation(start, 'TG5.1'), 'e0e1');
  for (const text of ['T7.5', 't7.5']) assert.throws(() => CC.parseNotation(elephant, text), /Tượng ghi là V/);
  for (const text of ['a3a4', 'A3A4', 'P2 bình 5', 'b9 tiến 1', 'P2+5', 'X trước.1', '']) {
    assert.throws(() => CC.parseNotation(start, text), /Không có nước/, text);
  }
  assert.throws(() => CC.notateMove(start, 'a3a5'), /đúng một ô/);
});

test('game import parses numbered standard notation atomically', () => {
  const result = CC.parseGameNotation(XQ.START_FEN, '1. P2-5 M2.3\n2) M8.7 b3.1');
  assert.deepEqual(result.moves, ['h2e2', 'b9c7', 'b0c2', 'c6c5']);
  assert.equal(result.positions.length, 5);
  assert.deepEqual(CC.parseGameNotation(XQ.START_FEN, '').moves, []);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 M2.3 B9.5'), /Nửa nước 3/);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 M2.3', 1), /giới hạn 1/);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 garbage'), /Không đọc được/);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 h9g7'), /Không đọc được biên bản ở nửa nước 2/);
  assert.throws(() => CC.parseGameNotation(XQ.START_FEN, 'P2-5 M2 tiến 3'), /Không đọc được/);
  // The owner's sample record used V for the Elephant and lower-case letters.
  assert.deepEqual(CC.parseGameNotation(XQ.START_FEN, 'v3.5').moves, ['g0e2']);
  assert.equal(start.fen(), XQ.START_FEN);
});

test('review text saved with machine coordinates is shown in standard notation', () => {
  const saved = text => CC.notateSavedText(XQ.START_FEN, text);
  assert.equal(saved('Trong ván bạn đi Pháo h2 → e2. Xem lại.'), 'Trong ván bạn đi P2-5. Xem lại.');
  assert.equal(saved('Pháo h2 → e2; sau đó Mã b9 → c7'), 'P2-5; sau đó M2.3');
  assert.equal(saved('Pháo b2 → b9 ăn Mã'), 'P8.7');
  assert.equal(saved('Xe a0 → a9'), 'Xe');
  assert.equal(saved('Không có nước nào'), 'Không có nước nào');
  assert.equal(CC.notateSavedText('hỏng', 'Xe a0 → a1'), 'Xe');
  assert.equal(CC.notateSavedText(XQ.START_FEN, undefined), undefined);
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
  assert.match(CC.illegalMoveReason(start, 'z0z1'), /không hợp lệ/);
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
