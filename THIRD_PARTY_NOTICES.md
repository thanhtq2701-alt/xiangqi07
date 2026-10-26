# Nguồn và quyền sử dụng V6 — 26/10/2026

- Đặc tả: tài liệu chủ sản phẩm V3/V4/V5/V6, Final Pack. `docs/spec/` giữ bản
  đặc tả gốc; câu trả lời cá nhân/Word gốc không đóng trong source public.
- Logo và cover do chủ sản phẩm cung cấp, dùng tại
  `online-preview/logo-co-chill.png` và `cover-co-chill.png`. Chưa có kiểm
  toán giấy phép độc lập cho mọi thành phần hình.
- 12 bài cơ bản, 8 hướng dẫn và 2 bài nhiều lượt tự dựng; không scrape kho
  ván, sao chép chú giải hoặc trích sách chỉ vì tài liệu đã cũ. Các hình nguồn
  sách/video chưa rõ quyền không được đưa vào bộ bài.
- UI dùng SVG/CSS và font hệ thống, không tải font/tracker bên ngoài.
- Python standard library + JavaScript thuần cho local. Gunicorn trong
  requirements.txt dành cho Linux production; giữ giấy phép dependency khi
  phân phối môi trường cài sẵn.
- app/pikafish.py là adapter dự án, không chứa engine binary/NNUE/mã nguồn
  Pikafish sao chép. Tests dùng UCI giả tự tạo. Kiểm tra giấy phép đúng binary,
  source và weights trước tải hoặc phân phối.

Nguồn chính thức tham khảo: [Pikafish](https://github.com/official-pikafish/Pikafish),
[UCI commands](https://github.com/official-pikafish/Pikafish/wiki/UCI-%26-Commands),
[networks](https://github.com/official-pikafish/Networks),
[WCAG](https://www.w3.org/WAI/WCAG22/quickref/).
Dẫn nguồn không cấp quyền sao chép nội dung hoặc chứng nhận tuân thủ.

Chủ dự án chưa chọn giấy phép mã nguồn chung. Repo public không tự xác định
quyền tái phân phối mọi phần. Trước công bố, xác nhận quyền ảnh/tài liệu,
chọn license phù hợp cho phần mình sở hữu và giữ notice của dependency.
