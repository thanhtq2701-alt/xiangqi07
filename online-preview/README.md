# Giao diện Cờ Chill V6

Đây là frontend đang được phục vụ bởi `co_chill_server.py` cùng API cùng
origin. Không mở `index.html` bằng `file://` để kiểm tra đăng nhập, đồng bộ
hoặc PvP.

Từ thư mục gốc repository, khởi động server:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`. Giữ terminal chạy; Ctrl+C để dừng. Python 3.12
trở lên. Node.js không cần để chạy ứng dụng.

Để kiểm tra frontend cùng backend, chạy từ thư mục gốc:

```powershell
python tools/run_checks.py
```

Cần Node.js để chạy toàn bộ bộ kiểm tra. Runner kiểm tra cú pháp JavaScript,
test client, fixture và parity luật; kết quả/bằng chứng cụ thể ở
`TEST_REPORT_CODEX.md`.

Các script được nạp theo thứ tự trong `index.html`; adapter UI dùng state và
guard của ứng dụng, vì vậy cần kiểm tra tích hợp khi thay đổi thứ tự hoặc tách
file. Luật/engine là nguồn sự thật cho nước đi và phân tích. Giữ reflection
trước lời giải và không hiển thị coaching trong ván live.

Xem [README gốc](../README.md), [hướng dẫn chạy/demo](../RUN_AND_DEMO_CODEX.md)
và [giới hạn](../KNOWN_LIMITATIONS.md) để biết cách dùng hiện hành.
