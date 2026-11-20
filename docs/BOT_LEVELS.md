# Thiết kế bot nhiều cấp (việc J, chỉ thiết kế)

Trạng thái: viết ngày 20/11/2026 theo quyết định số 6 của chủ dự án
(19/11/2026): giới hạn số nút + chọn ngẫu nhiên trong top MultiPV, nhãn "Cấp 1–7,
chưa hiệu chỉnh", không gán Elo. Chủ dự án trả lời 5 câu hỏi ngày 21/11/2026
(mục 10). **J1 (mục 4) đã làm ngày 21/11/2026**; J2–J4 đang làm.

## 1. Hiện trạng và ràng buộc

- Bot có hai lựa chọn: **máy cơ bản** (tìm kiếm heuristic 1–2 nửa nước trong
  trình duyệt) và **máy chủ** (Pikafish, `go movetime 600`, luôn chọn nước tốt
  nhất, `requireStrong: true`, không lặng lẽ thay bằng tìm kiếm nông).
- Binary Pikafish trên VM (bản 2026-09-06) **không có** `Skill Level`,
  `UCI_LimitStrength` hay `UCI_Elo`; chỉ có `Threads`, `Hash`, `MultiPV`,
  `Move Overhead`, `nodestime`, `UCI_ShowWDL`, `EvalFile`… Vì vậy không thể đặt
  sức cờ bằng tùy chọn của engine; phải giới hạn tìm kiếm và chọn nước.
- VM: 2 vCPU, 3,8 GiB RAM, **không có swap**. Một CPU cần dành cho web/SQLite.
- Trước J1, `app/pikafish.py` mở một tiến trình Pikafish mới cho mỗi yêu cầu
  (khởi động, bắt tay UCI, nạp NNUE) và chỉ có một suất engine; yêu cầu thứ hai
  bị từ chối ngay (`engine_busy`), không có hàng đợi. Từ J1: một tiến trình sống
  lâu và hàng đợi ưu tiên (mục 4).
- `PROJECT.md`: không dùng độ sâu 1/2 của máy cơ bản để giả bảy cấp; chờ engine
  tối đa mong muốn 10 giây/nước; một instance, một worker.
- Đo tải ngày 20/11/2026 (`tools/load_rooms.py`): SQLite đã là nút thắt ở
  khoảng 35–40 yêu cầu/giây; bot không được làm nặng thêm phần đó.

## 2. Mục tiêu và ngoài phạm vi

Mục tiêu: 7 cấp có sức cờ **tăng dần đo được** (cấp sau thắng cấp trước nhiều
hơn thua), mỗi nước của bot trả trong **≤ 10 giây kể cả thời gian chờ**, nhãn
trung thực, không ảnh hưởng PvP.

Ngoài phạm vi: Elo hay so sánh với hệ xếp hạng nào; bot cho ván online; phân
tích sau ván (giữ như hiện tại); bot chạy trong trình duyệt.

## 3. Bảy cấp

Mọi cấp đều dùng Pikafish trên máy chủ. Mỗi nước: `go nodes N` với `MultiPV K`,
nhận về tối đa K nước kèm điểm (centipawn hoặc mate, theo góc nhìn bot), rồi
chọn một nước theo luật của cấp.

| Cấp | Nút tìm kiếm `N` | `MultiPV K` | Cách chọn trong K nước | Cho phép kém nước tốt nhất tối đa |
|---|---|---|---|---|
| 1 | 2.000 | 5 | ngẫu nhiên đều | 400 cp |
| 2 | 5.000 | 5 | ngẫu nhiên đều | 300 cp |
| 3 | 10.000 | 4 | softmax, T = 150 cp | 250 cp |
| 4 | 30.000 | 4 | softmax, T = 100 cp | 150 cp |
| 5 | 100.000 | 3 | softmax, T = 60 cp | 100 cp |
| 6 | 300.000 | 2 | softmax, T = 30 cp | 50 cp |
| 7 | ~600 ms (như bot máy chủ hiện nay) | 1 | luôn nước tốt nhất | 0 |

Đây là **giá trị khởi điểm chưa hiệu chỉnh**; mục 7 mô tả cách đo để sửa.

Luật chọn nước:
1. Bỏ các nước kém nước tốt nhất quá ngưỡng của cấp (cột cuối). Luôn còn ít
   nhất nước tốt nhất.
2. Softmax: xác suất của nước *i* tỉ lệ `exp((điểm_i − điểm_tốt_nhất) / T)`.
   Điểm mate được đổi thành ±(30.000 − số nửa nước) trước khi tính.
3. Có nước chiếu bí ngay (mate in 1) thì cấp ≥ 2 luôn đi; cấp 1 đi với xác suất
   50% (người mới vẫn thấy bot "bỏ lỡ") — quyết định 21/11/2026.
4. Chỉ một nước hợp lệ: đi luôn, không gọi engine.
5. Nước được chọn phải nằm trong `pos.legal_moves()` của `app/rules.py`; nếu
   không, trả lỗi, không đoán.
6. Ngẫu nhiên phía máy chủ (`secrets.SystemRandom`), không lấy hạt giống từ
   client. Ghi lại thứ hạng nước đã chọn và độ chênh điểm vào `provenance`.

Ghi chú: với số nút nhỏ, điểm MultiPV dao động mạnh; đó là một phần của việc
làm yếu, không phải lỗi. Không hiển thị điểm này cho người học trong ván.

## 4. Hàng đợi và hạn 10 giây

1. **Một tiến trình Pikafish sống lâu** (`Threads 1`, `Hash 32`) thay cho mở
   mới mỗi lần; gửi `ucinewgame` khi đổi ván, `isready` trước mỗi lệnh. Khởi
   động lại khi tiến trình chết, quá hạn hoặc trả dữ liệu lạ. Bộ nhớ dự kiến
   dưới 150 MB (NNUE + hash), phải đo trên VM.
2. **Hàng đợi một luồng xử lý**, ưu tiên: `bot` (người đang chờ trong ván) >
   `review` (người đang xem) > `review-scan` (quét cả ván). Mỗi người tối đa 1
   yêu cầu đang chờ; hàng đợi tối đa 8 yêu cầu.
3. **Hạn 10 giây tính từ lúc nhận yêu cầu.** Khi nhận, ước lượng thời gian =
   tổng thời gian dự kiến của các việc đứng trước + việc này; nếu vượt 10 giây
   thì trả ngay 429 `engine_busy` với `retryAfter` (như hiện nay), không xếp
   hàng vô ích. Việc đang chạy vượt hạn thì `stop` và trả lỗi.
4. Thời gian dự kiến mỗi cấp lấy từ số đo thực tế trên VM (trung bình trượt),
   không đoán từ số nút.
5. Bot hết hạn hoặc engine không sẵn sàng: báo rõ "Máy chủ đang bận/chưa sẵn
   sàng", giữ ván, cho chọn thử lại hoặc chuyển sang **máy cơ bản** có nhãn
   riêng. Không bao giờ âm thầm thay nước Pikafish bằng nước của máy cơ bản.

## 5. Đổi cấp

Theo quyết định đã ghi trong PROJECT.md (chưa triển khai): xét **10 ván bot đã
kết thúc gần nhất ở cùng một cấp**; thua ≥ 6 thì xuống một cấp, thắng ≥ 7 thì
lên một cấp (mặc định tự đổi, xem quyết định 1).

- Tính: thắng, thua (kể cả xin thua, hết giờ). Hòa tính là không thắng không
  thua. Không tính: ván bỏ dở, ván `needsVerification`, ván có xin đi lại.
- Cấp 1 không xuống, cấp 7 không lên. Đổi cấp xong thì đếm lại từ đầu.
- Mặc định cấp tự đổi khi đủ điều kiện và báo cho người học; người học luôn
  chọn cấp tự do và tắt được việc tự đổi (quyết định 1, mục 10).
- Dữ liệu đếm nằm trong tiến độ học của người dùng như các ván hiện có, không
  cần bảng mới.

## 6. Nhãn và trung thực

- Hiển thị "Cấp 3 · chưa hiệu chỉnh". Không có Elo, không có "tương đương
  người chơi X".
- Trang giới thiệu bot: cấp được làm yếu bằng giới hạn tìm kiếm và chọn ngẫu
  nhiên trong các nước tốt nhất; chưa hiệu chỉnh theo người thật.
- `provenance` mỗi nước: cấp, số nút, MultiPV, thứ hạng nước đã chọn, chênh
  điểm, thời gian. Chỉ dùng để kiểm tra và hiệu chỉnh, không hiện trong ván.
- Trong ván vẫn không có coaching; phân tích sau ván vẫn dùng chế độ mạnh.

## 7. Hiệu chỉnh trước khi phát hành

Làm trên **VM thử** (không phải production), bằng một công cụ tự đấu mới:

1. Mỗi cặp cấp liền nhau đấu 100 ván, đổi màu luân phiên, khai cuộc từ 10 thế
   khởi đầu khác nhau. Mục tiêu: cấp cao hơn đạt 65–85% điểm. Dưới 60% thì tăng
   khoảng cách nút hoặc giảm `T`; trên 90% thì thu hẹp.
2. Đo thời gian mỗi nước p50/p95 từng cấp và bộ nhớ của tiến trình.
3. Thêm 20 ván người thật (pilot) mỗi cấp 1–3 để xem cấp 1 có thực sự dễ
   không; chỉ ghi nhận định tính, không suy ra Elo.
4. Ghi kết quả và bảng tham số cuối vào tài liệu này.

## 8. Thay đổi dự kiến (khi được duyệt)

| PR | Nội dung | Kiểm thử |
|---|---|---|
| J1 | Tiến trình Pikafish sống lâu + hàng đợi ưu tiên + hạn 10 giây | UCI giả: xếp hàng, ưu tiên, quá hạn, tiến trình chết, từ chối khi đầy |
| J2 | `level` 1–7 cho `purpose: "bot"`, luật chọn nước, `provenance` | UCI giả trả MultiPV cố định: ngưỡng, softmax, mate, một nước hợp lệ, nước sai luật |
| J3 | Chọn cấp trong giao diện, nhãn, tự đổi cấp theo 10 ván (tắt được), tiếng Anh | luật đếm ván, nhãn không có Elo, không coaching trong ván |
| J4 | Công cụ tự đấu và hiệu chỉnh (chạy trên VM thử) | chạy ngắn trong test với UCI giả |

API: `POST /api/engine/analyze` thêm `level` (số nguyên 1–7, chỉ với
`purpose: "bot"`); máy chủ tự quyết số nút và MultiPV, **không nhận số nút từ
client**. Giới hạn tần suất: tối đa 1 yêu cầu bot đang chờ cho mỗi người.

## 9. Rủi ro

- CPU: cấp 6–7 chiếm gần trọn 1 vCPU khi chạy; nhiều người chơi bot cùng lúc sẽ
  xếp hàng. Hàng đợi + từ chối sớm giữ được hạn 10 giây nhưng có thể báo bận.
- Tiến trình sống lâu: nếu rò bộ nhớ, VM không có swap sẽ giết tiến trình; cần
  khởi động lại định kỳ (ví dụ sau 500 lần tìm kiếm) và theo dõi RSS.
- Cấp thấp có thể đi nước rất "lạ"; đó là chủ ý, nhưng cần ván thử của người
  thật trước khi gắn với bài học.
- Một binary Pikafish khác (có `UCI_Elo`) sẽ làm thiết kế này không còn cần
  thiết; khi đó vẫn không gán Elo khi chưa hiệu chỉnh.

## 10. Quyết định của chủ dự án (21/11/2026)

1. Đổi cấp: **mặc định tự đổi** theo luật 10 ván (mục 5); người học luôn tự chọn
   được cấp bất kỳ, và tắt được việc tự đổi.
2. **Chỉ cấp 1** có thể bỏ lỡ chiếu bí trong một nước (xác suất 50%); từ cấp 2
   luôn đi nước chiếu bí ngay khi tìm thấy.
3. Bot nhiều cấp vẫn cần đăng nhập (giới hạn tải).
4. Người mới bắt đầu ở **cấp 2**; có thể đổi trong bản cập nhật sau nếu khoảng
   cách giữa các cấp quá lớn.
5. Làm J1 trước, rồi giảm tải PvP, rồi J2–J4; làm hết rồi mới deploy.
