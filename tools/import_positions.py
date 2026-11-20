"""Check a positions file and draft line-v1 exercises from it (rules only).

Format: docs/POSITION_IMPORT.md ("cochill-positions-v1", UTF-8 JSON).

    python tools/import_positions.py FILE                 # dry-run: report only
    python tools/import_positions.py FILE --write OUTDIR  # also write drafts

The tool never edits web/. It checks FEN, side to move, every move of every
line with app/rules.py, duplicates (exact, mirrored, colour-swapped) against the
file and the current bank, and required fields. It does NOT judge move quality:
every draft is marked as needing engine/human review. Vietnamese notation is
read through tools/notation_bridge.cjs (Node, same code as the app); board
coordinates such as h2e2 work without Node.
Exit code: 0 = no errors, 1 = errors found, 2 = cannot read the file.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.puzzles import PUZZLES  # noqa: E402
from app.rules import Position  # noqa: E402

FORMAT = 'cochill-positions-v1'
ID = re.compile(r'^[a-z0-9][a-z0-9-]{2,63}$')
COORD = re.compile(r'^[a-i][0-9][a-i][0-9]$')
DIFFICULTY = {
    'intermediate': ('Trung cấp · mức dự kiến', 'Intermediate · estimated difficulty', (3, 4)),
    'advanced': ('Nâng cao · mức dự kiến', 'Advanced · estimated difficulty', (6, 7)),
}
OBJECTIVES = ('mate', 'advantage')
RIGHTS = ('own-work', 'permission', 'licensed')
KNOWN_SKILLS = ('material', 'cannon', 'horse', 'safety')
PIECE_TAGS = {'r': 'rook', 'c': 'cannon', 'h': 'horse', 'p': 'pawn', 'a': 'advisor', 'e': 'elephant', 'k': 'king'}
MAX_PLIES = 40          # line-v1 allows depth 20 learner nodes
MAX_NODES = 256
REVIEW_ENGINE = 'Cần engine/người duyệt: nước được chấp nhận có phải nước tốt nhất và nước đáp có phải phản ứng mạnh nhất.'
REVIEW_OTHERS = 'Các nước hợp lệ ngoài cây sẽ ở trạng thái chờ kiểm chứng (chưa đánh dấu sai).'
REVIEW_DRAFT = 'line-v1 hiện chỉ nhận điểm kết thúc là chiếu hết; mục tiêu "advantage" cần mở rộng định dạng trước khi đưa vào ứng dụng.'


def board_key(fen):
    pos = Position.from_fen(fen)
    return pos.fen()


def mirrored(key):
    board, turn = key.split()
    return '/'.join(rank[::-1] for rank in board.split('/')) + ' ' + turn


def colour_swapped(key):
    board, turn = key.split()
    ranks = [rank[::-1].swapcase() for rank in reversed(board.split('/'))]
    return '/'.join(ranks) + ' ' + ('b' if turn == 'w' else 'w')


def existing_bank(include_pack=True):
    """Ids and positions already in the app: basic puzzles + curriculum exercises.

    include_pack adds the exercises generated from the owner's workbook
    (web/curriculum-pack.js); tools/import_curriculum_xlsx.py leaves them out
    because it regenerates that file.
    """
    ids, fens = set(), {}
    for puzzle in PUZZLES:
        ids.add(puzzle['id'])
        fens[board_key(puzzle['fen'])] = 'bài cơ bản ' + puzzle['id']
    text = (ROOT / 'web' / 'curriculum.js').read_text(encoding='utf-8')
    start = text.find('const exercises=')
    for block in re.split(r'\n  \{\n', text[start:])[1:]:
        found = re.search(r'"id": "([^"]+)"', block)
        if not found:
            continue
        ids.add(found.group(1))
        for fen in re.findall(r'"fen": "([^"]+)"', block):
            fens.setdefault(board_key(fen), 'bài nhiều lượt ' + found.group(1))
    chapters = dict(re.findall(r"\{id:'([^']+)',courseId:'([^']+)'", text))
    pack = ROOT / 'web' / 'curriculum-pack.js'
    if include_pack and pack.is_file():
        body = pack.read_text(encoding='utf-8')
        if '/*PACK-JSON-START*/' in body:
            data = json.loads(body.split('/*PACK-JSON-START*/', 1)[1].split('/*PACK-JSON-END*/', 1)[0])
            for exercise in data.get('exercises', []):
                ids.add(exercise['id'])
                fens.setdefault(board_key(exercise['fen']), 'bài nhiều lượt ' + exercise['id'])
    return ids, fens, chapters


def text_pair(value):
    """Accept "text" (Vietnamese only) or {"vi": ..., "en": ...}."""
    if isinstance(value, str):
        return {'vi': value.strip(), 'en': ''}
    if isinstance(value, dict):
        return {'vi': str(value.get('vi') or '').strip(), 'en': str(value.get('en') or '').strip()}
    return {'vi': '', 'en': ''}


def tokens(line):
    if isinstance(line, str):
        return [t for t in re.split(r'[\s,;]+', line.strip()) if t]
    if isinstance(line, list) and all(isinstance(t, str) for t in line):
        return [t.strip() for t in line if t.strip()]
    return None


def source_lines(raw):
    """Map position id -> line number in the file, for readable errors."""
    where = {}
    for number, row in enumerate(raw.splitlines(), 1):
        found = re.search(r'"id"\s*:\s*"([^"]+)"', row)
        if found:
            where.setdefault(found.group(1), number)
    return where


def resolve_notation(requests, node):
    """Convert every line to board moves; without Node only coordinates work."""
    if not node:
        if all(COORD.match(t) for r in requests for t in r['tokens']):
            return [{'moves': list(r['tokens']), 'notations': None} for r in requests]
        return [{'error': 'Cần Node.js để đọc ký pháp (ví dụ P2-5); hoặc ghi nước bằng tọa độ máy.', 'ply': 0}] * len(requests)
    result = subprocess.run([node, str(ROOT / 'tools' / 'notation_bridge.cjs')], input=json.dumps({'lines': requests}),
                            capture_output=True, text=True, encoding='utf-8', cwd=ROOT, timeout=120)
    if result.returncode:
        raise RuntimeError('notation_bridge.cjs lỗi: ' + result.stderr.strip()[-500:])
    return json.loads(result.stdout)['lines']


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, where, message):
        self.items.append({'level': level, 'where': where, 'message': message})

    def error(self, where, message):
        self.add('error', where, message)

    def warn(self, where, message):
        self.add('warning', where, message)

    @property
    def errors(self):
        return [i for i in self.items if i['level'] == 'error']


def build_tree(fen, lines, objective, where, report):
    """Merge lines (each from the start, learner first) into line-v1 nodes."""
    root = Position.from_fen(fen)
    learner = root.turn
    nodes = {'n0': {'id': 'n0', 'fen': root.fen(), 'choices': []}}
    ok = True
    for li, moves in enumerate(lines):
        label = f'{where} › lines[{li}]' + (' (đường chính)' if li == 0 else '')
        if len(moves) % 2 == 0:
            report.error(label, 'Mỗi đường phải kết thúc bằng nước của bên người học (số nửa nước lẻ).')
            ok = False
            continue
        if len(moves) > MAX_PLIES - 1:
            report.error(label, f'Đường quá dài ({len(moves)} nửa nước); line-v1 tối đa {MAX_PLIES - 1}.')
            ok = False
            continue
        pos, node_id = root, 'n0'
        for ply in range(0, len(moves), 2):
            move = moves[ply]
            if move not in pos.legal_moves():
                report.error(label, f'Nửa nước {ply + 1}: không hợp lệ theo app/rules.py.')
                ok = False
                break
            after = pos.play(move)
            node = nodes[node_id]
            edge = next((e for e in node['choices'] if e['move'] == move), None)
            last = ply == len(moves) - 1
            if last:
                status = after.status()
                if objective == 'mate' and not (status['over'] and status['winner'] == learner and after.in_check()):
                    report.error(label, f'Nửa nước {ply + 1}: mục tiêu "mate" nhưng nước cuối chưa chiếu hết.')
                    ok = False
                    break
                if objective == 'advantage' and status['over']:
                    report.warn(label, 'Nước cuối đã kết thúc ván; nên ghi objective là "mate".')
                if edge is None:
                    node['choices'].append({'move': move, 'reply': None, 'next': None})
                elif edge['next'] is not None:
                    report.error(label, f'Nửa nước {ply + 1}: đường này dừng ở chỗ đường khác còn đi tiếp.')
                    ok = False
                break
            reply = moves[ply + 1]
            if after.status()['over']:
                report.error(label, f'Nửa nước {ply + 1}: ván đã kết thúc nhưng đường còn tiếp.')
                ok = False
                break
            if reply not in after.legal_moves():
                report.error(label, f'Nửa nước {ply + 2}: nước đáp không hợp lệ theo app/rules.py.')
                ok = False
                break
            following = after.play(reply)
            if following.status()['over']:
                report.error(label, f'Nửa nước {ply + 2}: nước đáp kết thúc ván; bài phải kết thúc bằng nước người học.')
                ok = False
                break
            if edge is None:
                next_id = f'n{len(nodes)}'
                if len(nodes) >= MAX_NODES:
                    report.error(label, f'Quá {MAX_NODES} vị trí.')
                    return None
                nodes[next_id] = {'id': next_id, 'fen': following.fen(), 'choices': []}
                edge = {'move': move, 'reply': reply, 'next': next_id}
                node['choices'].append(edge)
            elif edge['next'] is None:
                report.error(label, f'Nửa nước {ply + 1}: đường khác đã kết thúc ở nước này, đường này lại đi tiếp.')
                ok = False
                break
            elif edge['reply'] != reply:
                report.error(label, f'Nửa nước {ply + 2}: line-v1 chỉ có một nước đáp cho mỗi nước đúng; đường chính và đường này đáp khác nhau.')
                ok = False
                break
            pos, node_id = following, edge['next']
    if not ok:
        return None

    def depth(node_id):
        return max(1 + (depth(e['next']) if e['next'] else 0) for e in nodes[node_id]['choices'])

    for node_id, node in nodes.items():
        node['remaining'] = depth(node_id)
        node['rejectedMoves'] = []
        nodes[node_id] = {k: node[k] for k in ('id', 'fen', 'remaining', 'choices', 'rejectedMoves')}
    return nodes


def piece_tags(fen, line):
    pos, tags = Position.from_fen(fen), []
    for i, move in enumerate(line):
        if i % 2 == 0:
            piece = pos.board[(9 - int(move[1])) * 9 + ord(move[0]) - 97].lower()
            if PIECE_TAGS[piece] not in tags:
                tags.append(PIECE_TAGS[piece])
        pos = pos.play(move)
    return tags


def check_position(entry, index, line_no, bank, seen, report, node):
    where = f'positions[{index}]'
    if not isinstance(entry, dict):
        report.error(where, 'Mỗi thế phải là một object JSON.')
        return None
    pid = entry.get('id')
    if isinstance(pid, str):
        where += f' "{pid}"' + (f' (dòng {line_no[pid]})' if pid in line_no else '')
    ids, fens, chapters = bank
    start_errors = len(report.errors)
    if not isinstance(pid, str) or not ID.match(pid):
        report.error(where, 'id cần 3–64 ký tự a-z, 0-9, gạch nối; bắt đầu bằng chữ hoặc số.')
    elif pid in ids:
        report.error(where, 'id đã có trong kho hiện tại.')
    elif pid in seen['ids']:
        report.error(where, 'id trùng với một thế khác trong file.')
    else:
        seen['ids'].add(pid)

    key = None
    try:
        key = board_key(entry.get('fen'))
    except (ValueError, AttributeError) as error:
        report.error(where, f'FEN không hợp lệ: {error}')
    if key:
        side = entry.get('sideToMove')
        if side not in ('w', 'b'):
            report.error(where, 'sideToMove phải là "w" (Đỏ) hoặc "b" (Đen).')
        elif side != key.split()[1]:
            report.error(where, 'sideToMove không khớp lượt đi trong FEN.')
        if Position.from_fen(key).status()['over']:
            report.error(where, 'Thế bắt đầu đã kết thúc ván.')
        if key in fens:
            report.error(where, f'Trùng thế với {fens[key]}.')
        elif key in seen['fens']:
            report.error(where, f'Trùng thế với {seen["fens"][key]} trong file.')
        else:
            for variant, name in ((mirrored(key), 'đối xứng trái–phải'), (colour_swapped(key), 'đổi màu/lật bàn')):
                other = fens.get(variant) or seen['fens'].get(variant)
                if other and variant != key:
                    report.warn(where, f'Gần trùng ({name}) với {other}.')
        seen['fens'].setdefault(key, f'"{pid}"')

    if entry.get('phase', 'middle') not in ('opening', 'middle', 'end'):
        report.error(where, 'phase phải là opening, middle hoặc end.')
    if not isinstance(entry.get('chapterId'), str) or entry['chapterId'] not in chapters:
        report.error(where, 'chapterId phải là một chương có sẵn: ' + ', '.join(chapters) + '.')
    skill = entry.get('skill')
    if not isinstance(skill, str) or not re.match(r'^[a-zA-Z][a-zA-Z0-9-]{1,40}$', skill):
        report.error(where, 'Thiếu skill (một từ, ví dụ cannon).')
    elif skill not in KNOWN_SKILLS:
        report.warn(where, f'skill "{skill}" chưa có bài cơ bản cùng kỹ năng ({", ".join(KNOWN_SKILLS)}).')
    difficulty = entry.get('difficulty')
    if not isinstance(difficulty, str) or difficulty not in DIFFICULTY:
        report.error(where, 'difficulty phải là intermediate hoặc advanced.')
    objective = entry.get('objective')
    if objective not in OBJECTIVES:
        report.error(where, 'objective phải là "mate" (chiếu hết) hoặc "advantage" (lợi thế, cần duyệt).')
    rights = entry.get('rights')
    source = entry.get('source') if isinstance(entry.get('source'), dict) else {}
    if rights not in RIGHTS:
        report.error(where, 'rights phải là own-work, permission hoặc licensed; nguồn chưa rõ quyền thì không nhập.')
    elif rights != 'own-work' and not str(entry.get('rightsNote') or '').strip():
        report.error(where, 'rights là permission/licensed thì cần rightsNote (ai cho phép, giấy phép nào).')
    if not str(source.get('name') or '').strip():
        report.error(where, 'Thiếu source.name (ai soạn hoặc lấy từ đâu).')

    title, goal = text_pair(entry.get('title')), text_pair(entry.get('goal'))
    for field, pair in (('title', title), ('goal', goal)):
        if not pair['vi']:
            report.error(where, f'Thiếu {field} tiếng Việt.')
    explanation = entry.get('explanation') if isinstance(entry.get('explanation'), dict) else {}
    texts = {k: text_pair(explanation.get(k)) for k in ('what', 'why', 'how')}
    if not any(t['vi'] for t in texts.values()):
        report.warn(where, 'Chưa có lời giải thích (explanation.what/why/how).')

    raw_lines = entry.get('lines')
    parsed = [tokens(line) for line in raw_lines] if isinstance(raw_lines, list) and raw_lines else None
    if not parsed or any(not p for p in parsed):
        report.error(where, 'lines cần ít nhất một đường (đường chính đứng đầu), mỗi đường là danh sách nước.')
    if len(report.errors) > start_errors or not key or not parsed:
        return None

    converted = resolve_notation([{'fen': key, 'tokens': p} for p in parsed], node)
    moves = []
    for li, result in enumerate(converted):
        if 'error' in result:
            token = f' "{result["token"]}"' if result.get('token') else ''
            report.error(f'{where} › lines[{li}]', f'Nửa nước {result["ply"]}{token}: {result["error"]}')
        else:
            moves.append(result)
    if len(moves) != len(parsed):
        return None
    nodes = build_tree(key, [m['moves'] for m in moves], objective, where, report)
    if nodes is None:
        return None

    decisions = nodes['n0']['remaining']
    low, high = DIFFICULTY[difficulty][2]
    if not low <= decisions <= high:
        report.warn(where, f'{decisions} quyết định; mục tiêu {difficulty} là {low}–{high}.')
    label_vi, label_en, _ = DIFFICULTY[difficulty]
    main = moves[0]['moves']
    review = [REVIEW_ENGINE, REVIEW_OTHERS] + ([REVIEW_DRAFT] if objective != 'mate' else [])
    verification = {
        'vi': 'Nhập từ file thế cờ. Bộ luật đã kiểm tra FEN và từng nước của các đường đã ghi; chưa kiểm tra mọi phản ứng của đối thủ, chưa có bằng chứng Pikafish hay chuyên gia duyệt.',
        'en': 'Imported from a positions file. The rules engine has checked the FEN and every move of the recorded lines; not every opponent reply has been checked, and there is no Pikafish or expert review yet.',
    }
    exercise = {
        'id': pid, 'version': 1, 'format': 'line-v1' if objective == 'mate' else 'line-v1-draft',
        'title': title['vi'], 'phase': entry.get('phase', 'middle'), 'chapterId': entry['chapterId'], 'skill': skill,
        'pieceTags': piece_tags(key, main), 'familyId': entry.get('familyId') or pid,
        'difficulty': difficulty, 'difficultyLabel': label_vi, 'goal': goal['vi'],
        'learner': key.split()[1], 'fen': key, 'root': 'n0', 'nodes': nodes,
        'exampleLine': main, 'decisions': decisions, 'source': str(source['name']).strip(),
        'proof': {'method': 'author-lines', 'objective': objective, 'engine': 'app/rules.py legal rules',
                  'expertReviewed': False, 'pikafishVerified': False, 'lines': len(moves)},
        'verification': verification['vi'],
        **{k: t['vi'] for k, t in texts.items() if t['vi']},
        'importReview': {'rights': rights, 'rightsNote': str(entry.get('rightsNote') or '').strip(), 'pending': review},
    }
    english = {'title': title, 'difficultyLabel': {'vi': label_vi, 'en': label_en}, 'goal': goal,
               'source': text_pair({'vi': source.get('name'), 'en': source.get('nameEn')}),
               'verification': verification, **{k: t for k, t in texts.items() if t['vi']}}
    content = {f'exercises#{pid}.{field}': pair for field, pair in english.items()}
    missing = sorted(field for field, pair in english.items() if not pair['en'])
    if missing:
        report.warn(where, 'Thiếu bản tiếng Anh: ' + ', '.join(missing) + ' (bắt buộc trước khi đưa vào web/).')
    notes = [m['notations'] for m in moves]
    return {'exercise': exercise, 'contentEn': content, 'notation': notes, 'review': review}


def run(path, write=None, node=None):
    raw = Path(path).read_text(encoding='utf-8-sig')
    data = json.loads(raw)
    report = Report()
    if not isinstance(data, dict) or data.get('format') != FORMAT:
        report.error('file', f'Thiếu "format": "{FORMAT}".')
        return report, []
    positions = data.get('positions')
    if not isinstance(positions, list) or not positions:
        report.error('file', 'Thiếu danh sách "positions".')
        return report, []
    bank, seen, line_no = existing_bank(), {'ids': set(), 'fens': {}}, source_lines(raw)
    drafts = [check_position(entry, i, line_no, bank, seen, report, node) for i, entry in enumerate(positions)]
    drafts = [d for d in drafts if d]
    if write and not report.errors:
        out = Path(write)
        if out.resolve().is_relative_to((ROOT / 'web').resolve()):
            raise SystemExit('Không ghi vào web/; đưa bài vào ứng dụng là bước duyệt riêng.')
        out.mkdir(parents=True, exist_ok=True)
        dump = lambda name, value: (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        dump('exercises.json', [d['exercise'] for d in drafts])
        dump('content-en.json', {k: v for d in drafts for k, v in d['contentEn'].items()})
        dump('report.json', {'positions': len(positions), 'drafts': len(drafts), 'items': report.items})
    return report, drafts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('file', help='File JSON định dạng cochill-positions-v1')
    parser.add_argument('--write', metavar='OUTDIR', help='Ghi exercises.json, content-en.json, report.json khi không có lỗi')
    parser.add_argument('--node', default=shutil.which('node'), help='Node.js để đọc ký pháp Việt')
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')  # Windows consoles default to cp1252
    try:
        report, drafts = run(args.file, args.write, args.node)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f'Không đọc được file: {error}', file=sys.stderr)
        return 2
    for item in report.items:
        print(('LỖI   ' if item['level'] == 'error' else 'LƯU Ý ') + item['where'] + ': ' + item['message'])
    for draft in drafts:
        ex = draft['exercise']
        main_line = draft['notation'][0] or ex['exampleLine']
        print(f'OK    "{ex["id"]}": {ex["format"]}, {ex["decisions"]} quyết định, {len(ex["nodes"])} vị trí; đường chính: {" ".join(main_line)}')
    errors = len(report.errors)
    print(f'\n{len(drafts)} bản nháp, {errors} lỗi, {len(report.items) - errors} lưu ý. '
          + ('Đã ghi vào ' + args.write if args.write and not errors else 'Chạy thử: chưa ghi file nào.' if not args.write else 'Có lỗi nên chưa ghi file.'))
    print('Mọi bản nháp vẫn cần engine/người duyệt nước tốt nhất trước khi đưa vào web/.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
