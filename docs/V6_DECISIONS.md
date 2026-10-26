# Quyết định V6 và đối chiếu thực hiện — 26/10/2026

Nguồn: bản trả lời V6 ngày 25/10/2026 của chủ sản phẩm, ZIP source ngày
24/10/2026, các chốt V4/V5 và yêu cầu cuối: chỉ hoàn thiện pack để đưa lên
GitHub/Claude, không xuất ChatGPT Site. File trả lời cá nhân gốc giữ nguyên
ngoài pack. Đây là bản tóm quyết định, không tự đổi câu trả lời của chủ dự án.

## Phạm vi và vận hành

- Chủ sản phẩm muốn UI, tài khoản, Pikafish, bài nhiều lượt và PvP cùng có;
  kho dữ liệu lớn được bổ sung sau. Không diễn giải việc đóng pack là đã đáp
  ứng toàn bộ các mục đó trên server thật.
- Pilot dự kiến 5–10 người, chưa phải số người dùng thực.
- Hướng triển khai chốt: Google Cloud cho web/API/database/engine và cochill.vn
  làm tên miền. Ngân sách dịch vụ khác tối đa 200.000 VND/tháng, Google Cloud
  đã được tính riêng. Không tạo dịch vụ trả phí hoặc đổi DNS trong lượt này.
- Chưa xác minh VM, OS, binary/NNUE, địa chỉ API, dung lượng/tải và backup.
  Link Cloud Console không thay thế hợp đồng API hoặc bằng chứng engine chạy.
- Quyền duyệt: chủ sản phẩm duyệt trước push/deploy, DNS, thay máy, chi phí,
  chuyển dữ liệu thật hoặc gửi email. Không khôi phục cơ chế auto-approve cũ.

## UI và thông tin

| Quyết định | Trạng thái source / giới hạn |
|---|---|
| Giữ logo/cover, font rõ dấu Việt, cover rộng đầu trang | Có lớp trình bày V6; không thay chữ thương hiệu trong ảnh |
| Vào bằng màn tài khoản/khách, không tự vào Home | Có; chọn khách không giả tạo tài khoản server |
| Ba theme ấm/lạnh/tối, dễ tìm trong cài đặt | Có thẻ chọn/xem trước và lưu theo hồ sơ |
| Tiếng Anh chỉ cho giao diện, bài học Việt | Có dictionary; chưa dịch hết thông báo động/PvP/quản trị/bài mới |
| Thêm bàn cờ/hình thay văn bản dài | Bàn cờ ví dụ, thẻ chương, icon; chưa có bộ minh họa riêng cho mọi bài |
| Chơi giữ đối thủ, đồng hồ, ký phổ, hòa/thua | Có; PvP từ trạng thái server |
| Tự lật bàn mỗi lượt khi hai người cùng máy | Chưa hoàn thiện; vẫn có nút lật thủ công |
| Dashboard học gọn, calendar tuần; admin đầy đủ | Dashboard hiện tại và bổ sung nhiều lượt; chưa tinh chỉnh đúng mọi bố cục chốt |

## Học, bài tập và engine

- 3 khóa khai/trung/tàn; trung cuộc có Xe, Pháo, Mã, an toàn Tướng và phối hợp.
  Người học chọn chương tự do. Có bản đồ chương và 8 bài hướng dẫn; không
  đánh đồng bài đã xem với hiểu/vững kỹ năng.
- 12 bài cũ chỉ là cơ bản. Hai bài nhiều lượt mới có cây quyết định hợp lệ,
  mục tiêu chiếu hết bằng chuỗi chiếu liên tục trong giới hạn, 3–4 lượt quyết
  định trên các nhánh được duyệt. Cả hai cùng một họ chiến thuật; không gán
  nhãn chuyển giao kỹ năng độc lập hoặc đã bao phủ trung cuộc.
- Độ khó mục tiêu: cơ bản 1–2 quyết định, trung cấp 3–4, nâng cao 6–7, tùy ý
  tưởng. Chưa có kho nâng cao 6–7 lượt; không kéo dài giả bằng nước vô nghĩa.
- Chỉ ba câu suy nghĩ ban đầu. Sau đó chọn nước và phản ứng đối thủ. Sai giữ
  checkpoint; sau ba lần sai đặt lại gốc và hẹn ngày sau. Nhánh hợp lệ ngoài
  cây đã duyệt được giữ để kiểm chứng, không bị kết luận sai bằng máy nông.
- Lời giải mở sau suy nghĩ/nước ứng viên. Hoàn thành cả chuỗi rồi mới ghi lần
  thử/lịch ôn; xem lời giải và có trợ giúp được ghi rõ. Có lưu nháp/khôi phục.
- Muốn vẽ mũi tên/đánh dấu làm câu trả lời: chưa có đầy đủ. Mục tiêu vẫn là
  câu trả lời của người học, chưa có AI chấm gần đúng ngữ nghĩa.
- Bài liên quan ưu tiên phù hợp/chưa gặp trong nội bộ; các câu D04/E06 mới hơn
  được ưu tiên: không hiển thị nhãn đã gặp/chưa gặp cho người học.
- Cấp chương sau 10 bài khác nhau là quyết định sản phẩm chưa đủ dữ liệu để
  nghiệm thu. Hai bài nhiều lượt không được nhân bản để đạt 10. EXP/cấp là
  heuristic, không Elo hay mô hình học máy.
- Chờ engine tối đa mong muốn 10 giây/nước; adapter hiện có ngân sách hữu hạn,
  chưa có hàng đợi ưu tiên bot/giới hạn SLA được đo trên GCP.
- Yêu cầu máy chủ/bài trung cấp không được thay bằng tìm kiếm nông. UI bật
  `requireStrong` cho bot server và review tài khoản. API trả lỗi khả dụng nếu
  adapter fallback. Bài cơ bản có nhãn vẫn chạy local.
- 7 cấp bot/tên hạng và đổi cấp theo 10 ván (thua >=6 hạ, thắng >=7 tăng):
  chưa hiệu chỉnh/triển khai. Không dùng độ sâu 1/2 để giả thành bảy cấp.
- LLM cá nhân hóa/nhận xét lập luận: chưa có provider/key/rubric; hiện lời giải
  là mẫu dựa trên luật/cây bài. Không tuyên bố LLM hoặc ML đã hoạt động.

## Tài khoản, dữ liệu và quyền riêng tư

| Quyết định | Source hiện tại |
|---|---|
| Username/password, một phiên tài khoản; social sau | Có scrypt/cookie/thu hồi phiên cũ |
| Quản trị xem người đăng ký và thống kê | Có owner TOTP và vai trò report riêng |
| Email/Gmail tự khôi phục mật khẩu | Chưa có; không coi cách hỗ trợ thủ công cũ là đã đáp ứng V6 |
| Đồng bộ chơi/học, không lẫn danh tính | Có revision/conflict và local scope từng người |
| Xuất/xóa dữ liệu của mình | Có; backup phải xử lý xóa riêng |
| Nhập file tiến độ cũ tự động | Chưa có phục hồi JSON đầy đủ; có chuyển guest trong cùng origin và nhập ký phổ |
| Công khai display name/avatar; tùy chọn lịch sử public/private | Có tên trong phòng; chưa có public profile/lịch sử cộng đồng đầy đủ |
| Phản hồi/report lưu và xuất riêng | Có quản trị phản hồi; kiểm tra lại định dạng export chuyên biệt trước phát hành |
| Gom ván người chơi làm dữ liệu học | Không tự bật. Cần đồng ý rõ ràng và quản trị dữ liệu; không gửi dữ liệu huấn luyện |

## PvP và luật

- Phòng riêng/công khai; ghép theo preset thời gian, chưa ghép theo trình độ.
- Khách có cookie phòng 24 giờ, riêng với đăng nhập học tập. Hai người cùng
  sẵn sàng trước chạy đồng hồ; màu đầu ngẫu nhiên, tái đấu đổi màu, game ID mới.
- Server kiểm tra quyền/lượt/nước, revision/nonce, đồng hồ và kết quả; client
  không tự khai thắng, FEN hoặc số giây. Hòa 15 giây, xin thua xác nhận, xin
  đi lại đối thủ duyệt theo cửa sổ hợp lệ; có khán giả và mời khán giả rời.
- Mất kết nối một bên 30 giây khi bên kia còn hoạt động có thể thua. Cả hai
  mất hoặc server restart thì tạm dừng; cần cả hai ready để tiếp tục.
- Chat chỉ tin nhắn trung tính định sẵn; chưa làm chat tự do vì chưa có cơ chế
  quản trị phù hợp. Không coi nó đã đáp ứng toàn bộ yêu cầu trò chuyện.
- Chặn engine/coaching của app cho người chơi/khán giả trong ván. Không thể
  ngăn họ dùng một thiết bị/engine ngoài. Friendly không ranked.
- Luật nước đi 7 quân, tự chiếu, bí nước, chiếu hết được test. Các phán quyết
  chiếu/đuổi/lặp giải đấu Việt Nam cần bộ tình huống và người duyệt; chưa
  được chứng nhận tuân thủ. Không đưa ranked lên khi chưa làm phần này.

## Thứ tự phát triển tiếp

1. Nghiệm thu pack sạch và hai tài khoản/hai thiết bị trên môi trường thử.
2. Nghiệm thu GCP/Pikafish thật, HTTPS, cookies, ổ bền và backup/restore.
3. Email recovery + nhập dữ liệu cũ, rồi rà quyền admin và thông tin công khai.
4. Bổ sung bài trung/nâng cao có nguồn và duyệt; rubric LLM trên bằng chứng.
5. Hiệu chỉnh bot, scheduler, journey/dashboard và English còn thiếu.
6. Thử tải nhỏ/PvP mạng thật; chốt luật trước bất kỳ ranked/giải đấu nào.
