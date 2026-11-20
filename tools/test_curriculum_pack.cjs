/* The 70 exercises imported from the owner's workbook (web/curriculum-pack.js):
 * data integrity, grading of the learner's moves, Black-to-move exercises and English coverage.
 * Run: node tools/test_curriculum_pack.cjs */
'use strict';
const assert = require('node:assert/strict');
const XQ = require('../web/xiangqi.js');
const GT = require('../web/game-tools.js');
const PACK = require('../web/curriculum-pack.js');
const C = require('../web/curriculum.js');
const L = require('../web/line-practice.js');
const CC = require('../web/learning.js');
const EN = require('../web/content-en.js');
const T = Date.parse('2026-11-20T08:00:00.000Z');
const answers = ['Tôi thấy quân bị bắt.', 'Giành quân hoặc chiếu hết.', 'Đối thủ sẽ chạy hoặc che.'];
const clone = value => JSON.parse(JSON.stringify(value));
const pack = PACK.exercises.map(e => C.findExercise(e.id));
const byId = id => C.findExercise(id);
const VI_NOTATION = /(?<![\wÀ-ỹ])(Tg|X|P|M|B|S|V)([1-9][tsg]?|[tsg][1-9]?)[.\-\/][1-9](?![\wÀ-ỹ])/i;
let passed = 0;
const tests = [];
const test = (name, fn) => tests.push({ name, fn });

function play(e, moves, from = e.fen) { let p = XQ.Position.fromFen(from); for (const m of moves) p = p.play(m); return p; }
// Walk the main line through line-practice.js exactly as the app does.
function solve(e, pick = node => node.choices[0].move) {
  let session = L.create(e, { now: T, firstExposure: true }), now = T + 1000, outcome;
  for (let guard = 0; !session.solved; guard++) {
    assert.ok(guard < 20, e.id + ' does not finish');
    const result = L.submit(e, session, { move: pick(e.nodes[session.nodeId], session), answers, now });
    outcome = result.outcome;
    assert.ok(['advanced', 'solved'].includes(outcome), e.id + ': ' + outcome);
    session = result.session; now += 1000;
  }
  return { session, outcome, now };
}
function sessionAt(e, nodeId) {
  let session = L.create(e, { now: T, firstExposure: true }), now = T + 1000;
  while (session.nodeId !== nodeId) { session = L.submit(e, session, { move: e.nodes[session.nodeId].choices[0].move, answers, now }).session; now += 1000; }
  return { session, now };
}

test('the pack holds the 70 reviewed exercises in the owner\'s 8 topics', () => {
  assert.equal(PACK.format, 'cochill-curriculum-pack-v1');
  assert.equal(pack.length, 70);
  assert.ok(pack.every(Boolean), 'every pack exercise is in the curriculum');
  const count = key => pack.reduce((acc, e) => (acc[e[key]] = (acc[e[key]] || 0) + 1, acc), {});
  assert.deepEqual(count('chapterId'), { 'opening-foundation': 10, rook: 9, cannon: 9, horse: 9, pawn: 5, kingSafety: 10, coordination: 9, 'end-basic': 9 });
  assert.deepEqual(count('objective'), { material: 35, mate: 35 });
  assert.deepEqual(count('difficulty'), { intermediate: 50, advanced: 20 });
  // 8 Black-to-move exercises; mid-opening-03 got its "Đen đi trước." in the workbook fix of 2026-11-20.
  assert.deepEqual(count('learner'), { w: 62, b: 8 });
  const ids = C.exercises.map(e => e.id);
  assert.equal(new Set(ids).size, ids.length, 'no duplicate exercise id');
  assert.deepEqual(ids.slice(0, 2), ['v6-rooks-palace-a', 'v6-rooks-palace-b'], 'the authored exercises stay first');
  for (const e of pack) {
    assert.ok(C.findChapter(e.chapterId).exerciseIds.includes(e.id), e.id);
    assert.equal(e.version >= 1, true);
    assert.equal(Object.isFrozen(e), true, 'curriculum content is frozen');
  }
  assert.deepEqual(C.courses[1].chapterIds, ['rook', 'cannon', 'horse', 'pawn', 'kingSafety', 'coordination']);
  assert.equal(C.findChapter('pawn').title, 'Tốt');
});

test('every tree is valid line-v1 and ends as its objective says', () => {
  for (const e of pack) {
    assert.equal(L.validate(e), true, e.id);
    assert.equal(Object.keys(e.nodes).length, e.decisions, e.id);
    assert.equal(e.exampleLine.length, 2 * e.decisions - 1, e.id);
    assert.equal(XQ.Position.fromFen(e.fen).turn, e.learner, e.id);
    const end = play(e, e.exampleLine), start = XQ.Position.fromFen(e.fen);
    if (e.objective === 'mate') {
      assert.equal(end.status().over && end.status().winner === e.learner && end.inCheck(), true, e.id + ' ends in checkmate');
    } else {
      assert.equal(end.status().over, false, e.id);
      assert.ok(L.material(end, e.learner) > L.material(start, e.learner), e.id + ' ends ahead in material');
      assert.equal(e.proof.materialGain, L.material(end, e.learner) - L.material(start, e.learner), e.id);
    }
    // Honest labels: the app checks rules; it does not claim Pikafish or expert proof.
    assert.equal(e.proof.method, 'author-tree');
    assert.equal(e.proof.pikafishVerified, false);
    assert.equal(e.proof.expertReviewed, false);
    assert.match(e.verification, /tác giả duyệt.*Pikafish ngoài ứng dụng.*chưa qua chuyên gia/);
  }
});

test('nothing shown before reflection gives the solution away', () => {
  for (const e of pack) {
    for (const text of [e.title, e.goal, e.difficultyLabel, e.verification]) {
      assert.equal(VI_NOTATION.test(text), false, e.id + ': ' + text);
      for (const move of e.exampleLine) assert.equal(text.includes(move), false, e.id);
      assert.equal(text.includes(e.idea), false, e.id);
    }
    assert.equal(e.goal.startsWith(e.learner === 'b' ? 'Đen đi trước.' : 'Đỏ đi trước.'), true, e.id);
    assert.ok(e.goal.includes(`trong ${e.decisions} lượt`), e.id);
  }
});

test('the main line is accepted move by move and completes once', () => {
  for (const e of pack) {
    const { session, outcome, now } = solve(e);
    assert.equal(outcome, 'solved', e.id);
    assert.equal(session.history.length, e.decisions, e.id);
    assert.equal(session.failureCount, 0, e.id);
    const done = L.finish(e, session, { now });
    assert.equal(done.attempt.learnerDecisions, e.decisions);
    assert.equal(done.attempt.verification, 'author-tree');
    // A synced attempt replays against the tree and survives sanitizing.
    assert.ok(L.sanitizeAttempt(e, clone(done.attempt), { now: now + 1000 }), e.id);
    const state = { ...CC.fresh(), lineAttempts: [done.attempt] };
    assert.equal(CC.sanitize(clone(state), { now: now + 1000 }).lineAttempts.length, 1, e.id);
  }
});

test('the workbook\'s other accepted move and every immediate final mate are accepted', () => {
  const hard = byId('hard-pawn-03'), last = hard.nodes.n5;
  assert.deepEqual(last.choices.map(c => c.move), ['f7e7', 'f7f8']);
  const alternative = solve(hard, (node, s) => node.id === 'n5' ? 'f7f8' : node.choices[0].move);
  assert.equal(alternative.outcome, 'solved');
  assert.equal(alternative.session.history.at(-1).move, 'f7f8');
  assert.ok(L.sanitizeAttempt(hard, L.finish(hard, alternative.session, { now: alternative.now }).attempt, { now: alternative.now + 1 }));
  // hard-pawn-01: the rules find two more mates on the last move (owner decision 20/11/2026).
  const pawn = byId('hard-pawn-01'), final = pawn.nodes.n4;
  assert.deepEqual(final.choices.filter(c => c.auto === 'mate').map(c => c.move).sort(), ['e8e9', 'e8f8']);
  for (const move of final.choices.map(c => c.move)) {
    const { session, now } = sessionAt(pawn, 'n4');
    const out = L.submit(pawn, session, { move, now });
    assert.equal(out.outcome, 'solved', move);
  }
  // Every accepted final move of a checkmate exercise mates, and no immediate mate is left out.
  for (const e of pack.filter(x => x.objective === 'mate')) {
    for (const node of Object.values(e.nodes)) {
      if (node.choices[0].next !== null) continue;
      const p = XQ.Position.fromFen(node.fen);
      const mates = p.legalMoves().filter(m => { const q = p.play(m); return q.status().over && q.inCheck(); }).sort();
      assert.deepEqual(node.choices.map(c => c.move).sort(), mates, e.id);
    }
  }
});

test('a legal move outside the reviewed tree waits for verification and costs no attempt', () => {
  for (const e of pack) {
    for (const node of Object.values(e.nodes)) {
      assert.deepEqual(node.rejectedMoves, [], e.id);
    }
    const node = e.nodes[e.root], other = XQ.Position.fromFen(node.fen).legalMoves().find(m => !node.choices.some(c => c.move === m));
    if (!other) continue;
    const out = L.submit(e, L.create(e, { now: T }), { move: other, answers, now: T + 1000 });
    assert.equal(out.outcome, 'pending_verification', e.id);
    assert.equal(out.session.failureCount, 0, e.id);
    assert.equal(out.session.attempts.length, 0, e.id);
    assert.equal(L.submit(e, L.create(e, { now: T }), { move: 'a0a9', answers, now: T + 1000 }).outcome, 'illegal', e.id);
  }
});

test('the material objective is checked by the rules, not assumed', () => {
  const e = clone(byId('mid-opening-01'));
  e.nodes.n0.choices[0] = { ...e.nodes.n0.choices[0], reply: null, next: null };
  delete e.nodes.n1; delete e.nodes.n2;
  assert.throws(() => L.validate(e), /chưa hơn quân/);
  const mate = clone(byId('mid-pawn-01'));
  mate.objective = 'material';
  assert.equal(L.validate(mate), true, 'a checkmate also satisfies the material objective');
  const unknown = clone(byId('mid-pawn-01'));
  unknown.objective = 'advantage';
  assert.throws(() => L.validate(unknown), /Mục tiêu/);
  const pilot = clone(C.exercises[0]);
  delete pilot.objective;
  assert.equal(L.validate(pilot), true, 'exercises without an objective stay checkmate exercises');
  const notes = clone(byId('mid-opening-01'));
  notes.nodes.n0.watchOut = 'x'.repeat(2001);
  assert.throws(() => L.validate(notes), /Ghi chú/);
});

test('Black-to-move exercises start with Black and use Black\'s file numbers', () => {
  const black = pack.filter(e => e.learner === 'b');
  assert.deepEqual(black.map(e => e.id), ['mid-opening-03', 'mid-opening-06', 'mid-opening-07', 'mid-rook-05', 'mid-cannon-04', 'mid-horse-05', 'mid-coordination-04', 'mid-endgame-07']);
  // Notation is counted from the side that moves, as the workbook writes it (Cay_nuoc_di).
  const expected = { 'mid-opening-03': ['X8.9', 'M3/2', 'P5.4'], 'mid-opening-06': ['M7.5', 'X2.9', 'M5/7'], 'mid-rook-05': ['X7.3', 'S6.5', 'X7/5'], 'mid-endgame-07': ['X2.4', 'V5/7', 'X2-3'] };
  for (const [id, notes] of Object.entries(expected)) {
    const e = byId(id);
    let p = XQ.Position.fromFen(e.fen);
    const written = e.exampleLine.slice(0, 3).map(m => { const n = GT.notateMove(p, m); p = p.play(m); return n; });
    assert.deepEqual(written, notes, id);
  }
  for (const e of black) {
    const { session } = solve(e);
    assert.equal(session.solved, true, e.id);
    assert.equal(L.currentPosition(e, session).turn, 'w', e.id + ': after Black\'s last move Red is to move');
  }
});

test('every Vietnamese text of the pack has an English entry, and English mode has no Vietnamese left', () => {
  const VI = /[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]/i;
  for (const e of pack) {
    for (const field of ['title', 'goal', 'difficultyLabel', 'verification', 'assessment', 'idea', 'urgency', 'source']) {
      const entry = EN[`exercises#${e.id}.${field}`];
      assert.ok(entry, e.id + '.' + field);
      assert.equal(entry.vi, e[field]);
      assert.equal(VI.test(entry.en), false, e.id + '.' + field);
    }
    for (const node of Object.values(e.nodes)) {
      node.choices.forEach((c, i) => { if (c.reason) assert.equal(EN[`exercises#${e.id}.nodes.${node.id}.choices[${i}].reason`]?.vi, c.reason); });
      if (node.watchOut) assert.equal(EN[`exercises#${e.id}.nodes.${node.id}.watchOut`]?.vi, node.watchOut);
    }
  }
  assert.equal(EN['exercises#hard-pawn-03.title'].en, 'Soldier · Checkmate 5');
  assert.equal(EN['chapters#pawn.title'].en, 'Soldier');
});

for (const { name, fn } of tests) {
  try { fn(); passed++; console.log('PASS ' + name); } catch (error) { console.error('FAIL ' + name + '\n' + error.stack); process.exitCode = 1; }
}
console.log(`${passed}/${tests.length} curriculum pack tests passed`);
