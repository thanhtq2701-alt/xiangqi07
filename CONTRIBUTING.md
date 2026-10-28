# Đóng góp cho Cờ Chill V6

Đọc [README](README.md), [giới hạn](KNOWN_LIMITATIONS.md), [AGENTS.md](AGENTS.md),
[handoff V6](docs/CLAUDE_HANDOFF_V6.md) và các quyết định trong
`docs/V6_DECISIONS.md` trước khi sửa. Đặc tả ở `docs/spec/` mô tả yêu cầu gốc;
báo cáo triển khai và kiểm thử mô tả bằng chứng hiện có.

## Quy trình thay đổi

1. Mô tả hành vi cần sửa, kèm bước tái hiện nếu có.
2. Tách thay đổi theo một mục tiêu; giữ rõ ranh giới luật/engine, backend,
   persistence và giao diện.
3. Thêm hoặc cập nhật test cho logic thay đổi. Không bỏ hoặc nới assertion để
   làm test qua.
4. Chạy bộ kiểm tra chuẩn từ thư mục gốc:

   ```powershell
   python tools/run_checks.py
   git diff --check
   ```

   Cần Python 3.12 trở lên và Node.js 24.22.1 cho bộ kiểm tra (phiên bản
   chuẩn nằm trong `.nvmrc`); app chạy bình thường không cần Node/npm. Runner
   kiểm tra syntax Python/JavaScript, nghiệp vụ, fixture và parity luật. Nếu
   chỉ sửa tài liệu, kiểm tra nội dung, liên kết và diff là đủ.
5. Ghi đúng lệnh và kết quả thực tế; cập nhật README, báo cáo hoặc giới hạn
   khi thay đổi ảnh hưởng người dùng.
6. Chỉ commit/push khi chủ repo cho phép; không sửa hoặc viết lại lịch sử Git.

## Điều kiện không được phá vỡ

- Luật và engine là nguồn sự thật cho nước hợp lệ, đánh giá và biến. Provider
  giải thích không được tự tạo nước, biến hoặc điểm.
- Phải cho người học suy nghĩ trước khi hiện lời giải; không coaching trong
  ván live.
- Ghi nhãn trung thực cho engine local, bài tập tổng hợp, heuristic và giải
  thích theo mẫu; không tuyên bố ML đã huấn luyện hoặc hiệu quả đã kiểm chứng.
- Không commit database, reflection, token, cookie hoặc dữ liệu không có
  quyền sử dụng. Giữ khả năng xuất/xóa dữ liệu và kiểm tra cô lập tài khoản.
- Không sửa đặc tả gốc trong `docs/spec/`, tự quyết câu trả lời đang chờ chủ
  dự án, hoặc làm yếu test hiện có.

## Báo lỗi có ích

Ghi hệ điều hành, phiên bản Python, commit đang chạy, bước tái hiện, kỳ vọng
và kết quả thực tế. Với lỗi luật, cung cấp FEN, bên đi, tọa độ nước và nguồn
luật nếu có. Dùng thế cờ tổng hợp thay dữ liệu cá nhân; che thông tin riêng tư
trong ảnh/log.

Repo chưa có giấy phép phát hành do chủ dự án lựa chọn. Tham khảo
`THIRD_PARTY_NOTICES.md`; không tự thêm giấy phép hoặc dataset bên ngoài.
