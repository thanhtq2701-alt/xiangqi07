/* English translation coverage for Cờ Chill.
 * 1. Every Vietnamese string in curriculum.js / fixtures.js has an entry in content-en.js, and no entry is stale.
 * 2. Every Vietnamese text fragment in the frontend and in server messages translates to English.
 * 3. WXF notation conversion and glossary terms. Run: node tools/test_i18n_en.cjs */
'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert');
const ROOT = path.resolve(__dirname, '..');
const WEB = f => path.join(ROOT, 'online-preview', f);
const VI = /[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]/i;
const BRAND = /Cờ Chill|CỜ CHILL/g;
const curriculum = require(WEB('curriculum.js'));
const fixtures = new Function(fs.readFileSync(WEB('fixtures.js'), 'utf8') + ';return FIXTURES;')();
const content = require(WEB('content-en.js'));
const english = require(WEB('i18n-en-ui.js'));
const legacy = require(WEB('v6-ui.js'));
english.addEntries(Object.values(content).map(e => [e.vi, e.en]));
const translate = text => english.translate(text, s => legacy.t(s, 'en'));
let passed = 0;
function test(name, fn) { fn(); passed++; console.log('PASS ' + name); }

test('every lesson string has a current English entry', () => {
  const found = new Map();
  const walk = (key, value) => {
    if (typeof value === 'string') { if (VI.test(value) || /^(Xe)$/.test(value)) found.set(key, value); return; }
    if (Array.isArray(value)) value.forEach((v, i) => walk(`${key}[${i}]`, v));
    else if (value && typeof value === 'object') for (const k of Object.keys(value)) walk(`${key}.${k}`, value[k]);
  };
  for (const kind of ['courses', 'chapters', 'lessons', 'exercises']) for (const item of curriculum[kind]) walk(`${kind}#${item.id}`, item);
  for (const item of fixtures) walk(`fixtures#${item.id}`, item);
  const missing = [...found].filter(([k]) => !content[k]).map(([k]) => k);
  const stale = [...found].filter(([k, v]) => content[k] && content[k].vi !== v).map(([k]) => k);
  const orphan = Object.keys(content).filter(k => !found.has(k));
  assert.deepStrictEqual(missing, [], 'Missing English for: ' + missing.join(', '));
  assert.deepStrictEqual(stale, [], 'Vietnamese source changed; update English for: ' + stale.join(', '));
  assert.deepStrictEqual(orphan, [], 'English entries with no source: ' + orphan.join(', '));
});

function fragments(text) {
  const out = [];
  for (let p of text.replace(/\$\{[^}]*\}/g, '\u0000').split(/<[^>]*>|\u0000/)) {
    p = p.replace(/&nbsp;/g, ' ').replace(/\\n/g, ' ').replace(/\s+/g, ' ').trim();
    if (p && VI.test(p)) out.push(p);
  }
  for (const m of text.matchAll(/(?:placeholder|title|aria-label|alt)="([^"$]*)"/g)) if (VI.test(m[1])) out.push(m[1].trim());
  return out;
}
// Code fragments produced by splitting template literals, not text a user sees.
const CODE = /\$\{|=>|\?'|':|btn\(|^:|^'|\.map\(|\+'/;
// Intentionally Vietnamese: notation keywords and examples that the importer only accepts in Vietnamese.
// Fragments of template strings whose full runtime text is covered by a dictionary entry or pattern.
const KEEP = new Set(['trước', 'sau', 'giữa', 'bạn', 'đối thủ', '. Chọn Vào chơi để tham gia hoặc Xem ván để theo dõi.', 'Không có nước hợp lệ khớp ký phổ này. Ví dụ P2-5, M2.3, X trước.1 hoặc a3a4.']);

test('every interface and server message fragment translates', () => {
  const sources = [];
  for (const f of fs.readdirSync(path.join(ROOT, 'online-preview'))) {
    if (!f.endsWith('.js') || ['curriculum.js', 'fixtures.js', 'content-en.js', 'i18n-en-ui.js'].includes(f)) continue;
    const src = fs.readFileSync(WEB(f), 'utf8');
    for (const m of src.matchAll(/'((?:[^'\\\n]|\\.)*)'|"((?:[^"\\\n]|\\.)*)"|`((?:[^`\\]|\\.)*)`/g)) {
      const s = m[1] ?? m[2] ?? m[3];
      if (s && VI.test(s)) for (const p of fragments(s.replace(/\\'/g, "'").replace(/\\"/g, '"'))) sources.push([f, p]);
    }
  }
  for (const p of fragments(fs.readFileSync(WEB('index.html'), 'utf8'))) sources.push(['index.html', p]);
  const py = [...fs.readdirSync(path.join(ROOT, 'app')).filter(f => f.endsWith('.py')).map(f => path.join(ROOT, 'app', f)), path.join(ROOT, 'co_chill_server.py')];
  for (const file of py) {
    const src = fs.readFileSync(file, 'utf8');
    for (const m of src.matchAll(/'((?:[^'\\\n]|\\.)*)'|"((?:[^"\\\n]|\\.)*)"/g)) {
      const s = m[1] ?? m[2];
      if (s && VI.test(s)) for (const p of fragments(s.replace(/\{[^}]*\}/g, '\u0000'))) sources.push([path.basename(file), p]);
    }
  }
  const failures = [...new Map(sources.filter(([, p]) => !CODE.test(p) && !KEEP.has(p))
    .filter(([, p]) => VI.test(translate(p).replace(BRAND, ''))).map(([f, p]) => [p, f]))];
  assert.deepStrictEqual(failures, [], 'Untranslated:\n' + failures.map(([p, f]) => `  ${f}: ${p}`).join('\n'));
});

test('Vietnamese notation converts to WXF', () => {
  const cases = { 'P2-5': 'C2=5', 'M8.7': 'H8+7', 'X1/2': 'R1-2', 'Tg5.1': 'K5+1', 'S4.5': 'A4+5', 'T3.5': 'E3+5', 'B7.1': 'P7+1', 'Xtrước.1': '+R+1', 'M sau/3': '-H-3' };
  for (const [vi, wxf] of Object.entries(cases)) assert.strictEqual(english.notation(vi), wxf, vi);
  assert.strictEqual(english.notation('Chiếu hết'), 'Chiếu hết');
});

test('English follows the glossary', () => {
  const banned = /\b(squares?|Rook|Knight|King|Bishop|practis\w*|centre|colour)\b/;
  const values = [...Object.values(english.dictionary), ...Object.values(content).map(e => e.en)];
  const bad = values.filter(v => banned.test(v));
  assert.deepStrictEqual(bad, [], 'Glossary violations: ' + bad.join(' | '));
});

console.log(`${passed}/4 i18n English tests passed`);
