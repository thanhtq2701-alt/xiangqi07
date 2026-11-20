'use strict';
/* Public profile rendering helpers. Run: node tools/test_public_profile_ui.cjs */
const assert = require('node:assert/strict');
const XQ = require('../web/xiangqi.js');
const CC = require('../web/game-tools.js');
const P = require('../web/public-profile.js');
const tests = [], test = (name, run) => tests.push({ name, run });

const profile = {
  publicId: '0123456789ab', displayName: '<img src=x onerror=alert(1)>', joined: '2026-11',
  totals: { games: 3, wins: 1, losses: 1, draws: 1 },
  games: [
    { gameId: 'g1', endedAt: '2026-11-18T17:30:00Z', side: 'w', outcome: 'win', reason: 'resigned', initialFen: XQ.START_FEN, moves: ['h2e2', 'h9g7'],
      opponent: { name: 'Bình', kind: 'public', publicId: 'abcdefabcdef' } },
    { gameId: 'g2', endedAt: '2026-11-18T16:59:00Z', side: 'b', outcome: 'loss', reason: 'Chiếu hết', initialFen: XQ.START_FEN, moves: [],
      opponent: { name: 'Người chơi ẩn', kind: 'private', publicId: null } },
    { gameId: 'g3', endedAt: '2026-11-17T01:00:00Z', side: 'w', outcome: 'draw', reason: 'draw_agreed', initialFen: XQ.START_FEN, moves: ['h2e2'],
      opponent: { name: 'Khách', kind: 'guest', publicId: 'abcdefabcdef' } }
  ]
};

test('page escapes user text and links only public opponents', () => {
  const html = P.profileHTML(profile, { tools: CC });
  assert.doesNotMatch(html, /<img/);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.match(html, /<a href="#u\/abcdefabcdef">Bình<\/a>/);
  assert.equal((html.match(/href="#u\//g) || []).length, 1, 'guest and private opponents are never linked');
  assert.match(html, /Người chơi ẩn/); assert.match(html, /Khách/);
  assert.match(html, /<b>3<\/b><span>ván online<\/span>/);
  assert.match(html, /Thắng[\s\S]*Thua[\s\S]*Hòa/);
  assert.match(html, /Xin thua/); assert.match(html, /Chiếu hết/); assert.match(html, /Hòa thỏa thuận/);
  assert.match(html, /Tham gia từ<\/span> 11\/2026/);
  assert.match(html, /Không xếp hạng, không phải Elo/);
  assert.doesNotMatch(html, /notation-table/, 'move lists stay closed until asked');
});

test('an opened game shows traditional notation, never machine coordinates', () => {
  const html = P.profileHTML(profile, { open: 'g1', tools: CC });
  assert.match(html, /<td>P2-5<\/td><td>M8\.7<\/td>/);
  assert.doesNotMatch(html, /h2e2|h9g7/);
  assert.match(html, /aria-expanded="true">Ẩn biên bản/);
  assert.match(P.profileHTML(profile, { open: 'g2', tools: CC }), /Ván kết thúc trước nước đầu tiên/);
});

test('dates use Vietnam time and unknown reasons pass through', () => {
  assert.equal(P.dayText('2026-11-18T17:30:00Z'), '19/11/2026');
  assert.equal(P.dayText('2026-11-18T16:59:00Z'), '18/11/2026');
  assert.equal(P.dayText('nope'), '');
  assert.equal(P.monthText('2026-03'), '03/2026'); assert.equal(P.monthText('x'), '');
  assert.equal(P.reasonText('timeout'), 'Hết giờ'); assert.equal(P.reasonText('Chiếu hết'), 'Chiếu hết'); assert.equal(P.reasonText(''), '');
  assert.equal(P.isPublicId('0123456789ab'), true);
  for (const bad of ['0123456789AB', '0123456789a', 'alice', null]) assert.equal(P.isPublicId(bad), false);
});

test('account panel: public shows a random-id link; private explains how others see you; admin has none', () => {
  const user = { username: 'alice', displayName: 'Alice', role: 'user', publicId: '0123456789ab', profileVisibility: 'public' };
  const pub = P.accountPanelHTML(user, 'https://example.test');
  assert.match(pub, /https:\/\/example\.test\/#u\/0123456789ab/);
  assert.doesNotMatch(pub, /alice/);
  assert.match(pub, /data-public-action="visibility" data-value="private"/);
  const priv = P.accountPanelHTML({ ...user, profileVisibility: 'private' }, 'https://example.test');
  assert.match(priv, /Người chơi ẩn/); assert.doesNotMatch(priv, /#u\//);
  assert.match(priv, /data-value="public"/);
  assert.match(P.accountPanelHTML({ ...user, role: 'admin' }, ''), /không có hồ sơ công khai/);
  assert.equal(P.accountPanelHTML(null, ''), '');
});

test('the one-time question appears only for members who have not chosen', () => {
  const base = { role: 'user', publicId: '0123456789ab' };
  assert.match(P.promptHTML({ ...base, profileVisibility: 'unset' }), /Giữ riêng tư/);
  for (const user of [{ ...base, profileVisibility: 'public' }, { ...base, profileVisibility: 'private' }, { ...base, role: 'admin', profileVisibility: 'unset' }, null])
    assert.equal(P.promptHTML(user), '');
  assert.match(P.SIGNUP_NOTE, /bật sẵn/);
});

let failed = 0;
for (const item of tests) {
  try { item.run(); console.log('PASS ' + item.name); } catch (error) { failed++; console.error('FAIL ' + item.name + '\n' + error.stack); }
}
console.log(`${tests.length - failed}/${tests.length} public profile UI tests passed`);
if (failed) process.exitCode = 1;
