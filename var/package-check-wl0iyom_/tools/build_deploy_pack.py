"""Create a minimal, allowlisted V5 handoff ZIP; never include runtime/user data.

Run from the repository: python tools/build_deploy_pack.py --output NEW_FILE.zip
Existing archives are not overwritten. Run again with a new output name after edits.
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'co_chill_server.py', 'requirements.txt', '.env.example', '.gitignore',
    'Mo_Co_Chill_V5.cmd', 'vercel.json',
    *('app/' + name + '.py' for name in (
        '__init__', 'cloud_store', 'content_store', 'pikafish', 'rules', 'engine', 'puzzles')),
    *('online-preview/' + name for name in (
        'index.html', 'style.css', 'v5.css', 'app.js', 'xiangqi.js', 'game-tools.js',
        'fixtures.js', 'learning.js', 'experience.js', 'cloud-client.js',
        'engine-client.js', 'v5-ui.js', 'favicon.svg', 'logo-co-chill.png', 'cover-co-chill.png')),
    *('tests/' + name + '.py' for name in ('__init__', 'test_rules', 'test_cloud', 'test_pikafish')),
    *('tools/' + name for name in (
        'build_deploy_pack.py', 'test_cloud_client.cjs', 'test_engine_client.cjs',
        'test_v5_ui.cjs', 'test_preview_learning.cjs', 'test_preview_experience.cjs',
        'test_preview_game_tools.cjs', 'check_online_preview.py',
        'check_browser_rules.py', 'export_preview_fixtures.py')),
    *('docs/' + name + '.md' for name in (
        'COCHILL_VN_CHO_NGUOI_MOI', 'DEPLOY_V5', 'PIKAFISH_SETUP_V5',
        'V5_DECISIONS_2026_10_24', 'SITES_V5_RELEASE_2026_10_24')),
    'AI_USAGE.md', 'KNOWN_LIMITATIONS.md', 'PRIVACY.md', 'THIRD_PARTY_NOTICES.md',
    'TEST_REPORT_CODEX.md', 'IMPLEMENTATION_REPORT_CODEX.md',
]

README = '''# Cờ Chill V5 — gói source để bàn giao/deploy

Đọc trước: [Hướng dẫn cochill.vn cho người mới](docs/COCHILL_VN_CHO_NGUOI_MOI.md).

Đây là bản sao các file V5 cần để chạy và tiếp tục phát triển. Giải nén vào thư
mục mới. Không có database, người chơi, mật khẩu thật, khóa TOTP, Word riêng,
Git history hoặc engine binary. Không xóa thư mục dự án gốc.

## Chạy local

Python 3.12 trở lên; mở terminal ngay tại thư mục chứa README này:

```powershell
python co_chill_server.py serve --port 8770
```

Mở http://127.0.0.1:8770/#home và giữ terminal chạy. Dùng `py -3.12` thay
`python` nếu có Python Launcher. SQLite mới ở `var/co_chill_accounts.sqlite3`.
Không cần Node hay API key để chạy. File `Mo_Co_Chill_V5.cmd` dùng cổng 8769.

## Deploy

Hosting phải hỗ trợ Python WSGI, HTTPS và SQLite trên vùng lưu bền. Không chỉ
upload toàn bộ gói vào public_html: source/API không phải toàn bộ là file public.
`co_chill_server.py` chỉ phục vụ tài nguyên từ `online-preview/`.

Lệnh Linux production (Gunicorn):

```sh
pip install -r requirements.txt
gunicorn co_chill_server:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 45 --graceful-timeout 15
```

Xem [DEPLOY_V5.md](docs/DEPLOY_V5.md) về origin, disk, tạo owner và backup.
`vercel.json` chỉ deploy giao diện khách; không tạo backend tài khoản.
`.env.example` là mẫu; ứng dụng không tự nạp `.env`.

## Cấu trúc

- `co_chill_server.py`: server/API/CLI V5.
- `app/`: luật, engine dự phòng, adapter UCI, dữ liệu, tài khoản và bài.
- `online-preview/`: toàn bộ giao diện và tài nguyên trình duyệt.
- `tests/`, `tools/`: kiểm thử V5 và tạo gói.
- `docs/` và các báo cáo: hướng dẫn, giới hạn, quyết định sản phẩm.
- `MANIFEST_SHA256.json`: danh sách, kích thước và hash của từng file (trừ manifest).

Gói bỏ ứng dụng legacy `server.py`/`web/`, tài liệu trả lời và các công cụ tạo
Word. Chúng còn trong dự án gốc nhưng không cần để chạy server V5.

## Kiểm tra gói độc lập

```powershell
python -m unittest discover -s tests -v
python tools/check_online_preview.py
python tools/check_browser_rules.py
node tools/test_preview_learning.cjs
node tools/test_preview_experience.cjs
node tools/test_preview_game_tools.cjs
node tools/test_cloud_client.cjs
node tools/test_engine_client.cjs
node tools/test_v5_ui.cjs
```

Có 68 kiểm thử Python V5/luật trong gói ở thời điểm tạo; 110 test trong báo
cáo dự án đầy đủ gồm thêm legacy không đóng gói. 101 test JavaScript được giữ.
Node chỉ cần khi chạy các kiểm thử JS. Adapter Pikafish được thử bằng UCI giả;
chưa có binary/NNUE thật. Lời giải hiện theo mẫu, chưa có LLM/ML huấn luyện.

## Cập nhật

Sửa code → test → xem diff → commit/push các file được chọn → deploy khi bạn
quyết định. Sau khi đã giải nén và chạy, `var/` có thể chứa dữ liệu riêng:
không upload toàn bộ thư mục một cách mù quáng. Chạy lại
`python tools/build_deploy_pack.py --output deliverables/BAN_MOI.zip` để tạo
gói allowlist mới. Lệnh từ chối ghi đè ZIP cũ. Database cần backup/chuyển riêng.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New ZIP path; no overwrite')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.suffix.lower() != '.zip' or output.exists():
        raise SystemExit('Choose a new .zip path; existing files are never overwritten.')
    entries = {'README.md': README.encode('utf-8')}
    for name in FILES:
        file = ROOT / name
        if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(ROOT):
            raise SystemExit('Missing or unsafe allowlisted file: ' + name)
        entries[name] = file.read_bytes()
    manifest = {
        'createdAt': datetime.now(timezone(timedelta(hours=7))).isoformat(),
        'kind': 'co-chill-v5-source-only',
        'containsUserData': False,
        'files': [{'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                  for name, data in sorted(entries.items())],
    }
    entries['MANIFEST_SHA256.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(entries)
        for item in manifest['files']:
            assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
    print(json.dumps({'archive': str(output), 'files': len(entries), 'bytes': output.stat().st_size,
                      'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'verification': 'ZIP integrity and all file hashes passed'}, ensure_ascii=True))


if __name__ == '__main__':
    main()
