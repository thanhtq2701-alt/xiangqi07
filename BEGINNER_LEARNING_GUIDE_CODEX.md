# Hướng dẫn hiểu code Cờ Chill

Bạn không cần học hết lập trình rồi mới tiếp tục. Bắt đầu bằng việc chạy app, theo một nước đi qua hệ thống, sau đó đọc từng mô-đun nhỏ.

## Năm khái niệm quan trọng nhất

1. **Luật khác đánh giá.** `Position.legal_moves()` trong `app/rules.py` trả lời nước nào được phép. `LocalEngine.analyze()` trong `app/engine.py` xếp các nước hợp lệ theo tìm kiếm nông. Hợp lệ không có nghĩa là hay; điểm engine không phải sự thật tuyệt đối về chiến lược.
2. **Trạng thái và chuyển bước.** `app/service.py` giữ game, exercise, reflection, revealed, complete. Client không tự quyết mở đáp án: `reflect()` yêu cầu câu trả lời; `attempt()` kiểm tra luật và ghi kết quả. Chuyển bước sai phải bị server từ chối.
3. **API là hợp đồng dữ liệu.** `web/app.js` gọi HTTP/JSON đến `server.py`, rồi `Service.dispatch()` chuyển yêu cầu vào nghiệp vụ. Ví dụ `/api/attempt` nhận id và move, trả correct, complete, lịch ôn. API nội bộ không đồng nghĩa với phải trả tiền cho AI.
4. **Persistence và transaction.** `app/storage.py` lưu JSON có owner/kind/id trong SQLite. Transaction gom một hành động thành một lần thành công hoặc hoàn tác. Context manager phải đóng connection để tránh khóa file trên Windows. Cookie khách chỉ chọn đúng chủ sở hữu bản ghi.
5. **Kiểm thử và bằng chứng.** `tests/` kiểm tra cả luật, dữ liệu, logic học và HTTP. Một test đạt chứng minh tình huống được test, không chứng minh engine mạnh hoặc người học đã tiến bộ. Test đối chiếu với chuyên gia/engine độc lập là bước tiếp theo.

## Đi theo một lần thử

Người dùng bấm quân → JavaScript gửi move → server kiểm tra phiên → Service đọc thế cờ → Rules kiểm tra hợp lệ → Engine score được so sánh → scheduler tạo lịch → Repository lưu attempt và skill trong một transaction → UI hiển thị kết quả.

Lời giải đi đường khác: Rules/Engine tạo dữ kiện → TemplateProvider tạo WHAT/WHY/HOW → service chỉ gửi sau reflection. Không có LLM đoán nước cờ. `recommend()` chọn bài cùng kỹ năng nhưng khác family chưa thấy trước, thay vì chỉ lặp lại đáp án vừa học.

## Đọc theo thứ tự

1. README và RUN_AND_DEMO_CODEX: chạy và hiểu trải nghiệm.
2. KNOWN_LIMITATIONS: hiểu những điều chưa được chứng minh.
3. `tests/test_rules.py`, rồi `app/rules.py`: hiểu đầu vào/đầu ra từng luật.
4. `tests/test_learning.py`, rồi `app/service.py`: hiểu cách kiểm thử vòng học.
5. `app/learning.py`: vì sao lần sai ôn sớm và lần có gợi ý không tính chuyển giao độc lập.
6. `web/app.js`, `server.py`: đi theo một HTTP request bằng DevTools Network.

## Những lỗi thường gặp

- Sai hệ tọa độ: code lưu hàng từ phía Đen, notation a0 từ phía Đỏ. Dùng `square()`/`index()`, không tự đổi theo cảm tính.
- Mở đáp án ở frontend nhưng không khóa API: có thể bypass. Test phải gọi API trực tiếp.
- Thử nhiều lần cộng nhiều điểm: lần đầu mới cập nhật scheduler; retry chỉ phục vụ học.
- Nhầm text reflection dài là tư duy tốt: chưa có rubric thì không chấm tự động.
- Chạy server ở cổng khác nhưng vào URL cũ: dùng đúng hostname/cổng và cùng trình duyệt để giữ phiên.
- Sửa Python rồi không restart: server không hot reload. Dừng Ctrl+C, chạy lại.

Ngày đầu dành 45 phút: 10 phút demo, 15 phút theo một request, 10 phút đọc test Pháo/Mã, 10 phút tự giải thích data flow bằng lời mình. Sau đó gửi 3 chỗ bạn chưa hiểu cùng mã file/hàm.
