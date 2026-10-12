# Đóng góp cho Cờ Chill

Đây là prototype local đang hoàn thiện. Đọc [README](README.md), [giới hạn](KNOWN_LIMITATIONS.md), [AGENTS.md](AGENTS.md) và đặc tả trong `docs/spec/` trước khi sửa. Đặc tả mô tả mục tiêu; báo cáo triển khai mô tả những gì thực sự đã có.

## Thay đổi nhỏ, có bằng chứng

1. Mô tả lỗi hoặc hành vi muốn cải thiện, kèm bước tái hiện nếu có.
2. Tách một nhóm thay đổi rõ ràng. Giữ ranh giới luật/engine, nghiệp vụ, lưu trữ và giao diện.
3. Thêm kiểm thử khi sửa logic quan trọng; không bỏ hoặc nới assertion chỉ để test qua.
4. Chạy kiểm tra và mô tả kết quả thực tế trong commit/PR. Nếu chưa chạy, ghi rõ.
5. Cập nhật hướng dẫn hoặc giới hạn khi thay đổi ảnh hưởng người dùng.

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app server.py tests
node --check web/app.js
git diff --check
```

Node hiện đại chỉ cần để kiểm tra cú pháp JS; app không cần Node để chạy. Chưa có bundler, TypeScript hay pipeline CI đã xác minh. HTTP tests dùng server và database tạm, không cần sửa dữ liệu học thật.

## Điều kiện không được phá vỡ

- Luật và engine quyết định nước hợp lệ, đánh giá và biến. Lời giải không được bịa thông tin cờ.
- Phải phản tư trước lời giải; không coaching khi đang chơi ván live.
- Không phóng đại engine local, bài tổng hợp hoặc heuristic thành ML được huấn luyện/kết quả học tập đã chứng minh.
- Không commit database, reflection của người dùng, token, cookie hay dữ liệu không có quyền sử dụng.
- Giữ xuất/xóa dữ liệu; kiểm tra cách ly phiên khách và lưu trữ khi sửa API.
- Không sửa đặc tả gốc, tự quyết câu trả lời V4 hoặc viết lại lịch sử Git.

## Báo lỗi có ích

Ghi hệ điều hành, phiên bản Python, commit đang chạy, bước tái hiện, kỳ vọng và thực tế. Với lỗi luật cờ, cung cấp FEN, bên đi, nước đi tọa độ và nguồn luật nếu có. Dùng thế cờ tổng hợp thay cho export cá nhân; che thông tin riêng tư trong ảnh/log.

Repo hiện chưa có giấy phép phát hành do chủ dự án lựa chọn. Tham khảo `THIRD_PARTY_NOTICES.md`; việc đổi Public không tự quyết định giấy phép hoặc cho phép lấy dataset bên ngoài.
