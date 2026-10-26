# Bàn giao Cờ Chill cho trợ lý tiếp theo

Gói nguồn ngày 17/10/2026. Đọc README, manifest và code thực tế trước khi sửa. Người dùng là người mới: giải thích bằng tiếng Việt, nói rõ file nào thay đổi và cách kiểm tra.

## Phạm vi thực tế

- Nguồn website là `online-preview/`: HTML/CSS/JavaScript thuần; không có bước build hoặc API trả phí.
- Python trong `app/` chỉ là tham chiếu luật/engine/bài để chạy kiểm thử. Gói này không có app backend Python/SQLite đầy đủ.
- Giữ vòng chơi/nhập ván → chọn điểm cần học → phản hồi trước đáp án → giải thích có căn cứ → thử lại → bài liên quan → lịch ôn → tiến độ.
- Không coaching khi ván đang chạy. Luật/engine quyết định nước hợp lệ, biến và đánh giá; lời giải không được bịa nước.
- Engine nông, bài tự dựng, lời giải template, lịch ôn heuristic: mô tả trung thực, không nhận có LLM/ML hay hiệu quả học tập đã kiểm chứng.
- Dữ liệu hiện là localStorage theo trình duyệt/origin. Chưa có tài khoản thật, admin tập trung, cloud sync hoặc online PvP.
- Kế hoạch V5 có tài khoản tập trung, quản lý/thống kê đăng ký từ nhiều thiết bị, quyền admin và đồng bộ tiến độ. Đây là yêu cầu dự kiến, chưa triển khai; đọc câu trả lời V5 mới của chủ dự án trước khi quyết định chi tiết.
- Tài liệu gốc không nằm trong gói này. Không tự giả định các phần thiếu đã được chốt; yêu cầu chủ dự án cung cấp khi công việc phụ thuộc chúng. Không cần các tài liệu đó chỉ để chạy code hiện tại.

## Quy tắc làm việc

1. Kiểm tra trạng thái file và các test trước khi thay đổi. Chạy `python tools/check_all.py` sau thay đổi liên quan; không xóa hoặc làm yếu test để pass.
2. Không rewrite toàn bộ hoặc chuyển framework nếu chưa có lý do cụ thể và phạm vi phù hợp yêu cầu.
3. Không scrape dữ liệu, commit secret, lưu mật khẩu dạng rõ, dùng dữ liệu người học để huấn luyện. Giữ xuất/xóa dữ liệu và hạn chế thật trong giao diện.
4. **Luôn hỏi chủ dự án trước khi push GitHub, deploy, thay đổi quyền public, mua dịch vụ hoặc xóa dữ liệu/file có giá trị.** Auto-approve đã bị thu hồi. Việc đọc file, chuẩn bị phương án và kiểm tra local không phải bằng chứng được phép xuất bản.
5. Không force-push, không xóa lịch sử Git. Gói này không chứa `.git` hoặc hosting credentials. Trước thao tác Git phải kiểm tra repo/nhánh/remote thực tế.
6. Ghi rõ nội dung đã sửa, test đã chạy, lỗi/giới hạn còn lại và bước cần chủ dự án duyệt. Không nói đã deploy chỉ vì source chạy local.

## Prompt có thể gửi cùng gói

“Hãy đọc README.md, AI_HANDOFF.md và SOURCE_MANIFEST.json. Mở online-preview để hiểu website Cờ Chill hiện tại. Chạy các test và giải thích ngắn kiến trúc trước khi thực hiện thay đổi tôi yêu cầu. Giữ luật cờ, reflection gating và vòng học. Không tự push/deploy, đổi public hoặc xóa dữ liệu. Tôi sẽ cung cấp V5/UI UX và luật khi làm nâng cấp tiếp.”

File này là tài liệu để chủ dự án gửi/cho phép trợ lý đọc; không dựa vào việc một extension cụ thể tự động nạp file.
