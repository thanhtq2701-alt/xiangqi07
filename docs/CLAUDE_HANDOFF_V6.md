# Bàn giao Claude — Cờ Chill V6, 26/10/2026

## Bắt đầu từ bản này

Đọc AGENTS.md → README.md → docs/V6_DECISIONS.md → KNOWN_LIMITATIONS.md →
TEST_REPORT_CODEX.md. Pack không có dữ liệu cá nhân, khóa, binary Pikafish,
NNUE hay lịch sử Git. Giữ repository cũ để đối chiếu; không force push.

Entry point: `python co_chill_server.py serve --port 8769`. Không dùng
`server.py` legacy, không chỉ chạy `http.server` nếu cần tài khoản/PvP.
Frontend không có npm build; toàn bộ script nạp theo thứ tự trong index.
Backend standard library, WSGI + SQLite; Gunicorn chỉ dùng khi deploy Linux.

## Ranh giới code

- Luật: `app/rules.py` và `online-preview/xiangqi.js`, test parity bằng tool.
- Bằng chứng phân tích: `app/pikafish.py` và `engine-client.js`. Kiểm tra mọi
  PV hợp lệ, góc nhìn điểm, mate/cp và bound; không để LLM tự chế nước/điểm.
- Phiên học cũ: `learning.js` + `experience.js`; nhiều lượt: `line-practice.js`.
  `curriculum.js` chứa nội dung và cây đáp án; frontend source vẫn đọc được
  đáp án, không coi reflection gate là cơ chế chống xem source.
- Persistence: luôn `save()`/cloud client; không tự tạo key localStorage chung
  cho mọi tài khoản. `state.lineSession`, `lineAttempts`, `lessonViews` đã có
  sanitize/replay. Xem bài không phải hoàn thành/đạt trình độ.
- UI bổ sung: v5-ui (account/admin), online-play (PvP), v6-learning-ui,
  v6-ui (presentation) theo thứ tự. Khi thay render, giữ các lớp bảo vệ;
  học phải tôn trọng activeGame và CCOnline live guard.
- PvP: server giữ room/game/revision/nonce/clock; không lấy whole client JSON
  làm ván chính thức. Review phải khớp `online-<gameId>` đã kết thúc trên server.
- Một instance/worker: engine semaphore và lifecycle phòng có scope process.
  Chưa được tăng nhiều worker/replica mà không thiết kế lại điều phối.

## Các phần cần ưu tiên

1. Xác minh GCP/Pikafish qua quyền riêng: version, path, NNUE, UCI handshake,
   search hai bên, timeouts, load. Không dùng URL Console như API.
2. Email recovery: verified email, token ngẫu nhiên một lần có hạn, chống
   dò tài khoản, rate limit, thu hồi phiên, provider gửi thư chỉ backend.
   Không log token, không dùng mật khẩu gửi qua mail. Cần owner duyệt dịch vụ.
3. Nhập tiến độ riêng có preview/dry-run, schema/version, validation và chọn
   merge; không nhập answer keys hoặc quyền admin. Bảo toàn cô lập tài khoản.
4. Phát triển nội dung trung/nâng cao thật: FEN + cây biến + tiêu chí chấm +
   nguồn/quyền + bằng chứng engine + người duyệt. Hai bài hiện cùng họ chiến
   thuật, không đủ tuyên bố coverage hoặc trình độ chương.
5. LLM explanation dùng schema từ evidence; thất bại chuyển template có nhãn.
   Không sinh nước, nhận định không có căn cứ hay chấm khả năng chỉ từ độ dài
   câu trả lời. Cần rubric, tập kiểm thử và đồng ý dữ liệu trước gửi provider.
6. 7 cấp bot, hàng đợi ưu tiên bot, deadline10s, chính sách10 ván: cần kiểm tra
   thực tế, không gán Elo. Nghiệm thu mất engine không trừ thời gian người chơi.
7. Tiếng Anh còn thiếu, auto-flip local, drawing answers, public profile,
   calendar/dashboard, luật lặp/chiếu đuổi, chat có quản trị và retention phòng.

## Hợp đồng phát hành

Chạy `python tools/run_checks.py`, browser E2E, đọc diff, cập nhật report,
rồi tạo pack mới bằng `tools/build_v6_pack.py`. Không bỏ hoặc làm yếu test
đang fail. Kiểm tra pack sau giải nén ở thư mục mới; hash khớp không thay thế
test chạy. Không tự deploy/push/DNS/chi tiền/chuyển DB thật khi chưa được chủ
sản phẩm duyệt. Không xóa tài liệu gốc hoặc dữ liệu của người chơi.

## Demo 60 giây khi chưa có Pikafish

Vào khách → Hành trình học → một chương/bài → bài nhiều lượt. Tự trả lời ba
câu, thử nước, xem đối thủ đáp, hoàn tất chuỗi rồi mở giải thích. Hoàn thành
và thấy lịch ôn, reload để kiểm tra lưu. Một cửa sổ ẩn danh khác tạo khách
phòng PvP để thử kết nối cùng server. Đây là minh họa local, không xác nhận
khả năng chơi Internet hay sức cờ engine thật.
