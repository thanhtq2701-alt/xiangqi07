from pathlib import Path
import shutil, zipfile, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'var/co-chill-web-source-gon'
OUT.mkdir(exist_ok=True)
runtime=['index.html','style.css','app.js','xiangqi.js','game-tools.js','fixtures.js','learning.js','experience.js','logo-co-chill.png','favicon.svg']
files=['online-preview/'+n for n in runtime]+[
 'tools/test_preview_learning.cjs','tools/test_preview_game_tools.cjs','tools/test_preview_experience.cjs',
 'tools/check_browser_rules.py','tools/check_online_preview.py','tools/export_preview_fixtures.py',
 'app/__init__.py','app/rules.py','app/engine.py','app/puzzles.py',
 'tests/__init__.py','tests/test_rules.py']
for name in files:
 dest=OUT/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
readme='''# Cờ Chill mã nguồn web

Đây là gói nguồn gọn của giao diện ChatGPT Site phiên bản 3 phát hành ngày 16/10/2026. Mã web được sao chép nguyên vẹn từ commit local 77f3fbe. Có 10 file chạy web; các file còn lại giữ kiểm thử và mã luật tham chiếu. Không chứa dữ liệu học, tài liệu Word, secret hoặc thư mục Git cũ.

Website đang hoạt động: https://co-chill-ngay-mai.cosmicanole32.chatgpt.site/

## Mở và chạy

1. Giải nén ZIP ra một thư mục riêng, không ghi đè repo cũ.
2. Trong VS Code chọn File > Open Folder, chọn thư mục có README này.
3. Mở Terminal tại thư mục đó; cần Python 3.10 trở lên.

```powershell
python -m http.server 8769 --bind 127.0.0.1 --directory online-preview
```

Nếu máy dùng Python Launcher, thay `python` bằng `py`. Mở http://127.0.0.1:8769/ và giữ terminal chạy; Ctrl+C để dừng. Python ở lệnh này chỉ phục vụ file tĩnh, không phải backend nghiệp vụ. Nếu cổng bận, đổi sang 8770; dữ liệu học sẽ ở một origin khác. Không cần npm install, API key hoặc database. VS Code là trình soạn thảo; một cửa sổ VS Code mới không tự khởi động web.

## Những file nào làm gì

| File | Vai trò |
|---|---|
| online-preview/index.html | Khung trang, tải các script và CSS đúng thứ tự |
| online-preview/style.css | Màu, bố cục, theme, responsive, hình quân và bàn |
| online-preview/app.js | Trang, nút bấm và điều phối chơi/học/xem lại |
| online-preview/xiangqi.js | Bộ luật, nước hợp lệ, tìm kiếm cờ nông |
| online-preview/game-tools.js | Ký phổ Việt, nhập ván, nước cấm, xử lý lặp trong phạm vi kiểm chứng |
| online-preview/fixtures.js | 12 bài mẫu và lời giải dựa trên luật |
| online-preview/learning.js | Phiên học, lưu trạng thái, đề xuất, lịch ôn |
| online-preview/experience.js | Tùy chọn, điều kiện gửi suy nghĩ, đồng hồ, thống kê, xuất dữ liệu |
| online-preview/logo-co-chill.png | Logo được chủ sản phẩm cung cấp |
| online-preview/favicon.svg | Biểu tượng tab |

Giữ đủ 10 file để giống bản đã phát hành. Hai ảnh không quyết định logic nhưng thiếu sẽ mất logo/icon. Đừng ghép tất cả code vào một file, đổi tên file hoặc đổi thứ tự script tùy ý. Để chỉnh giao diện, chủ yếu sửa index.html/style.css/app.js; để sửa luật cần sửa module liên quan và chạy kiểm thử.

`app/` trong gói này chỉ gồm bốn file tham chiếu luật/engine/bài mẫu phục vụ kiểm thử. Không có server.py, HTTP API hoặc SQLite. `tests/test_rules.py` kiểm tra luật tham chiếu; `tools/` chứa kiểm thử browser và đối chiếu Python/JavaScript. Các file này không được trình duyệt tải, nhưng nên giữ để tránh làm sai luật khi sửa code.

## Kiểm thử

Cần Node hiện đại, khuyến nghị Node 22 trở lên. Không có package npm bên ngoài.

```powershell
node tools/test_preview_learning.cjs
node tools/test_preview_game_tools.cjs
node tools/test_preview_experience.cjs
python -m unittest discover -s tests -v
python tools/check_online_preview.py
python tools/check_browser_rules.py
```

Nếu Node không có trong PATH, `check_browser_rules.py` nhận `--node "đường/dẫn/node.exe"`. Ba bộ Node gồm 51 test. Kiểm tra bài mẫu gồm 12 hình. Giữ mã tham chiếu vì xóa app/ sẽ làm hai công cụ kiểm tra Python không chạy được. Gói này không chứa 72 test backend đầy đủ vì không chứa backend đó; repo gốc giữ nguyên tất cả.

Chỉ khi sửa nguồn bài tập `app/puzzles.py`, chạy `python tools/export_preview_fixtures.py` rồi kiểm tra lại `fixtures.js`. Không tự lấy hoặc scrape bài bên ngoài.

## Giới hạn và dữ liệu

Engine local tìm kiếm tối đa hai nửa nước; lời giải theo mẫu, không gọi LLM, không phải trained ML. Có chơi máy/hai người cùng thiết bị; chưa có PvP online, tài khoản, đồng bộ hoặc luật phân xử giải đấu đầy đủ. Chặn đáp án là cơ chế UI; đáp án có trong mã client, không phải bảo mật đề thi.

Tiến độ ở localStorage của từng origin (giao thức + tên miền + cổng), không nằm trong mã. Copy code sang máy khác hoặc mở localhost không mang theo tiến độ online. Có xuất/xóa trong Cài đặt; JSON xuất để đọc, chưa tự nhập phục hồi. Không dùng dữ liệu học để huấn luyện. Logo do chủ sản phẩm cung cấp; chưa chọn giấy phép tái phân phối source. Không có thư viện cờ, dữ liệu cờ hoặc engine bên thứ ba được đóng gói.

Lỗi nhỏ đã biết: góc lật bàn chưa giữ qua reload; đồng hồ sau xin thua/thỏa thuận hòa còn hiển thị mốc nước gần nhất. Tùy chọn giọng mới đổi lời mở đầu. Chưa có bằng chứng hiệu quả học tập.

## GitHub và deploy là các việc khác nhau

Commit lưu mốc trong Git local. Push đưa các commit lên GitHub. Deploy đưa một phiên bản ra hosting để người khác mở URL. Push không tự cập nhật ChatGPT Site hiện tại. Đang dùng Sites source repository riêng với commit 55bd70cd4c19c52192d5d80160d13982e1c7a80a, project appgprj_6acd061322c08191a4c912862bc05124. AI có thể triển khai qua Sites bằng quyền được cấp; không chép credential vào repo.

Với một repo Git đã có sẵn, sau khi xem thay đổi:

```powershell
git status
git add online-preview app tests tools README.md .gitignore
git diff --cached --stat
git commit -m "Describe the actual change"
```

Push chỉ sau khi kiểm tra đúng remote/nhánh và được phép. Gói ZIP chưa có .git và chưa gắn remote. Nếu dùng gói này thay nội dung repo GitHub hiện có, phải làm trên một bản clone/nhánh sạch và lưu trữ bản Python/tài liệu cũ trước. Không chạy force push hoặc tạo lịch sử mới đè lên repo cũ. Nếu chỉ cần thử code, không cần git init.

Để deploy static ở dịch vụ khác, thư mục xuất bản là online-preview, không cần build. Cấu hình hosting, tài khoản và quyền truy cập là bước riêng; bộ nguồn này chưa tự cấu hình kết nối GitHub/Vercel.

## Gửi cho chat mới

Tôi đang phát triển Cờ Chill. Hãy đọc README trước, dùng online-preview làm nguồn web. Giữ vòng chơi/nhập ván → suy nghĩ trước đáp án → giải thích theo luật → thử lại → bài liên quan → lịch ôn → tiến độ. Không coaching trong ván đang chơi. Không giả ML/LLM hoặc chấm lập luận. Không bỏ hoặc nới test để vượt lỗi. Không tự push/deploy, xóa dữ liệu hoặc đổi quyền public nếu tôi chưa yêu cầu hành động cụ thể. Gói này là bản web gọn; backend và tài liệu V4/UI UX/V5 vẫn ở repo gốc. Trước khi sửa thiết kế tiếp, đọc câu trả lời mới của tôi thay vì đoán phần chưa chốt.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
(OUT/'.gitignore').write_text('__pycache__/\n*.pyc\n.env\n.env.*\n!.env.example\nnode_modules/\nvar/\nartifacts/\n*.sqlite3*\n*.zip\n~$*\n',encoding='utf-8')
archive=ROOT/'deliverables/Co_Chill_Web_Source_Gon.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for name in sorted(files+['README.md','.gitignore']):z.write(OUT/name,arcname='co-chill-web/'+name)
for name in runtime:
 assert (ROOT/'online-preview'/name).read_bytes()==(OUT/'online-preview'/name).read_bytes()
print(json.dumps({'archive':str(archive),'directory':str(OUT),'files':len(files)+2,'runtime_identical':len(runtime),'bytes':archive.stat().st_size},ensure_ascii=True))
