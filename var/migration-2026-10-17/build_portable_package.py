from pathlib import Path
import hashlib
import json
import subprocess
import textwrap
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'deliverables/Co_Chill_VSCode_2026_10_17'
ARCHIVE = TARGET.with_suffix('.zip')
if TARGET.exists() or ARCHIVE.exists():
    raise SystemExit('Refusing to overwrite an existing package directory or archive.')

SOURCE_FILES = [
    'online-preview/index.html', 'online-preview/style.css', 'online-preview/app.js',
    'online-preview/xiangqi.js', 'online-preview/game-tools.js', 'online-preview/fixtures.js',
    'online-preview/learning.js', 'online-preview/experience.js',
    'online-preview/logo-co-chill.png', 'online-preview/favicon.svg',
    'app/__init__.py', 'app/rules.py', 'app/engine.py', 'app/puzzles.py',
    'tests/__init__.py', 'tests/test_rules.py',
    'tools/export_preview_fixtures.py', 'tools/check_online_preview.py',
    'tools/check_browser_rules.py', 'tools/test_preview_learning.cjs',
    'tools/test_preview_game_tools.cjs', 'tools/test_preview_experience.cjs',
    'THIRD_PARTY_NOTICES.md',
]
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
TARGET.mkdir()
manifest = []
for relative in SOURCE_FILES:
    source = ROOT / relative
    content = source.read_bytes()
    destination = TARGET / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    try:
        committed = subprocess.check_output(['git', 'show', head + ':' + relative], cwd=ROOT, stderr=subprocess.DEVNULL)
        matches_head = content == committed
    except subprocess.CalledProcessError:
        matches_head = None
    manifest.append({'original_relative_path': relative, 'package_relative_path': relative,
                     'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
                     'matches_source_head': matches_head})

def write(relative, content):
    path = TARGET / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding='utf-8', newline='\n')

write('README.md', '''
    # Cờ Chill — bộ mã nguồn dành cho VS Code

    Đóng gói ngày **17/10/2026** từ các file đang có trong repository gốc. Gói này giữ nguyên byte của 10 tài nguyên chạy website trong `online-preview/`, thêm mã tham chiếu và kiểm thử để tiếp tục phát triển. Không chứa tài khoản đăng nhập, dữ liệu người chơi, tài liệu Word riêng, lịch sử Git hoặc thông tin truy cập hosting.

    Đây là **bản web tĩnh chạy trong trình duyệt**. Không phải ứng dụng Python/SQLite `server.py` + `web/` của repository gốc. Không cần Codex hoặc Claude để chạy; VS Code và trợ lý AI chỉ hỗ trợ đọc/sửa code. `SOURCE_MANIFEST.json` ghi đường dẫn nguồn, hash và commit nền lúc sao chép, không khẳng định commit nền chứa mọi thay đổi hiện có hoặc là phiên bản đang được phát trên Internet.

    ## 1. Mở và chạy trong VS Code

    1. Giải nén ZIP vào một thư mục mới. Không ghi đè hoặc xóa repository cũ.
    2. Chọn **File → Open Folder** trong VS Code, mở thư mục chứa README này.
    3. Cần Python 3.10 trở lên trên máy; mở **Terminal → New Terminal** tại thư mục đó.

    ```powershell
    python --version
    python -m http.server 8769 --bind 127.0.0.1 --directory online-preview
    ```

    Mở **http://127.0.0.1:8769/#home**. Giữ terminal đang chạy; Ctrl+C để dừng. Nếu Windows dùng Python Launcher, thay `python` bằng `py`. Có thể dùng **Terminal → Run Task → Cờ Chill: Chạy web local**; task mặc định gọi `python`.

    Lệnh trên chỉ phục vụ file tĩnh. Trình duyệt chạy luật cờ và lưu tiến độ. Không có `npm install`, API key, database hoặc bước build. Không nên chỉ nhấp đúp `index.html`: hãy dùng HTTP local để cách tải file và lưu dữ liệu nhất quán. Nếu đang chạy server ở cổng 8769, dùng lại hoặc chọn cổng khác; đổi cổng tạo vùng dữ liệu trình duyệt khác. Mở cửa sổ VS Code mới không tự bật server.

    Để độc lập với Codex, dùng Python và Node đã cài vào máy/PATH; không coi đường dẫn runtime nằm trong thư mục cache Codex là thành phần của dự án. Có thể chạy bằng đường dẫn đầy đủ tới `python.exe` nếu chưa có PATH.

    ## 2. Mười file chạy website

    Tất cả nằm trong `online-preview/`.

    | File | Vai trò | Nếu thiếu |
    |---|---|---|
    | `index.html` | Khung trang, vùng nội dung, menu và thứ tự tải CSS/JS | Mất điểm mở website và khởi tạo giao diện |
    | `style.css` | Màu, theme, bố cục, bàn cờ, responsive | Mất giao diện và bố cục bàn cờ đúng |
    | `app.js` | Điều phối trang, sự kiện, chơi/học/xem lại, lưu trình duyệt | Không còn ứng dụng tương tác hoạt động |
    | `xiangqi.js` | Luật đi quân, FEN, nước hợp lệ, an toàn Tướng, tìm kiếm nông | Chơi và phân tích không chạy đúng |
    | `game-tools.js` | Ký phổ Việt, nhập ván, lịch sử, lý do nước sai, kiểm tra lặp | Hỏng các luồng tương ứng và thao tác ván |
    | `fixtures.js` | 12 bài tổng hợp, lời giải mẫu và thông tin nguồn | Mất dữ liệu bài học/luyện liên quan |
    | `learning.js` | Phiên học, phản hồi trước đáp án, hoàn thành, lịch ôn, đề xuất | Hỏng vòng học và khôi phục tiến độ |
    | `experience.js` | Tùy chọn, gợi mở, kiểm tra phản hồi, đồng hồ, thống kê, xuất dữ liệu | Hỏng khởi tạo/tùy chọn và các luồng liên quan |
    | `logo-co-chill.png` | Logo hiện có | Mất hình logo; luật vẫn có thể hoạt động |
    | `favicon.svg` | Biểu tượng trên tab | Mất icon tab; luật vẫn có thể hoạt động |

    Giữ đủ cả 10 file để bảo toàn trải nghiệm. Không ghép tất cả thành một file, đổi tên hoặc đổi thứ tự script tùy ý. `index.html` tải `xiangqi.js → game-tools.js → fixtures.js → learning.js → experience.js → app.js`; các thẻ đều dùng `defer`.

    `xiangqi.js` cung cấp đối tượng `XQ`. Các module game-tools, learning và experience bổ sung hàm vào `CC`. `fixtures.js` cung cấp `FIXTURES`. `app.js` dùng chúng để dựng nội dung vào vùng `main`.

    ## 3. Kiến trúc và cách sửa

    ```text
    Static hosting / Python http.server
      └─ HTML + CSS + JavaScript + ảnh
           └─ Trình duyệt
                ├─ app.js: điều phối giao diện và thao tác
                ├─ xiangqi.js: luật và engine cục bộ
                ├─ game-tools.js: ký phổ và kiểm tra ván
                ├─ fixtures.js: dữ liệu bài học
                ├─ learning.js: vòng học, đề xuất, lịch ôn
                ├─ experience.js: tùy chọn và tương tác hỗ trợ
                └─ localStorage: dữ liệu trên trình duyệt này
    ```

    Đây là ứng dụng một trang dùng đường dẫn sau dấu `#`: `#home`, `#play`, `#lessons`, `#learn`, `#game/{id}`, `#moments/{id}`, `#replay/{id}`, `#mistakes`, `#review`, `#summary`, `#profile`, `#settings`, `#howto`, `#path`, `#rules`, `#about`. Mỗi mục không có một file HTML riêng; các hàm trong `app.js` dựng nội dung tương ứng.

    - Chỉnh màu/khoảng cách/giao diện điện thoại: bắt đầu ở `style.css`.
    - Chỉnh khung menu/header: `index.html`; chỉnh nội dung từng trang/sự kiện: `app.js`.
    - Chỉnh luật: `xiangqi.js` và tham chiếu `app/rules.py`, rồi chạy toàn bộ kiểm thử.
    - Chỉnh ký phổ hoặc phán quyết lặp: `game-tools.js` và bộ test tương ứng.
    - Chỉnh lịch ôn/tiêu chí ghi nhận: `learning.js`; tiêu chí thống kê/gợi mở: `experience.js`.
    - Chỉnh bài mẫu: sửa `app/puzzles.py` hoặc exporter có chủ đích, tạo lại `fixtures.js`, kiểm tra nước hợp lệ và lời giải. Không chỉ sửa đáp án mà bỏ qua FEN/nước hợp lệ.

    Chưa có thư viện React/Vue, TypeScript, máy chủ API chung, tài khoản thật hoặc đồng bộ nhiều thiết bị. Chưa có yêu cầu chuyển framework chỉ để mở lại website trong VS Code.

    ## 4. Những file giữ để bảo trì

    | File/thư mục | Mục đích; hậu quả nếu bỏ |
    |---|---|
    | `app/__init__.py` | Dấu hiệu package Python của mã tham chiếu |
    | `app/rules.py` | Luật Python để tạo/kiểm tra bài và so sánh JavaScript; bỏ sẽ làm kiểm tra tham chiếu hỏng |
    | `app/engine.py` | Engine Python tham chiếu để so kết quả tìm kiếm; bỏ sẽ mất parity check |
    | `app/puzzles.py` | Nguồn 12 bài tổng hợp; bỏ sẽ không tái tạo/đối chiếu fixtures được |
    | `tests/__init__.py`, `tests/test_rules.py` | Kiểm thử luật Python; bỏ sẽ mất bảo vệ hồi quy |
    | `tools/export_preview_fixtures.py` | Tạo lại fixtures từ nguồn Python; chỉ chạy khi chủ đích sửa nguồn bài |
    | `tools/check_online_preview.py` | Kiểm tra 12 bài xuất ra khớp luật và nguồn |
    | `tools/check_browser_rules.py` | So luật/engine trình duyệt với Python |
    | `tools/test_preview_learning.cjs` | Kiểm tra vòng học, lưu/khôi phục, đề xuất và lịch ôn |
    | `tools/test_preview_game_tools.cjs` | Kiểm tra ký phổ, nhập ván và các trường hợp luật lặp |
    | `tools/test_preview_experience.cjs` | Kiểm tra phản hồi, tùy chọn, đồng hồ, xuất dữ liệu và thống kê |
    | `tools/check_all.py` | Chạy toàn bộ kiểm tra trong gói bằng một lệnh |
    | `.vscode/tasks.json` | Hai tác vụ tiện ích chạy web và chạy test; thiếu vẫn dùng terminal được |
    | `.gitignore` | Giúp tránh commit cache, dữ liệu và secret; không bảo đảm mọi secret đều được phát hiện |
    | `README.md`, `AI_HANDOFF.md` | Hướng dẫn cho bạn và trợ lý tiếp theo; không phải runtime |
    | `SOURCE_MANIFEST.json` | Dấu vết nguồn và hash các file đã sao chép; không phải runtime |
    | `THIRD_PARTY_NOTICES.md` | Thông tin nguồn/tham khảo kế thừa; không phải giấy phép sử dụng hay tái phân phối |

    `app/` trong gói này chỉ là bốn file tham chiếu, không phải backend hoàn chỉnh. Không có `server.py`, `web/`, SQLite hay test backend. Repository gốc giữ nguyên các phần đó.

    ## 5. Kiểm tra trước và sau khi sửa

    Cần Python 3.10+ và Node.js 18+; dùng Node còn được nhà cung cấp hỗ trợ. Không cần package Python/npm ngoài thư viện chuẩn.

    ```powershell
    python tools/check_all.py
    ```

    Nếu Node không ở PATH:

    ```powershell
    python tools/check_all.py --node "C:\\duong-dan\\node.exe"
    ```

    Hoặc chọn **Terminal → Run Task → Cờ Chill: Kiểm tra toàn bộ**. Runner kiểm tra cú pháp cả sáu JavaScript, ba bộ Node test, luật Python, dữ liệu 12 bài và đối chiếu engine/luật. Nó trả mã lỗi nếu bất kỳ kiểm tra nào thất bại. Nó không tự cài thư viện hay sửa source.

    Các lệnh riêng để tìm lỗi:

    ```powershell
    node tools/test_preview_learning.cjs
    node tools/test_preview_game_tools.cjs
    node tools/test_preview_experience.cjs
    python -m unittest discover -s tests -v
    python tools/check_online_preview.py
    python tools/check_browser_rules.py --node node
    ```

    Sau khi có chủ đích sửa nguồn bài: `python tools/export_preview_fixtures.py`, xem diff, rồi chạy lại toàn bộ kiểm tra. Không xóa hoặc nới test chỉ để vượt lỗi.

    ## 6. Dữ liệu, giới hạn và giấy phép

    Tiến độ dùng `localStorage` với khóa `co-chill-v4-browser`; tùy chọn dùng `co-chill-preferences-v1`. Dữ liệu thuộc trình duyệt/profile/origin (giao thức + tên miền + cổng), không nằm trong source. Copy code sang máy khác không copy tiến độ; tên miền online và localhost là hai vùng riêng. Có xuất/xóa trong Cài đặt; file JSON xuất để đọc, chưa có nhập phục hồi tự động. Không xóa dữ liệu trình duyệt trước khi sao lưu nếu cần giữ tiến độ.

    Engine là tìm kiếm cục bộ tối đa hai nửa nước và ước lượng vật chất; lời giải theo mẫu, không phải LLM hoặc ML được huấn luyện. 12 bài do dự án tự dựng, chưa được chuyên gia độc lập thẩm định. Khóa lời giải là cơ chế UI, đáp án vẫn nằm trong source client. Có chơi máy/hai người cùng máy; chưa có PvP online, tài khoản tập trung, admin hoặc đồng bộ đa thiết bị. Luật phân xử giải đấu đầy đủ chưa được bảo đảm. Không có số liệu hiệu quả học tập đã kiểm chứng.

    File `THIRD_PARTY_NOTICES.md` được sao chép nguyên văn từ repository gốc; có đoạn nói về backend Python/SQLite và tài liệu gốc không nằm trong gói này. Logo PNG là tài nguyên thương hiệu hiện có, không phải toàn bộ đồ họa đều chỉ là SVG/CSS. Chủ dự án chưa chọn giấy phép tái phân phối công khai; gói này **không bổ sung giấy phép hoặc cấp quyền mới**. Không đóng gói engine, dữ liệu cờ hay thư viện cờ bên thứ ba.

    ## 7. GitHub, hosting và trợ lý tiếp theo

    Gói này không có `.git`, không gắn remote, không mang theo quyền quản trị website. Source đã được lưu trong gói không có nghĩa đã push GitHub hoặc deploy. Đừng tạo lịch sử Git mới rồi force-push đè repository hiện có. Nếu muốn đưa các file này vào repo cũ, làm trên một bản clone/nhánh có kiểm tra, giữ nguyên lịch sử và bản sao tài liệu/backend.

    Địa chỉ web đã dùng trong dự án: https://co-chill-ngay-mai.cosmicanole32.chatgpt.site/. Copy code không thay thế website đó và không chuyển quyền tên miền. Hosting là bước riêng: thư mục static để xuất bản là `online-preview/`, không có bước build. Gói này chưa tạo cấu hình hay kết nối tài khoản hosting mới.

    Mở `AI_HANDOFF.md`, gửi nội dung cho Claude hoặc trợ lý bạn chọn. Đây là file bàn giao thông thường, không khẳng định extension tự động đọc nó. Các file Word V4/UI UX/V5, đặc tả và câu trả lời cá nhân vẫn nằm ở repository/thư mục gốc; cung cấp phần cần thiết khi bắt đầu công việc mới. Luôn yêu cầu bạn duyệt trước push/deploy, đổi public, mua dịch vụ hoặc xóa dữ liệu/file có giá trị. Không có chế độ auto-approve trong gói này.
''')

write('.gitignore', '''
    __pycache__/
    *.py[cod]
    .venv/
    node_modules/
    .env
    .env.*
    !.env.example
    var/
    artifacts/
    .openai/
    *.sqlite3
    *.sqlite3-wal
    *.sqlite3-shm
    *.log
    *.zip
    co-chill-data*.json
    co-chill-personal*.json
    ~$*
''')

write('AI_HANDOFF.md', '''
    # Bàn giao Cờ Chill cho trợ lý tiếp theo

    Gói nguồn ngày 17/10/2026. Đọc README, manifest và code thực tế trước khi sửa. Người dùng là người mới: giải thích bằng tiếng Việt, nói rõ file nào thay đổi và cách kiểm tra.

    ## Phạm vi thực tế

    - Nguồn website là `online-preview/`: HTML/CSS/JavaScript thuần; không có bước build hoặc API trả phí.
    - Python trong `app/` chỉ là tham chiếu luật/engine/bài để chạy kiểm thử. Gói này không có app backend Python/SQLite đầy đủ.
    - Giữ vòng chơi/nhập ván → chọn điểm cần học → phản hồi trước đáp án → giải thích có căn cứ → thử lại → bài liên quan → lịch ôn → tiến độ.
    - Không coaching khi ván đang chạy. Luật/engine quyết định nước hợp lệ, biến và đánh giá; lời giải không được bịa nước.
    - Engine nông, bài tự dựng, lời giải template, lịch ôn heuristic: mô tả trung thực, không nhận có LLM/ML hay hiệu quả học tập đã kiểm chứng.
    - Dữ liệu hiện là localStorage theo trình duyệt/origin. Chưa có tài khoản thật, admin tập trung, cloud sync hoặc online PvP.
    - Kế hoạch V5 có tài khoản tập trung, quản lý/thống kê đăng ký từ nhiều thiết bị, quyền admin và đồng bộ tiến độ. Đây là yêu cầu dự kiến, chưa triển khai; đọc câu trả lời V5 mới của chủ dự án trước khi quyết định chi tiết.
    - Tài liệu gốc không nằm trong gói này. Không tự giả định các phần thiếu đã được chốt; yêu cầu chủ dự án cung cấp khi công việc phụ thuộc chúng. Không cần các tài liệu đó chỉ để chạy code hiện tại.

    ## Quy tắc làm việc

    1. Kiểm tra trạng thái file và các test trước khi thay đổi. Chạy `python tools/check_all.py` sau thay đổi liên quan; không xóa hoặc làm yếu test để pass.
    2. Không rewrite toàn bộ hoặc chuyển framework nếu chưa có lý do cụ thể và phạm vi phù hợp yêu cầu.
    3. Không scrape dữ liệu, commit secret, lưu mật khẩu dạng rõ, dùng dữ liệu người học để huấn luyện. Giữ xuất/xóa dữ liệu và hạn chế thật trong giao diện.
    4. **Luôn hỏi chủ dự án trước khi push GitHub, deploy, thay đổi quyền public, mua dịch vụ hoặc xóa dữ liệu/file có giá trị.** Auto-approve đã bị thu hồi. Việc đọc file, chuẩn bị phương án và kiểm tra local không phải bằng chứng được phép xuất bản.
    5. Không force-push, không xóa lịch sử Git. Gói này không chứa `.git` hoặc hosting credentials. Trước thao tác Git phải kiểm tra repo/nhánh/remote thực tế.
    6. Ghi rõ nội dung đã sửa, test đã chạy, lỗi/giới hạn còn lại và bước cần chủ dự án duyệt. Không nói đã deploy chỉ vì source chạy local.

    ## Prompt có thể gửi cùng gói

    “Hãy đọc README.md, AI_HANDOFF.md và SOURCE_MANIFEST.json. Mở online-preview để hiểu website Cờ Chill hiện tại. Chạy các test và giải thích ngắn kiến trúc trước khi thực hiện thay đổi tôi yêu cầu. Giữ luật cờ, reflection gating và vòng học. Không tự push/deploy, đổi public hoặc xóa dữ liệu. Tôi sẽ cung cấp V5/UI UX và luật khi làm nâng cấp tiếp.”

    File này là tài liệu để chủ dự án gửi/cho phép trợ lý đọc; không dựa vào việc một extension cụ thể tự động nạp file.
''')

tasks = {
    'version': '2.0.0',
    'tasks': [
        {'label': 'Cờ Chill: Chạy web local', 'type': 'process', 'command': 'python',
         'args': ['-m', 'http.server', '8769', '--bind', '127.0.0.1', '--directory', 'online-preview'],
         'options': {'cwd': '${workspaceFolder}'}, 'isBackground': True, 'problemMatcher': [],
         'presentation': {'reveal': 'always', 'panel': 'dedicated'}},
        {'label': 'Cờ Chill: Kiểm tra toàn bộ', 'type': 'process', 'command': 'python',
         'args': ['tools/check_all.py'], 'options': {'cwd': '${workspaceFolder}'},
         'group': {'kind': 'test', 'isDefault': True}, 'problemMatcher': [],
         'presentation': {'reveal': 'always', 'panel': 'dedicated'}},
    ],
}
write('.vscode/tasks.json', json.dumps(tasks, ensure_ascii=False, indent=2) + '\n')

write('tools/check_all.py', '''
    """Run the portable web package checks without installing dependencies.

    Usage: python tools/check_all.py [--node PATH_TO_NODE]
    Requires Python 3.10+ and Node.js 18+. Does not modify source or access a network.
    """
    import argparse
    from pathlib import Path
    import re
    import shutil
    import subprocess
    import sys
    import time

    ROOT = Path(__file__).resolve().parents[1]
    SCRIPT_NAMES = ('xiangqi.js', 'game-tools.js', 'fixtures.js', 'learning.js', 'experience.js', 'app.js')

    def main():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--node', default='node', help='Node executable name or full path (default: node on PATH)')
        args = parser.parse_args()
        if sys.version_info < (3, 10):
            parser.error('Python 3.10 or newer is required.')
        node = shutil.which(args.node)
        if not node:
            parser.error('Node.js was not found. Install a supported Node release or supply --node PATH.')
        try:
            version = subprocess.check_output([node, '--version'], text=True, timeout=15).strip()
        except (OSError, subprocess.SubprocessError) as error:
            parser.error('Cannot start Node.js: ' + str(error))
        match = re.fullmatch(r'v(\\d+)\\.\\d+\\.\\d+(?:[-+].*)?', version)
        if not match or int(match.group(1)) < 18:
            parser.error('Node.js 18 or newer is required; found ' + version)
        commands = [(f'JavaScript syntax: {name}', [node, '--check', str(ROOT / 'online-preview' / name)]) for name in SCRIPT_NAMES]
        commands.extend((name, [node, str(ROOT / 'tools' / name)]) for name in (
            'test_preview_learning.cjs', 'test_preview_game_tools.cjs', 'test_preview_experience.cjs'))
        commands.extend([
            ('Python reference rules', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_rules.py', '-v']),
            ('Exported exercises match source', [sys.executable, str(ROOT / 'tools/check_online_preview.py')]),
            ('Browser/Python rule and engine parity', [sys.executable, str(ROOT / 'tools/check_browser_rules.py'), '--node', node]),
        ])
        failures = []
        began = time.monotonic()
        print(f'Python {sys.version.split()[0]} | Node {version} | {len(commands)} checks', flush=True)
        for number, (label, command) in enumerate(commands, 1):
            print(f'\\n[{number}/{len(commands)}] {label}', flush=True)
            try:
                result = subprocess.run(command, cwd=ROOT, timeout=300, check=False)
                if result.returncode:
                    failures.append((label, f'exit {result.returncode}'))
                else:
                    print('PASS', flush=True)
            except (OSError, subprocess.TimeoutExpired) as error:
                failures.append((label, str(error)))
                print('FAIL: ' + str(error), flush=True)
        elapsed = time.monotonic() - began
        print(f'\\nResult: {len(commands) - len(failures)}/{len(commands)} checks passed in {elapsed:.1f}s', flush=True)
        for label, reason in failures:
            print(f'FAIL: {label}: {reason}', flush=True)
        return 1 if failures else 0

    if __name__ == '__main__':
        raise SystemExit(main())
''')

write('SOURCE_MANIFEST.json', json.dumps({
    'package_date': '2026-10-17', 'date_timezone': 'Asia/Bangkok',
    'source_git_head': head,
    'source_kind': 'working-tree files copied unchanged; HEAD is context, not a deployment claim',
    'note': 'Only copied source files are listed. README, AI_HANDOFF, tasks, check_all, .gitignore and this manifest were authored for the package.',
    'files': manifest,
}, ensure_ascii=False, indent=2) + '\n')

package_files = sorted(p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file())
assert len(package_files) == 29, len(package_files)
(ROOT / 'var/migration-2026-10-17/package-files.json').write_text(json.dumps(package_files, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'directory': str(TARGET), 'files': len(package_files), 'copied_source_files': len(SOURCE_FILES), 'source_git_head': head}, ensure_ascii=False))
