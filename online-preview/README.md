# Cờ Chill — bản thử nghiệm trên trình duyệt

Thư mục này là bản nguồn của website thử nghiệm tĩnh trên ChatGPT Sites. Nó tách
biệt với ứng dụng Python trong `web/`, `server.py` và SQLite. Cập nhật thư mục này
hoặc đẩy lên GitHub **không tự triển khai** website.

## Phạm vi của bản cập nhật

- Trang chủ theo phác thảo đã chốt: logo, khu vực cá nhân và bốn cửa Chơi, Bài học,
  Xem lại lỗi sai, Ôn tập.
- Luật đi của bảy loại quân chạy trong trình duyệt, có kiểm tra Tướng an toàn;
  máy chơi dùng tìm kiếm cục bộ nông, không phải Pikafish hay mô hình được huấn luyện.
- Luồng học có câu trả lời trước lời giải, giải thích mẫu dựa trên nước hợp lệ,
  bài liên quan và bản tự đánh giá cuối phiên.
- Bài dang dở, câu trả lời và kết quả được lưu trong localStorage để tiếp tục ở
  **cùng trình duyệt**. Lịch ôn gợi ý lấy thời điểm hoàn thành từng bài làm gốc.
- Có xuất và xóa dữ liệu tại trình duyệt. Không đồng bộ tài khoản hoặc thiết bị;
  xóa dữ liệu trình duyệt/chế độ riêng tư có thể làm mất tiến trình.

Các giới hạn này cần được hiển thị trong giao diện, không chỉ ghi ở README.

## Điều gì là thật, điều gì là bản mẫu?

`fixtures.js` chứa đủ 12 bài tập tổng hợp gốc trong `app/puzzles.py`, thuộc bốn
nhóm quan sát quân, Pháo, Mã và an toàn Tướng. Mỗi bài có FEN, vị trí quân,
toàn bộ nước hợp lệ, một nước mẫu, nguồn gốc và giải thích WHAT / WHY / HOW.
Không bài nào được lấy từ ván đấu của người thật hoặc tài liệu thương mại.
Chúng chưa được chuyên gia độc lập thẩm định và không phải bộ dữ liệu đã đo
hiệu quả học tập. Các thế ít quân được xếp vào phần tàn cuộc để tiện tìm,
không mang nghĩa một giáo trình tàn cuộc đầy đủ.

Nước mẫu được kiểm tra bằng luật. Phần giải thích nói rõ đường đi của quân,
ngòi Pháo/chân Mã nếu có và an toàn Tướng. Không khẳng định đó là nước tốt duy
nhất. Điểm máy từ tìm kiếm nông chỉ là ước lượng cục bộ; không dùng làm bằng
chứng xếp hạng thi đấu, xác định mọi lỗi chiến lược hoặc đánh giá lời giải tự do.

Đây không phải LLM, ML được huấn luyện, hay dịch vụ AI trả phí. Câu trả lời tự do
được giữ để người học suy nghĩ và đối chiếu; bản này chưa tự chấm năng lực diễn
đạt bằng LLM. Tự đánh giá cuối phiên không được coi là bằng chứng thành thạo.
Lịch ôn là quy tắc gợi ý, chưa phải mô hình tối ưu thời điểm ghi nhớ.

Không có PvP online, tài khoản thật, server riêng cho học viên, cơ sở dữ liệu
chung, email/notification nền hoặc đồng bộ nhiều thiết bị. Luật xử lý chiếu dai,
đuổi dai và các tình huống giải đấu đầy đủ vẫn cần đối chiếu với bộ luật chủ
sở hữu sẽ cung cấp. Không dùng bản mẫu này để phân xử một giải đấu.

Khóa lời giải trước phản hồi là cơ chế UI: đáp án có trong bundle tĩnh và có thể
đọc bằng công cụ lập trình. Không phải khóa đáp án phía server của ứng dụng
Python. Mã ứng dụng không gửi câu trả lời để huấn luyện mô hình; nhà cung cấp
hosting vẫn xử lý request web thông thường theo chính sách của họ.

## Tạo lại và kiểm tra dữ liệu

```powershell
python tools/export_preview_fixtures.py
python tools/check_online_preview.py
```

Exporter chỉ đọc dữ liệu tổng hợp trong repository và kiểm tra luật, không truy
cập mạng. Checker xác nhận đủ 12 ID, FEN, vị trí quân, nước mẫu, toàn bộ tập nước
hợp lệ, metadata nguồn, bốn nhóm kỹ năng và nội dung xuất khớp với nguồn. Chạy
lại sau mọi thay đổi của `app/puzzles.py` hoặc `app/rules.py`.

Đã chạy kiểm tra dữ liệu thành công ngày 15/10/2026. Kiểm tra giao diện và triển
khai của bản mới được ghi trong báo cáo triển khai; kết quả ngày 12/10/2026 của
bản hai bài không được dùng làm bằng chứng cho bản này.

## Hosting

- Site ID: `appgprj_6acd061322c08191a4c912862bc05124`.
- URL đã được xuất bản trước đó: <https://co-chill-ngay-mai.cosmicanole32.chatgpt.site>.
- Audience: **public**, theo yêu cầu của chủ sở hữu; dùng lại dự án này cho bản cập nhật.
- Checkout của công cụ hosting nằm ở `var/site-preview`, được Git ignore;
  `.openai/hosting.json` thuộc checkout đó. Công cụ Sites quản lý repository riêng.
- Chỉ xuất bản các tài nguyên web được chọn. Không xuất bản tài liệu trả lời,
  kế hoạch riêng, Git history, SQLite, dữ liệu học viên hoặc token.

Bản đầu ngày 12/10/2026 có hai bài; source commit khi đó là
`4ea27de5c90c3080cd673f3a00e669aa3f579bfb`. Đó là lịch sử triển khai, **không
phải mã phiên bản của bản cập nhật hiện tại**.

Ghi chú Windows cho công cụ đóng gói: dùng Node hiện đại, Git Bash và
`TAR_OPTIONS=--force-local` để tránh WSL/đường dẫn ổ đĩa. Credentials chỉ qua
stdin ẩn của công cụ, không lưu vào repository.
