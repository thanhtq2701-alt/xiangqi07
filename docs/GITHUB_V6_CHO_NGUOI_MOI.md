# Đưa gói V6 lên GitHub — 26/10/2026

## 1. Bạn đang nhận gì?

ZIP là bản source sạch. Giải nén sẽ thấy `README.md`, `co_chill_server.py`,
`online-preview/`, `app/`, `tests/`, `tools/`, `docs/` cùng cấu hình mẫu.
Mở **cả thư mục** bằng VS Code → File → Open Folder. Không chỉ mở một file HTML.
GitHub lưu code và lịch sử chỉnh sửa; việc push code chưa làm website chạy trên Internet.

## 2. Kiểm tra trước

Cài Python 3.12 trở lên. Trong Terminal của VS Code, ở thư mục chứa README:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769`. Giữ terminal chạy; Ctrl+C để dừng. Máy khác dùng
localhost sẽ mở máy của họ, không phải máy bạn. Nếu báo cổng đã dùng, đổi thành
`--port 8770`. Không tắt tiến trình lạ để giành cổng.

Để test cần thêm Node.js (ứng dụng chạy bình thường không cần Node):

```powershell
python tools/run_checks.py
```

## 3. Cập nhật repository đã có, giữ lịch sử

Cách dễ kiểm soát: dùng GitHub Desktop → File → Clone repository → chọn
`thanhtq2701-alt/xiangqi07` → chọn một thư mục mới. Nếu đã có bản clone đúng
repo, dùng bản đó sau khi kiểm tra những thay đổi chưa commit.

Giải nén ZIP vào thư mục tạm, rồi **chép các file bên trong** vào thư mục clone,
để README nằm ngay gốc repo. Không chép file ZIP làm source; không tạo thư mục
`xiangqi-ai/xiangqi-ai/` lồng nhau. Không xóa `.git/`, database cũ hoặc file bạn
chưa kiểm tra. Pack không tự xóa file legacy khỏi repo cũ: nếu cần dọn, xem diff
và giữ bản sao trước. Các file cũ không nằm trong pack có thể là tài liệu lịch sử.

GitHub Desktop → Changes: đọc danh sách thay đổi → bỏ chọn dữ liệu riêng hoặc
tài liệu trả lời cá nhân → ghi commit, ví dụ `Add V6 learning and online room pilot`
→ Commit → Push origin. Nếu xuất hiện conflict, dừng để đọc và hợp nhất;
không Force Push và không xóa lịch sử để làm mất lỗi.

Với Terminal, trong bản clone đã có remote:

```powershell
git status --short
git diff --stat
git add README.md AGENTS.md CLAUDE.md .gitignore .gitattributes .env.example requirements.txt co_chill_server.py Mo_Co_Chill_V5.cmd app online-preview tests tools docs AI_USAGE.md IMPLEMENTATION_REPORT_CODEX.md TEST_REPORT_CODEX.md KNOWN_LIMITATIONS.md PRIVACY.md THIRD_PARTY_NOTICES.md
git diff --cached --stat
git diff --cached --check
git commit -m "Add V6 learning and online room pilot"
git push
```

Chỉ chạy `git add` sau khi đã rà các thư mục được liệt kê trong **bản clone của bạn**;
repo cũ có thể có file riêng mà pack sạch không chứa. `.gitignore` không tự bỏ
theo dõi một secret đã commit từ trước. Nếu từng lộ secret, phải thu hồi/đổi
secret đó; xóa khỏi commit mới không xóa nó khỏi lịch sử.

## 4. File nào phải giữ?

| Nhóm | Nếu bỏ đi |
|---|---|
| `co_chill_server.py`, `app/*.py` trong pack | Mất API, tài khoản, lưu trữ, PvP hoặc engine |
| Toàn bộ `online-preview/` | Thiếu màn hình, ảnh, luật hoặc thao tác học/chơi |
| `requirements.txt` | Thiếu hướng dẫn cài server production Linux |
| `.env.example` | Mất mẫu cấu hình; đây không phải secret thật |
| `.gitignore` | Dễ đưa dữ liệu riêng phát sinh sau khi chạy vào Git |
| `tests/`, `tools/` | App có thể chạy nhưng mất khả năng kiểm tra và đóng gói đáng tin cậy |
| README, báo cáo, `docs/`, AGENTS, CLAUDE | Mất bối cảnh quyết định và hướng dẫn phát triển tiếp |
| `MANIFEST_SHA256.json` | Mất dấu vân tay của bản ZIP; sau sửa code cần tạo pack/manifest mới |

Không commit `var/`, `.env` thật, database, log, backup, private key, thông tin
đăng nhập, `node_modules/` hoặc ZIP cũ. Gói không chứa tài khoản người chơi;
copy code không chuyển database. Backup dữ liệu cần quy trình riêng, giữ kín.

## 5. Tiếp tục với Claude

Mở thư mục source trong VS Code; đưa Claude đọc `CLAUDE.md` rồi
`docs/CLAUDE_HANDOFF_V6.md`. Yêu cầu làm từng mục còn thiếu, chạy tests và
giải thích diff. Mỗi đợt: sửa → thử → xem diff → commit → push. Chỉ deploy khi
bạn duyệt. Không cần mua lại tên miền hay copy code từ website công khai.
