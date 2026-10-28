# Chạy và demo Cờ Chill V6

## Khởi động local

Cần Python 3.12 trở lên. Từ thư mục gốc repository:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`, giữ terminal chạy và nhấn Ctrl+C để dừng. Có thể
dùng `py -3.12` trên Windows hoặc `python3` trên Linux/macOS. Không cần Node,
npm hay API key để chạy ứng dụng.

Dữ liệu SQLite mặc định được tạo trong `var/`; không commit database, backup,
log hay thông tin tài khoản. Localhost chỉ truy cập được từ máy đang chạy
server, đây không phải triển khai Internet.

## Kiểm tra

Cần Node.js 24.22.1 để chạy toàn bộ bộ kiểm tra; phiên bản chuẩn nằm trong
`.nvmrc`. App không cần Node lúc sử dụng và repo không cần npm packages.
Trên Windows, nếu `node --version` chưa ra `v24.22.1`, truyền đúng Node bằng
`--node`. Chạy từ thư mục gốc repository:

```powershell
python tools/run_checks.py --node "C:\Program Files\nodejs\node.exe"
```

Runner biên dịch cú pháp Python không tạo `.pyc`, chạy kiểm tra Python,
JavaScript, fixture và parity luật. Không thay bằng lệnh test legacy hoặc
chạy một phần test mà không nêu rõ phạm vi.

## Demo hành trình học

Mở chế độ khách → Hành trình học → chọn bài nhiều lượt → trả lời các câu hỏi
suy nghĩ và thử nước → hoàn tất chuỗi → đọc giải thích có căn cứ → thử lại →
mở bài liên quan và lịch ôn. Giữ reflection trước lời giải; không bật coaching
trong ván live.

Có thể mở thêm cửa sổ trình duyệt để thử PvP qua cùng server local. Đây chỉ là
kiểm tra local, không chứng minh khả năng hoạt động qua Internet, engine
Pikafish trên hạ tầng thật hoặc tải production.

Xem [README](README.md) để biết kiến trúc và lệnh đóng gói,
[TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md) để biết phạm vi/kết quả đã ghi,
và [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) để biết các giới hạn hiện tại.
