# Khảo sát website cờ tướng và cải tiến trong lúc chờ V4

Ngày thực hiện: 09/10/2026, Asia/Bangkok. Chủ dự án tiếp tục trả lời hai file V4. Đợt này dùng yêu cầu V3 đã chốt, code hiện có và tài liệu công khai; không giả định câu trả lời mới của chủ dự án.

## Kết quả chính

Đã khảo sát 14 địa chỉ/dịch vụ, đọc được nguồn chính thức của 11 và ghi nhận 3 nơi chưa truy cập thành công. Quan sát trực tiếp giao diện 3 trang: Xiangqi.com, ChessDB, Việt Cờ Tướng. Đây là khảo sát có phạm vi và bằng chứng, không phải tuyên bố đã biết mọi website cờ tướng trên Internet, đã dùng mọi tính năng hoặc đã kiểm chứng chất lượng engine của họ.

Đã cải tiến prototype: tự lưu bản nháp reflection, phục hồi khi mở lại/tải lại sau lưu, tiếp tục bài đang dở, tên quân tiếng Việt tùy chọn, di chuyển bàn cờ bằng bàn phím, cải thiện độ đọc và responsive, trạng thái chờ có thời gian thực, thông báo lỗi kết nối và nút kết nối lại. Không thay luật cờ, engine, thuật toán điểm/lịch, thương hiệu đã chốt hoặc lấy dữ liệu bài tập từ website khác.

## Phương pháp và giới hạn bằng chứng

- Chỉ đọc trang công khai, tài liệu tính năng và xem giao diện. Không tạo tài khoản, đánh ván với người thật, gửi dữ liệu riêng, mua dịch vụ hoặc tải ngân hàng ván/bài.
- “Nguồn mô tả” là điều website tự công bố, chưa thử chức năng đó. “Quan sát UI” chỉ xác nhận các thành phần nhìn thấy tại lúc xem.
- Không suy ra stack backend của một dịch vụ từ giao diện. Không xác nhận Elo engine, độ chính xác AI, lượt người dùng, quy mô kho hoặc hiệu quả học từ lời quảng bá.
- Ghi nhận tính năng của đối thủ để rút ra nguyên tắc; không sao chép code, hình quân, hình nền, bài học hoặc giao diện nguyên bản.
- Không lấy quy tắc lặp/chiếu/đuổi từ một trang chơi để tự thay luật dự án. Các trang có thể áp dụng quy ước riêng; cần bộ luật và case do chủ dự án xác nhận.

## Danh sách khảo sát có nguồn

| Website và nguồn trực tiếp | Bằng chứng thu được | Bài học cho Cờ Chill |
| --- | --- | --- |
| [Xiangqi.com](https://play.xiangqi.com/) và [Resources](https://www.xiangqi.com/resources) | Quan sát UI: sidebar Play/Puzzles/Learn/Social, lựa chọn chơi người/máy, bài tập, bài học, xem ván. Trang resources có board editor và tài nguyên học. Có quảng cáo trong phiên xem. | Lối vào theo tác vụ rõ. Cờ Chill nên ưu tiên việc đang học, giữ quảng cáo ngoài vòng học local. Không chứng minh họ thiếu reflection chỉ vì không thấy ở trang chủ. |
| [Club Xiangqi](https://www.clubxiangqi.com/) | Nguồn chính thức có Guest, đăng nhập, hướng dẫn, luật, records và bảng điểm; mô tả chơi, chat và xem ván. Chưa vào phòng chơi. | Giảm rào cản bắt đầu bằng khách. Tách nhu cầu chơi cộng đồng khỏi mục tiêu sửa lỗi tư duy. |
| [PlayStrategy Xiangqi](https://playstrategy.org/variant/xiangqi) | Trang luật và menu có game library, puzzle themes/dashboard, analysis, board editor và study. Tài liệu nêu giới hạn phần chasing. Chưa thử toàn bộ công cụ cho biến thể Xiangqi. | Phân biệt chơi, nghiên cứu và học. Gắn nhãn giới hạn luật cụ thể; không suy diễn app mình đã có study chỉ vì có board. |
| [PyChess Xiangqi](https://www.pychess.org/variants/xiangqi) | Trang chính thức giải thích bàn/quân, có menu study, analysis, editor và import; dùng ví dụ bộ quân quốc tế trong phần hướng dẫn. | Nhãn quân dễ hiểu giúp tiếp cận. Cờ Chill thêm tên tiếng Việt tùy chọn, giữ chữ Hán cho người quen. |
| [ChessDB](https://www.chessdb.cn/query_en/) | Quan sát UI bàn bên trái, nước/điểm ở giữa, history bên phải; có input/copy FEN, flip, bên đi và link API docs. Không gọi API để nhập ván riêng. | Công cụ phân tích có mật độ cao hữu ích cho người biết cờ. Với người mới nên giảm nhiễu và chỉ mở lời giải sau reflection. |
| [Sachess Help](https://sachess.com/xiangqi-help/) | Trang trợ giúp tự mô tả Pikafish trong browser, review, photo-to-FEN, cloud book, tùy chỉnh bàn, dữ liệu local và tài khoản tùy chọn. Chưa benchmark/kiểm chứng các luồng. | Chuyển tiếp từ một công cụ sang công cụ tiếp theo nên giữ ngữ cảnh. Chưa thêm OCR/3D/cloud vì chưa phải nút thắt của prototype. |
| [Learn Xiangqi About](https://learnxiangqi.com/about) | Trang giới thiệu mô tả engine/coach chạy tại thiết bị và chức năng Analyze dùng dịch vụ ngoài. Nội dung có mô tả trải nghiệm không login và tài khoản tùy chọn; cần kiểm tra từng luồng nếu chọn làm chuẩn. | Công bố ranh giới local và dịch vụ ngoài rõ. Coaching trong ván của họ không được bê sang dự án vì V3 yêu cầu chơi trước, học sau. |
| [Việt Cờ Tướng](https://vietcotuong.com/) | Quan sát UI chia thư viện theo giai đoạn, nút online/offline, theme, ngôn ngữ, feedback và cài đặt bàn. Không xác minh quy mô kho ván quảng bá. | Tách tài nguyên theo mục đích và cho tùy chỉnh bàn ở chỗ dễ tìm. Chưa thêm kho lớn hoặc nhiều lựa chọn theme khi chưa chốt V4. |
| [Kỳ Vương](https://kyvuong.mobi/gioi-thieu/) | Nguồn giới thiệu nêu chơi cờ tướng/cờ úp, cờ chớp, tái đấu, xem/luận ván và hệ thống điểm. Chưa tạo tài khoản hoặc thử lobby. | Các hành động chơi cần phân biệt rõ; Elo/PvP không phải ưu tiên của vòng học hiện tại. Không áp dụng cờ úp vào rules tiêu chuẩn. |
| [XiangqiAI](https://xiangqiai.com/) | Trang công khai mô tả dùng Pikafish để nghiên cứu thế, xem ứng viên, chơi AI và review; báo lần đầu tải engine. Chưa đo tốc độ hoặc sức mạnh. | Loading engine cần giải thích nhiệm vụ thật; không hiển thị tiến độ giả. Cờ Chill thêm thời gian chờ đã trôi qua, không giả vờ có engine tải ngoài. |
| [Dpxq](https://www.dpxq.com/) | Trang công khai có kho kỳ phổ, bàn động, giải đấu và nhóm tra theo kỳ thủ/khai cuộc/giải. Không tải nội dung kho. | Metadata nguồn và cấu trúc tìm ván là việc đáng làm khi có dữ liệu được phép sử dụng. Kho tham khảo không mặc nhiên là dataset được cấp quyền. |

Chưa xác minh được: `https://lixiangqi.com/`, `https://www.xqbase.com/`, `https://www.xqinenglish.com/` trả lỗi truy cập/timeout qua công cụ tại lần này. Không kết luận các website ngừng hoạt động và không gán tính năng từ bài viết thứ cấp. Các kết quả tìm kiếm không đúng tên miền cờ tướng đã bị loại bỏ.

## Kết luận thiết kế của tôi

Đây là nhận định cho dự án, không phải số liệu nghiên cứu người dùng: giao diện cờ thường đặt bàn cờ gần công cụ và phân chia theo hành động. Cờ Chill cần kết hợp điều đó với một ưu tiên riêng đã có trong V3: quay lại đúng điểm học và suy nghĩ trước đáp án. Nút “Tiếp tục suy nghĩ” và nháp được bảo toàn có giá trị trực tiếp hơn thêm một trang trang trí hoặc nhiều chế độ chơi.

Không có đủ bằng chứng để gọi vòng học này là độc nhất trên thị trường. Cũng chưa đủ để chọn mẫu thiết kế đẹp nhất thay chủ dự án. Đợt này giữ hướng màu đang có, chỉnh độ rõ/hierarchy và luồng bị đứt; bản thiết kế mới hoàn chỉnh chờ V4.

## Những gì đã thực hiện trong code

| Thay đổi | Hành vi mới | File chính |
| --- | --- | --- |
| Nháp reflection | Tự lưu sau khoảng 600 ms ngừng nhập, nút lưu ngay, thông báo trạng thái; lưu SQLite theo đúng guest và exercise. | web/app.js, app/service.py |
| Khóa sư phạm | Nháp chưa phải reflection đã gửi; không mở đáp án, không ghi attempt/điểm. Autosave đến muộn không ghi đè câu đã gửi. | app/service.py, tests/test_learning.py |
| Tiếp tục bài | Trang chủ/dashboard hiện tối đa 8 bài chưa xong với bước cần tiếp tục. Chọn bài tải lại đúng dữ liệu server. | app/service.py, web/app.js |
| Phục hồi sau reload | Hash định danh bài/ván giữ màn hiện tại; server vẫn kiểm tra owner. Hash không chứa câu trả lời. Không triển khai router/back-forward đầy đủ. | web/app.js |
| Bàn cờ dễ tiếp cận | Chữ Hán hoặc tên tiếng Việt, nhớ tùy chọn trên trình duyệt; quân ở chế độ chỉ xem không bị giảm opacity. | web/app.js, web/style.css |
| Bàn phím | Một điểm Tab vào bàn; mũi tên theo vị trí nhìn thấy, Home/End theo hàng, Enter chọn/đi, Escape bỏ chọn. | web/app.js |
| Độ đọc và mobile | Chữ phụ rõ hơn, hero gọn, phân cấp hành động, ô nhập 16 px, thanh bước học 2 cột, metric xếp dọc trên màn hẹp; cài đặt khách hiện trên mobile. | web/style.css |
| Chờ và kết nối | Hiện số giây đã trôi qua, khóa thao tác nền khi xử lý, timeout 75 giây; startup lỗi có nút kết nối lại và lệnh chạy server. Không tự retry nước/attempt. | web/app.js, web/index.html |
| API đầu vào | Thiếu/sai id hoặc move ở các route liên quan trả 400 thay vì bị hiểu thành lỗi tìm dữ liệu. | app/service.py, tests/test_http.py |

API mới: POST `/api/draft`, JSON gồm `id`, `evaluation`, `threat`, `plan`, `confidence`. Mỗi ô text tối đa 1500 ký tự, cho phép trống; confidence là unsure/some/sure. Trả `saved` và `submitted`. GET exercise có `draft` nếu còn; dashboard có `pending` chứa metadata tối thiểu. Cookie, same-origin, local-only và giới hạn request hiện tại được giữ. Không có database migration vì draft nằm trong JSON record sẵn có.

## Kiểm tra đã thực hiện

- `python -m unittest discover -s tests -v`: 72 test pass, 64.517 giây. Gồm 65 test cũ và 7 test mới về draft, bảo mật phiên, export/delete, giữ reflection đã gửi, pending và API đầu vào.
- `python -m compileall -q app server.py` và bundled Node `--check web/app.js`: pass. Không có npm build/TypeScript/linter cấu hình sẵn.
- Browser thực tế: demo → lưu một câu nháp → về trang chủ → tiếp tục → reload → nháp còn và lời giải vẫn khóa → gửi đủ câu → thử a2a7 bằng bàn phím → bài mới b3g3 → dashboard. Bài liên quan khác demo trước vì ngân hàng ưu tiên family chưa gặp.
- Hai attempt mới trong database là thao tác QA, không phải người dùng pilot hoặc bằng chứng cải thiện học. Dashboard tăng từ 2 lên 4 attempt; hai bài mới đúng độc lập tổng cộng, lịch kỹ năng sau lần thứ hai là 30 ngày. Đây là kết quả quy tắc hiện có.
- Kiểm tra responsive ở viewport thực tế 390×844: clientWidth và scrollWidth đều 375 px trên trang chủ và màn học; bàn cờ khoảng 329 px. Đây là kiểm tra browser mô phỏng kích thước, không phải test thiết bị điện thoại vật lý.
- Cuối kiểm tra có một phiên browser không còn truy cập được bài thuộc guest cũ sau chuỗi thao tác đổi viewport/tab; chưa khẳng định nguyên nhân mất liên kết phiên. Server không cho đọc/ghi bài không thuộc guest. Trong phiên khách mới, tạo bài → lưu nháp → reload đã xác minh thành công lại. Không có cơ chế khôi phục guest sau mất cookie; đây vẫn là giới hạn đã công bố.
- Nhật ký lỗi/cảnh báo browser ở lần cuối rỗng. Ảnh bàn giao local: artifacts/co-chill-2026-10-09.png. Các request lưu thất bại được hiển thị cả lý do để không che lỗi dưới thông báo chung.

## Còn giới hạn gì

- Draft cần server đang chạy để bền vững; chưa có hàng đợi offline bền vững. Khi lưu lỗi, text còn trong trang và có cảnh báo khi rời nếu browser hỗ trợ; đóng cưỡng bức trước khi lưu có thể mất phần chưa lưu.
- Autosave được tuần tự hóa trong một tab, chưa có xử lý xung đột nhiều tab sửa cùng một bài. Mỗi phản hồi đã gửi vẫn được server bảo vệ khỏi autosave đến muộn.
- Hash phục hồi khi reload, chưa có history router hoàn chỉnh hoặc khôi phục vị trí cuộn/focus sau mọi thao tác. Nháp góp ý/import chưa tự lưu.
- Chưa audit WCAG/screen reader đầy đủ; chưa có kéo thả. Thiết kế mới chỉ là cải thiện khả dụng, chưa phải bản UI cuối do chủ dự án duyệt.
- Engine vẫn tìm nông tối đa 2 ply; không Pikafish tích hợp, không LLM/ML. Luật lặp thế vẫn quy ước demo. Kho vẫn 12 bài tổng hợp, chưa dùng ván mới hoặc luật mới từ bạn.
- Phân tích vẫn đồng bộ và có thể chặn ghi SQLite một thời gian. Hiện thời gian chờ không làm công việc chạy nhanh hơn; tác vụ nền cần thiết kế riêng khi nâng engine.

## Phần chờ bạn và thứ tự tiếp theo

Bạn trả lời cả hai Word; có thể tham chiếu câu cũ, ghi chưa chốt hoặc giao phần kỹ thuật đề xuất. Ưu tiên hướng hình ảnh, năm trang cần sửa, bố cục màn học, thiết bị thật và nguồn luật. Gửi ảnh/bản vẽ có mã Pxx/UXxx.xx và tình huống luật theo LUAT001.

Sau đó mới chốt design tokens và mockup toàn trang, ưu tiên backlog, chọn luật/engine và xác minh bộ thế cờ. Các hướng OCR, 3D, PvP, thuê bao, đăng nhập công khai, chuyển stack hoặc gọi API ngoài chưa được triển khai trong đợt này.

## Cách chạy và xem thay đổi

Từ thư mục `E:\ThanhTQ\App cờ tướng\xiangqi-ai`, chạy `python server.py --port 8765`, mở `http://127.0.0.1:8765/`. Nếu server đang chạy bản cũ, dừng bằng Ctrl+C rồi chạy lại. Giữ terminal mở.

Demo thay đổi: bắt đầu demo → review → nhập một phần suy nghĩ → đợi thông báo đã lưu → về trang chủ → Tiếp tục → reload → chọn chữ quân tiếng Việt → gửi đủ suy nghĩ → thử lại bằng bàn phím → bài liên quan → Tiến bộ. Không gửi suy nghĩ cho dịch vụ bên ngoài.
