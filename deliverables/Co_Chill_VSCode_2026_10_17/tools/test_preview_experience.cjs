'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const XQ = require('../online-preview/xiangqi.js');
const learning = require('../online-preview/learning.js');
const experience = require('../online-preview/experience.js');
const gameTools = require('../online-preview/game-tools.js');
const CC = { ...learning, ...experience, ...gameTools };
const T0 = Date.parse('2026-10-16T08:00:00Z');
const puzzle = { id: 'sample', skill: 'cannon', fen: XQ.START_FEN, solution: 'h2e2', alternatives: ['b2e2'], what: 'ANSWER_SPOILER_what', why: 'ANSWER_SPOILER_why', how: 'ANSWER_SPOILER_how' };
const tests = [], test = (name, fn) => tests.push({ name, fn });
function session() {
  const value = CC.createSession(puzzle, { now: T0 });
  value.answers = ['Tôi thấy vị trí các quân.', 'Tôi kiểm tra đường Pháo.', 'Tôi xem phản ứng của đối phương.'];
  value.candidate = 'h2e2';
  return value;
}

test('preferences accept only supported options and exact booleans', () => {
  assert.deepEqual(CC.preferences(null), CC.DEFAULT_PREFS);
  assert.deepEqual(CC.preferences({ theme: 'purple', pieces: 'secret', font: 44, level: 'master', sound: 'true', sidebar: 1, injected: true }), CC.DEFAULT_PREFS);
  const result = CC.preferences({ theme: 'dark', pieces: 'vi', font: 'large', sound: true, sidebar: true, level: 'beginner', tone: 'friendly' });
  assert.deepEqual(result, { theme: 'dark', pieces: 'vi', font: 'large', sound: true, sidebar: true, level: 'beginner', tone: 'friendly' });
  result.theme = 'cool'; assert.equal(CC.preferences().theme, 'warm');
});

test('incomplete reflection never consumes attempts or exposes a solution', () => {
  const value = session(); value.answers[1] = '   ';
  const result = CC.reflectionCheck(value, puzzle);
  assert.equal(result.ready, false); assert.deepEqual(result.missing, [1]);
  assert.equal(result.attempts, undefined); assert.equal(result.reveal, undefined);
  value.answers[1] = 'Tôi nhìn đường quân'; value.candidate = null;
  assert.equal(CC.reflectionCheck(value, puzzle).needsMove, true);
  assert.equal(value.submissionCount, 0);
});

test('a matching first move and a legal alternative reveal without claiming to grade prose', () => {
  for (const move of ['h2e2', 'b2e2']) {
    const value = session(); value.candidate = move;
    const result = CC.reflectionCheck(value, puzzle);
    assert.equal(result.ready, true); assert.equal(result.matches, true);
    assert.equal(result.attempts, 1); assert.equal(result.reveal, true); assert.equal(result.assisted, false);
    assert.equal(result.reasoningCorrect, undefined);
  }
});

test('wrong candidates get at most three submissions and never become independent success', () => {
  const value = session(); value.candidate = 'a3a4';
  for (let attempt = 1; attempt <= 3; attempt++) {
    const result = CC.reflectionCheck(value, puzzle);
    assert.equal(result.attempts, attempt); assert.equal(result.reveal, attempt === 3);
    assert.equal(result.assisted, true); value.submissionCount = result.attempts;
  }
  assert.equal(CC.reflectionCheck(value, puzzle).attempts, 3);
  value.submissionCount = 99; assert.equal(CC.reflectionCheck(value, puzzle).attempts, 3);
  value.submissionCount = 1; value.candidate = puzzle.solution;
  assert.equal(CC.reflectionCheck(value, puzzle).assisted, true);
  value.submissionCount = 0; value.assisted = true;
  assert.equal(CC.reflectionCheck(value, puzzle).assisted, true);
});

test('new sessions round-trip through migration without losing defaults', () => {
  const state = CC.fresh(); state.session = CC.createSession(puzzle, { now: T0 });
  const restored = CC.sanitize(JSON.parse(JSON.stringify(state)), { now: T0 + 1000 });
  assert.deepEqual(restored, state);
});

test('migration retains assistance, drafts, first submission and summary drafts', () => {
  const state = CC.fresh(); state.session = session();
  Object.assign(state.session, { candidate: 'a3a4', firstCandidate: 'b2e2', firstAnswers: ['Đầu 1', 'Đầu 2', 'Đầu 3'], helpLevel: 2, helpReadyAt: T0 + 10000, assisted: true, submissionCount: 1, retryCount: 2, coachFeedback: 'Hãy xem lại đường quân', selected: 'h2', summaryNote: 'Nhớ kiểm tra', summaryChecks: ['0', '3'] });
  const restored = CC.sanitize(JSON.parse(JSON.stringify(state)), { now: T0 + 2000 });
  assert.deepEqual(restored.session, state.session);
  assert.equal(restored.session.seenExplanation, false);
  assert.equal(restored.session.stage, 'reflect');
  assert.equal(restored.records.sample, undefined);
});

test('finishing and reloading retain first answers separately from corrected answers', () => {
  const value = session(); value.firstAnswers = ['Ban đầu 1', 'Ban đầu 2', 'Ban đầu 3'];
  value.firstCandidate = 'a3a4'; value.submissionCount = 2; value.assisted = true;
  const finished = CC.finishPuzzle(CC.fresh(), CC.reveal(value), puzzle, { now: T0 + 20000, success: true });
  const recorded = finished.records.sample.attempts[0];
  assert.deepEqual(recorded.firstAnswers, value.firstAnswers); assert.equal(recorded.firstCandidate, 'a3a4');
  assert.deepEqual(recorded.answers, value.answers); assert.equal(recorded.candidate, 'h2e2');
  assert.equal(recorded.assisted, true);
  const restored = CC.sanitize(JSON.parse(JSON.stringify(finished)), { now: T0 + 30000 });
  assert.deepEqual(restored.records.sample.attempts[0], recorded);
  assert.equal(CC.evidence(restored.records).firstCorrect, 0);
});

test('legacy records migrate without inventing initial response history', () => {
  const value = session();
  const state = CC.finishPuzzle(CC.fresh(), CC.reveal(value), puzzle, { now: T0 + 20000, success: true });
  delete state.records.sample.attempts[0].firstAnswers;
  delete state.records.sample.attempts[0].firstCandidate;
  const restored = CC.sanitize(state, { now: T0 + 30000 });
  assert.equal(restored.records.sample.attempts[0].firstAnswers, null);
  assert.equal(restored.records.sample.attempts[0].firstCandidate, null);
  assert.equal(restored.records.sample.attempts[0].candidate, 'h2e2');
});

test('export omits answer keys at every exported nested boundary', () => {
  const secret = { solution: 'SECRET_KEY', alternatives: ['SECRET_KEY'], what: 'SECRET_KEY', why: 'SECRET_KEY' };
  const state = { ...CC.fresh(), profile: { name: 'Thanh', ...secret },
    games: [{ id: 'g1', createdAt: T0, initialFen: XQ.START_FEN, status: { over: true, winner: null, reason: 'Đã nhập', ...secret }, moments: [secret], moves: [{ move: 'h2e2', ...secret }], ...secret }],
    records: { sample: { puzzleId: 'sample', skill: 'cannon', attempts: [{ answers: ['Tự trả lời', '', ''], candidate: 'a3a4', success: false, assisted: true, ...secret }], ...secret } },
    session: { ...session(), puzzle: secret, ...secret },
    summaries: [{ id: 's1', at: '2026-10-16T08:00:00Z', checks: ['0'], note: 'Ghi chú cá nhân', ...secret }] };
  const output = CC.safeExport(state), json = JSON.stringify(output);
  assert.equal(json.includes('SECRET_KEY'), false);
  for (const field of ['solution', 'alternatives', 'moments', 'puzzle']) assert.equal(json.includes('"' + field + '"'), false);
  assert.equal(output.profile.name, 'Thanh'); assert.equal(output.games[0].moves[0], 'h2e2');
  assert.equal(output.summaries[0].note, 'Ghi chú cá nhân'); assert.equal(output.records[0].attempts[0].answers[0], 'Tự trả lời');
  assert.equal(output.draft.answers.length, 3);
  output.games[0].status.reason = 'changed'; output.summaries[0].note = 'changed'; output.draft.answers[0] = 'changed';
  assert.equal(state.games[0].status.reason, 'Đã nhập'); assert.equal(state.summaries[0].note, 'Ghi chú cá nhân');
  assert.notEqual(state.session.answers[0], 'changed');
});

test('export preserves personal initial-answer and self-assessment drafts without key snapshots', () => {
  const state = CC.fresh(); state.session = session();
  Object.assign(state.session, { firstAnswers: ['Cũ 1', 'Cũ 2', 'Cũ 3'], firstCandidate: 'a3a4', summaryNote: 'Lần sau chú ý', summaryChecks: ['1'] });
  const result = CC.safeExport(state);
  assert.deepEqual(result.draft.firstAnswers, state.session.firstAnswers);
  assert.equal(result.draft.firstCandidate, 'a3a4'); assert.equal(result.draft.summaryNote, 'Lần sau chú ý');
  assert.deepEqual(result.draft.summaryChecks, ['1']);
  assert.equal(result.draft.puzzle, undefined); assert.equal(CC.safeExport(CC.fresh()).draft, null);
});

test('evidence threshold is six attempts but unseen accuracy requires six separate positions', () => {
  const attempts = Array.from({ length: 6 }, () => ({ success: true, assisted: false }));
  const five = CC.evidence({ one: { skill: 'cannon', attempts: attempts.slice(0, 5) } });
  assert.equal(five.eligible, false); assert.equal(five.firstEligible, false);
  const sixRepeated = CC.evidence({ one: { skill: 'cannon', attempts } });
  assert.equal(sixRepeated.eligible, true); assert.equal(sixRepeated.firstCount, 1); assert.equal(sixRepeated.firstEligible, false);
  const records = Object.fromEntries(attempts.map((a, i) => ['p' + i, { skill: i < 3 ? 'cannon' : 'horse', attempts: [{ ...a, assisted: i === 0 }, { success: false, assisted: true }] }]));
  const all = CC.evidence(records);
  assert.equal(all.firstEligible, true); assert.equal(all.firstCount, 6); assert.equal(all.firstCorrect, 5);
  assert.equal(all.count, 12); assert.equal(all.assisted, 7);
  assert.equal(CC.evidence(records, 'horse').count, 6);
  assert.equal(CC.evidence(records, 'horse').firstEligible, false);
  assert.equal(CC.evidence(records, 'material').count, 0);
});

test('a later correct review cannot rewrite a failed first encounter', () => {
  const result = CC.evidence({ sample: { skill: 'cannon', attempts: [{ success: false, assisted: false }, ...Array.from({ length: 8 }, () => ({ success: true, assisted: false }))] } });
  assert.equal(result.firstCorrect, 0); assert.equal(result.firstCount, 1); assert.equal(result.independent, 8);
});

test('clock subtracts elapsed wall time then adds increment only after a timely move', () => {
  const clock = { enabled: true, w: 600000, b: 600000, last: T0, increment: 5000 };
  const result = CC.applyClockMove(clock, 'w', T0 + 12000);
  assert.equal(result.expired, false); assert.equal(result.clock.w, 593000);
  assert.equal(result.clock.b, 600000); assert.equal(result.clock.last, T0 + 12000);
  assert.equal(clock.w, 600000); assert.equal(clock.last, T0);
  const next = CC.applyClockMove(result.clock, 'b', T0 + 15000);
  assert.equal(next.clock.b, 602000); assert.equal(next.clock.w, 593000);
});

test('clock exact expiry and time away cannot be rescued by increment', () => {
  for (const elapsed of [5000, 6000, 600000]) {
    const result = CC.applyClockMove({ enabled: true, w: 5000, b: 6000, last: T0, increment: 10000 }, 'w', T0 + elapsed);
    assert.equal(result.expired, true); assert.equal(result.clock.w, 0); assert.equal(result.clock.b, 6000);
  }
  const disabled = { enabled: false, w: 0, b: 0, last: T0, increment: 0 };
  assert.deepEqual(CC.applyClockMove(disabled, 'w', T0 + 500000), { clock: disabled, expired: false });
  const backward = CC.applyClockMove({ enabled: true, w: 5000, b: 5000, last: T0, increment: -1 }, 'w', T0 - 2000);
  assert.equal(backward.clock.w, 5000);
});

// Minimal DOM/event harness: tests real app handlers and rendered HTML; visual QA
// remains a separate browser check. No source-text assertions mirror the app.
function appHarness(initialState, initialHash = '#learn') {
  const listeners = {}, elements = new Map(), storage = new Map(); let now = T0;
  function element(id) {
    if (!elements.has(id)) elements.set(id, { innerHTML: '', textContent: '', hidden: false, dataset: {}, classList: { toggle() {} }, setAttribute() {}, focus() {} });
    return elements.get(id);
  }
  storage.set('co-chill-v4-browser', JSON.stringify(initialState));
  const document = { getElementById: element, documentElement: { dataset: {} }, body: { classList: { toggle() {} } }, querySelector: () => null, querySelectorAll: () => [], addEventListener: (kind, fn) => { listeners[kind] = fn; } };
  // Modules loaded in the host share the same simulated clock as the app VM.
  const sandbox = { CC: { ...CC, sanitize: (raw, options) => CC.sanitize(raw, options || { now }) }, XQ, FIXTURES: [puzzle], document, location: { hash: initialHash }, console, Date: class extends Date { static now() { return now; } },
    localStorage: { getItem: k => storage.get(k) || null, setItem: (k, v) => storage.set(k, v), removeItem: k => storage.delete(k) },
    setInterval() {}, setTimeout() {}, clearTimeout() {}, confirm: () => true, FormData: class { constructor() {} } };
  sandbox.window = { addEventListener() {}, scrollTo() {} };
  vm.createContext(sandbox); vm.runInContext(fs.readFileSync(path.join(__dirname, '../online-preview/app.js'), 'utf8'), sandbox);
  return { run: text => vm.runInContext(text, sandbox), advance: delta => { now += delta; }, html: () => element('main').innerHTML,
    click(action) { const target = { dataset: { action, value: '' } }; listeners.click({ target: { closest: selector => selector === '[data-action]' ? target : null } }); },
    submit() { listeners.submit({ target: { id: 'reflection-form' }, preventDefault() {} }); }, stored: () => JSON.parse(storage.get('co-chill-v4-browser')) };
}

test('actual app keeps answer hidden until requested help has been read and explicitly accepted', () => {
  const state = CC.fresh(); state.session = CC.createSession(puzzle, { now: T0 });
  const app = appHarness(state);
  assert.equal(app.html().includes('ANSWER_SPOILER'), false);
  app.click('guided-reveal'); assert.equal(app.run('state.session.stage'), 'reflect');
  app.click('unknown'); assert.equal(app.run('state.session.assisted'), true);
  assert.equal(app.html().includes('ANSWER_SPOILER'), false);
  app.click('guided-reveal'); assert.equal(app.run('state.session.stage'), 'reflect');
  app.advance(9999); app.click('guided-reveal'); assert.equal(app.run('state.session.stage'), 'reflect');
  app.advance(1); app.click('guided-reveal'); assert.equal(app.run('state.session.stage'), 'explain');
  assert.equal(app.html().includes('ANSWER_SPOILER'), true);
  assert.equal(app.run('state.session.unknown'), true);
});

test('actual app wrong first submission preserves thoughts, offers gated help, reveals at third attempt', () => {
  const state = CC.fresh(); state.session = session(); state.session.candidate = 'a3a4';
  const app = appHarness(state); app.submit();
  assert.equal(app.run('state.session.submissionCount'), 1); assert.equal(app.run('state.session.stage'), 'reflect');
  assert.equal(app.run('state.session.firstCandidate'), 'a3a4'); assert.equal(app.html().includes('ANSWER_SPOILER'), false);
  app.click('guided-reveal'); assert.equal(app.run('state.session.stage'), 'reflect');
  app.run('state.session.answers[0] = "Đã sửa suy nghĩ"'); app.submit();
  assert.equal(app.run('state.session.submissionCount'), 2); assert.equal(app.run('state.session.stage'), 'reflect');
  app.submit(); assert.equal(app.run('state.session.submissionCount'), 3); assert.equal(app.run('state.session.stage'), 'explain');
  assert.notEqual(app.run('state.session.firstAnswers[0]'), 'Đã sửa suy nghĩ');
  assert.equal(app.stored().session.firstCandidate, 'a3a4'); assert.equal(app.stored().session.assisted, true);
});

test('actual app blocks training answers and opening guidance during a live game', () => {
  const state = CC.fresh(); state.session = CC.reveal(session());
  state.games = [{ id: 'live', initialFen: XQ.START_FEN, fen: XQ.START_FEN, status: { over: false }, mode: 'local', player: 'w', moves: [], clock: { enabled: false } }];
  const app = appHarness(state);
  assert.equal(app.html().includes('ANSWER_SPOILER'), false); assert.ok(app.html().includes('Ván đang diễn ra'));
  for (const route of ['lessons', 'opening/0', 'rules', 'replay/live', 'moments/live']) {
    app.run('location.hash=' + JSON.stringify('#' + route) + ';render()');
    assert.ok(app.html().includes('Ván đang diễn ra'), route);
  }
});

test('a fresh direct learn route displays an empty state without dereferencing a missing session', () => {
  const app = appHarness(CC.fresh());
  assert.ok(app.html().includes('Chọn một hình cờ để bắt đầu'));
  assert.equal(app.html().includes('ANSWER_SPOILER'), false);
});

let failed = 0;
for (const { name, fn } of tests) {
  try { fn(); console.log('PASS ' + name); } catch (error) { failed++; console.error('FAIL ' + name + '\n' + error.stack); }
}
console.log((tests.length - failed) + '/' + tests.length + ' experience tests passed');
process.exitCode = failed ? 1 : 0;
