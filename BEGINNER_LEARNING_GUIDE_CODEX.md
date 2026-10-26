# Hướng dẫn đọc code Cờ Chill V6

Bắt đầu bằng cách chạy ứng dụng và theo một luồng học qua frontend, API,
nghiệp vụ và lưu trữ. Tài liệu này mô tả source V6 hiện tại; xem
[README](README.md), [handoff](docs/CLAUDE_HANDOFF_V6.md) và
[giới hạn](KNOWN_LIMITATIONS.md) để biết trạng thái/bằng chứng mới nhất.

## Năm khái niệm quan trọng

1. **Luật khác đánh giá.** `app/rules.py` quyết định nước hợp lệ. Engine phân
   tích vị trí dựa trên nước hợp lệ; điểm tìm kiếm không phải chân lý chiến
   lược tuyệt đối.
2. **Backend giữ trạng thái có thẩm quyền.** Tài khoản, tiến độ và phòng PvP
   không được coi dữ liệu client gửi lên là sự thật đã xác minh.
3. **Reflection trước lời giải.** Luồng học phải ghi nhận người học đã suy
   nghĩ trước khi tiết lộ lời giải; không coaching trong ván live.
4. **Persistence và quyền riêng tư.** `app/cloud_store.py` xử lý tài khoản/
   trạng thái; SQLite local nằm trong `var/`. Không đưa database hay dữ liệu
   reflection vào Git.
5. **Test chỉ chứng minh phạm vi đã chạy.** Bộ kiểm tra không xác nhận engine
   production, chất lượng sư phạm, sức cờ hoặc trải nghiệm trên Internet.

## Theo một request

Mở ứng dụng bằng `python co_chill_server.py serve --port 8769`, rồi dùng
DevTools Network để theo HTTP request cùng origin. Đọc
`online-preview/index.html` để xem thứ tự nạp script, các client trong
`online-preview/` để hiểu request, `co_chill_server.py` để theo route/API,
rồi vào module `app/` tương ứng để kiểm tra luật, nghiệp vụ và persistence.

Không chuyển logic quyền truy cập hoặc luật sang client chỉ để đơn giản hóa UI.
Engine/rules quyết định nước và phân tích; lời giải chỉ được gửi sau reflection.

## Đọc theo thứ tự

1. `README.md`, `RUN_AND_DEMO_CODEX.md`: khởi động và demo.
2. `KNOWN_LIMITATIONS.md`, `TEST_REPORT_CODEX.md`: phạm vi chưa hoàn thành và
   bằng chứng kiểm tra.
3. `tests/test_rules.py`, `app/rules.py`: luật và vị trí.
4. `tests/test_online_rooms.py`, `app/online_rooms.py`: luồng PvP phía server.
5. `tests/test_cloud.py`, `app/cloud_store.py`: tài khoản, lưu trữ và quyền.
6. `online-preview/index.html`, các script UI/client theo thứ tự nạp, rồi
   route tương ứng trong `co_chill_server.py`.

Chạy đầy đủ kiểm tra bằng `python tools/run_checks.py` từ thư mục gốc; cần
Python 3.12 trở lên và Node.js. Không dùng lệnh test từ snapshot V4/V5 thay
runner này.

## Lỗi thường gặp

- Nhầm nước hợp lệ với nước tốt: kiểm tra luật trước khi diễn giải điểm engine.
- Tiết lộ đáp án từ client: reflection gate phải được kiểm soát bởi luồng
  nghiệp vụ/API, không chỉ ẩn nút trên giao diện.
- Tin dữ liệu trạng thái từ client trong PvP: đối chiếu revision/game state
  ở server.
- Chạy ở cổng khác nhưng mở URL cũ: dùng đúng hostname và cổng server.
- Sửa code nhưng quên restart: server local không tự reload; dừng bằng Ctrl+C
  rồi chạy lại lệnh khởi động.
