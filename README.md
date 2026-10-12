# Cờ Chill AI

Ứng dụng học cờ tướng tiếng Việt chạy cục bộ: chơi hoặc nhập ván → tìm điểm cần xem lại → tự suy nghĩ → lời giải có căn cứ → thử lại → bài liên quan → lịch ôn → tiến bộ.

## Chạy ngay trên Windows

**Cách dễ nhất:** nhấp đúp `Mo_Co_Chill.cmd` trong thư mục dự án. File này bật server nền rồi mở trình duyệt; nếu server đã chạy thì dùng lại. Có thể đóng ChatGPT mà server vẫn chạy độc lập khi bạn khởi động bằng file này. Sau khi khởi động lại Windows, bấm file lần nữa. Không cần mở ChatGPT. Có thể tạo shortcut của file ra Desktop bằng chuột phải → Send to → Desktop.

Địa chỉ `127.0.0.1` là máy của bạn, không phải hosting online. Việc mở lại tab không tự bật Python. Nếu mở bằng trình duyệt khác, phiên khách có thể khác: hãy dùng cùng trình duyệt và giữ cookie để tiếp tục tiến độ. Muốn dùng tab trong ChatGPT, chạy file rồi tải lại `http://127.0.0.1:8765/` ở tab đó.

Launcher không tự cài vào Windows Startup, không dừng ứng dụng đang chiếm cổng và không sửa dữ liệu học. Log khởi động nằm trong `var/server-output.log`, `var/server-error.log` (không commit). Để dừng server nền, dùng Task Manager, xác định tiến trình Python có dòng lệnh `server.py --port 8765`, rồi End task. Cách terminal bên dưới phù hợp khi cần xem lỗi hoặc dừng bằng Ctrl+C.

Yêu cầu Python 3.10 trở lên. Đã kiểm tra với Python 3.14. Không cần cài package, npm, API key hoặc tài khoản cloud.

```powershell
cd "E:\ThanhTQ\App cờ tướng\xiangqi-ai"
python server.py --port 8765
```

Mở **http://127.0.0.1:8765/**. Giữ cửa sổ terminal đang chạy. Dừng bằng Ctrl+C. Có thể dùng `py server.py --port 8765` nếu máy dùng Python Launcher.

## Demo một phút

1. Bấm **Thử hành trình 60 giây** → **Bắt đầu xem lại**.
2. Trả lời 3 câu theo suy nghĩ của bạn; có thể viết “Chưa biết”.
3. Bấm **Lưu suy nghĩ & xem phân tích**. Đọc WHAT, WHY, HOW.
4. Bấm **Tôi đã hiểu · thử lại**. Chọn Xe Đỏ **a2 → a7**.
5. Bấm **Luyện một thế cờ liên quan**. Ở phiên mới, bài tiếp là Xe **h2 → h7**. Trả lời suy nghĩ trước khi đi; hệ thống ưu tiên bài chưa gặp nên bài có thể thay đổi ở lần sau.
6. Mở **Tiến bộ của tôi**. Lần thử và lịch ôn được lưu qua lần tải lại trang.

## Thực sự có gì

- Cập nhật 09/10: tự lưu nháp suy nghĩ, tiếp tục bài đang dở, khôi phục bài/ván khi reload, chữ quân tiếng Việt tùy chọn và bàn phím mũi tên/Enter/Esc. Nháp chưa mở đáp án hoặc tính điểm. Đợi thông báo đã lưu trước khi đóng trang.
- [Báo cáo khảo sát website và cải tiến](RESEARCH_AND_IMPROVEMENTS_2026_10_09.md): nguồn tham khảo, việc đã làm, 72 test và giới hạn còn lại.

- Luật cả 7 quân, cản chân Mã, cản mắt Tượng, ngòi Pháo, cung, sông, lộ Tướng; chiếu hết và hết nước là thua.
- Máy cục bộ, hai người cùng máy; lưu biên bản, nhập FEN và nước tọa độ.
- Xem tối đa 24 nước Đỏ gần nhất, chọn tối đa 3 điểm đáng học; không gán mọi ván là có sai lầm.
- Khóa lời giải trên server trước suy nghĩ; lời giải mẫu từ biến hợp lệ; thử lại và góp ý cục bộ.
- 12 bài tổng hợp, 4 kỹ năng; ưu tiên nhóm bài chưa gặp; ghi nhận lần đầu để không tăng điểm bằng thử lặp.
- SQLite, phiên khách tách biệt, xuất JSON, xóa dữ liệu phiên, dashboard và lịch ôn theo quy tắc.

## Giới hạn phải biết

Đây là prototype local, **chưa phải web công khai**. Engine tự viết chỉ tìm tối đa 2 nửa nước; chưa tích hợp Pikafish. Lời giải là template, **không có LLM hay mô hình ML được huấn luyện**. Bài tổng hợp chưa được chủ dự án/chuyên gia duyệt. Lặp thế 3 lần là quy ước demo, chưa có phán quyết chiếu dai/đuổi dai theo luật giải đấu. Chưa có OAuth, PvP qua mạng, đồng hồ, placement test hoặc đánh giá chất lượng lập luận tự động.

## Kiểm tra

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app server.py tests
node --check web/app.js
```

HTTP tests mở server tạm trên loopback. Nếu chạy trong sandbox chặn socket, cần quyền chạy test bên ngoài sandbox; người dùng chạy PowerShell thông thường không cần cấu hình đặc biệt này. Không có bước build/bundler hoặc typecheck TypeScript vì frontend dùng JavaScript thuần.

## Cấu trúc và tài liệu

- [Word bổ sung V4 về UI UX kiến trúc và luật](deliverables/Co_Chill_V4_Bo_sung_UI_UX_Kien_truc_Luat.docx): 272 câu riêng để trả lời cùng V4 cũ, kèm mẫu bản vẽ, API và case luật.

- [Sổ tay hiện trạng toàn dự án](PROJECT_MEMORY_VI.md), [danh mục từng file](PROJECT_INVENTORY_VI.md), [bản HTML tổng hợp dễ đọc](deliverables/Co_Chill_So_tay_hien_trang.html).
- Cập nhật kiểm kê toàn thư mục **App cờ tướng** bằng `python tools/update_inventory.py`; cập nhật diễn giải trong `PROJECT_MEMORY_VI.md` khi tính năng thay đổi. Snapshot ghi commit nền tại lúc quét; xem hướng dẫn commit trong sổ tay.

- `app/rules.py`: luật và FEN; `engine.py`: search adapter; `learning.py`: lời giải và lịch ôn.
- `app/service.py`: hành trình học; `storage.py`: SQLite; `puzzles.py`: fixture tổng hợp.
- `server.py`: HTTP local; `web/`: giao diện; `tests/`: unit, service và HTTP.
- `docs/spec/`: bản gốc Final Pack, không sửa.
- [Báo cáo triển khai](IMPLEMENTATION_REPORT_CODEX.md), [chạy và demo](RUN_AND_DEMO_CODEX.md), [kết quả test](TEST_REPORT_CODEX.md), [hướng dẫn học code](BEGINNER_LEARNING_GUIDE_CODEX.md).
- [AI usage](AI_USAGE.md), [giới hạn](KNOWN_LIMITATIONS.md), [riêng tư](PRIVACY.md), [nguồn](THIRD_PARTY_NOTICES.md).

Dữ liệu nằm ở `var/chill.sqlite3`, không commit. Cookie trình duyệt là khóa phiên khách; không có khôi phục tài khoản sau khi xóa cookie. Không tự động chia sẻ hoặc dùng dữ liệu làm tập huấn luyện. Tác giả ý tưởng: Trần Quốc Thanh. Implementation có hỗ trợ Codex; chưa có thử nghiệm hiệu quả học tập với người dùng thật.
