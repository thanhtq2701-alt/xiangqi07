'use strict';
/* Progress import with preview: formats, validation, merge/replace, isolation. Run: node tools/test_progress_import.cjs */
const assert = require('node:assert/strict');
const XQ = require('../web/xiangqi.js');
const C = require('../web/curriculum.js');
const L = require('../web/line-practice.js');
const CC = require('../web/learning.js');
const E = require('../web/experience.js');
const I = require('../web/progress-import.js');
const T = Date.parse('2026-10-25T08:00:00.000Z'), NOW = T + 10 * L.DAY;
const responses = ['Tôi quan sát đường thoát.', 'Hai Xe và Tướng phối hợp.', 'Chiếu liên tục và kiểm tra phản ứng.'];
const puzzle = { id: 'loose-rook', skill: 'material', title: 'Quan sát', fen: 'demo', solution: 'a2a7' };
const clone = value => JSON.parse(JSON.stringify(value));
const tests = [], test = (name, run) => tests.push({ name, run });

function learner() {
  let state = CC.markSeen(CC.fresh(), puzzle, { now: T });
  const session = CC.createSession(puzzle, { now: T });
  session.answers = responses.slice(); session.candidate = 'a2a7';
  state = CC.finishPuzzle(state, CC.reveal(session), puzzle, { now: T + 10000, success: true });
  const e = C.exercises[0];
  let line = L.create(e, { now: T, firstExposure: true }), now = T + 1000;
  while (!line.solved) { line = L.submit(e, line, { move: e.nodes[line.nodeId].choices[0].move, answers: responses, now }).session; now += 1000; }
  const done = L.finish(e, line, { now: now + 1000 });
  state.lineAttempts = [done.attempt];
  state.lessonViews = [{ id: C.lessons[0].id, at: new Date(T).toISOString(), kind: 'viewed' }];
  state.summaries = [{ id: 'sum1', kind: 'self_report', sessionId: null, at: new Date(T).toISOString(), checks: ['a'], note: 'ghi chú' }];
  let pos = XQ.Position.fromFen(XQ.START_FEN); const moves = [];
  for (const move of ['h2e2', 'h9g7']) { const next = pos.play(move); moves.push({ move, before: pos.fen(), after: next.fen(), side: pos.turn }); pos = next; }
  state.games = [{ id: 'g1', title: 'Ván với máy', createdAt: T, mode: 'bot', player: 'w', initialFen: XQ.START_FEN, fen: pos.fen(), moves,
    status: { over: true, winner: 'b', reason: 'Bạn xin thua' } }];
  state.profile = { name: 'Lan' };
  return CC.sanitize(clone(state), { now: NOW });
}
const exported = state => JSON.stringify(E.safeExport(state));
const accountFile = state => JSON.stringify({ format: 'co-chill-account-export-v1', account: { username: 'lan', role: 'admin', id: 'u1' },
  revision: 7, state: clone(state), feedback: [{ id: 'f1', message: 'x' }], onlineGames: [{ id: 'room1' }], answerKeysIncluded: false });
const sum = state => Object.values(state.records).reduce((n, r) => n + r.attempts.length, 0);

test('personal export round-trips into an empty learner without answer keys', () => {
  const source = learner(), imported = I.parse(exported(source), { now: NOW });
  assert.equal(imported.kind, 'personal');
  assert.deepEqual(imported.ignored, ['profile']);
  const result = I.apply(CC.fresh(), imported, 'merge', { now: NOW });
  assert.equal(sum(result), 1);
  assert.equal(result.records['loose-rook'].attempts[0].success, true);
  assert.deepEqual(result.records['loose-rook'].attempts[0].answers, responses);
  assert.equal(result.records['loose-rook'].dueAt, source.records['loose-rook'].dueAt);
  assert.equal(result.lineAttempts.length, 1);
  assert.equal(result.lineAttempts[0].finalNodeId, source.lineAttempts[0].finalNodeId);
  assert.equal(result.lessonViews.length, 1);
  assert.equal(result.summaries.length, 1);
  assert.equal(result.games.length, 1);
  assert.equal(result.games[0].moves.length, 2);
  assert.equal(result.profile.name, '', 'profile name is not imported');
  const text = JSON.stringify(result);
  for (const field of ['"solution"', '"alternatives"', '"rejectedMoves"', '"choices"', '"role"']) assert.equal(text.includes(field), false, field);
});

test('importing the same file twice, or into the source learner, adds nothing', () => {
  const source = learner();
  for (const file of [exported(source), accountFile(source)]) {
    const imported = I.parse(file, { now: NOW });
    const once = I.apply(source, imported, 'merge', { now: NOW });
    assert.equal(sum(once), 1); assert.equal(once.lineAttempts.length, 1); assert.equal(once.games.length, 1);
    const twice = I.apply(once, imported, 'merge', { now: NOW });
    assert.deepEqual(twice, once);
  }
});

test('preview counts before, file and after; nothing is saved by preview', () => {
  const source = learner(), target = CC.fresh(), before = clone(target);
  const preview = I.preview(target, I.parse(exported(source), { now: NOW }), 'merge', { now: NOW });
  assert.deepEqual(preview.before, { games: 0, positions: 0, attempts: 0, lineAttempts: 0, lessonViews: 0, summaries: 0 });
  assert.deepEqual(preview.file, { games: 1, positions: 1, attempts: 1, lineAttempts: 1, lessonViews: 1, summaries: 1 });
  assert.deepEqual(preview.after, preview.file);
  assert.deepEqual(target, before);
});

test('merge keeps current data; replace swaps history but keeps drafts and profile', () => {
  const current = learner(), other = clone(current);
  other.records = {}; other.lineAttempts = []; other.lessonViews = []; other.summaries = [];
  other.games = [{ ...clone(current.games[0]), id: 'g2' }];
  const imported = I.parse(exported(other), { now: NOW });
  const merged = I.apply(current, imported, 'merge', { now: NOW });
  assert.deepEqual(merged.games.map(g => g.id), ['g1', 'g2']);
  assert.equal(sum(merged), 1);
  const draft = CC.createSession(puzzle, { now: NOW - 1000 });
  const replaced = I.apply({ ...current, session: draft }, imported, 'replace', { now: NOW });
  assert.deepEqual(replaced.games.map(g => g.id), ['g2']);
  assert.equal(sum(replaced), 0); assert.equal(replaced.lineAttempts.length, 0);
  assert.equal(replaced.session.id, draft.id);
  assert.equal(replaced.profile.name, 'Lan');
  assert.throws(() => I.apply(current, imported, 'overwrite'), /gộp hoặc thay thế/);
});

test('merging attempts of the same position replays the schedule in time order', () => {
  const current = learner(), later = clone(current);
  const attempt = later.records['loose-rook'].attempts[0];
  later.records['loose-rook'].attempts = [{ ...attempt, id: 'later', startedAt: new Date(T + 3 * L.DAY).toISOString(), completedAt: new Date(T + 3 * L.DAY + 5000).toISOString() }];
  const merged = I.apply(current, I.parse(exported(later), { now: NOW }), 'merge', { now: NOW });
  const attempts = merged.records['loose-rook'].attempts;
  assert.equal(attempts.length, 2);
  assert(Date.parse(attempts[0].completedAt) < Date.parse(attempts[1].completedAt));
  assert(Date.parse(merged.records['loose-rook'].dueAt) > Date.parse(current.records['loose-rook'].dueAt));
});

test('account export: only learning data, account/role/feedback/online games ignored', () => {
  const source = learner();
  const imported = I.parse(accountFile(source), { now: NOW });
  assert.equal(imported.kind, 'account');
  assert.equal(imported.account, 'lan');
  assert.deepEqual(imported.ignored.sort(), ['feedback', 'onlineGames', 'profile']);
  const result = I.apply(CC.fresh(), imported, 'merge', { now: NOW });
  assert.equal(sum(result), 1); assert.equal(result.lineAttempts.length, 1);
  for (const field of ['"role"', '"username"', '"feedback"', '"room1"', '"revision"']) assert.equal(JSON.stringify(result).includes(field), false, field);
});

test('games are replayed by the rules: illegal, forged, unfinished and server games are refused', () => {
  const source = learner(), data = E.safeExport(source);
  const good = data.games[0];
  data.games = [
    { ...good, id: 'illegal', moves: ['h2e2', 'a0a9'] },
    { ...good, id: 'bad-fen', initialFen: 'not a fen' },
    { ...good, id: 'open', status: { over: false } },
    { ...good, id: 'online-abc' },
    { ...good, id: 'ok', moves: ['h2e2'] }
  ];
  const imported = I.parse(JSON.stringify(data), { now: NOW });
  assert.deepEqual(imported.raw.games.map(g => g.id), ['ok']);
  assert.deepEqual({ games: imported.rejected.games, unfinished: imported.rejected.unfinished }, { games: 3, unfinished: 1 });
  const game = imported.raw.games[0];
  assert.equal(game.fen, XQ.Position.fromFen(XQ.START_FEN).play('h2e2').fen());
  assert.equal(game.moves[0].before, XQ.Position.fromFen(XQ.START_FEN).fen());
  assert.equal(game.status.over, true);
});

test('a checkmate in the file is taken from the rules, not the stated result', () => {
  const data = E.safeExport(learner()), e = C.exercises[0];
  data.games = [{ id: 'mate', title: 'x', createdAt: T, initialFen: e.fen, player: 'w', mode: 'local', moves: e.exampleLine,
    status: { over: true, winner: 'b', reason: 'Bên Đỏ thua' } }];
  const game = I.parse(JSON.stringify(data), { now: NOW }).raw.games[0];
  assert.equal(game.status.winner, 'w');
  assert.equal(game.status.reason, 'Chiếu hết');
});

test('forged learning entries are dropped and counted, never trusted', () => {
  const source = learner(), data = E.safeExport(source);
  data.lineAttempts.push({ ...data.lineAttempts[0], startedAt: new Date(T + 2 * L.DAY).toISOString(), history: [{ move: 'a0a9', reply: '', at: data.lineAttempts[0].startedAt }] });
  data.lineAttempts.push({ ...data.lineAttempts[0], puzzleId: 'missing-exercise' });
  data.records[0].attempts.push({ ...data.records[0].attempts[0], startedAt: new Date(NOW + 30 * L.DAY).toISOString(), completedAt: new Date(NOW + 31 * L.DAY).toISOString() });
  data.lessonViews.push({ id: 'no-such-lesson', at: new Date(T).toISOString() });
  const imported = I.parse(JSON.stringify(data), { now: NOW });
  const preview = I.preview(CC.fresh(), imported, 'merge', { now: NOW });
  assert.equal(preview.file.lineAttempts, 1);
  assert.equal(preview.rejected.lineAttempts, 2);
  assert.equal(preview.file.attempts, 1);
  assert.equal(preview.rejected.attempts, 1);
  assert.equal(preview.file.lessonViews, 1);
});

test('the source state passed to apply is never mutated (account isolation)', () => {
  const target = learner(), snapshot = clone(target), file = I.parse(accountFile(learner()), { now: NOW });
  I.apply(target, file, 'merge', { now: NOW });
  I.apply(target, file, 'replace', { now: NOW });
  assert.deepEqual(target, snapshot);
});

test('unreadable, foreign or unsupported files are refused with a clear message', () => {
  const cases = [['', /trống/], ['{oops', /JSON/], ['[]', /Không nhận ra/], ['{"format":"other"}', /Không nhận ra/],
    ['{"format":"co-chill-personal-export","version":2}', /Phiên bản/], ['{"format":"co-chill-account-export-v1"}', /thiếu phần tiến độ/],
    ['x'.repeat(5 * 1024 * 1024 + 1), /5 MB/]];
  for (const [text, message] of cases) assert.throws(() => I.parse(text), message);
  const withBom = '﻿' + exported(learner());
  assert.equal(I.parse(withBom, { now: NOW }).kind, 'personal');
});

test('drafts in the file are reported as not imported', () => {
  const source = learner();
  source.session = CC.createSession(puzzle, { now: NOW - 1000 });
  assert(I.parse(exported(source), { now: NOW }).ignored.includes('drafts'));
  assert.equal(I.apply(CC.fresh(), I.parse(exported(source), { now: NOW }), 'merge', { now: NOW }).session, null);
});

let failed = 0;
for (const item of tests) {
  try { item.run(); console.log('PASS ' + item.name); } catch (error) { failed++; console.error('FAIL ' + item.name + '\n' + error.stack); }
}
console.log(`${tests.length - failed}/${tests.length} progress import tests passed`);
if (failed) process.exitCode = 1;
