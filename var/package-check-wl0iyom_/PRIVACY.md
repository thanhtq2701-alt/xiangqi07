# Dữ liệu và quyền riêng tư của V5 — 24/10/2026

Tài liệu này mô tả hành vi code hiện tại; chưa phải chứng nhận tuân thủ pháp luật hay chính sách đầy đủ cho một dịch vụ đã vận hành. Bản V5 chưa được phát hành trong đợt này. Khi mở pilot, chủ sản phẩm cần điền đơn vị/người vận hành, địa chỉ liên hệ, phạm vi người dùng/độ tuổi và thời hạn backup thực tế.

## Dữ liệu nằm ở đâu

| Cách dùng | Dữ liệu được lưu |
|---|---|
| Khách chưa đăng nhập | Ván, nháp suy nghĩ, lượt học, lịch ôn và sở thích trong localStorage của trình duyệt; không tự chuyển thành tài khoản |
| Đăng nhập bản đầy đủ | Tên đăng nhập, tên hiển thị, mật khẩu đã băm, phiên, trạng thái học đồng bộ, thời điểm hoạt động, phản hồi gửi chủ web và một số nhật ký quản trị trong SQLite của máy chủ |
| Vercel static hoặc site chưa có API | Dữ liệu trình duyệt; không có tài khoản tập trung chỉ nhờ deploy HTML |

Database V5 mặc định là `var/co_chill_accounts.sqlite3`. Đây là database khác với `var/chill.sqlite3` của ứng dụng legacy. Khi đăng nhập, cache/nháp theo tài khoản vẫn có trên thiết bị để giữ công việc khi kết nối gián đoạn; localStorage không phải kho mã hóa. Trên máy dùng chung, đăng xuất và quản lý dữ liệu trình duyệt trước khi bàn giao máy.

Không yêu cầu ngày sinh hoặc email trong luồng username/password hiện có; không có email xác minh/khôi phục. Không đặt tracker, không gọi LLM để xử lý câu trả lời, không gửi dữ liệu cho huấn luyện mô hình. Gửi phản hồi là thao tác chủ động: nội dung bạn nhập và ngữ cảnh bài/trang được lưu để owner xử lý.

## Tài khoản và người có thể xem

Mật khẩu không được lưu nguyên văn; server dùng scrypt với salt ngẫu nhiên. Cookie phiên là giá trị ngẫu nhiên, HttpOnly và SameSite=Strict; database giữ bản băm token. Cookie thêm Secure khi cấu hình địa chỉ HTTPS công khai. Đăng nhập mới thu hồi phiên trước của cùng tài khoản. Server kiểm tra quyền, origin và CSRF cho thao tác thay đổi dữ liệu.

- Người dùng lấy/xuất/xóa dữ liệu tài khoản của mình qua API được kiểm tra phiên.
- Owner và người có vai trò báo cáo xem thống kê, danh sách tài khoản và biên bản đã lọc. API này không trả mật khẩu, token phiên hoặc câu trả lời phản ánh riêng.
- Owner có thêm quyền xử lý phản hồi do người dùng gửi, khóa có lý do/thời hạn và biên tập nội dung. Vai trò báo cáo không đọc hộp phản hồi riêng hoặc bản nháp nội dung.
- Người vận hành có quyền truy cập file/database vẫn có khả năng đọc dữ liệu máy chủ. Phân quyền API không bảo vệ khỏi quyền hệ điều hành. SQLite/backup chưa mã hóa ở mức ứng dụng.

Thống kê là dữ liệu do thiết bị đồng bộ, không dùng để chứng nhận kỹ năng, Elo hay hiệu quả học. Không công khai tự động lời phản ánh cá nhân. Bản đồng bộ nội bộ có thể chứa snapshot bài/lời giải để tiếp tục học; cổng phản ánh là cơ chế học tập, không ngăn chủ thiết bị kiểm tra mã nguồn.

## Xuất, xóa và giữ dữ liệu

Mục tài khoản cho phép xuất JSON cá nhân và xóa tài khoản thường sau khi xác nhận mật khẩu. Export giữ câu trả lời của bạn, nước đã chọn, lượt thử, nháp và lịch; bỏ snapshot đáp án, biến/đánh giá sinh tự động. Đây là file đọc/lưu cá nhân, **không phải** định dạng backup có thể nhập phục hồi toàn bộ. Owner không tự xóa tài khoản owner đang giữ quyền quản trị; việc bàn giao quyền cần thao tác vận hành.

Xóa tài khoản xóa dữ liệu liên quan ở database hoạt động; không chỉ ẩn khỏi dashboard và không bí mật giữ để huấn luyện. Xóa không tự thu hồi các file bạn đã tải xuống hoặc bản backup người vận hành giữ. Quy trình backup phải có thời hạn riêng và áp dụng lại các yêu cầu xóa khi phục hồi bản cũ.

Có lệnh xem trước các tài khoản không hoạt động 365 ngày và lệnh xóa khi người vận hành xác nhận. **Chưa có tác vụ tự chạy**, email nhắc hàng tuần hoặc thời hạn backup đã được triển khai. Không hiểu yêu cầu mong muốn trong V5 là một cam kết lưu trữ tự động đã có.

Source Word, database, backup và biến môi trường không nằm trong thư mục public `online-preview/`. Không đưa các dữ liệu này vào output deploy. Hướng dẫn vận hành: [DEPLOY_V5.md](docs/DEPLOY_V5.md).

## Lịch sử: chính sách prototype local cũ

Phần bên dưới mô tả `server.py`/cookie khách của bản cũ, không thay thế phần tài khoản V5 ở trên.

# Local prototype privacy

Update 9 October 2026: partially typed reflection drafts are autosaved to the same local SQLite exercise record after a short pause, before submission. Drafts do not reveal solutions or count as attempts. They are included in guest export and removed by guest deletion or replaced by the submitted reflection. Piece-label preference alone is stored in browser localStorage. The app still sends no learner data to external services.

The local server stores games, reflections, practice attempts, skill schedules and feedback in `var/chill.sqlite3`. An HttpOnly, SameSite=Strict random cookie links your browser to its records. No email, name, password, date of birth or contact information is requested. No analytics tracker, remote font, paid LLM or external API is called by the application.

Data is not automatically shared, transmitted for model training or sent to a coach. The project owner must obtain appropriate consent and define a reviewed privacy policy before any external pilot, particularly involving children. This file is a description of the prototype, not a legal compliance certification.

Use the Data and privacy screen to export your session records as JSON or delete them. Exported data retains the reflection gate for exercises whose answers are not yet revealed. Deletion removes active records for that guest; it does not erase separately downloaded exports or external backups. Losing the guest cookie loses the UI association to old records. Anyone with operating-system access to the database may read it; this is not encrypted multi-user production storage.

Only the web assets are served as files. Source documents and database files are not available through the HTTP server. Host and Origin checks prevent ordinary cross-origin writes; production security needs further work.
