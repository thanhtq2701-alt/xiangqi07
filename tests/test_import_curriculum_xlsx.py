"""tools/import_curriculum_xlsx.py: workbook reading, rule checks, deterministic output."""
from pathlib import Path
from xml.sax.saxutils import escape
import json
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import import_curriculum_xlsx as imp  # noqa: E402

NODE = shutil.which('node')
HEAD = {name: list(columns) for name, columns in imp.SHEETS.items()}
# Four exercises from the owner's workbook (moves only; the texts here are test placeholders):
# Red capture, Black capture, Red checkmate with a Soldier, and a 6-decision checkmate with an
# alternative final move.
EXERCISES = {
    'mid-opening-01': ('Ăn quân / giành ưu thế', 'Khai cuộc', 'Trung cấp', 'Đỏ',
                       '1nbakabnr/9/2c4c1/p3C1p1p/5N3/2p6/P3P1P1P/1r7/9/R1BAKABNR w - - 0 1', 'f5e7 f9e8 e7g8 e9f9 g8i9',
                       [('m4.5', 's6.5'), ('m5.3', 'tg5-6'), ('m3.1', None)]),
    'mid-opening-06': ('Ăn quân / giành ưu thế', 'Khai cuộc', 'Trung cấp', 'Đen',
                       '1nbakabr1/9/r3c1n1c/p3C1p1p/2p6/6P2/P1P1P3P/1CN3N2/9/1RBAKABR1 b - - 0 1', 'g7e6 h0h9 e6g7 c0e2 g7h9',
                       [('m7.5', 'x2.9'), ('m5/7', 'v7.5'), ('m7/8', None)]),
    'mid-pawn-01': ('Chiếu hết', 'Tốt', 'Trung cấp', 'Đỏ',
                    '3k1n2r/4R4/1N2P3b/9/6b1p/9/2r6/3A1A3/5p3/4KnB2 w - - 0 1', 'e8e9 d9e9 e7e8 e9d9 e8e9',
                    [('x5.1', 'tg4-5'), ('b5.1', 'tg5-4'), ('b5.1', None)]),
    'hard-pawn-03': ('Chiếu hết', 'Tốt', 'Khó', 'Đỏ',
                     '2r1RNbC1/3ka1P2/b4r3/2p2P3/6p2/2pnP4/P2R2C2/9/1c7/1N3KB2 w - - 0 1',
                     'd3d4 c4d4 e9e8 d8e8 g8f8 e8f8 f6f7 f8e8 g3e3 g9e7 f7e7',
                     [('x6.1', 'bt-4'), ('x5/1', 'tg4-5'), ('b3-4', 'tg5-6'), ('b4.1', 'tg6-5'), ('p3-5', 'v7.5'), ('b4-5', None)]),
}
ALTERNATIVE = ('hard-pawn-03', 5, 'b4.1 (tốt tiến chiếu) cũng chiếu hết ngay.', 'f7f8')
LEVELS = {'Trung cấp': 'Trung cấp', 'Khó': 'Khó'}


def rows():
    """Workbook rows as {sheet: [dict]} for the four sample exercises."""
    tech, lessons, tree = [], [], []
    for pid, (kind, topic, level, side, fen, line, moves) in EXERCISES.items():
        decisions = str(len(moves))
        tech.append({'id': pid, 'loai_bai': kind, 'chu_de': topic, 'muc_do': level, 'so_quyet_dinh': decisions,
                     'ben_di': side, 'fen': fen, 'loi_giai_uci': line, 'nguon': 'Ván tự đấu Pikafish'})
        lessons.append({'id': pid, 'chu_de': topic, 'muc_do': level, 'so_quyet_dinh': decisions, 'loai_bai': kind,
                        'danh_gia_hinh_co': f'Nhận định {pid}', 'muc_tieu': ('Đen đi trước. ' if side == 'Đen' else '') + f'Ý tưởng {pid}',
                        'ghi_chu_kiem_chung': f'Vì sao ngay {pid}'})
        uci = line.split()
        for k, (learner, reply) in enumerate(moves):
            last = k == len(moves) - 1
            tree.append({'exercise_id': pid, 'node_id': f'n{k}', 'nuoc_nguoi_hoc': learner,
                         'nuoc_dap_doi_thu': 'kết thúc' if last else reply, 'next_node_id': '' if last else f'n{k + 1}',
                         'ly_do_nuoc_di': f'Lý do {pid} {k}', 'nuoc_khac_chap_nhan': '', 'phan_ung_can_luu_y': f'Lưu ý {pid} {k}' if k == 0 else '',
                         'uci_nguoi_hoc': uci[2 * k], 'uci_doi_thu': '' if last else uci[2 * k + 1], 'uci_nuoc_khac_chap_nhan': ''})
    pid, k, note, uci_alt = ALTERNATIVE
    row = next(r for r in tree if r['exercise_id'] == pid and r['node_id'] == f'n{k}')
    row.update(nuoc_khac_chap_nhan=note, uci_nuoc_khac_chap_nhan=uci_alt)
    return {'Du_lieu_ky_thuat': tech, 'Bai_hoc': lessons, 'Cay_nuoc_di': tree}


def write_xlsx(path, sheets, shared=False, doctype=False, extra_sheet=True):
    """A minimal .xlsx: inline strings by default, a shared-string table when shared=True."""
    table, index = [], {}

    def cell(ref, value):
        value = str(value)
        if shared:
            if value not in index:
                index[value] = len(table)
                table.append(value)
            return f'<c r="{ref}" t="s"><v>{index[value]}</v></c>'
        return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(value)}</t></is></c>'

    names = list(sheets) + (['Engine_doi_chieu'] if extra_sheet else [])
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr('xl/workbook.xml', '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + ''.join(f'<sheet name="{n}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, n in enumerate(names)) + '</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + ''.join(f'<Relationship Id="rId{i + 1}" Target="worksheets/sheet{i + 1}.xml" Type="worksheet"/>' for i in range(len(names))) + '</Relationships>')
        for i, name in enumerate(names):
            data = sheets.get(name, [])
            columns = HEAD.get(name, ['exercise_id'])
            lines = [[*columns]] + [[r.get(c, '') for c in columns] for r in data]
            body = ''.join('<row r="%d">%s</row>' % (y + 1, ''.join(cell(f'{chr(65 + x)}{y + 1}', v) for x, v in enumerate(line) if v != ''))
                           for y, line in enumerate(lines))
            dtd = '<!DOCTYPE x [<!ENTITY a "aaaa">]>' if doctype and i == 0 else ''
            z.writestr(f'xl/worksheets/sheet{i + 1}.xml', f'<?xml version="1.0"?>{dtd}<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{body}</sheetData></worksheet>')
        if shared:
            z.writestr('xl/sharedStrings.xml', '<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                       + ''.join(f'<si><t xml:space="preserve">{escape(s)}</t></si>' for s in table) + '</sst>')


class ImportCurriculumXlsxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.out = self.tmp / 'curriculum-pack.js'
        self.en = self.tmp / 'en.json'
        # The real bank (without the generated pack) so id clashes with the app are tested for real.
        self.bank = imp.positions.existing_bank(include_pack=False)

    def book(self, sheets=None, **options):
        path = self.tmp / 'book.xlsx'
        write_xlsx(path, sheets or rows(), **options)
        return path

    def translate(self, path):
        """Fill an English translation for every Vietnamese text (placeholder English)."""
        report, _, _ = imp.run(path, self.out, False, self.en, None, bank=self.bank, template=self.en)
        data = json.loads(self.en.read_text(encoding='utf-8'))
        data['entries'] = {vi: f'Draft English {i}' for i, vi in enumerate(data['entries'])}
        self.en.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def run_import(self, path, write=True):
        return imp.run(path, self.out, write, self.en, None, bank=self.bank)

    def messages(self, report, level='error'):
        return [f'{i["where"]}: {i["message"]}' for i in report.items if i['level'] == level]

    def test_valid_workbook_writes_pack_and_running_again_changes_nothing(self):
        for shared in (False, True):
            with self.subTest(shared=shared):
                path = self.book(shared=shared)
                self.translate(path)
                report, pack, status = self.run_import(path)
                self.assertEqual(self.messages(report), [])
                self.assertEqual(status, 'written')
                first = self.out.read_bytes()
                report, again, status = self.run_import(path)
                self.assertEqual(status, 'unchanged')
                self.assertEqual(self.out.read_bytes(), first)
                ids = [ex['id'] for ex in again['exercises']]
                self.assertEqual(ids, list(EXERCISES))
                self.assertEqual(len(ids), len(set(ids)))
                self.out.unlink()

    def test_fields_map_to_the_line_model(self):
        path = self.book()
        self.translate(path)
        _, pack, _ = self.run_import(path)
        ex = {e['id']: e for e in pack['exercises']}
        red, black, mate, hard = ex['mid-opening-01'], ex['mid-opening-06'], ex['mid-pawn-01'], ex['hard-pawn-03']
        self.assertEqual((red['objective'], red['chapterId'], red['phase'], red['learner'], red['difficulty'], red['decisions']),
                         ('material', 'opening-foundation', 'opening', 'w', 'intermediate', 3))
        self.assertGreater(red['proof']['materialGain'], 0)
        self.assertEqual(red['fen'], '1heakaehr/9/2c4c1/p3C1p1p/5H3/2p6/P3P1P1P/1r7/9/R1EAKAEHR w')
        self.assertEqual(red['nodes']['n0']['choices'][0], {'move': 'f5e7', 'reply': 'f9e8', 'next': 'n1', 'reason': 'Lý do mid-opening-01 0'})
        self.assertEqual(red['nodes']['n0']['watchOut'], 'Lưu ý mid-opening-01 0')
        self.assertEqual(red['nodes']['n2']['choices'][0]['next'], None)
        self.assertEqual(red['nodes']['n2']['rejectedMoves'], [])     # other legal moves wait for verification
        self.assertEqual((red['assessment'], red['idea'], red['urgency']),
                         ('Nhận định mid-opening-01', 'Ý tưởng mid-opening-01', 'Vì sao ngay mid-opening-01'))
        self.assertEqual(black['learner'], 'b')
        self.assertTrue(black['goal'].startswith('Đen đi trước.'))
        self.assertTrue(red['goal'].startswith('Đỏ đi trước.'))
        for e in (red, black, mate, hard):
            # The goal shown before solving is a template: no author text, no move.
            self.assertNotIn(e['idea'], e['goal'])
            self.assertIsNone(imp.NOTATION.search(e['goal']))
        self.assertEqual((mate['objective'], mate['chapterId'], mate['skill']), ('mate', 'pawn', 'safety'))
        self.assertEqual((hard['difficulty'], hard['decisions'], hard['title']), ('advanced', 6, 'Tốt · Chiếu hết 2'))
        self.assertEqual(pack['en']['hard-pawn-03']['title'], 'Soldier · Checkmate 2')
        self.assertFalse(hard['proof']['pikafishVerified'])
        self.assertFalse(hard['proof']['expertReviewed'])

    def test_alternative_and_every_immediate_mate_are_accepted_on_the_last_move(self):
        path = self.book()
        self.translate(path)
        _, pack, _ = self.run_import(path)
        last = next(e for e in pack['exercises'] if e['id'] == 'hard-pawn-03')['nodes']['n5']
        self.assertEqual([(c['move'], c.get('note'), c.get('auto')) for c in last['choices']],
                         [('f7e7', None, None), ('f7f8', 'B4.1 (tốt tiến chiếu) cũng chiếu hết ngay.', None)])
        # Without the listed alternative, the rules still find the second mate and accept it.
        sheets = rows()
        for row in sheets['Cay_nuoc_di']:
            row.update(nuoc_khac_chap_nhan='', uci_nuoc_khac_chap_nhan='')
        path = self.book(sheets)
        self.translate(path)
        report, pack, _ = self.run_import(path, write=False)
        last = next(e for e in pack['exercises'] if e['id'] == 'hard-pawn-03')['nodes']['n5']
        self.assertEqual([(c['move'], c.get('auto')) for c in last['choices']], [('f7e7', None), ('f7f8', 'mate')])
        self.assertTrue(any('f7f8' in m for m in self.messages(report, 'warning')))

    def test_errors_stop_the_import_with_a_clear_message(self):
        def change(sheet, pid, **values):
            def apply(sheets):
                for row in sheets[sheet]:
                    if row.get('id', row.get('exercise_id')) == pid and (sheet != 'Cay_nuoc_di' or row['node_id'] == values.get('_node', 'n0')):
                        row.update({k: v for k, v in values.items() if not k.startswith('_')})
            return apply

        def duplicate(sheets):
            sheets['Du_lieu_ky_thuat'].append(dict(sheets['Du_lieu_ky_thuat'][0]))

        cases = [
            (change('Du_lieu_ky_thuat', 'mid-opening-01', fen='bad fen w'), 'FEN không đọc được'),
            (change('Du_lieu_ky_thuat', 'mid-opening-01', loi_giai_uci='f5e7 f9e8 e7g8 e9f9 g8i8'), 'không hợp lệ theo app/rules.py'),
            (change('Du_lieu_ky_thuat', 'mid-opening-01', ben_di='Đen'), 'ben_di là Đen nhưng FEN cho Đỏ đi'),
            (change('Du_lieu_ky_thuat', 'mid-opening-01', loai_bai='Chiếu hết'), 'chưa chiếu bí'),
            (change('Du_lieu_ky_thuat', 'mid-opening-01', id='v6-rooks-palace-a'), 'đã có trong kho bài'),
            (change('Du_lieu_ky_thuat', 'mid-opening-01', so_quyet_dinh='4'), 'so_quyet_dinh là 4'),
            (duplicate, 'trùng'),
            (change('Cay_nuoc_di', 'mid-opening-01', uci_nguoi_hoc='f5d6'), 'khác loi_giai_uci'),
            (change('Cay_nuoc_di', 'mid-opening-01', uci_doi_thu='d9e8'), 'uci_doi_thu "d9e8" khác loi_giai_uci'),
            (change('Cay_nuoc_di', 'mid-opening-01', ly_do_nuoc_di=''), 'Thiếu ly_do_nuoc_di'),
            (change('Cay_nuoc_di', 'mid-opening-01', uci_nuoc_khac_chap_nhan='a0a9'), 'uci_nuoc_khac_chap_nhan "a0a9" không hợp lệ'),
            (change('Cay_nuoc_di', 'hard-pawn-03', _node='n5', uci_nuoc_khac_chap_nhan='f9h8'), 'chưa đạt mục tiêu'),
            (change('Bai_hoc', 'mid-opening-01', muc_do='Khó'), 'muc_do "Khó" khác Du_lieu_ky_thuat'),
            (change('Bai_hoc', 'mid-opening-01', muc_tieu=''), 'Thiếu muc_tieu'),
        ]
        self.translate(self.book())
        for modify, expected in cases:
            with self.subTest(expected=expected):
                sheets = rows()
                modify(sheets)
                path = self.book(sheets)
                report, pack, status = self.run_import(path)
                self.assertEqual(status, 'errors')
                self.assertIsNone(pack)
                self.assertTrue(any(expected in m for m in self.messages(report)), self.messages(report))
                self.assertFalse(self.out.exists())

    def test_missing_english_blocks_the_write_and_keeps_the_existing_pack(self):
        path = self.book()
        self.translate(path)
        self.run_import(path)
        before = self.out.read_bytes()
        sheets = rows()
        sheets['Bai_hoc'][0]['muc_tieu'] = 'Một mục tiêu mới chưa dịch'
        report, pack, status = self.run_import(self.book(sheets))
        self.assertEqual(status, 'errors')
        self.assertTrue(any('Thiếu bản dịch' in m for m in self.messages(report)))
        self.assertEqual(self.out.read_bytes(), before)

    def test_version_goes_up_only_when_the_moves_change(self):
        path = self.book()
        self.translate(path)
        self.run_import(path)
        # Text only: a saved session still replays, so the version stays.
        sheets = rows()
        sheets['Cay_nuoc_di'][0]['phan_ung_can_luu_y'] = 'Ghi chú khác'
        path = self.book(sheets)
        self.translate(path)
        report, pack, status = self.run_import(path)
        self.assertEqual(status, 'written')
        self.assertEqual({e['id']: e['version'] for e in pack['exercises']}['mid-opening-01'], 1)
        # A new accepted move changes the tree: version 2, so old drafts of that exercise are not restored.
        for row in sheets['Cay_nuoc_di']:
            if row['exercise_id'] == 'mid-opening-01' and row['node_id'] == 'n2':
                row.update(nuoc_khac_chap_nhan='Pháo ăn quân khác cũng hơn quân.', uci_nuoc_khac_chap_nhan='e6i6')
        path = self.book(sheets)
        self.translate(path)
        report, pack, status = self.run_import(path)
        versions = {e['id']: e['version'] for e in pack['exercises']}
        self.assertEqual((versions['mid-opening-01'], versions['mid-pawn-01']), (2, 1))
        self.assertTrue(any('tăng version lên 2' in m for m in self.messages(report, 'warning')))
        report, pack, status = self.run_import(path)
        self.assertEqual(status, 'unchanged')

    def test_workbook_shape_and_unsafe_xml_are_rejected(self):
        with self.assertRaisesRegex(imp.WorkbookError, 'Thiếu sheet'):
            imp.read_workbook(self.book({'Du_lieu_ky_thuat': rows()['Du_lieu_ky_thuat']}, extra_sheet=False))
        sheets = rows()
        for row in sheets['Bai_hoc']:
            row.pop('ghi_chu_kiem_chung')
        original = HEAD['Bai_hoc']
        HEAD['Bai_hoc'] = [c for c in original if c != 'ghi_chu_kiem_chung']
        try:
            with self.assertRaisesRegex(imp.WorkbookError, 'thiếu cột: ghi_chu_kiem_chung'):
                imp.read_workbook(self.book(sheets))
        finally:
            HEAD['Bai_hoc'] = original
        with self.assertRaisesRegex(imp.WorkbookError, 'DOCTYPE'):
            imp.read_workbook(self.book(doctype=True))
        not_zip = self.tmp / 'plain.xlsx'
        not_zip.write_text('hello', encoding='utf-8')
        with self.assertRaisesRegex(imp.WorkbookError, 'không phải .xlsx'):
            imp.read_workbook(not_zip)

    def test_display_text_keeps_words_and_uses_the_app_case_for_notation(self):
        self.assertEqual(imp.display_text('  xe 2   ăn tốt (x5.5), tg5-6 rồi xt.1\n'), 'xe 2 ăn tốt (X5.5), Tg5-6 rồi Xt.1')
        self.assertEqual(imp.display_text('bt4.1 và b4.1'), 'Bt4.1 và B4.1')

    @unittest.skipUnless(NODE, 'Node.js is needed to compare Vietnamese notation')
    def test_author_notation_is_compared_with_the_app(self):
        sheets = rows()
        sheets['Cay_nuoc_di'][0]['nuoc_nguoi_hoc'] = 'm4.6'
        path = self.book(sheets)
        self.translate(path)
        report, _, _ = imp.run(path, self.out, False, self.en, NODE, bank=self.bank)
        self.assertTrue(any('"m4.6", ứng dụng ghi "M4.5"' in m for m in self.messages(report, 'warning')), report.items)

    @unittest.skipUnless(imp.DEFAULT_XLSX.is_file(), 'the owner workbook lives only in var/import/ on the owner machine')
    def test_owner_workbook_matches_the_committed_pack(self):
        report, pack, status = imp.run(imp.DEFAULT_XLSX, imp.DEFAULT_OUT, False, imp.DEFAULT_EN, None)
        self.assertEqual(self.messages(report), [])
        self.assertEqual(status, 'unchanged')
        self.assertEqual(len(pack['exercises']), 70)


if __name__ == '__main__':
    unittest.main()
