# Kiểm thử V6 — 26/10/2026

## Kiểm tra giao diện sau chỉnh sửa — 27/10/2026

- `python tools/check_online_preview.py`: PASS; 12 fixture synthetic, provenance
  và danh sách nước hợp lệ khớp luật.
- Phần Python của `python tools/run_checks.py --node E:\ThanhTQ\Code\node.exe`:
  104/104 test đạt với Python 3.14.0.
- Không thể xác nhận JavaScript suite bằng Node trong PATH: phiên bản thực tế
  là 6.14.0, không hỗ trợ optional chaining/nullish coalescing dùng trong source;
  syntax checks và một số test dừng với `SyntaxError`. Runner kết thúc lỗi, sau
  đó còn gặp lỗi encoding Windows khi in lỗi ra console. Đây là giới hạn runtime
  kiểm thử, không ghi nhận là JavaScript suite đạt; cần chạy lại bằng Node.js
  phù hợp với README trước khi phát hành.
- Browser thủ công trên `http://127.0.0.1:8769/` với SQLite thử riêng: trang
  chơi với máy và form reflection hiển thị; đã xem desktop 1280x900 và mobile
  390x844. Trên mobile, document width 375px, không tràn ngang viewport 390px.
  API `/api/session` trả 200 cho khách. Không kiểm tra PvP, engine thật, luồng
  đăng ký user hoặc production trong lần này.
- Server dùng cho kiểm tra đã tách khỏi database mặc định/production. Kết quả
  browser là kiểm tra giao diện thủ công; không thay E2E, usability test hay
  kiểm thử account đầy đủ.

## Lượt xác minh sau đối chiếu — 26/10/2026

- Đã chạy `python tools/run_checks.py` tại workspace C với Python 3.14.2 và Node.js 22.23.4.
- Đạt: 104 bài Python; kiểm tra 12 fixture synthetic với luật và nước hợp lệ; parity/kiểm tra luật trên trình duyệt; cú pháp toàn bộ JavaScript; toàn bộ 10 bộ test JavaScript của runner.
- Chạy riêng `tests.test_online_rooms` và `tests.test_online_http`: 36/36 đạt; `tests.test_cloud`: 21/21 đạt.
- Bổ sung regression coverage cho preset/visibility/message/userId sai kiểu, payload không phải object, rời phòng paused và rollback giao dịch xóa tài khoản. Kiểm tra diff whitespace đạt.
- Lần chạy toàn bộ đầu tiên có một timeout trong test `test_untrusted_or_incomplete_engine_output_falls_back` của Pikafish; không đổi test hay logic để né lỗi. Test đạt khi chạy riêng và cả lượt đầy đủ chạy lại đạt.
- Gói nguồn mới gồm 91 file; manifest, SHA-256 và CRC được xác minh. Chạy lại runner trên bản đã giải nén ở thư mục tạm độc lập: cả 27 bước kiểm tra đạt, gồm 104 bài Python, fixture/parity, syntax và các bộ test JavaScript.
- Đây là kiểm tra local của source hiện tại; không phải browser E2E đầy đủ cho toàn bộ hành trình học/tài khoản/PvP và không xác nhận Internet, GCP, Pikafish/NNUE thật, cochill.vn, tải hoặc kiểm toán bảo mật.

## Phạm vi

Tests chạy trên source hiện tại; không xác nhận binary Pikafish thật, VM
Google Cloud, production HTTPS/DNS, hai mạng Internet, tải lớn hoặc kiểm toán
bảo mật. Không bỏ/giảm test để qua. Bộ legacy vẫn giữ trong repo gốc.

## Python

Core pack gồm 103 test: 30 rules, 22 cloud, 17 Pikafish adapter, 21 online rooms,
13 online HTTP. Runner cuối đã chạy một lượt đủ 103/103 đạt (436,190 giây).
Legacy 34 learning và 8 HTTP đạt;
8 HTTP ban đầu gặp WinError10013 vì localhost bị chặn, sau cấp quyền chạy lại
đạt8/8. Tổng145 Python test qua các lượt, không gọi là một lượt discover145.

Một test content từng báo fail ở lượt trước nhưng không còn traceback lưu;
hai test content đã qua lượt kiểm tra gần nhất. Không kết luận nguyên nhân
khi chưa có bằng chứng và không bỏ test. Gói dùng core103, không mang legacy.

## JavaScript và parity

155/155 test JavaScript đạt: học cơ bản 26; experience 20; notation 14
(4.054 roundtrip); cloud client 21; engine client 11; V5 UI 11; V6 UI 10;
V6 learning 19; V6 online UI 13; V6 learning UI 10. Kiểm tra syntax toàn bộ
14 file JS và compile Python đạt. Không có eslint/TypeScript/build riêng.

Fixture checker: 12 bài khớp luật. Parity Python/JS: 205 vị trí, 5.468 vị trí
con, 25 FEN cases, perft2=1.920, 12 thế engine/153 biến, 10 input sai: PASS.
Lệnh tái lập: `python tools/run_checks.py`, có thể truyền `--node PATH`.

## Trình duyệt thực

Chrome headless, database thử riêng, không dùng tài khoản/người chơi thật:

- Hai context guest: tạo/join/ready, đi quân đồng bộ, reload giữ màu/history,
  khóa bài học trong ván, hòa có chấp nhận, history riêng mỗi người.
- Tái đấu đổi bên/gameID, đầu hàng ghi kết quả mới. Không pageerror.
- Học:3 câu suy nghĩ nháp giữ qua reload, không hiện giải thích trước gate,
  đi4 quyết định có đối thủ đáp, xem/phát lại explanation, finish một attempt,
  lịch ôn sau completion, reload giữ tiến độ, mở bài liên quan và lịch ôn.
- Chọn theme cool và EN, viewport390px không tràn ngang. Ảnh desktop/mobile
  đã mở kiểm tra; tiếng Anh một phần và nội dung học vẫn Việt như giới hạn.
- Bản đã giải nén chạy server riêng: đăng ký qua form thật, đồng bộ theme
  sang context trình duyệt thứ hai, đăng nhập mới thu hồi phiên cũ. Không
  pageerror; mật khẩu test sinh ngẫu nhiên trong bộ nhớ, không ghi file/log.

Bằng chứng local: var/v6/online-browser-result.json,
var/v6/learning-browser-result.json và ảnh cùng thư mục. Không đưa DB/log
kiểm thử vào gói public. Browser automation tự thao tác, chưa thay người chơi
thử tính dễ dùng hoặc hai mạng thật.

## Gói nguồn

Builder chỉ lấy allowlist; verifier đối chiếu manifest/hash/CRC, không merge
vào thư mục tồn tại, từ chối đường dẫn unsafe và file runtime/private thường
gặp. Cần chạy lại bộ checks trên thư mục vừa giải nén để xác minh đủ dependency.
Hash đảm bảo khớp nội dung, không tự chứng minh không có lỗ hổng hoặc secret.

### Kết quả kiểm tra bản giải nén

Bản thử gồm 90 file, không thiếu asset được index tham chiếu; không có var,
.git, node_modules, database, log hoặc tài liệu trả lời cá nhân. Quét mẫu
private key/token phổ biến không thấy kết quả; đây không phải kiểm toán secret.

Chạy checks trên bản giải nén: 155 test JS, syntax, fixture/parity đều đạt.
Python đạt 102/103; test còn lại bị lỗi giả tại ranh giới TOTP30 giây: test
tạo mã mới nhưng coi là phát lại mã cũ. Đã sửa test để cố định đồng hồ, dùng
lại đúng mã, đồng thời bổ sung kiểm tra mã ở bước thời gian sau được chấp
nhận một lần và phát lại từ client khác bị từ chối. Không đổi logic bảo mật
production. Test đã sửa đạt khi chạy riêng; không loại bỏ/làm yếu assertion.

Gói cuối giữ nguyên toàn bộ runtime đã chạy ở bản giải nén, chỉ cập nhật
test xác thực và tài liệu. Verifier kiểm CRC/hash/manifest cho ZIP cuối;
test xác thực đã sửa được kiểm lại từ bản giải nén cuối. Như vậy core103 và
JS155 đều có kết quả đạt qua các lượt kiểm tra, không tuyên bố bản thử ban
đầu đạt tất cả trong một lượt.
