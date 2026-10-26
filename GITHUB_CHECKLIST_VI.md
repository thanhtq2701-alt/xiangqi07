# Checklist GitHub và quy trình làm việc — Cờ Chill V6

Đây là hướng dẫn cho source V6 hiện tại; không phải hướng dẫn triển khai
production. Đọc [README](README.md), [handoff V6](docs/CLAUDE_HANDOFF_V6.md),
[quyết định V6](docs/V6_DECISIONS.md), [giới hạn](KNOWN_LIMITATIONS.md) và
[báo cáo kiểm thử](TEST_REPORT_CODEX.md) trước khi phát hành.

## 1. Entry point và yêu cầu

- Entry point duy nhất để chạy ứng dụng local:
  `python co_chill_server.py serve --port 8769`.
- Giao diện hiện hành nằm trong `online-preview/`; backend và persistence nằm
  trong `app/`.
- Python 3.12 trở lên để chạy ứng dụng. Node.js chỉ cần để chạy test.
- Dùng `python tools/run_checks.py` để chạy bộ kiểm tra chuẩn từ thư mục gốc.
- Không cần API key hay dịch vụ trả phí để chạy local.
- Không deploy, đổi DNS, tạo dịch vụ trả phí hoặc push GitHub khi chưa được
  chủ dự án cho phép.

## 2. Chạy và kiểm tra

Từ thư mục gốc repository:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`. Giữ terminal mở; Ctrl+C để dừng. Trên Windows
có thể thay `python` bằng `py -3.12`; Linux/macOS có thể dùng `python3`.
Localhost không phải URL public.

Trước khi bàn giao thay đổi code:

```powershell
python tools/run_checks.py
git diff --check
```

`tools/run_checks.py` kiểm tra Python, JavaScript, nội dung bài, fixture và
parity luật. Cần Node.js cho toàn bộ runner. Khi chỉ sửa tài liệu, đọc lại
nội dung/liên kết và chạy `git diff --check`; ghi rõ nếu không chạy test code.

## 3. Kiểm tra Git trước khi stage

```powershell
git status --short
git diff --stat
git diff --check
```

Chỉ stage những file đã đọc và xác nhận. Trước khi commit, xem cả nội dung
staged:

```powershell
git add <cac-file-da-xem>
git diff --cached --stat
git diff --cached
git diff --cached --check
```

Không dùng `git add .` một cách mù quáng. Không commit `var/`, database,
backup, log, secret, `.env` thật, cookie, dữ liệu reflection hoặc file build
cá nhân. Các quy tắc ignore không thể thay thế việc kiểm tra staged diff.

Chỉ commit/push theo quy trình đã được chủ dự án chấp thuận. Không force-push,
không xóa lịch sử, không tạo repository phát hành mới và không thay đổi
visibility khi chưa được cho phép. Nếu secret từng bị lộ, thu hồi secret;
xóa file khỏi commit mới không xóa được dữ liệu khỏi lịch sử cũ.

## 4. Thành phần của source V6

| Nhóm | Vai trò |
|---|---|
| `co_chill_server.py` | CLI, HTTP server, API và phục vụ giao diện |
| `app/` | Luật/backend, tài khoản, lưu trữ, phòng PvP, adapter engine |
| `online-preview/` | Giao diện, luật phía trình duyệt và luồng học |
| `tests/`, `tools/` | Test, kiểm tra parity, runner và đóng gói |
| `docs/spec/` | Final Pack gốc; giữ nguyên nội dung |
| `README.md`, báo cáo và handoff | Cách chạy, quyết định, kết quả và giới hạn đã xác minh |

Dùng `tools/build_v6_pack.py` để tạo source pack bằng allowlist và
`tools/verify_source_pack.py` để xác minh pack. Builder yêu cầu đường dẫn ZIP
mới, không ghi đè bản phát hành cũ.

## 5. An toàn dữ liệu và ranh giới phát hành

- SQLite mặc định ở `var/`; không đưa database hay backup người chơi lên Git.
- Không gửi secret, cookie, backup hoặc dữ liệu người học cho AI/GitHub.
- Không tuyên bố source local đã xác minh Pikafish/NNUE hoặc hạ tầng Google
  Cloud của chủ dự án.
- Luật và engine là nguồn sự thật cho nước đi/đánh giá; lời giải không được
  xuất hiện trước reflection.
- Xem `PRIVACY.md`, `THIRD_PARTY_NOTICES.md` và xác nhận giấy phép trước khi
  công khai hoặc phân phối lại source.

Để biết thao tác GitHub cho người mới, xem
[docs/GITHUB_V6_CHO_NGUOI_MOI.md](docs/GITHUB_V6_CHO_NGUOI_MOI.md). Hướng dẫn
đưa lên hạ tầng nằm ở [docs/DEPLOY_GCP_V6.md](docs/DEPLOY_GCP_V6.md); đây
không phải sự cho phép deploy hoặc phát sinh chi phí.
