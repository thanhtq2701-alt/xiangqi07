# Bằng chứng kiểm tra lại ngày 08/10/2026

Commit code được kiểm tra: e66c6c060ef71e52db3b5f944a1cad4c5ecca9b3. Đợt kiểm kê chỉ thêm tài liệu/công cụ kiểm kê, không đổi code ứng dụng hoặc tests.

- `python -m unittest discover -s tests -v`: 65/65 pass, 57.899 giây, khi chạy ngoài sandbox. Lần chạy đầu trong sandbox có 59 test pass và 6 lỗi HTTP WinError 10013 vì bị chặn socket; không bỏ/sửa test để đạt kết quả.
- GET `http://127.0.0.1:8765/`: HTTP 200 tại thời điểm kiểm tra. GET `/api/bootstrap` phản hồi thành công. Server có thể dừng sau khi terminal đóng; đây không phải đảm bảo uptime.
- `python -m py_compile tools/update_inventory.py`: pass. `git diff --check`: pass tại thời điểm kiểm tra.
- Chương trình kiểm kê đọc mọi file ngoài metadata .git trong phạm vi App cờ tướng; đọc các thành viên ZIP và XML nội dung 6 bản Word; so SHA-256, phân tích định nghĩa Python, đọc số lượng bản ghi SQLite qua kết nối read-only. Không có lỗi đọc ở lần quét.
- Hai ảnh trong Failing/10-08 đã được xem: lỗi nhập extension trình duyệt. Không thay đổi ảnh/tài liệu gốc.
- Lần này không lặp lại thao tác browser toàn flow. Bằng chứng browser trước đó nằm trong TEST_REPORT_CODEX.md; bộ test service và HTTP toàn flow đã chạy lại hôm nay.
- Bản HTML là tài liệu có thể mở bằng trình duyệt; sổ tay Markdown và manifest JSON là nguồn có thể theo dõi qua Git. Không tạo bản Word mới trong đợt này. Word V4 đã có vẫn giữ nguyên; chưa có xác minh bố cục Word bằng renderer vì môi trường trước đó thiếu LibreOffice.

Khi code đổi, chạy lại kiểm tra cần thiết và cập nhật file này. Lệnh kiểm kê không tự chạy test và không tự làm mới bằng chứng ở đây.
