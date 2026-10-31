# Hướng dẫn cochill.vn — Production và local

Website Production `https://cochill.vn` hiện đang chạy theo cấu hình GCP do chủ
dự án cung cấp. Tài liệu cài đặt/cập nhật server mới nhất là
[hướng dẫn deploy GCP](../deploy/DEPLOY_GCP_VI.md). Không dùng tài liệu hosting
V5 hoặc mẫu chuẩn bị cũ để thay cấu hình Production.

Để chạy source trên máy cá nhân:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`. Cần Python 3.12 trở lên. Để chạy bộ kiểm tra
source, cài Node.js rồi chạy từ thư mục gốc:

```powershell
python tools/run_checks.py
```

Thông tin VM và deploy trong repo được ghi theo xác nhận của chủ dự án, không
phải bằng chứng kiểm tra trực tiếp từ GCP. Pikafish/NNUE Production, khả năng
chịu tải và kết quả khôi phục backup chưa được xác minh độc lập. Không deploy,
đổi DNS, phát sinh chi phí hay push khi chưa được chủ dự án chấp thuận.

Tham khảo tài liệu hiện hành:

- [README V6](../README.md): khởi động, kiến trúc và source pack.
- [Hướng dẫn GitHub V6](GITHUB_V6_CHO_NGUOI_MOI.md): cập nhật source an toàn.
- [Deploy GCP Production](../deploy/DEPLOY_GCP_VI.md): systemd, Nginx,
  cập nhật code, log, backup/restore và TOTP.
- [Ghi chú GCP V6 cũ](DEPLOY_GCP_V6.md): bối cảnh lịch sử, không dùng thay
  hướng dẫn Production hiện hành.
- [Giới hạn hiện tại](../KNOWN_LIMITATIONS.md): những gì chưa được xác minh.
