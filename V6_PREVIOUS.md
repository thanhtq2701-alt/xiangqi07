# V6 Previous

Tóm lược các ý tưởng và quyết định V3–V5 đã được hợp nhất hoặc thay thế. Đây
là ghi chú lịch sử, không phải đặc tả hay hướng dẫn vận hành hiện hành. Nếu có
khác biệt, dùng [README](README.md), [quyết định V6](docs/V6_DECISIONS.md),
[giới hạn](KNOWN_LIMITATIONS.md) và [báo cáo kiểm thử](TEST_REPORT_CODEX.md).

## Ý tưởng được giữ lại

- Dạy cách suy nghĩ và lý do đằng sau nước đi, không chỉ đưa đáp án; ưu tiên
  vòng chơi/nhập ván → chọn thời điểm đáng học → tự suy nghĩ → giải thích có
  căn cứ → thử lại → bài liên quan → ôn → tiến độ.
- Làm UI tiếng Việt dễ đọc, hỗ trợ người mới nhưng có đường học sâu hơn; ưu
  tiên bàn cờ, thao tác bàn phím/cảm ứng, trạng thái lưu và khôi phục.
- Luật và engine làm nguồn sự thật. Ký phổ, nhập/phát lại ván và phán quyết
  luật phải kiểm tra được; tình huống chưa đủ căn cứ cần được ghi rõ, không
  tự đoán. Ghi chú luật cũ dùng WXF 2018 để đối chiếu; vẫn cần lịch sử ván và
  người duyệt cho trường hợp lặp, chiếu/đuổi dai và luật giải đấu.
- Giữ ranh giới thay thế được giữa giao diện, server, persistence và engine.
  Ghi nhãn trung thực cho máy heuristic, bài tổng hợp, lịch ôn và giải thích
  mẫu; không tuyên bố có ML được huấn luyện hay hiệu quả học đã được chứng minh.
- Bảo vệ dữ liệu người học, hỗ trợ xuất/xóa, không scrape nội dung hoặc dùng
  dữ liệu người chơi để huấn luyện khi chưa có quyền và sự đồng ý.
- Tách bài giảng xem trước khỏi bài thực hành; xem lời giải không phải mastery.
  Một lần thử gồm suy nghĩ và nước đi; bài dở phải giữ đúng chỗ để học tiếp.
- Ghi riêng bài gốc, biến thể cùng ý, bài liên quan và trạng thái có trợ giúp.
  Chỉ tính nội dung mới khi mục tiêu hoặc cấu trúc thực sự khác; lịch ôn bắt
  đầu từ lúc hoàn thành từng bài, tự đánh giá không thay kết quả thực hành.
- Độ khó dựa vào quyết định cần đưa ra, phản ứng quan trọng và phương án gây
  nhiễu, không chỉ độ dài biến hay độ sâu engine. Nhãn trình độ chưa hiệu
  chỉnh không phải Elo hoặc bằng chứng mastery.
- Nội dung chia sẻ cần nguồn/quyền dùng và duyệt; bài gửi của người học không
  tự vào kho chung. Nước hợp lệ khác với nước tối ưu; nếu ngoài cây đáp án hoặc
  bằng chứng chưa đủ thì giữ trạng thái chưa xác định, không tự chấm sai.

## Ý tưởng đã được nâng cấp hoặc thay thế

- Các prototype V3–V5, web tĩnh và hướng dẫn hosting cũ không phải entry point
  hiện tại. Chạy V6 theo lệnh trong README; không dùng hướng dẫn Sites/Vercel,
  DNS hoặc server cũ để kết luận V6 đã được triển khai.
- Các câu hỏi UI, tài khoản, luật, nội dung và kế hoạch theo ngày đã được thay
  bằng code hiện có, quyết định V6 và giới hạn được ghi nhận. Câu trả lời trong
  tài liệu cũ không tự chứng minh tính năng đã hoạt động.
- Màu sắc, hình thức, scope PvP, tài khoản và engine đã được cập nhật qua các
  vòng chủ sản phẩm duyệt. Chi tiết đúng hiện nay nằm trong V6, không lấy mức
  ưu tiên/ngân sách hoặc kế hoạch phát hành cũ làm chỉ thị mới.
- Báo cáo, inventory, ảnh chụp và gói source V3–V5 là snapshot lịch sử; không
  thay cho kiểm thử V6 hoặc trạng thái repository hiện tại.

## Ý tưởng vẫn chưa được xác nhận hoàn tất

Kho bài nâng cao đã được chuyên gia duyệt; chấm tự do bằng LLM; cấp bot được
hiệu chỉnh; phục hồi mật khẩu qua email; luật giải đấu đầy đủ; và vận hành
Pikafish/Google Cloud, tải, backup, HTTPS hay DNS thực tế. Chỉ coi là hoàn tất
khi có bằng chứng mới trong [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) và
[TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md).

## Tài liệu nguồn

Các ghi chú, kế hoạch, báo cáo, câu hỏi và bản bàn giao V3–V5 đã được rút gọn
ở đây; bản gốc không còn cần cho việc chạy web. Riêng tài liệu Final Pack gốc
trong `docs/spec/` và `docs/materials/` được giữ nguyên theo quy ước dự án.
