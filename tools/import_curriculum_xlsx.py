"""Import the owner's curriculum workbook (.xlsx) into web/curriculum-pack.js.

    python tools/import_curriculum_xlsx.py                    # dry-run: check and report only
    python tools/import_curriculum_xlsx.py --write            # also write web/curriculum-pack.js
    python tools/import_curriculum_xlsx.py FILE.xlsx --write
    python tools/import_curriculum_xlsx.py --translation-template OUT.json

The default workbook is var/import/CoChill_70_bai_final.xlsx (var/ is ignored by
Git; the workbook is read in place, never copied, changed or committed). Only the
Python standard library is used: an .xlsx file is a zip archive of XML parts.

Sheets read: Du_lieu_ky_thuat (source of truth for logic), Bai_hoc (text shown
to the learner), Cay_nuoc_di (move tree). Engine_doi_chieu and the board images
are not imported: the board is drawn from the FEN and the move tree is the answer.

Checks with app/rules.py (errors stop the write):
  every FEN parses and its side to move matches ben_di; every UCI move is legal;
  Cay_nuoc_di matches loi_giai_uci row by row; every checkmate exercise ends in
  a real checkmate; every capture exercise ends with more material than at the
  start (rough piece values) and the game not over; ids are well formed, unique
  and not already used in the app; the same position is not imported twice;
  Bai_hoc agrees with Du_lieu_ky_thuat; every text has an English translation
  in tools/curriculum_pack_en.json.
On the last move of a checkmate exercise every legal move that mates at once is
also accepted (owner decision 20/11/2026); other legal moves outside the tree
wait for verification in the app and are never marked wrong.

The output is deterministic: running the script again on the same workbook
rewrites the same file, so nothing is duplicated. A version number only goes up
when the moves of an exercise change. Exit code: 0 = no errors, 1 = errors,
2 = the workbook or the translation file cannot be read.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))

from app.rules import Position  # noqa: E402
import import_positions as positions  # noqa: E402

DEFAULT_XLSX = ROOT / 'var' / 'import' / 'CoChill_70_bai_final.xlsx'
DEFAULT_OUT = ROOT / 'web' / 'curriculum-pack.js'
DEFAULT_EN = ROOT / 'tools' / 'curriculum_pack_en.json'
PACK_FORMAT = 'cochill-curriculum-pack-v1'
EN_FORMAT = 'cochill-translations-v1'
START, END = '/*PACK-JSON-START*/', '/*PACK-JSON-END*/'

MAX_XLSX_BYTES = 64 * 1024 * 1024      # the workbook with its 70 pictures is about 3 MB
MAX_PART_BYTES = 16 * 1024 * 1024      # any single XML part we read, after decompression
MAX_TEXT = 2000                        # characters in one text cell
MAX_DECISIONS = 20                     # line-v1 walks at most 20 learner nodes

SHEETS = {
    'Du_lieu_ky_thuat': ('id', 'loai_bai', 'chu_de', 'muc_do', 'so_quyet_dinh', 'ben_di', 'fen', 'loi_giai_uci', 'nguon'),
    'Bai_hoc': ('id', 'chu_de', 'muc_do', 'so_quyet_dinh', 'loai_bai', 'danh_gia_hinh_co', 'muc_tieu', 'ghi_chu_kiem_chung'),
    'Cay_nuoc_di': ('exercise_id', 'node_id', 'nuoc_nguoi_hoc', 'nuoc_dap_doi_thu', 'next_node_id', 'ly_do_nuoc_di',
                    'nuoc_khac_chap_nhan', 'phan_ung_can_luu_y', 'uci_nguoi_hoc', 'uci_doi_thu', 'uci_nuoc_khac_chap_nhan'),
}
# chu_de -> (chapterId in web/curriculum.js, phase, English topic name used in titles)
TOPICS = {
    'khai cuộc': ('opening-foundation', 'opening', 'Khai cuộc', 'Opening'),
    'xe': ('rook', 'middle', 'Xe', 'Chariot'),
    'pháo': ('cannon', 'middle', 'Pháo', 'Cannon'),
    'mã': ('horse', 'middle', 'Mã', 'Horse'),
    'tốt': ('pawn', 'middle', 'Tốt', 'Soldier'),
    'an toàn tướng': ('kingSafety', 'middle', 'An toàn Tướng', 'General safety'),
    'phối hợp quân': ('coordination', 'middle', 'Phối hợp quân', 'Piece coordination'),
    'tàn cuộc': ('end-basic', 'end', 'Tàn cuộc', 'Endgame'),
}
OBJECTIVES = {'chiếu hết': 'mate', 'ăn quân / giành ưu thế': 'material'}
LEVELS = {
    'trung cấp': ('intermediate', 'Trung cấp · mức dự kiến', 'Intermediate · estimated difficulty', (3, 4)),
    'khó': ('advanced', 'Khó · mức dự kiến', 'Hard · estimated difficulty', (5, 7)),
}
SIDES = {'đỏ': 'w', 'đen': 'b'}
# Rough piece values, the same table as web/line-practice.js. A consistency check
# for "the learner ends ahead in material", not an engine evaluation.
VALUES = {'r': 9, 'c': 4.5, 'h': 4, 'a': 2, 'e': 2, 'p': 1, 'k': 0}
VERIFICATION = {
    'mate': ('Lời giải do tác giả duyệt, có đối chiếu Pikafish ngoài ứng dụng; ứng dụng kiểm tra luật và chiếu bí; chưa qua chuyên gia.',
             'Solution reviewed by the author and compared with Pikafish outside the app; the app checks the rules and the checkmate; not reviewed by an expert.'),
    'material': ('Lời giải do tác giả duyệt, có đối chiếu Pikafish ngoài ứng dụng; ứng dụng kiểm tra luật và quân lực cuối biến; chưa qua chuyên gia.',
                 'Solution reviewed by the author and compared with Pikafish outside the app; the app checks the rules and the material at the end of the line; not reviewed by an expert.'),
}
ID = re.compile(r'^[a-z0-9][a-z0-9-]{2,63}$')
COORD = re.compile(r'^[a-i][0-9][a-i][0-9]$')
# Same character class as tools/test_i18n_en.cjs: a string with any of these needs English.
VI = re.compile('[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]', re.I)
# Vietnamese move notation written inside the author's text, e.g. "x5.5", "tg5-6", "xt.1", "bt4.1".
NOTATION = re.compile(r'(?<!\w)(tg|x|p|m|b|s|v)((?:[1-9][tsg]?)|(?:[tsg][1-9]?))([.\-/])([1-9])(?!\w)', re.I)
# Words the glossary bans from English (docs/I18N_GLOSSARY.md), and machine coordinates.
BANNED_EN = re.compile(r'\b(squares?|Rook|Knight|King|Bishop|practis\w*|centre|colour)\b')
MACHINE = re.compile(r'(?<![A-Za-z0-9])[a-i][0-9](?:[a-i][0-9])?(?![A-Za-z0-9])')


class WorkbookError(Exception):
    """The file is not a readable workbook of the expected shape."""


# ---------------------------------------------------------------- workbook --

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
M = '{%s}' % NS['m']


def _part(archive, name):
    """Read one XML part with a hard size limit (a zip can claim any size)."""
    try:
        info = archive.getinfo(name)
    except KeyError:
        raise WorkbookError(f'Thiếu phần {name} trong file .xlsx.') from None
    if info.file_size > MAX_PART_BYTES:
        raise WorkbookError(f'Phần {name} quá lớn ({info.file_size} byte).')
    with archive.open(info) as stream:
        data = stream.read(MAX_PART_BYTES + 1)
    if len(data) > MAX_PART_BYTES:
        raise WorkbookError(f'Phần {name} quá lớn sau khi giải nén.')
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
        raise WorkbookError(f'Phần {name} có khai báo DOCTYPE/ENTITY; file .xlsx bình thường không có.')
    try:
        return ET.fromstring(data)
    except ET.ParseError as error:
        raise WorkbookError(f'Không đọc được XML {name}: {error}') from None


def _column(ref):
    letters = re.match(r'[A-Z]+', ref or '')
    if not letters:
        raise WorkbookError(f'Ô có địa chỉ lạ: {ref!r}.')
    number = 0
    for char in letters.group():
        number = number * 26 + ord(char) - 64
    return number - 1


def _text(node):
    """Text of a <si> or <is> element: plain <t> or rich-text runs, without phonetic hints."""
    if node is None:
        return ''
    parts = [node.findtext(M + 't') or '']
    parts += [run.findtext(M + 't') or '' for run in node.findall(M + 'r')]
    return ''.join(parts)


def _cell(cell, shared):
    kind = cell.get('t')
    if kind == 'inlineStr':
        return _text(cell.find(M + 'is'))
    value = cell.findtext(M + 'v')
    if value is None:
        return ''
    if kind == 's':
        try:
            return shared[int(value)]
        except (ValueError, IndexError):
            raise WorkbookError(f'Ô {cell.get("r")} trỏ tới chuỗi không tồn tại.') from None
    if kind in (None, 'n') and re.fullmatch(r'-?\d+\.0+', value):
        return value.split('.')[0]          # 3.0 -> "3"
    return value


def read_workbook(path, wanted=SHEETS):
    """Return {sheet: [ {column: text, '_row': n}, ... ]} for the wanted sheets."""
    path = Path(path)
    if not path.is_file():
        raise WorkbookError(f'Không thấy file {path}.')
    if path.stat().st_size > MAX_XLSX_BYTES:
        raise WorkbookError(f'File quá lớn ({path.stat().st_size} byte).')
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise WorkbookError('File không phải .xlsx (không mở được như file zip).') from None
    with archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [_text(si) for si in _part(archive, 'xl/sharedStrings.xml').findall(M + 'si')]
        book = _part(archive, 'xl/workbook.xml')
        rels = _part(archive, 'xl/_rels/workbook.xml.rels')
        targets = {r.get('Id'): r.get('Target') for r in rels.findall('{%s}Relationship' % NS['rel'])}
        sheets = {}
        for sheet in book.iter(M + 'sheet'):
            target = targets.get(sheet.get('{%s}id' % NS['r']), '')
            target = target.lstrip('/')
            sheets[sheet.get('name')] = target if target.startswith('xl/') else 'xl/' + target
        missing = [name for name in wanted if name not in sheets]
        if missing:
            raise WorkbookError('Thiếu sheet: ' + ', '.join(missing) + '. Các sheet có: ' + ', '.join(sheets) + '.')
        result = {}
        for name, columns in wanted.items():
            rows = []
            for row in _part(archive, sheets[name]).iter(M + 'row'):
                values = {}
                for cell in row.findall(M + 'c'):
                    values[_column(cell.get('r'))] = _cell(cell, shared)
                if any(str(v).strip() for v in values.values()):
                    rows.append((int(row.get('r') or len(rows) + 1), values))
            if not rows:
                raise WorkbookError(f'Sheet {name} trống.')
            header_row, header = rows[0]
            names = {index: str(value).strip() for index, value in header.items()}
            absent = [c for c in columns if c not in names.values()]
            if absent:
                raise WorkbookError(f'Sheet {name} thiếu cột: ' + ', '.join(absent) + '.')
            result[name] = [{**{names[i]: str(v) for i, v in values.items() if i in names}, '_row': number}
                            for number, values in rows[1:]]
    return result


# ------------------------------------------------------------------- helpers --

def plain(value):
    """Collapse whitespace; Excel cells often carry trailing spaces or line breaks."""
    return ' '.join(str(value or '').split())


def key(value):
    return plain(value).casefold()


def display_text(value):
    """Author text for display: whitespace collapsed and move notation in the app's case (x5.5 -> X5.5)."""
    def upper(match):
        piece = 'Tg' if match.group(1).lower() == 'tg' else match.group(1).upper()
        return piece + match.group(2).lower() + match.group(3) + match.group(4)
    return NOTATION.sub(upper, plain(value))


def material(pos, side):
    total = 0
    for piece in pos.board:
        if piece != '.':
            value = VALUES[piece.lower()]
            total += value if (piece.isupper()) == (side == 'w') else -value
    return total


def is_mate(pos, learner):
    """The side to move is the learner's opponent, in check, with no legal move (the cheap test first)."""
    return pos.turn != learner and pos.in_check() and not pos.legal_moves()


def play_legal(pos, move):
    """Play a move already taken from pos.legal_moves() without generating the moves again."""
    return pos.after_unchecked(move)


def moves_of(text):
    return [t for t in re.split(r'[\s,;]+', plain(text)) if t]


def read_pack(path):
    """The JSON inside an existing generated pack, or None."""
    try:
        text = Path(path).read_text(encoding='utf-8')
    except OSError:
        return None
    if START not in text or END not in text:
        return None
    try:
        return json.loads(text.split(START, 1)[1].split(END, 1)[0])
    except json.JSONDecodeError:
        return None


def chess_fingerprint(exercise):
    """What a saved session depends on: start position, learner, objective and the move tree."""
    nodes = {nid: [(c['move'], c['reply'], c['next']) for c in node['choices']] for nid, node in exercise['nodes'].items()}
    return json.dumps([exercise['fen'], exercise['learner'], exercise['objective'], exercise['root'], nodes], sort_keys=True)


def strings(prefix, value, out):
    """Every string that tools/test_i18n_en.cjs requires English for, keyed the same way."""
    if isinstance(value, str):
        if VI.search(value) or value == 'Xe':
            out[prefix] = value
    elif isinstance(value, list):
        for i, item in enumerate(value):
            strings(f'{prefix}[{i}]', item, out)
    elif isinstance(value, dict):
        for k, item in value.items():
            strings(f'{prefix}.{k}', item, out)
    return out


def load_translations(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict) or data.get('format') != EN_FORMAT or not isinstance(data.get('entries'), dict):
        raise WorkbookError(f'{path}: cần {{"format": "{EN_FORMAT}", "entries": {{"tiếng Việt": "English"}}}}.')
    return {plain(vi): plain(en) for vi, en in data['entries'].items() if isinstance(en, str)}


# ------------------------------------------------------------------- import --

def build(book, report, bank=None):
    """Turn the workbook rows into exercises. Returns (exercises, English for the generated texts)."""
    ids, fens, chapters = bank if bank else positions.existing_bank(include_pack=False)
    tech, lessons, tree = book['Du_lieu_ky_thuat'], book['Bai_hoc'], book['Cay_nuoc_di']
    lesson_rows, tree_rows = {}, {}
    for row in lessons:
        lesson_rows.setdefault(plain(row.get('id')), []).append(row)
    for row in tree:
        tree_rows.setdefault(plain(row.get('exercise_id')), []).append(row)
    known = {plain(r.get('id')) for r in tech}
    for orphan in sorted(set(lesson_rows) - known):
        report.error(f'Bai_hoc "{orphan}" (dòng {lesson_rows[orphan][0]["_row"]})', 'id không có trong Du_lieu_ky_thuat.')
    for orphan in sorted(set(tree_rows) - known):
        report.error(f'Cay_nuoc_di "{orphan}" (dòng {tree_rows[orphan][0]["_row"]})', 'exercise_id không có trong Du_lieu_ky_thuat.')

    exercises, english, seen_ids, seen_fens, numbering = [], {}, set(), {}, {}
    for row in tech:
        pid = plain(row.get('id'))
        where = f'Du_lieu_ky_thuat "{pid}" (dòng {row["_row"]})'
        errors_before = len(report.errors)
        if not ID.match(pid):
            report.error(where, 'id cần 3–64 ký tự a-z, 0-9, gạch nối; bắt đầu bằng chữ hoặc số.')
            continue
        if pid in ids:
            report.error(where, 'id đã có trong kho bài hiện tại của ứng dụng.')
        if pid in seen_ids:
            report.error(where, 'id trùng với một dòng khác trong sheet.')
        seen_ids.add(pid)

        objective = OBJECTIVES.get(key(row.get('loai_bai')))
        topic = TOPICS.get(key(row.get('chu_de')))
        level = LEVELS.get(key(row.get('muc_do')))
        learner = SIDES.get(key(row.get('ben_di')))
        decisions = plain(row.get('so_quyet_dinh'))
        if not objective:
            report.error(where, f'loai_bai "{plain(row.get("loai_bai"))}" phải là "Chiếu hết" hoặc "Ăn quân / giành ưu thế".')
        if not topic:
            report.error(where, f'chu_de "{plain(row.get("chu_de"))}" không thuộc 8 chủ đề: ' + ', '.join(t[2] for t in TOPICS.values()) + '.')
        elif topic[0] not in chapters:
            report.error(where, f'Chương {topic[0]} chưa có trong web/curriculum.js.')
        if not level:
            report.error(where, f'muc_do "{plain(row.get("muc_do"))}" phải là "Trung cấp" hoặc "Khó".')
        if not learner:
            report.error(where, f'ben_di "{plain(row.get("ben_di"))}" phải là "Đỏ" hoặc "Đen".')
        if not decisions.isdigit() or not 1 <= int(decisions) <= MAX_DECISIONS:
            report.error(where, f'so_quyet_dinh "{decisions}" phải là số nguyên 1–{MAX_DECISIONS}.')
            decisions = None
        else:
            decisions = int(decisions)

        try:
            start = Position.from_fen(plain(row.get('fen')))
        except ValueError as error:
            report.error(where, f'FEN không đọc được: {error}')
            continue
        fen = start.fen()
        if learner and start.turn != learner:
            report.error(where, f'ben_di là {plain(row.get("ben_di"))} nhưng FEN cho {"Đỏ" if start.turn == "w" else "Đen"} đi.')
        if start.status()['over']:
            report.error(where, 'Thế bắt đầu đã kết thúc ván.')
        if fen in fens:
            report.error(where, f'Trùng thế với {fens[fen]}.')
        elif fen in seen_fens:
            report.error(where, f'Trùng thế với {seen_fens[fen]} trong file.')
        else:
            for variant, name in ((positions.mirrored(fen), 'đối xứng trái–phải'), (positions.colour_swapped(fen), 'đổi màu/lật bàn')):
                other = fens.get(variant) or seen_fens.get(variant)
                if other and variant != fen:
                    report.warn(where, f'Gần trùng ({name}) với {other}.')
        seen_fens.setdefault(fen, f'"{pid}"')

        line = moves_of(row.get('loi_giai_uci'))
        bad = [m for m in line if not COORD.match(m)]
        if not line or bad:
            report.error(where, 'loi_giai_uci cần các nước UCI cách nhau bằng dấu cách' + (f'; không đọc được: {" ".join(bad)}' if bad else '') + '.')
            continue
        if len(line) % 2 == 0:
            report.error(where, f'loi_giai_uci có {len(line)} nửa nước; biến phải kết thúc bằng nước của người học (số lẻ).')
            continue
        if decisions and (len(line) + 1) // 2 != decisions:
            report.error(where, f'so_quyet_dinh là {decisions} nhưng loi_giai_uci có {(len(line) + 1) // 2} lượt của người học.')
        # Replay the main line with the project's rules.
        played, pos = [start], start
        for ply, move in enumerate(line, 1):
            if move not in pos.legal_moves():
                report.error(where, f'loi_giai_uci nửa nước {ply} ({move}) không hợp lệ theo app/rules.py.')
                played = None
                break
            pos = pos.play(move)
            played.append(pos)
            if ply < len(line) and pos.status()['over']:
                report.error(where, f'Ván đã kết thúc ở nửa nước {ply} nhưng biến còn tiếp.')
                played = None
                break
        if not played or not objective:
            continue
        final = played[-1]
        gain = material(final, start.turn) - material(start, start.turn)
        if objective == 'mate' and not is_mate(final, start.turn):
            report.error(where, 'Bài Chiếu hết nhưng nước cuối của loi_giai_uci chưa chiếu bí.')
        if objective == 'material':
            if final.status()['over']:
                report.error(where, 'Bài Ăn quân nhưng biến kết thúc ván; nên ghi loai_bai là Chiếu hết.')
            elif gain <= 0:
                report.error(where, f'Bài Ăn quân nhưng cuối biến quân lực không hơn lúc đầu ({gain:+g} theo thang điểm quân thô).')

        lesson = lesson_rows.get(pid, [])
        lwhere = f'Bai_hoc "{pid}"' + (f' (dòng {lesson[0]["_row"]})' if lesson else '')
        texts = {}
        if len(lesson) != 1:
            report.error(lwhere, 'Cần đúng một dòng trong Bai_hoc' + (f' (đang có {len(lesson)}).' if lesson else '.'))
        else:
            lrow = lesson[0]
            for column in ('chu_de', 'muc_do', 'so_quyet_dinh', 'loai_bai'):
                if key(lrow.get(column)) != key(row.get(column)):
                    report.error(lwhere, f'{column} "{plain(lrow.get(column))}" khác Du_lieu_ky_thuat "{plain(row.get(column))}".')
            for column, field in (('danh_gia_hinh_co', 'assessment'), ('muc_tieu', 'idea'), ('ghi_chu_kiem_chung', 'urgency')):
                value = display_text(lrow.get(column))
                if not value:
                    report.error(lwhere, f'Thiếu {column}.')
                elif len(value) > MAX_TEXT:
                    report.error(lwhere, f'{column} dài quá {MAX_TEXT} ký tự.')
                texts[field] = value
            idea = texts.get('idea', '')
            if start.turn == 'b' and not idea.startswith('Đen đi trước'):
                report.warn(lwhere, 'Bài Đen đi trước nhưng muc_tieu không mở đầu bằng "Đen đi trước." (mục tiêu hiển thị trước khi giải vẫn ghi đúng bên đi).')
            if start.turn == 'w' and idea.startswith('Đen đi trước'):
                report.error(lwhere, 'muc_tieu ghi "Đen đi trước" nhưng FEN cho Đỏ đi.')

        nodes = build_nodes(pid, fen, start.turn, objective, line, played, tree_rows.get(pid, []), decisions, report)
        if nodes is None or len(report.errors) > errors_before or not (topic and level and learner):
            continue

        chapter_id, phase, topic_vi, topic_en = topic
        difficulty, label_vi, label_en, (low, high) = level
        count = decisions or (len(line) + 1) // 2
        if not low <= count <= high:
            report.warn(where, f'{count} quyết định; mức {plain(row.get("muc_do"))} dự kiến {low}–{high}.')
        number = numbering[(chapter_id, objective)] = numbering.get((chapter_id, objective), 0) + 1
        kind_vi, kind_en = ('Chiếu hết', 'Checkmate') if objective == 'mate' else ('Ăn quân', 'Win material')
        side_vi, side_en = ('Đỏ', 'Red') if start.turn == 'w' else ('Đen', 'Black')
        goal_vi = f'{side_vi} đi trước. {"Chiếu hết" if objective == "mate" else "Giành lợi thế quân"} trong {count} lượt đi của bạn.'
        goal_en = f'{side_en} to move. {"Checkmate" if objective == "mate" else "Win material"} in {count} moves.'
        skill = {'cannon': 'cannon', 'horse': 'horse'}.get(chapter_id, 'safety' if objective == 'mate' else 'material')
        proof = {'method': 'author-tree', 'objective': objective, 'maximumPlies': len(line),
                 'defender': 'author-selected-replies', 'engine': 'XQ legal rules', 'authorEngineCheck': 'outside-app',
                 'expertReviewed': False, 'pikafishVerified': False}
        if objective == 'material':
            proof['materialGain'] = gain
        auto = sorted({c['move'] for n in nodes.values() for c in n['choices'] if c.get('auto') == 'mate'})
        if auto:
            proof['autoAcceptedMates'] = len(auto)
        exercise = {
            'id': pid, 'version': 1, 'format': 'line-v1', 'objective': objective,
            'title': f'{topic_vi} · {kind_vi} {number}', 'phase': phase, 'chapterId': chapter_id, 'skill': skill,
            'pieceTags': positions.piece_tags(fen, line), 'familyId': f'{chapter_id}-{objective}',
            'difficulty': difficulty, 'difficultyLabel': label_vi, 'goal': goal_vi,
            'learner': start.turn, 'fen': fen, 'root': 'n0', 'nodes': nodes,
            'exampleLine': line, 'decisions': count, 'source': display_text(row.get('nguon')) or 'Tác giả Cờ Chill',
            'proof': proof, 'verification': VERIFICATION[objective][0],
            'assessment': texts['assessment'], 'idea': texts['idea'], 'urgency': texts['urgency'],
        }
        exercises.append(exercise)
        english[pid] = {exercise['title']: f'{topic_en} · {kind_en} {number}', goal_vi: goal_en, label_vi: label_en,
                        VERIFICATION[objective][0]: VERIFICATION[objective][1]}
    return exercises, english


def build_nodes(pid, fen, learner, objective, line, played, rows, decisions, report):
    """Cay_nuoc_di rows -> line-v1 nodes, checked against loi_giai_uci."""
    where = f'Cay_nuoc_di "{pid}"'
    if not rows:
        report.error(where, 'Không có dòng nào trong Cay_nuoc_di.')
        return None
    expected = (len(line) + 1) // 2
    if len(rows) != expected:
        report.error(where, f'Có {len(rows)} dòng nhưng loi_giai_uci có {expected} lượt của người học.')
        return None
    nodes, ok = {}, True
    for k, row in enumerate(rows):
        rwhere = f'{where} {plain(row.get("node_id")) or "?"} (dòng {row["_row"]})'
        last = k == expected - 1
        node_id, before = f'n{k}', played[2 * k]
        if plain(row.get('node_id')) != node_id:
            report.error(rwhere, f'node_id phải là {node_id} (các dòng của một bài đánh số n0, n1, … theo thứ tự).')
            ok = False
        move, reply, nxt = plain(row.get('uci_nguoi_hoc')), plain(row.get('uci_doi_thu')), plain(row.get('next_node_id'))
        if move != line[2 * k]:
            report.error(rwhere, f'uci_nguoi_hoc "{move}" khác loi_giai_uci ở nửa nước {2 * k + 1} ("{line[2 * k]}").')
            ok = False
        if last:
            if reply or nxt:
                report.error(rwhere, 'Dòng cuối không được có uci_doi_thu hoặc next_node_id.')
                ok = False
            if key(row.get('nuoc_dap_doi_thu')) not in ('kết thúc', ''):
                report.warn(rwhere, f'Dòng cuối nên ghi nuoc_dap_doi_thu là "kết thúc" (đang là "{plain(row.get("nuoc_dap_doi_thu"))}").')
        else:
            if reply != line[2 * k + 1]:
                report.error(rwhere, f'uci_doi_thu "{reply}" khác loi_giai_uci ở nửa nước {2 * k + 2} ("{line[2 * k + 1]}").')
                ok = False
            if nxt != f'n{k + 1}':
                report.error(rwhere, f'next_node_id phải là n{k + 1}.')
                ok = False
        reason = display_text(row.get('ly_do_nuoc_di'))
        watch = display_text(row.get('phan_ung_can_luu_y'))
        note = display_text(row.get('nuoc_khac_chap_nhan'))
        if not reason:
            report.error(rwhere, 'Thiếu ly_do_nuoc_di.')
            ok = False
        for column, value in (('ly_do_nuoc_di', reason), ('phan_ung_can_luu_y', watch), ('nuoc_khac_chap_nhan', note)):
            if len(value) > MAX_TEXT:
                report.error(rwhere, f'{column} dài quá {MAX_TEXT} ký tự.')
                ok = False
        if not ok:
            continue
        main = {'move': move, 'reply': None if last else reply, 'next': None if last else f'n{k + 1}', 'reason': reason}
        choices = [main]
        legal = before.legal_moves()
        alternatives = moves_of(row.get('uci_nuoc_khac_chap_nhan'))
        if note and not alternatives:
            report.error(rwhere, 'Có nuoc_khac_chap_nhan nhưng thiếu uci_nuoc_khac_chap_nhan.')
            ok = False
        for alt in alternatives:
            if not COORD.match(alt) or alt not in legal:
                report.error(rwhere, f'uci_nuoc_khac_chap_nhan "{alt}" không hợp lệ theo app/rules.py.')
                ok = False
                continue
            if alt in {c['move'] for c in choices}:
                report.error(rwhere, f'uci_nuoc_khac_chap_nhan "{alt}" trùng một nước đã có.')
                ok = False
                continue
            after = before.play(alt)
            if last:
                good = is_mate(after, learner) if objective == 'mate' else (
                    not after.status()['over'] and material(after, learner) > material(played[0], learner)) or is_mate(after, learner)
                if not good:
                    report.error(rwhere, f'Nước khác chấp nhận "{alt}" chưa đạt mục tiêu ({"chiếu bí" if objective == "mate" else "hơn quân"}).')
                    ok = False
                    continue
                choices.append({'move': alt, 'reply': None, 'next': None, 'note': note})
            else:
                # line-v1 keeps one reply per accepted move; the alternative must reach the same next position.
                if reply not in after.legal_moves() or after.play(reply).fen() != played[2 * k + 2].fen():
                    report.error(rwhere, f'Nước khác chấp nhận "{alt}" ở lượt giữa phải dẫn tới cùng thế sau nước đáp {reply}.')
                    ok = False
                    continue
                choices.append({'move': alt, 'reply': reply, 'next': f'n{k + 1}', 'note': note})
        if last and objective == 'mate':
            for candidate in legal:
                if candidate not in {c['move'] for c in choices} and is_mate(play_legal(before, candidate), learner):
                    choices.append({'move': candidate, 'reply': None, 'next': None, 'auto': 'mate'})
                    report.warn(rwhere, f'Thêm nước chiếu bí ngay {candidate} vào đáp án (bộ luật kiểm tra; quyết định 20/11/2026).')
        if not last:
            early = [c for c in legal if c != move and is_mate(play_legal(before, c), learner)]
            if early:
                report.warn(rwhere, f'Có nước chiếu bí ngay ở lượt giữa ({", ".join(early)}); trong ứng dụng sẽ chờ kiểm chứng.')
        node = {'id': node_id, 'fen': before.fen(), 'remaining': expected - k, 'choices': choices, 'rejectedMoves': []}
        if watch:
            node['watchOut'] = watch
        nodes[node_id] = node
    return nodes if ok else None


def check_notation(exercises, book, node, report):
    """Compare the author's Vietnamese notation with the app's (warnings only: display uses the app's)."""
    if not node:
        report.warn('Cay_nuoc_di', 'Không có Node.js nên bỏ qua đối chiếu ký pháp Việt (hiển thị vẫn do ứng dụng sinh từ UCI).')
        return
    rows = {}
    for row in book['Cay_nuoc_di']:
        rows.setdefault(plain(row.get('exercise_id')), []).append(row)
    requests, owners = [], []
    for ex in exercises:
        requests.append({'fen': ex['fen'], 'tokens': ex['exampleLine']})
        owners.append(ex)
    results = positions.resolve_notation(requests, node)
    for ex, result in zip(owners, results):
        if 'error' in result:
            report.warn(f'Cay_nuoc_di "{ex["id"]}"', 'Không đối chiếu được ký pháp: ' + result['error'])
            continue
        notes = result['notations']
        for k, row in enumerate(rows.get(ex['id'], [])):
            pairs = [('nuoc_nguoi_hoc', row.get('nuoc_nguoi_hoc'), notes[2 * k])]
            if 2 * k + 1 < len(notes):
                pairs.append(('nuoc_dap_doi_thu', row.get('nuoc_dap_doi_thu'), notes[2 * k + 1]))
            for column, author, app in pairs:
                if key(author).replace(' ', '') != app.casefold():
                    report.warn(f'Cay_nuoc_di "{ex["id"]}" {plain(row.get("node_id"))} (dòng {row["_row"]})',
                                f'{column} ghi "{plain(author)}", ứng dụng ghi "{app}"; giao diện dùng cách ghi của ứng dụng.')


def english_entries(exercises, generated, translations, report):
    """content-en entries for every Vietnamese string; missing translations are errors."""
    entries, missing, used = {}, {}, set()
    for ex in exercises:
        own = generated.get(ex['id'], {})
        for path, vi in strings(f'exercises#{ex["id"]}', ex, {}).items():
            en = own.get(vi) or translations.get(vi)
            if vi in translations:
                used.add(vi)
            if not en:
                missing.setdefault(vi, path)
                continue
            problems = []
            if VI.search(en):
                problems.append('còn chữ tiếng Việt')
            if BANNED_EN.search(en):
                problems.append('dùng từ bảng thuật ngữ cấm (' + BANNED_EN.search(en).group(0) + ')')
            if MACHINE.search(en) and re.search(r'\s', en):
                problems.append('có tọa độ máy (' + MACHINE.search(en).group(0) + ')')
            if problems:
                report.error(path, 'Bản tiếng Anh ' + ', '.join(problems) + ': ' + en[:80])
            entries[path] = {'vi': vi, 'en': en}
    if missing:
        sample = '; '.join(f'{p}: {v[:50]}' for v, p in list(missing.items())[:5])
        report.error('tiếng Anh', f'Thiếu bản dịch cho {len(missing)} đoạn (ví dụ {sample}). Tạo file mẫu bằng --translation-template.')
    unused = sorted(set(translations) - used)
    if unused:
        report.warn('tiếng Anh', f'{len(unused)} bản dịch không còn dùng (nội dung tiếng Việt đã đổi?).')
    return entries, missing


def english_by_exercise(exercises, entries):
    """{id: {field path: English}}: the Vietnamese stays in the exercise, so it is not stored twice."""
    out = {}
    for ex in exercises:
        prefix = f'exercises#{ex["id"]}.'
        out[ex['id']] = {path[len(prefix):]: entry['en'] for path, entry in entries.items() if path.startswith(prefix)}
    return out


def assign_versions(exercises, previous, report):
    old = {ex['id']: ex for ex in (previous or {}).get('exercises', [])}
    for ex in exercises:
        before = old.get(ex['id'])
        if before:
            ex['version'] = before['version'] if chess_fingerprint(before) == chess_fingerprint(ex) else before['version'] + 1
            if ex['version'] != before['version']:
                report.warn(f'"{ex["id"]}"', f'Cây nước đi đổi so với bản đang có; tăng version lên {ex["version"]} (nháp cũ của bài này sẽ không khôi phục).')


def render_pack(pack):
    """One exercise and one translation per line: compact, and a change shows up as a readable diff."""
    def compact(value):
        return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    body = ('{\n"format":' + compact(pack['format']) + ',\n"source":' + compact(pack['source'])
            + ',\n"exercises":[\n' + ',\n'.join(compact(ex) for ex in pack['exercises'])
            + '\n],\n"en":{\n' + ',\n'.join(compact(pid) + ':' + compact(en) for pid, en in pack['en'].items()) + '\n}\n}')
    return ('/* GENERATED by tools/import_curriculum_xlsx.py. Do not edit by hand: change the workbook or\n'
            ' * tools/curriculum_pack_en.json, then run the script again (see docs/POSITION_IMPORT.md).\n'
            ' * Exercises authored and reviewed by the project owner; the app checks rules, checkmate and material.\n'
            ' * en: English by exercise id and field path (draft translation for owner review); web/content-en.js\n'
            " * turns it into exercises#<id>.<path> entries. Browser: CCCurriculumPack. Node: require('./curriculum-pack.js'). */\n"
            "(function (root, factory) {\n  'use strict';\n  const api = factory();\n"
            "  if (typeof module !== 'undefined' && module.exports) module.exports = api;\n  root.CCCurriculumPack = api;\n"
            "})(typeof globalThis !== 'undefined' ? globalThis : this, function () {\n  'use strict';\n"
            f'  return {START}{body}{END};\n}});\n')


def translation_template(exercises, translations):
    needed = {}
    for ex in exercises:
        for vi in strings('', {k: v for k, v in ex.items() if k not in ('title', 'goal', 'difficultyLabel', 'verification')}, {}).values():
            needed.setdefault(vi, translations.get(vi, ''))
    return {'format': EN_FORMAT, 'note': 'Vietnamese source text -> English. Glossary: docs/I18N_GLOSSARY.md.', 'entries': needed}


def run(xlsx=DEFAULT_XLSX, out=DEFAULT_OUT, write=False, translations_path=DEFAULT_EN, node=None, bank=None, template=None):
    """Returns (report, pack or None, status) where status is 'written', 'unchanged', 'dry-run' or 'errors'."""
    report = positions.Report()
    book = read_workbook(xlsx)
    translations = load_translations(translations_path)
    exercises, generated = build(book, report, bank=bank)
    check_notation(exercises, book, node, report)
    if template:
        Path(template).write_bytes((json.dumps(translation_template(exercises, translations), ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    entries, _ = english_entries(exercises, generated, translations, report)
    if report.errors:
        return report, None, 'errors'
    assign_versions(exercises, read_pack(out), report)
    digest = hashlib.sha256(Path(xlsx).read_bytes()).hexdigest()
    pack = {'format': PACK_FORMAT, 'source': {'file': Path(xlsx).name, 'sha256': digest, 'sheets': list(SHEETS)},
            'exercises': exercises, 'en': english_by_exercise(exercises, entries)}
    text = render_pack(pack)
    out = Path(out)
    current = out.read_bytes() if out.is_file() else None
    if current == text.encode('utf-8'):
        return report, pack, 'unchanged'
    if not write:
        return report, pack, 'dry-run'
    if out.resolve() == Path(xlsx).resolve():
        raise SystemExit('Không ghi đè file Excel.')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(text.encode('utf-8'))
    return report, pack, 'written'


def summary(pack):
    rows = {}
    for ex in pack['exercises']:
        row = rows.setdefault(ex['chapterId'], {'mate': 0, 'material': 0, 'intermediate': 0, 'advanced': 0, 'b': 0})
        row[ex['objective']] += 1
        row[ex['difficulty']] += 1
        row['b'] += ex['learner'] == 'b'
    lines = [f'  {cid:<20} {sum(r[o] for o in ("mate", "material")):>3} bài · chiếu hết {r["mate"]} · ăn quân {r["material"]}'
             f' · trung cấp {r["intermediate"]} · khó {r["advanced"]} · Đen đi trước {r["b"]}' for cid, r in rows.items()]
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file', nargs='?', default=str(DEFAULT_XLSX), help='File .xlsx (mặc định var/import/CoChill_70_bai_final.xlsx)')
    parser.add_argument('--write', action='store_true', help='Ghi web/curriculum-pack.js khi không có lỗi')
    parser.add_argument('--out', default=str(DEFAULT_OUT), help=argparse.SUPPRESS)
    parser.add_argument('--translations', default=str(DEFAULT_EN), help='File bản dịch tiếng Anh (mặc định tools/curriculum_pack_en.json)')
    parser.add_argument('--translation-template', metavar='OUT.json', help='Ghi danh sách đoạn cần dịch (đã điền bản dịch hiện có)')
    parser.add_argument('--node', default=shutil.which('node'), help='Node.js để đối chiếu ký pháp Việt')
    parser.add_argument('--quiet', action='store_true', help='Không in từng lưu ý')
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')  # Windows consoles default to cp1252
    if args.translation_template and Path(args.translation_template).resolve().is_relative_to((ROOT / 'web').resolve()):
        parser.error('Không ghi file mẫu bản dịch vào web/.')
    try:
        report, pack, status = run(args.file, args.out, args.write, args.translations, args.node, template=args.translation_template)
    except (WorkbookError, OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f'Không đọc được file: {error}', file=sys.stderr)
        return 2
    errors = report.errors
    for item in report.items:
        if item['level'] == 'error' or not args.quiet:
            print(('LỖI   ' if item['level'] == 'error' else 'LƯU Ý ') + item['where'] + ': ' + item['message'])
    if pack:
        print(f'\n{len(pack["exercises"])} bài, {len(pack["en"])} mục tiếng Anh:\n' + summary(pack))
    print(f'\n{len(errors)} lỗi, {len(report.items) - len(errors)} lưu ý. ' + {
        'errors': 'Có lỗi nên chưa ghi file.',
        'unchanged': f'{args.out} đã khớp với file Excel; không cần ghi lại.',
        'dry-run': 'Chạy thử: chưa ghi file. Thêm --write để ghi.',
        'written': f'Đã ghi {args.out}. Chạy python tools/stamp_static_versions.py rồi python tools/run_checks.py.',
    }[status])
    if args.translation_template:
        print(f'Đã ghi danh sách cần dịch vào {args.translation_template}.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
