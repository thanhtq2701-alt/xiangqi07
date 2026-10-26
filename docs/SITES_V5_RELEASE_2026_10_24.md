# Cờ Chill V5 — phát hành bản xem thử ngày 24/10/2026

Theo yêu cầu mở web mà không bật localhost, giao diện V5 đã được cập nhật vào Site Cờ Chill hiện có. Giữ nguyên địa chỉ và audience public; không tạo site khác hoặc đổi DNS cochill.vn.

- URL: https://co-chill-ngay-mai.cosmicanole32.chatgpt.site/#home
- Phiên bản sản phẩm: V5. Phiên bản do Sites đánh số: **4**.
- Project: `appgprj_6acd061322c08191a4c912862bc05124`.
- Source commit tại repository Sites: `748aa97d42c3437a9a36cbc9bf16e3a5c1469a3c`.
- Saved version: `appgprj_6acd061322c08191a4c912862bc05124~appgver_ecbdb20c660881918f539f3d102c3e45`.
- Deployment: `appgdep_6adce149ef0c8191abd89963e4a6a6c7`, kết quả native **succeeded** và trả đúng URL.
- Gói phát hành gồm 15 tài nguyên frontend và manifest hosting; không có database, tài liệu riêng hoặc thông tin đăng nhập.

Chạy được chơi máy cơ bản, hai người cùng máy, nhập/xem lại ván, phản ánh trước lời giải, retry, bài liên quan, lịch ôn, tiến độ và giao diện mới. Tiến độ khách thuộc trình duyệt/origin đó, không tự đồng bộ qua thiết bị.

Không có Python API trong bản static: đăng ký/đăng nhập tài khoản Cờ Chill, quản trị người chơi, đồng bộ cloud, phản hồi gửi tới server và Pikafish server chưa chạy trên Site này. Giao diện thông báo chế độ khách khi thiếu API. Không suy thành V5 đã hoàn thiện toàn bộ hay đã deploy backend.

Các file frontend được sao chép từ bản local đã qua 101 kiểm thử JavaScript ở đợt chốt trước; kiểm tra cú pháp app.js/v5-ui.js thêm lần nữa trong quy trình đóng gói. Source helper commit/push đúng source trước khi lưu archive và native deploy. Không chạy lại toàn bộ 110 Python tests vì không sửa backend trong lần phát hành static này. Không có lượt browser QA tương tác mới; xác nhận phát hành dựa trên native deployment succeeded.

Repository Sites đã có commit/push phục vụ phát hành. Repository GitHub xiangqi07 chưa được commit/push bởi thao tác này. Ngày hôm nay có hai giai đoạn: bàn giao code local trước, rồi phát hành frontend theo yêu cầu mới; các báo cáo ghi “chưa deploy” trước đó thuộc thời điểm bàn giao local.
