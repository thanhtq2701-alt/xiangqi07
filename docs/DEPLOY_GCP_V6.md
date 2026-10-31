# GCP V6 — ghi chú chuẩn bị cũ

Tài liệu ngày 26/10/2026 là bản chuẩn bị trước khi Production được triển
khai. Các đường dẫn, port, lệnh Gunicorn và bước DNS của bản cũ không mô tả
Production hiện tại; không dùng tài liệu này để thay cấu hình VM.

Theo thông tin chủ dự án ngày 31/10/2026, `cochill.vn` đã chạy trên GCP VM
Ubuntu 24.04, source ở `/var/www/html`, Python 3.12 trong `.venv`, systemd
`cochill.service` với `serve --host 127.0.0.1 --port 8000`, Nginx HTTPS và
SQLite trên đĩa bền. Production dùng một process; trạng thái phòng và
semaphore Pikafish không được thiết kế cho nhiều worker/replica.

Để cập nhật code, xem log, sao lưu/khôi phục, gia hạn chứng chỉ, quản lý TOTP
và chuyển Gunicorn tùy chọn, dùng
[hướng dẫn Production hiện hành](../deploy/DEPLOY_GCP_VI.md). Thông tin này
dựa trên xác nhận của chủ dự án; chưa kiểm tra trực tiếp VM, chứng chỉ, backup
thực tế hoặc binary Pikafish/NNUE.
