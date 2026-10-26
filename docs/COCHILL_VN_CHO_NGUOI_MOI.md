# Hướng dẫn cochill.vn — trạng thái V6

Tài liệu triển khai V5 trước đây đã lỗi thời; không dùng các hướng dẫn hosting,
DNS hoặc lệnh cũ trong bản lưu lịch sử. Source hiện hành là V6, chạy local bằng:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`. Cần Python 3.12 trở lên. Để chạy bộ kiểm tra
source, cài Node.js rồi chạy từ thư mục gốc:

```powershell
python tools/run_checks.py
```

Hiện chưa xác nhận V6 đã được triển khai lên cochill.vn hoặc hạ tầng Google
Cloud. Không thực hiện deploy, đổi DNS, phát sinh chi phí hay push khi chưa
được chủ dự án chấp thuận.

Tham khảo tài liệu hiện hành:

- [README V6](../README.md): khởi động, kiến trúc và source pack.
- [Hướng dẫn GitHub V6](GITHUB_V6_CHO_NGUOI_MOI.md): cập nhật source an toàn.
- [Chuẩn bị Google Cloud V6](DEPLOY_GCP_V6.md): các bước chuẩn bị/kiểm tra
  triển khai; không phải bằng chứng đã deploy hoặc phê duyệt chi phí.
- [Giới hạn hiện tại](../KNOWN_LIMITATIONS.md): những gì chưa được xác minh.
