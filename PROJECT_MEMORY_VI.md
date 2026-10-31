# Sổ tay hiện trạng Cờ Chill V6

Cập nhật 31/10/2026. Đây là ghi chú hiện trạng, không thay thế đặc tả gốc,
quyết định của chủ dự án hoặc báo cáo kiểm thử.

## Trạng thái Production theo chủ dự án

`cochill.vn` đang chạy HTTPS trên GCP VM Ubuntu 24.04 (2 vCPU, 3.8 GB RAM).
Source deploy ở `/var/www/html`, venv Python 3.12 ở `.venv`; systemd unit
`cochill.service` chạy `co_chill_server.py serve --host 127.0.0.1 --port
8000`, đọc `/etc/cochill.env`. SQLite ở
`/var/www/html/var/co_chill_accounts.sqlite3`; backup cron hằng ngày giữ 14
ngày. Nginx proxy HTTPS đến loopback; cấu hình chi tiết và thao tác vận hành
nằm trong [deploy/DEPLOY_GCP_VI.md](deploy/DEPLOY_GCP_VI.md).

Đây là thông tin Production do chủ dự án cung cấp, chưa được xác minh trực tiếp
từ VM. Source Production được báo cáo tại `3365734` ngày 28/10/2026; thay đổi
nhánh làm việc hiện tại chưa được deploy.

## 1. Nguồn thông tin

- [README](README.md): quick start, kiến trúc, đóng gói và liên kết tài liệu.
- [AGENTS.md](AGENTS.md): quy tắc phát triển và các bất biến sản phẩm.
- [docs/CLAUDE_HANDOFF_V6.md](docs/CLAUDE_HANDOFF_V6.md) và
  [docs/V6_DECISIONS.md](docs/V6_DECISIONS.md): handoff, ranh giới kiến trúc,
  quyết định và ưu tiên tiếp theo.
- [docs/spec/](docs/spec/): Final Pack gốc; giữ nguyên nội dung. Khi có khác
  biệt, ưu tiên quyết định mới nhất của chủ dự án theo handoff.
- [IMPLEMENTATION_REPORT_CODEX.md](IMPLEMENTATION_REPORT_CODEX.md),
  [TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md) và
  [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md): trạng thái thực hiện, bằng
  chứng kiểm thử và giới hạn chưa giải quyết.
- [AI_USAGE.md](AI_USAGE.md), [PRIVACY.md](PRIVACY.md) và
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md): AI, dữ liệu và thông báo
  quyền sử dụng.

Inventory cũ và tài liệu V4/V5 là snapshot lịch sử, không phải bản kiểm kê
hoặc hướng dẫn chạy V6 hiện hành. Dùng README và các tài liệu V6 ở trên để
thực hiện công việc mới.

## 2. Chạy và kiểm tra

Từ thư mục gốc repository, dùng Python 3.12 trở lên:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`; giữ terminal chạy và nhấn Ctrl+C để dừng.
Windows có thể dùng `py -3.12`; Linux/macOS có thể dùng `python3`. Ứng dụng
không cần Node.js, npm hoặc API key để chạy.

Để chạy bộ kiểm tra chuẩn, cài Node.js rồi chạy:

```powershell
python tools/run_checks.py
```

Runner bao gồm kiểm tra Python/JavaScript, nghiệp vụ, fixture và parity luật.
Chỉ ghi kết quả đã thực sự chạy; phạm vi và bằng chứng chi tiết nằm trong
`TEST_REPORT_CODEX.md`.

## 3. Kiến trúc hiện hành

```text
online-preview/  giao diện HTML/CSS/JavaScript
       │ HTTP cùng origin
       ▼
co_chill_server.py  server/API/CLI
       ├── app/rules.py, app/online_rooms.py
       ├── app/cloud_store.py, app/content_store.py
       └── app/pikafish.py
```

| Thành phần | Trách nhiệm |
|---|---|
| `co_chill_server.py` | Điểm khởi động local/WSGI, API và phục vụ giao diện |
| `app/rules.py` | Luật phía server; cùng frontend kiểm tra parity |
| `app/pikafish.py` | Adapter UCI; chỉ báo bằng chứng engine khi có kết quả hợp lệ |
| `app/cloud_store.py` | Tài khoản, phiên, tiến độ và SQLite |
| `app/content_store.py` | Nội dung có phiên bản |
| `app/online_rooms.py` | Trạng thái phòng, ván và đồng hồ PvP phía server |
| `online-preview/` | Bàn cờ, client API, trải nghiệm học và giao diện |
| `tests/`, `tools/` | Test, kiểm tra parity, runner và đóng gói source |

Script frontend được nạp theo thứ tự trong `online-preview/index.html`; không
di chuyển riêng một file mà chưa kiểm tra thứ tự và các guard tích hợp.

## 4. Luồng học và nguồn sự thật

Luồng mục tiêu: chơi/nhập ván → chọn điểm đáng học → reflection → giải thích
có căn cứ → retry → bài liên quan → spaced review → tiến độ.

- Luật và engine quyết định tính hợp lệ, nước đi và phân tích. Explanation
  provider không được tự tạo nước, biến hoặc đánh giá.
- Không hiện lời giải trước reflection; không hiện coaching trong live game.
- Ghi nhãn trung thực cho engine local, bài tập tổng hợp, heuristic và giải
  thích theo mẫu. Không tuyên bố ML được huấn luyện hay hiệu quả đã chứng minh.
- Dữ liệu người học không tự trở thành dữ liệu huấn luyện. Giữ chức năng xuất
  và xóa; không commit database, secret hoặc dữ liệu cá nhân.

## 5. Cấu hình và giới hạn vận hành

- SQLite local mặc định nằm trong `var/`; không đưa database hoặc backup vào
  Git/source pack.
- Engine Pikafish cần cấu hình binary/trọng số riêng; source pack không chứng
  minh engine trên Google Cloud hoạt động.
- Thiết kế hiện tại giả định một instance/process cho các tài nguyên có scope
  process. Không tăng workers/replicas nếu chưa thiết kế lại điều phối.
- Production đã được triển khai theo thông tin chủ dự án; không tự thay máy,
  DNS, dịch vụ hoặc đẩy code. Cần duyệt riêng trước khi deploy source mới.
  Tham khảo `deploy/DEPLOY_GCP_VI.md` cho quy trình đã khớp cấu hình hiện tại.

## 6. Quy trình cập nhật ghi chú

Sau thay đổi đáng kể, cập nhật tài liệu trực tiếp liên quan và ghi đúng test
đã chạy. Trước khi bàn giao, xem:

```powershell
git status --short
git diff --check
python tools/run_checks.py
```

Chỉ chạy bộ kiểm tra nếu môi trường đã cài Node.js; với thay đổi tài liệu
thuần, kiểm tra nội dung/liên kết và diff là đủ. Không tự sinh lại inventory
cũ nếu chưa có yêu cầu và chưa xác định nó phục vụ workflow V6 nào.
