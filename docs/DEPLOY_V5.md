# Hướng dẫn triển khai V5 — tài liệu lịch sử

Các bước hosting trong tài liệu V5 này không áp dụng cho source hiện hành và
không nên dùng để triển khai. Entry point V6 là `co_chill_server.py`; hướng
dẫn chuẩn bị hiện hành ở [DEPLOY_GCP_V6.md](DEPLOY_GCP_V6.md).

Để chạy V6 trên máy local:

```powershell
python co_chill_server.py serve --port 8769
```

Để kiểm tra source từ thư mục gốc repository, cần Node.js:

```powershell
python tools/run_checks.py
```

Việc chuẩn bị hướng dẫn không xác nhận hạ tầng thật, DNS, HTTPS, database,
Pikafish/NNUE hoặc khả năng production. Không deploy, đổi DNS, phát sinh chi
phí hay push khi chưa được chủ dự án chấp thuận.
