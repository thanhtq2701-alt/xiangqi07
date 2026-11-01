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
// Every string literal in a JavaScript source: '...', "..." and template literals, including templates
// nested inside ${...} of another template. In a template, each ${...} becomes \u0000 so the text splits there;
// strings inside the expression are returned as literals of their own. A regex scan cannot pair nested backticks.
function literals(src) {
  const out = [], templates = [];
  let i = 0, prev = '';
  while (i < src.length) {
    const c = src[i], top = templates[templates.length - 1];
    if (top && top.inText) {
      if (c === '\\') { top.text += src.slice(i, i + 2); i += 2; }
      else if (c === '`') { out.push(top.text); templates.pop(); i++; prev = '`'; }
      else if (c === '$' && src[i + 1] === '{') { top.text += '\u0000'; top.inText = false; top.depth = 0; i += 2; prev = '{'; }
      else { top.text += c; i++; }
      continue;
    }
    if (c === '/' && src[i + 1] === '/') { while (i < src.length && src[i] !== '\n') i++; continue; }
    if (c === '/' && src[i + 1] === '*') { const end = src.indexOf('*/', i + 2); i = end < 0 ? src.length : end + 2; continue; }
    if (c === "'" || c === '"') {
      let j = i + 1, text = '';
      while (j < src.length && src[j] !== c && src[j] !== '\n') { if (src[j] === '\\') { text += src.slice(j, j + 2); j += 2; } else text += src[j++]; }
      out.push(text); i = j + 1; prev = 'a'; continue;
    }
    if (c === '`') { templates.push({ text: '', inText: true, depth: 0 }); i++; continue; }
    if (c === '/' && (prev === '' || '(,=:[!&|?{};+-*%<>~^'.includes(prev))) {
      let j = i + 1, inClass = false;
      while (j < src.length && src[j] !== '\n') {
        if (src[j] === '\\') { j += 2; continue; }
        if (src[j] === '[') inClass = true; else if (src[j] === ']') inClass = false; else if (src[j] === '/' && !inClass) break;
        j++;
      }
      i = j + 1; while (/[a-z]/i.test(src[i] || '')) i++; prev = 'a'; continue;
    }
    if (top) {
      if (c === '{') top.depth++;
      else if (c === '}') { if (top.depth === 0) { top.inText = true; i++; continue; } top.depth--; }
    }
    if (!/\s/.test(c)) prev = c;
    i++;
  }
  return out;
}
// Code fragments produced by splitting template literals, not text a user sees.
const CODE = /\$\{|=>|\?'|':|btn\(|^:|^'|\.map\(|\+'/;
// Intentionally Vietnamese: notation keywords and examples that the importer only accepts in Vietnamese.
// Fragments of template strings whose full runtime text is covered by a dictionary entry or pattern.
const KEEP = new Set(['trước', 'sau', 'giữa', 'bạn', 'đối thủ', '. Chọn Vào chơi để tham gia hoặc Xem ván để theo dõi.', 'Không có nước hợp lệ khớp ký phổ này. Ví dụ P2-5, M2.3, X trước.1 hoặc a3a4.',
  // Pieces joined with numbers, names or moves at runtime; the full text is checked in RUNTIME below.
  'hình đến hạn', 'Nước bạn chọn:', '· độ sâu ghi nhận', 'nửa nước.', 'Tìm kiếm cơ bản gợi ý', 'Kết quả tìm kiếm đề xuất',
  'quy ước tìm kiếm nông', 'centipawn của engine', 'Đối thủ', '· hiệu lực 15 giây', 'Phòng', 'Bạn cầm', 'Tạm khóa 24 giờ',
  'hình cờ đã đến lúc ôn', 'LƯỢT', 'TỰ QUAN SÁT ·', 'Suy nghĩ ban đầu', 'đề nghị hòa. Bên còn lại xác nhận trong 15 giây; đồng hồ vẫn chạy.',
  '· đã kiểm tra', 'vị trí ·', 'nước đầu phù hợp mẫu, không hỗ trợ ·', 'bài', 'mục)', 'Đến lượt', 'ván ·', '· phiên bản', 'Chương', 'chương',
  'hình minh họa ·', 'Biến mẫu đã kiểm chứng:']);
// Full runtime text built from the KEEP pieces above (and similar), as the user sees it.
const RUNTIME = ['3 hình đến hạn', 'Nước bạn chọn: P2-5', 'Phòng 0123456789', 'Bạn cầm Đỏ', 'Bạn cầm Đen · Đỏ đến lượt', 'Bạn đang xem ván · Đen đến lượt',
  'Bạn đề nghị hòa · hiệu lực 15 giây.', 'Đối thủ đề nghị hòa · hiệu lực 15 giây.', 'Bạn đề nghị đi lại.', 'Đối thủ đề nghị đi lại.',
  'Tạm khóa 24 giờ @user_1?', 'Mở khóa @user_1?', 'Cần học tiếp · chưa hoàn thành · Đến hạn', 'Cần học tiếp · chưa hoàn thành · Hẹn 14:30 02/11',
  'Ôn hình đã học · Đến hạn', 'Lịch ôn tính từ 14:30 01/11. Hẹn ôn 14:30 02/11.', 'Bài do chủ website biên tập và duyệt · WXF',
  'Lượt có hỗ trợ hoặc đã xem lời giải. Chưa chấm chất lượng lập luận.', 'Lượt tự thực hiện chuỗi nước. Chưa chấm chất lượng lập luận.',
  'Lời giải theo mẫu hoặc nội dung đã duyệt, dựa trên nước hợp lệ. Pikafish · độ sâu ghi nhận 12 nửa nước. Chưa có AI chấm lập luận. Không dùng điểm này làm xếp hạng.',
  'Lời giải theo mẫu hoặc nội dung đã duyệt, dựa trên nước hợp lệ.  Chưa có AI chấm lập luận. Không dùng điểm này làm xếp hạng.',
  'Trong ván bạn đi Xe a2 → a7 ăn Pháo. Tìm kiếm cơ bản gợi ý một phương án để đối chiếu; chưa phải phán quyết chắc chắn về tư duy.',
  'Trong ván bạn đi Mã b0 → c2. Kết quả tìm kiếm đề xuất một phương án để đối chiếu; chưa phải phán quyết chắc chắn về tư duy.',
  'Biến hợp lệ được tính: Pháo h2 → e2; sau đó Mã h9 → g7. Chênh lệch 35 điểm centipawn của engine từ cùng thế và cùng bên đi.',
  'Biến hợp lệ được tính: Xe a0 → a9 ăn Xe. Chênh lệch -4 điểm quy ước tìm kiếm nông từ cùng thế và cùng bên đi.',
  'Vị trí ở nửa nước 12', 'Số liệu do thiết bị đồng bộ, chưa được xác minh độc lập. Không dùng tài khoản thử để tuyên bố tác động sản phẩm.',
  'Thống kê ghi nhận từ tài khoản đã đồng bộ · UTC+7', '3 hình cờ đã đến lúc ôn', 'TỰ QUAN SÁT · LƯỢT 2/3', 'TỰ QUAN SÁT · TRƯỚC LỜI GIẢI',
  'Suy nghĩ ban đầu 1:', 'Đỏ đề nghị hòa. Bên còn lại xác nhận trong 15 giây; đồng hồ vẫn chạy.', 'Đen đề nghị hòa. Bên còn lại xác nhận trong 15 giây; đồng hồ vẫn chạy.',
  'Máy gặp sự cố. Đồng hồ tạm dừng; ván chưa bị tính thua. Đang dùng máy cơ bản; gợi ý cần được đối chiếu.',
  'Pikafish · đã kiểm tra 40 vị trí · lượt phân tích nhanh.', 'máy cơ bản · đã kiểm tra 1 vị trí · lượt phân tích kỹ hơn. Đang dùng máy cơ bản; gợi ý cần được đối chiếu.',
  'nước đầu phù hợp mẫu, không hỗ trợ · 3/6 bài', '(3 mục)', 'Đã lưu tự đánh giá. (1 mục)', 'Đến lượt bạn', 'Đến lượt đối thủ', 'Đỏ đến lượt',
  '3 ván · 5 lượt học', 'draft · phiên bản 2',
  'Số đếm từ dữ liệu đã đồng bộ; chưa xác minh kỹ năng, Elo hoặc hiệu quả học. Không dùng tài khoản thử để tuyên bố tác động sản phẩm.', 'Chương 1', '7 chương', '3 hình minh họa · Cơ bản', 'Biến mẫu đã kiểm chứng: 2/5 nửa nước'];

test('every interface and server message fragment translates', () => {
  const sources = [];
  for (const f of fs.readdirSync(path.join(ROOT, 'online-preview'))) {
    if (!f.endsWith('.js') || ['curriculum.js', 'fixtures.js', 'content-en.js', 'i18n-en-ui.js'].includes(f)) continue;
    const src = fs.readFileSync(WEB(f), 'utf8');
    for (const lit of literals(src)) {
      if (VI.test(lit)) for (const p of fragments(lit.replace(/\\'/g, "'").replace(/\\"/g, '"'))) sources.push([f, p]);
    }
  }
  for (const p of fragments(fs.readFileSync(WEB('index.html'), 'utf8'))) sources.push(['index.html', p]);
  for (const p of RUNTIME) sources.push(['runtime', p]);
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
