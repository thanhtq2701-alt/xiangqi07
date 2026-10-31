# Giới hạn V6 — 26/10/2026

Website Production hiện được chủ dự án xác nhận đang chạy tại cochill.vn.
Tài liệu và source trong repo không phải xác minh trực tiếp VM, triển khai,
khả năng chịu tải hay mức sẵn sàng vận hành.

## Chưa hoàn tất theo V6

- Chưa xác minh độc lập VM Google Cloud, binary/NNUE Pikafish thật, cấu hình
  HTTPS/DNS, tải thực hoặc backup/restore. Thông số VM, HTTPS, service và
  lịch backup hiện tại là thông tin do chủ dự án cung cấp.
- Chưa có email/Gmail tự khôi phục mật khẩu, OAuth, nhập phục hồi JSON tiến độ
  đầy đủ, public profile/lịch sử cộng đồng, chat tự do có quản trị.
- Chưa có LLM chấm tư duy/cá nhân hóa, bảy cấp bot hiệu chỉnh, chính sách lên
  xuống cấp sau 10 ván hoặc hàng đợi ưu tiên bot với SLA 10 giây đã đo.
- Kho bài nhỏ: 12 cơ bản +8 hướng dẫn +2 bài nhiều lượt. Hai bài mới cùng họ
  chiếu hết; chưa có kho nâng cao 6–7 quyết định hoặc coverage từng chương.
  Chưa đủ 10 hình khác nhau/chương để đánh giá cấp.
- Ngôn ngữ EN chưa phủ hết các chuỗi động, màn mới, quản trị/PvP. Bài học vẫn
  tiếng Việt theo yêu cầu. Auto-flip hai người cùng máy, câu trả lời bằng mũi
  tên, dashboard/calendar đúng thiết kế cuối chưa đầy đủ.
- Chưa xác minh mọi phán quyết lặp/chiếu dai/đuổi dai theo luật giải đấu Việt
  Nam. Friendly không ranked; trường hợp ngoài phạm vi cần xác minh.

## Giới hạn kỹ thuật và dữ liệu

- Một VM/instance, một process worker. Tăng worker/replica cần thiết kế lại
  semaphore engine, transaction/lifecycle phòng và xử lý restart.
- PvP polling2 giây; tab nền/mạng yếu có thể quá hạn30 giây và bị coi mất kết
  nối. Cả hai mất/restart thì tạm dừng. Cần nghiệm thu hai mạng và thiết bị thật.
- Polling phòng khoảng mỗi 2 giây lấy snapshot và cập nhật trạng thái/presence
  trong SQLite. `/api/rooms/session` không bị gọi ở mỗi poll (identity được
  làm mới theo chu kỳ dài hơn), nhưng snapshot tạo ghi và tranh chấp SQLite
  theo số người/phòng. Tải/độ trễ trên VM 2 vCPU chưa được benchmark; đo trước
  khi tăng lượng người hoặc thay tần suất polling.
- Ghép cộng đồng theo thời gian, chưa theo trình độ. Không chống được dùng
  engine bên ngoài hoặc thiết bị khác; chỉ khóa coaching/engine của app.
- Chat chỉ mẫu trung tính. Guest room cookie24 giờ; hết cookie chưa tự xóa
  dữ liệu room. Chưa có retention tự động toàn bộ phòng và backup.
- Xóa danh tính có ghế trong phòng hiện xóa cả biên bản chung liên quan của
  đối thủ. Cần chính sách ẩn danh/lưu giữ rõ trước mở pilot rộng.
- Thống kê học do client đồng bộ, không phải hệ thống chứng nhận chống gian
  lận. Người xem source có thể đọc đáp án; gate reflection là thiết kế học.
- Lịch ôn nhiều lượt hiện1 ngày độc lập,2 ngày có trợ giúp; chưa thống nhất với
  thuật toán lịch ôn tiến triển của bài cơ bản hoặc kiểm chứng hiệu quả.
- Những nhánh bài hợp lệ ngoài cây duyệt dừng chờ kiểm chứng; chưa tự chuyển
  engine/LLM để chấm. Xem giải thích trước khi giải xong được ghi có trợ giúp.
- Database/localStorage/backup chưa mã hóa ở mức ứng dụng. Người vận hành
  có quyền hệ điều hành có thể đọc dữ liệu. Cần cấu hình lưu bền và HTTPS.
- Quên mật khẩu chưa có quy trình tự phục hồi đã triển khai. Không dùng
  tài khoản pilot như kho lưu duy nhất cho dữ liệu quan trọng.
- Báo cáo kiểm thử không phải kiểm toán bảo mật, khả năng truy cập hay xác
  nhận sức cờ/hiệu quả giáo dục. Đọc TEST_REPORT_CODEX.md đúng phạm vi từng test.

Không chứa secret/database người chơi, không tự cập nhật ChatGPT Site hoặc
Production. Việc đưa source lên GitHub không tự chạy hoặc cập nhật máy chủ.
