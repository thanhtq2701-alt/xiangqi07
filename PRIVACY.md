# Dữ liệu và quyền riêng tư V6 — 26/10/2026

Mô tả hành vi code, không phải chứng nhận tuân thủ hoặc chính sách đã được
phê duyệt cho dịch vụ công khai. Người vận hành cần bổ sung liên hệ, phạm vi
độ tuổi, quy trình yêu cầu xóa và thời hạn backup trước pilot.

## Nơi lưu

| Cách dùng | Dữ liệu |
|---|---|
| Học/chơi local với guest | localStorage: ván, nháp, lượt học, lịch ôn, sở thích |
| Guest tham gia phòng online | Server: danh tính khách, tên hiển thị, phòng, biên bản, lời nhắn mẫu; cookie phòng24 giờ |
| Đăng nhập | Server SQLite: username, display name, hash mật khẩu, phiên, tiến độ đồng bộ, feedback và nhật ký vận hành |
| Bản nháp tài khoản trên thiết bị | Cache riêng theo tài khoản; không phải kho mã hóa |

Server mặc định dùng `var/co_chill_accounts.sqlite3`. Không có email, ngày
sinh, số điện thoại trong đăng ký hiện tại; chưa có email recovery. Không
tracker/LLM huấn luyện hoặc tự gửi dữ liệu người học ra ngoài. Gửi feedback
là thao tác chủ động; không đính kèm mọi câu trả lời riêng.

## Phiên và quyền

Mật khẩu băm scrypt với salt; token ngẫu nhiên có bản băm trên server.
Cookie HttpOnly/SameSite, Secure khi cấu hình HTTPS. Một phiên tài khoản;
Origin/CSRF/role kiểm tra ở server. Cookie guest phòng riêng với tài khoản.
Tên hiển thị/nước đi/lời nhắn trong phòng được người tham gia và người xem
phòng thấy. Không công khai suy nghĩ sau ván.

Owner/report được thống kê và danh sách/biên bản lọc; không có password/token
hoặc câu trả lời phản ánh riêng qua giao diện báo cáo. Owner được xử lý
feedback và nội dung; report không có quyền quản trị. Người có quyền đọc
database ở hệ điều hành vẫn có thể đọc dữ liệu; SQLite/backup không mã hóa
ở mức ứng dụng. Không coi quyền API là bảo vệ khỏi chủ máy.

## Xuất và xóa

Có xuất JSON cá nhân, xóa học trên thiết bị, xóa tài khoản xác nhận password,
xóa khách phòng chủ động. File xuất là bản cá nhân, không phải chức năng nhập
khôi phục đầy đủ. Không chứa snapshot khóa đáp án/biến tự sinh; có phản ánh
và nước do người học chọn. Đồng bộ giữ dữ liệu cần để khôi phục nháp.

Xóa tài khoản/khách có ghế phòng hiện xóa phòng/biên bản chung, kể cả phần đối
thủ liên quan. Hết cookie24 giờ không tự xóa biên bản. Database hoạt động và
backup là hai nơi khác nhau: yêu cầu xóa phải áp dụng khi phục hồi backup;
file đã tải xuống không tự bị thu hồi. Chưa tự cài tác vụ dọn phòng/backup.
Có lệnh xem trước/xóa tài khoản không hoạt động365 ngày khi operator xác nhận.

Trên máy dùng chung, đồng bộ/xuất trước khi đăng xuất; quản lý dữ liệu trình
duyệt và khách riêng. Thống kê là dữ liệu client gửi, không chứng minh trình
độ. Muốn dùng ván người chơi làm bộ bài chung cần đồng ý riêng, không tự
coi tham gia pilot là đồng ý chia sẻ/huấn luyện. Xem docs/DEPLOY_GCP_V6.md.
