# Cờ Chill bản thử V4 ngày 15 tháng 10 năm 2026

Bản mới đã xuất bản công khai tại https://co-chill-ngay-mai.cosmicanole32.chatgpt.site/#home.
Đây là prototype triển khai các quyết định đã chốt từ V4 và bản phác giao diện, không phải toàn bộ sản phẩm V4 đã hoàn thiện.
Người dùng tiếp tục hoàn thiện UI/UX + Luật và BS01–BS08 theo ý định sản phẩm; không cần sửa yêu cầu để khớp giới hạn demo.

## Đã xây và chạy được

- Trang chủ logo trái, hồ sơ phải, bốn cửa Chơi / Bài học / Lỗi của tôi / Ôn tập. Bố cục đáp ứng điện thoại.
- Luật bảy quân chạy trong trình duyệt; kiểm tra FEN, an toàn Tướng, chiếu hết và hết nước.
- Chơi với máy tìm kiếm vật chất tối đa hai nửa nước, hoặc hai người cùng máy. Chọn màu và thời gian; không gợi ý trong ván.
- Nhập FEN và chuỗi nước tọa độ, kiểm tra toàn bộ trước khi lưu. Giới hạn 200 nửa nước.
- Lưu ván, xem tiến/lùi và chọn tối đa ba điểm cần học từ tối đa 16 lượt gần nhất được tìm kiếm nông.
- Ba câu phản hồi và nước ứng viên trước lời giải; lựa chọn “Tôi chưa biết” được đánh dấu có hỗ trợ.
- Giải thích WHAT / WHY / HOW bằng mẫu có căn cứ luật hoặc dòng tìm kiếm hợp lệ. Mũi tên chỉ mở sau phản hồi.
- Thử lại tùy chọn, chuyển sang hình cùng kỹ năng, ưu tiên hình chưa gặp; trung thực khi kho bài đã xem hết.
- “Để lần sau” giữ đúng bước chuyển bài; lưu câu trả lời và nước đã chọn. Tiếp tục cùng trình duyệt sau tải lại.
- Lịch ôn mỗi hình tính từ lúc hoàn thành. Quy tắc 1 / 2 / 7 / 14 / 30 ngày, không tối ưu bằng ML.
- Cuối phiên có ô tự đánh giá và ghi chú, tách biệt kết quả nước đi; không tự tăng trình độ.
- 12 thế tổng hợp gốc, bốn kỹ năng; bốn minh họa nước khai cuộc, phân biệt đã xem với đã hiểu.
- Hồ sơ, tiến độ thực tế, xuất JSON và xóa dữ liệu trong trình duyệt.

## Kiến trúc và file thay đổi

Website tĩnh HTML/CSS/JavaScript. Tính toán chạy ở trình duyệt, lưu bằng localStorage.
Ứng dụng Python/SQLite trong server.py không bị thay thế và không được đóng gói vào Site.

- online-preview/index.html, style.css, app.js: giao diện và điều phối luồng.
- online-preview/xiangqi.js: port luật từ app/rules.py và tìm kiếm vật chất có giới hạn.
- online-preview/learning.js: phản hồi, phiên học, lịch ôn, đề xuất, chuẩn hóa dữ liệu.
- online-preview/fixtures.js: xuất 12 bài từ app/puzzles.py, không lấy nguồn thương mại.
- online-preview/favicon.svg, README.md: biểu tượng chữ quân và tài liệu.
- tools/check_browser_rules.py, test_preview_learning.cjs, export_preview_fixtures.py, check_online_preview.py: xuất và kiểm chứng.

## Kiểm thử ngày 15 tháng 10

- Node --check app.js: PASS. Các module rules/fixtures đã kiểm tra cú pháp.
- node tools/test_preview_learning.cjs: 19/19 PASS, gồm khóa lời giải, trợ giúp, hoàn thành không lặp, mốc hẹn ôn, resume và dữ liệu hỏng.
- python tools/check_online_preview.py: 12/12 bài, tập nước hợp lệ, nội dung xuất và nguồn gốc khớp Python.
- python tools/check_browser_rules.py: PASS 205 thế, 5.468 thế con, 25 trường hợp FEN, 10 nhóm đầu vào sai, perft độ sâu 2 = 1.920. Engine khớp 153 dòng ở 12 bài.
- python -m unittest discover -s tests -v: 72/72 PASS, 61,081 giây khi chạy ngoài sandbox. Lượt đầu các test HTTP bị sandbox chặn socket; không sửa hay bỏ test, chạy lại đầy đủ với quyền mạng localhost.
- Trình duyệt: chặn lời giải khi thiếu phản hồi; nhập ba câu và nước, tải lại vẫn giữ; mở lời giải; chuyển hình liên quan; để lần sau; tải lại và tiếp tục đúng bước; ghi tự đánh giá; hồ sơ có hai hình hoàn thành và không tính lượt được trợ giúp là tự giải độc lập.
- Trình duyệt: chơi với máy và máy trả nước; dừng ván, tạo điểm review, mở lời giải từ ván; từ chối FEN sai và nhập chuỗi hợp lệ.
- Viewport 390 px không tràn ngang ở trang chủ và màn nhập/review được kiểm tra. Không tuyên bố kiểm định toàn bộ khả năng tiếp cận.
- Link công khai mở đúng giao diện mới. Không phát hiện lỗi JavaScript trong các luồng đã thử.
- git diff --check: PASS (chỉ cảnh báo chuyển LF/CRLF).

Không có bước build, TypeScript hoặc trình lint riêng vì đây là website JavaScript thuần, không cài dependency mới.

## Thật và giới hạn

Engine: local, vật chất và Tốt qua sông, tối đa hai nửa nước. Không Pikafish, không Elo, không đủ cơ sở kết luận mọi lỗi chiến lược. Nhãn kỹ năng là heuristic. Tìm kiếm không hoàn tất không được báo giả độ sâu.

LLM: chưa tích hợp. Câu trả lời tự do được lưu để đối chiếu, chưa được chấm hiểu biết tự động. Lời giải là template, không để AI tự bịa nước hoặc biến.

Dữ liệu: 12 thế tự dựng gốc; không scrape, không dùng bộ dữ liệu thương mại, không thu ván/câu trả lời để train. Chưa có chuyên gia kiểm định sư phạm và chưa có dữ liệu chứng minh hiệu quả. Font hệ thống; không mang ảnh Ziga hoặc ảnh tham khảo của chủ sở hữu lên website.

Lưu trữ: trên đúng trình duyệt và origin. Không tài khoản, không đồng bộ thiết bị, không backend dữ liệu chung. Không tự di chuyển dấu hoàn thành của bản hai bài cũ sang bản mới vì tiêu chí hoàn thành đã đổi. File JSON xuất là bản sao, chưa có giao diện nhập khôi phục JSON. Đáp án có trong bundle tĩnh, khóa lời giải là UX chứ không phải bảo mật phía server.

Chưa có: PvP online, phòng bạn bè/chat, engine mạnh, LLM chấm lập luận, ML đã huấn luyện, kho bài lớn, giáo trình đầy đủ, email/thông báo đẩy, kéo thả quân, ký pháp truyền thống đầy đủ, lật bàn theo màu cầm quân, tự lưu ghi chú cuối phiên trước khi nhấn Lưu, thu phản hồi về trang quản trị.

Luật: xử lý lặp vị trí ba lần theo quy tắc demo; chưa phân xử chiếu dai/đuổi dai theo luật giải đấu. Tàn cuộc có mục tiêu ngắn, chưa buộc chơi đến hết. Khai cuộc chỉ bốn nước minh họa, không phải thư viện biến.

## Xuất bản và quyền đã dùng

Chủ sở hữu yêu cầu cập nhật ChatGPT Site công khai hiện có. Giữ nguyên audience public và URL; không đổi quyền GitHub, không tạo dịch vụ trả phí, không triển khai Vercel.
Đã xin quyền công cụ cho kết nối kho Sites, máy chủ preview localhost và test socket. Plugin Sites đổi thư mục phiên bản trong lúc làm; đã chuyển sang helper được cài hiện tại.

- Site: appgprj_6acd061322c08191a4c912862bc05124
- Source commit của kho Sites: 4f8dded4726ac4ec39451e54f612aa06f944b1b9
- Saved version 2: appgprj_6acd061322c08191a4c912862bc05124~appgver_06c9c313a75c81919693f4cf9d78844d
- Deployment: appgdep_6ad084e894288191ae3e5c5e9bb42095 — succeeded
- Chỉ bảy asset web và hosting manifest được đóng gói; không có V4.docx, bản phác, SQLite, thông tin người học hoặc token.

## Chạy lại và demo

Từ thư mục repository:

```powershell
python -m http.server 8768 --bind 127.0.0.1 --directory online-preview
```

Mở http://127.0.0.1:8768/#home. Ứng dụng Python đầy đủ cũ vẫn chạy bằng `python server.py --port 8765`.

Demo 60 giây: trang chủ → Thử một bài → ba ý ngắn và nước Xe a2-a7 → xem giải thích → hoàn thành và chuyển bài liên quan → Để lần sau → Tiếp tục → hồ sơ/ôn tập. Có thể chọn “Tôi chưa biết” để trình diễn nhánh được hỗ trợ; không trình bày đó là thành tích tự giải.

Năm khái niệm nên học: state machine của phiên học; rules engine so với explanation provider; localStorage so với database server; kiểm thử đối chiếu hai implementation; deployment theo phiên bản và phân biệt source commit của Sites với GitHub.

## Việc chủ sở hữu làm tiếp

Hoàn thiện UI/UX + Luật và BS01–BS08. Ghi mong muốn sản phẩm độc lập với giới hạn demo. Dùng link này thử thực tế và ghi màn nào, thao tác nào, kỳ vọng và kết quả. Sau khi chốt, chọn kiến trúc backend/lưu trữ phù hợp để triển khai Vercel; việc đó cần một lượt triển khai riêng được duyệt.
