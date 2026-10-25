'use strict';

const assert = require('node:assert/strict');
const CC = require('../online-preview/learning.js');
const T0 = Date.parse('2026-10-15T10:00:00.000Z');
const puzzle = { id: 'rook-a', skill: 'material', title: 'Observe', fen: 'demo', solution: 'a2a7' };
const tests = [];
function test(name, action) { tests.push({ name, action }); }
function ready(now = T0, options = {}) {
  const session = CC.createSession(puzzle, { now, ...options });
  session.answers = ['I see a target.', 'Opponent can respond.', 'Check a capture.'];
  session.candidate = 'a2a7';
  return CC.reveal(session);
}
function completed(now = T0) {
  const session = ready(now);
  return CC.finishPuzzle(CC.markSeen(CC.fresh(), puzzle, { now }), session, puzzle, { now: now + 10000, success: true });
}

test('fresh creates independent state objects', () => {
  const first = CC.fresh(); first.profile.name = 'Changed';
  assert.equal(CC.fresh().profile.name, '');
  assert.deepEqual(CC.fresh().records, {});
});

test('all reflection answers and a candidate gate explanation', () => {
  const session = CC.createSession(puzzle, { now: T0 });
  assert.equal(CC.canReveal(session), false);
  assert.throws(() => CC.reveal(session), /Reflect/);
  session.answers = ['one', 'two', '   ']; session.candidate = 'a2a7';
  assert.equal(CC.canReveal(session), false);
  session.answers[2] = 'three'; session.candidate = null;
  assert.equal(CC.canReveal(session), false);
  session.candidate = 'a2a7';
  const revealed = CC.reveal(session);
  assert.equal(revealed.stage, 'explain');
  assert.equal(session.stage, 'reflect');
});

test('explicit unknown permits learning and marks assistance', () => {
  const session = CC.createSession(puzzle, { now: T0 });
  session.unknown = 'true'; assert.equal(CC.canReveal(session), false);
  session.unknown = true;
  assert.equal(CC.canReveal(session), true);
  const revealed = CC.reveal(session);
  assert.equal(revealed.assisted, true);
  const state = CC.finishPuzzle(CC.fresh(), revealed, puzzle, { now: T0 + 5000, success: false, assisted: false });
  assert.equal(state.records[puzzle.id].attempts[0].assisted, true);
});

test('session identity is stable for a specific start and distinct at another start', () => {
  assert.equal(CC.createSession(puzzle, { now: T0 }).id, CC.createSession(puzzle, { now: T0 }).id);
  assert.notEqual(CC.createSession(puzzle, { now: T0 }).id, CC.createSession(puzzle, { now: T0 + 1 }).id);
});

test('exposure and unfinished related exercises have no completion or due date', () => {
  let state = CC.markSeen(CC.fresh(), puzzle, { now: T0 });
  state.session = CC.createSession(puzzle, { now: T0, related: true });
  state.session.answers[0] = 'Saved draft';
  const restored = CC.sanitize(JSON.parse(JSON.stringify(state)), { now: T0 + CC.DAY });
  assert.equal(restored.session.related, true);
  assert.equal(restored.session.answers[0], 'Saved draft');
  assert.equal(restored.records[puzzle.id].completionCount, 0);
  assert.equal(restored.records[puzzle.id].dueAt, null);
});

test('completion anchors the due date at finish, even after an overnight pause', () => {
  const session = ready(T0);
  const finish = T0 + 2 * CC.DAY + 5000;
  const state = CC.finishPuzzle(CC.fresh(), session, puzzle, { now: finish, success: true });
  assert.equal(state.records[puzzle.id].completedAt, new Date(finish).toISOString());
  assert.equal(state.records[puzzle.id].dueAt, new Date(finish + CC.DAY).toISOString());
  assert.equal(state.records[puzzle.id].attempts[0].startedAt, new Date(T0).toISOString());
});

test('pending related stage resumes exactly without opening an answer or scheduling review', () => {
  const state = CC.fresh();
  state.session = CC.createSession(puzzle, { now: T0, related: true });
  state.session.stage = 'related_pending';
  const restored = CC.sanitize(state, { now: T0 + CC.DAY });
  assert.equal(restored.session.stage, 'related_pending');
  assert.equal(CC.canReveal(restored.session), false);
  assert.equal(restored.session.completedAt, null);
  assert.deepEqual(restored.records, {});
});

test('completion is immutable and repeated submission cannot shift the schedule', () => {
  const state = completed();
  const previous = JSON.stringify(state);
  const repeated = CC.finishPuzzle(state, state.session, puzzle, { now: T0 + 10 * CC.DAY, success: false });
  assert.equal(JSON.stringify(repeated), previous);
  const initial = CC.fresh();
  CC.finishPuzzle(initial, ready(), puzzle, { now: T0 + 5000, success: true });
  assert.deepEqual(initial.records, {});
});

test('correct independent reviews follow explicit 1/2/7/14/30 day intervals', () => {
  let state = CC.fresh();
  [1, 2, 7, 14, 30, 30].forEach((interval, index) => {
    const now = T0 + index * 40 * CC.DAY;
    state = CC.finishPuzzle(state, ready(now), puzzle, { now: now + 10000, success: true });
    assert.equal(state.records[puzzle.id].intervalDays, interval);
  });
  assert.equal(state.records[puzzle.id].completionCount, 6);
});

test('incorrect and assisted attempts have honest independent schedules', () => {
  let state = completed();
  state = CC.finishPuzzle(state, ready(T0 + CC.DAY), puzzle, { now: T0 + CC.DAY + 10000, success: false });
  assert.equal(state.records[puzzle.id].intervalDays, 1);
  assert.equal(state.records[puzzle.id].successStreak, 0);
  state = CC.finishPuzzle(state, ready(T0 + 2 * CC.DAY), puzzle, { now: T0 + 2 * CC.DAY + 10000, success: true, assisted: true });
  assert.equal(state.records[puzzle.id].intervalDays, 2);
  assert.equal(state.records[puzzle.id].successStreak, 0);
});

test('cannot complete before reflection, with a mismatched puzzle, or with invalid times', () => {
  const blank = CC.createSession(puzzle, { now: T0 });
  assert.throws(() => CC.finishPuzzle(CC.fresh(), blank, puzzle, { now: T0, success: true }), /reflection/);
  assert.throws(() => CC.finishPuzzle(CC.fresh(), ready(), { ...puzzle, id: 'different' }, { now: T0, success: true }), /match/);
  assert.throws(() => CC.finishPuzzle(CC.fresh(), ready(), puzzle, { now: T0 - 1, success: true }), /precede/);
  assert.throws(() => CC.finishPuzzle(CC.fresh(), ready(), puzzle, { now: Infinity, success: true }), /valid/);
  assert.throws(() => CC.finishPuzzle(CC.fresh(), ready(), puzzle, { now: T0 }), /observed/);
});

test('recommendation prefers unseen same-skill positions and excludes current position', () => {
  const seen = { ...puzzle, id: 'seen' }, unseen = { ...puzzle, id: 'unseen' }, other = { ...puzzle, id: 'other', skill: 'horse' };
  const state = CC.markSeen(CC.fresh(), seen, { now: T0 });
  const choice = CC.recommend([seen, other, unseen, puzzle], state.records, 'material', puzzle.id);
  assert.equal(choice.puzzle.id, 'unseen');
  assert.equal(choice.unseen, true);
  assert.equal(CC.recommend([puzzle, other], state.records, 'material', puzzle.id), null);
});

test('all-seen recommendation picks the least recent and never falsely says unseen', () => {
  const old = { ...puzzle, id: 'old' }, newer = { ...puzzle, id: 'newer' };
  let state = CC.markSeen(CC.fresh(), old, { now: T0 });
  state = CC.markSeen(state, newer, { now: T0 + 5000 });
  const choice = CC.recommend([newer, old], state.records, 'material', puzzle.id);
  assert.equal(choice.puzzle.id, 'old');
  assert.equal(choice.unseen, false);
});

test('self-assessment never changes objective performance, completion or review time', () => {
  const state = completed();
  const records = JSON.stringify(state.records);
  const summary = CC.summarizeSession(state, { checks: ['I understand'], note: 'Need more practice' }, { now: T0 + 20000 });
  assert.equal(JSON.stringify(summary.records), records);
  assert.equal(summary.summaries[0].kind, 'self_report');
  assert.equal(summary.session.stage, 'complete');
  assert.equal(state.summaries.length, 0);
  const twice = CC.summarizeSession(summary, { checks: ['Changed'], note: '' }, { now: T0 + 30000 });
  assert.equal(twice.summaries.length, 1);
});

test('roundtrip keeps draft stage, board selection and dynamic game snapshot', () => {
  const state = CC.fresh();
  state.session = CC.createSession({ ...puzzle, gameId: 'game-1', ply: 12, alternatives: ['a2a7', 'i2i7'], what: 'Verified explanation' }, { now: T0, source: 'game-review' });
  Object.assign(state.session, { answers: ['partial', '', ''], selected: 'a2', resumeSide: 'red', pendingPuzzleId: 'next' });
  state.games = [{ id: 'game-1', moves: ['a0a1'], fen: 'saved' }];
  const restored = CC.sanitize(JSON.parse(JSON.stringify(state)), { now: T0 + 10000 });
  assert.deepEqual(restored.session, state.session);
  assert.deepEqual(restored.games, state.games);
});

test('sanitization rejects corrupt input, prototype keys and oversized data', () => {
  assert.deepEqual(CC.sanitize(null), CC.fresh());
  assert.deepEqual(CC.sanitize({ version: 1, records: {} }), CC.fresh());
  const attack = JSON.parse('{"version":2,"records":{"__proto__":{"polluted":true},"constructor":{}},"games":[{"__proto__":{"polluted":true},"id":"good"}],"profile":{"name":"safe"}}');
  const restored = CC.sanitize(attack, { now: T0 });
  assert.equal({}.polluted, undefined);
  assert.deepEqual(restored.records, {});
  assert.equal(Object.prototype.hasOwnProperty.call(restored.games[0], '__proto__'), false);
  assert.equal(CC.sanitize({ version: 2, profile: { name: 'x'.repeat(1000) } }).profile.name.length, 80);
});

test('invalid imported dates cannot fabricate progress or bypass reflection', () => {
  const state = completed();
  state.records[puzzle.id].dueAt = '2099-01-01T00:00:00.000Z';
  state.records[puzzle.id].completionCount = 99999;
  state.records[puzzle.id].attempts.push({ ...state.records[puzzle.id].attempts[0], id: 'future', completedAt: '2099-01-01T00:00:00.000Z' });
  state.session.answers = ['', '', '']; state.session.unknown = false;
  const restored = CC.sanitize(state, { now: T0 + 10000 });
  assert.equal(restored.records[puzzle.id].completionCount, 1);
  assert.equal(restored.records[puzzle.id].dueAt, new Date(T0 + 10000 + CC.DAY).toISOString());
  assert.equal(restored.session.stage, 'reflect');
  const futureSession = CC.createSession(puzzle, { now: T0 + CC.DAY });
  assert.equal(CC.sanitize({ ...CC.fresh(), session: futureSession }, { now: T0 }).session, null);
});

test('duplicate imported completions do not count twice', () => {
  const state = completed();
  state.records[puzzle.id].attempts.push(state.records[puzzle.id].attempts[0]);
  const restored = CC.sanitize(state, { now: T0 + 10000 });
  assert.equal(restored.records[puzzle.id].completionCount, 1);
  assert.equal(restored.records[puzzle.id].intervalDays, 1);
});

test('out-of-order imported history cannot move the completion anchor backwards', () => {
  const state = completed();
  const original = state.records[puzzle.id].attempts[0];
  state.records[puzzle.id].attempts.push({ ...original, id: 'older-attempt', startedAt: new Date(T0 - 20000).toISOString(), completedAt: new Date(T0 - 10000).toISOString() });
  const restored = CC.sanitize(state, { now: T0 + 10000 });
  assert.equal(restored.records[puzzle.id].completionCount, 1);
  assert.equal(restored.records[puzzle.id].completedAt, original.completedAt);
  assert.throws(() => CC.finishPuzzle(restored, ready(T0 - 10000), puzzle, { now: T0, success: true }), /previous review/);
});

let failures = 0;
tests.forEach(({ name, action }) => {
  try { action(); console.log('PASS ' + name); }
  catch (error) { failures += 1; console.error('FAIL ' + name); console.error(error); }
});
console.log(`${tests.length - failures}/${tests.length} learning-state tests passed`);
if (failures) process.exitCode = 1;
