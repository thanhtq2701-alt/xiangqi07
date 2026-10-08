"""Read-only parent-folder inventory; write only generated reports inside repo."""
import ast
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT.parent
OUTPUTS = {'PROJECT_INVENTORY_VI.md', 'inventory/manifest.json',
           'deliverables/Co_Chill_So_tay_hien_trang.html'}


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args],
                                   cwd=ROOT).decode('utf-8').strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()


def role(path):
    name = path.name
    rel = path.relative_to(SCOPE).as_posix()
    if name.startswith('~$'): return 'File khóa Word; không phải nội dung tài liệu'
    if '__pycache__' in path.parts: return 'Cache Python tái tạo được'
    if name == 'Answer V3.docx': return 'Ý định sản phẩm và câu trả lời chủ dự án V3'
    if name == 'Codex.docx': return 'Hướng dẫn thực thi đầu vào'
    if name == 'V3.docx': return 'Bộ câu hỏi khám phá V3 cũ'
    if name == 'Co_Chill_V4_Bo_sung_UI_UX_Kien_truc_Luat.docx': return '272 câu bổ sung V4 về từng trang UI UX kiến trúc API và luật; chờ trả lời'
    if 'V4_' in name: return 'Bộ câu hỏi bổ sung V4; không tự coi là câu trả lời đã chốt'
    if rel.startswith('Failing/'): return 'Ảnh lỗi nhập tiện ích trình duyệt; đã xem ngày 08/10/2026'
    if '/var/' in rel: return 'Dữ liệu local; không đưa nội dung riêng tư vào báo cáo'
    if '/docs/materials/' in rel: return 'Bản trích xuất/giải nén đầu vào, ngoài Git'
    if '/docs/spec/' in rel or '/XiangqiAI_V3_Final_Pack/' in rel: return 'Đặc tả V3; nội dung yêu cầu không phải trạng thái triển khai'
    if name.endswith('.zip'): return 'Gói đặc tả gốc; xem danh mục thành viên bên dưới'
    if '/artifacts/' in rel: return 'Ảnh/bằng chứng kiểm tra cục bộ'
    if '/tests/' in rel: return 'Kiểm thử tự động' if name != '__init__.py' else 'Đánh dấu package tests'
    if '/app/' in rel: return 'Logic backend; xem vai trò chi tiết trong sổ tay'
    if '/web/' in rel: return 'Giao diện trình duyệt'
    if '/tools/' in rel: return 'Công cụ tạo tài liệu/kiểm kê'
    if name == 'server.py': return 'Điểm khởi động HTTP server local'
    if name == 'sources.csv': return 'Sổ nguồn dữ liệu và quyền sử dụng'
    return 'Tài liệu/quy tắc dự án' if path.suffix == '.md' else 'File cấu hình hoặc tài nguyên; xem đường dẫn'


def render_markdown(text):
    """Small escaped renderer for the headings, tables and paragraphs we emit."""
    out, table = [], False
    def inline(s):
        return re.sub(r'`([^`]+)`', r'<code>\1</code>', html.escape(s))
    for line in text.splitlines():
        if line.startswith('|'):
            if re.fullmatch(r'[| :\-]+', line): continue
            if not table: out.append('<table>'); table = True
            out.append('<tr>' + ''.join('<td>'+inline(c.strip())+'</td>' for c in line.strip('|').split('|'))+'</tr>')
            continue
        if table: out.append('</table>'); table = False
        if not line: continue
        match = re.match(r'^(#{1,6}) (.*)', line)
        if match:
            n = len(match[1]); out.append(f'<h{n}>{inline(match[2])}</h{n}>')
        else: out.append('<p>'+inline(line)+'</p>')
    if table: out.append('</table>')
    return '\n'.join(out)


def main():
    stamp = datetime.now().astimezone().isoformat(timespec='seconds')
    tracked = set(git('ls-files').splitlines())
    old_path = ROOT / 'inventory/manifest.json'
    old = json.loads(old_path.read_text(encoding='utf-8')) if old_path.exists() else None
    records, archives, words, symbols, errors, git_meta = [], [], [], {}, [], Counter()
    for base, dirs, files in os.walk(SCOPE, followlinks=False):
        dirs.sort()
        for name in sorted(files):
            path = Path(base) / name
            rel = path.relative_to(SCOPE).as_posix()
            if '.git' in path.relative_to(SCOPE).parts:
                git_meta['files'] += 1
                git_meta['bytes'] += path.stat().st_size
                continue
            repo_rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else None
            state = 'Ngoài repo'
            if repo_rel:
                state = 'Tracked' if repo_rel in tracked else ('Ignored' if subprocess.run(['git', 'check-ignore', '-q', '--', repo_rel], cwd=ROOT).returncode == 0 else 'Chưa tracked')
            sensitive = name.startswith('.env') or path.suffix.lower() in {'.pem', '.key', '.sqlite3', '.db'} or '/var/' in rel
            generated = repo_rel in OUTPUTS
            try:
                stat = path.stat()
                checksum = None if sensitive or generated or name.startswith('~$') else digest(path)
                record = dict(path=rel, bytes=None if generated else stat.st_size,
                              modified=None if generated else datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds'),
                              sha256=checksum, git=state, role=role(path), generated=generated)
                records.append(record)
                if path.suffix == '.zip' and not sensitive:
                    with zipfile.ZipFile(path) as z:
                        for member in z.infolist():
                            if not member.is_dir():
                                archives.append(dict(archive=rel, member=member.filename, bytes=member.file_size,
                                                     sha256=hashlib.sha256(z.read(member)).hexdigest()))
                if path.suffix == '.docx' and not name.startswith('~$'):
                    with zipfile.ZipFile(path) as z:
                        root = ET.fromstring(z.read('word/document.xml'))
                        ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        paragraphs = [''.join(p.itertext()) for p in root.findall('.//w:p', ns)]
                        words.append(dict(path=rel, paragraphs=len(paragraphs), characters=sum(map(len, paragraphs))))
                if repo_rel and path.suffix == '.py' and '__pycache__' not in path.parts:
                    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
                    symbols[repo_rel] = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
            except Exception as exc:
                errors.append(rel + ': ' + type(exc).__name__)
    db_counts = {}
    dbpath = ROOT / 'var/chill.sqlite3'
    if dbpath.exists():
        try:
            con = sqlite3.connect(dbpath.as_uri() + '?mode=ro', uri=True)
            try: db_counts = dict(con.execute('SELECT kind, COUNT(*) FROM records GROUP BY kind'))
            finally: con.close()
        except sqlite3.Error as exc: errors.append('Database: ' + type(exc).__name__)
    records.sort(key=lambda r:r['path'])
    previous = {r['path']:r for r in old['files']} if old else {}
    current = {r['path']:r for r in records}
    changes = dict(added=sorted(current.keys()-previous.keys()), removed=sorted(previous.keys()-current.keys()),
                   changed=[p for p in sorted(current.keys() & previous.keys()) if not current[p]['generated'] and
                            (current[p]['sha256'],current[p]['bytes'],current[p]['modified']) !=
                            (previous[p]['sha256'],previous[p]['bytes'],previous[p]['modified'])])
    duplicates = defaultdict(list)
    for r in records:
        if r['sha256'] and r['bytes']: duplicates[r['sha256']].append(r['path'])
    snap = dict(time=stamp, scope=str(SCOPE), head=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'),
                files=records, archives=archives, word_documents=words, python_symbols=symbols,
                database_counts=db_counts, git_metadata=dict(git_meta), changes=changes, errors=errors)
    lines = ['# Danh mục toàn bộ thư mục App cờ tướng', '', f'Lần quét: {stamp}.',
             f'Phạm vi: `{SCOPE}`; gồm mọi file thường/ẩn ngoài .git, kể cả cache và file bị Git bỏ qua. Không đi theo thư mục symlink.',
             f'Commit nền: `{snap["head"]}`; nhánh `{snap["branch"]}`. Metadata Git nội bộ: {git_meta["files"]} file, {git_meta["bytes"]} byte, chỉ thống kê tổng; không chép nội dung cấu hình/log/object.',
             'Các báo cáo tự sinh được liệt kê nhưng không hash/kích thước chính chúng để tránh tự tham chiếu. Không chép nội dung database, cookie hoặc secrets. Đây là metadata kiểm kê, không tự xác minh chức năng.',
             f'Tổng file ngoài .git: **{len(records)}**. Trạng thái: ' + ', '.join(f'{k}: {v}' for k,v in Counter(r['git'] for r in records).items()) + '.',
             '## Các thư mục cấp đầu', '| Nhóm | Số file |', '| --- | --- |']
    lines += [f'| {k} | {v} |' for k,v in sorted(Counter(r['path'].split('/')[0] for r in records).items())]
    lines += ['## Lịch sử Git hiện có', git('log', '--format=%h — %ad — %s', '--date=iso-strict'),
              'Remote: ' + ('Có cấu hình tên: ' + git('remote') if git('remote') else 'Chưa có remote; chưa có bằng chứng backup lên GitHub.'),
              '## Thay đổi so với lần kiểm kê trước', 'Lần đầu tạo baseline.' if not old else f'Baseline trước: {old["time"]}.']
    if old:
        for label,key in [('Thêm','added'),('Xóa/di chuyển khỏi đường dẫn','removed'),('Nội dung/metadata thay đổi','changed')]:
            lines.append(label + ': ' + ('; '.join(changes[key]) or 'Không có'))
    lines += ['## Danh sách từng file', 'Đường dẫn tương đối với App cờ tướng. Hash đầy đủ và thời gian sửa nằm trong inventory/manifest.json.',
              '| File | Byte | Git lúc quét | Vai trò |', '| --- | --- | --- | --- |']
    lines += [f'| {r["path"]} | {r["bytes"] if r["bytes"] is not None else "Tự sinh"} | {r["git"]} | {r["role"]} |' for r in records]
    lines += ['## Các bản trùng nguyên byte (SHA-256)', 'Bản trùng không tự đồng bộ. Không xóa tự động.']
    lines += ['- ' + ' = '.join(paths) for paths in duplicates.values() if len(paths)>1]
    lines += ['## Nội dung từng ZIP', '| Archive | Thành viên | Byte giải nén |', '| --- | --- | --- |']
    lines += [f'| {r["archive"]} | {r["member"]} | {r["bytes"]} |' for r in archives]
    lines += ['## Word đã kiểm tra cấu trúc', 'Đọc toàn bộ document.xml để thống kê đoạn và ký tự; không xác nhận bố cục trang hoặc tài liệu đã được trả lời.',
              '| File | Đoạn XML | Ký tự văn bản |', '| --- | --- | --- |']
    lines += [f'| {r["path"]} | {r["paragraphs"]} | {r["characters"]} |' for r in words]
    lines += ['## Thành phần Python cấp module', '| File | Hàm/lớp |', '| --- | --- |']
    lines += [f'| {p} | {", ".join(names) or "Không có định nghĩa cấp module"} |' for p,names in sorted(symbols.items())]
    lines += ['## Database tại lúc quét', 'Chỉ đếm bản ghi, không đếm người dùng và không đánh giá hiệu quả học tập.',
              '| Loại bản ghi | Số lượng |', '| --- | --- |']
    lines += [f'| {k} | {v} |' for k,v in db_counts.items()]
    lines += ['## Phạm vi chưa xác minh / lỗi đọc', '\n'.join(errors) if errors else 'Không có lỗi đọc file trong phạm vi quét.',
              'Báo cáo này không khảo sát toàn bộ ổ đĩa, tài khoản cloud, tài liệu chưa lưu trong Word hoặc lịch sử trình duyệt. Tests và server cần bằng chứng chạy riêng; xem inventory/VERIFICATION_VI.md.']
    markdown = '\n\n'.join(lines) + '\n'
    # Keep table rows adjacent for the small renderer and normal Markdown viewers.
    markdown = re.sub(r'(?<=\|)\n\n(?=\|)', '\n', markdown)
    old_path.parent.mkdir(exist_ok=True)
    old_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (ROOT/'PROJECT_INVENTORY_VI.md').write_text(markdown, encoding='utf-8')
    memory = (ROOT/'PROJECT_MEMORY_VI.md').read_text(encoding='utf-8')
    verify_path = ROOT/'inventory/VERIFICATION_VI.md'
    verification = verify_path.read_text(encoding='utf-8') if verify_path.exists() else ''
    document = '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sổ tay Cờ Chill AI</title><style>body{font:16px/1.6 system-ui,sans-serif;background:#f5f3ed;color:#1d3430;margin:0}main{max-width:1200px;margin:auto;padding:32px}h1,h2{color:#16604f}h2{margin-top:2em;border-bottom:2px solid #ccd8d0}table{border-collapse:collapse;width:100%;background:white;font-size:13px;table-layout:auto}td{border:1px solid #d4dcd5;padding:9px;overflow-wrap:anywhere}tr:first-child{background:#dcebe3;font-weight:bold}code{background:#e3e8e2;padding:2px 4px;overflow-wrap:anywhere}p{overflow-wrap:anywhere}@media print{body{background:white}main{padding:0}table{font-size:10px}tr{break-inside:avoid}}</style><main>'
    document += render_markdown(memory+'\n'+verification+'\n'+markdown) + '</main></html>'
    (ROOT/'deliverables').mkdir(exist_ok=True)
    (ROOT/'deliverables/Co_Chill_So_tay_hien_trang.html').write_text(document, encoding='utf-8')
    print(json.dumps(dict(files=len(records), errors=errors, database=db_counts, head=snap['head']), ensure_ascii=False))


if __name__ == '__main__':
    main()
