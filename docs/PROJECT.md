# Cờ Chill — tài liệu dự án

Tài liệu duy nhất về trạng thái hiện hành: kiến trúc, quyết định sản phẩm, luật
và ký phổ, giới hạn, dữ liệu, nguồn và quy trình đóng góp. Cách chạy và giới
thiệu chung ở [README](../README.md); vận hành máy chủ ở
[deploy/DEPLOY_GCP_VI.md](../deploy/DEPLOY_GCP_VI.md); thuật ngữ dịch ở
[I18N_GLOSSARY.md](I18N_GLOSSARY.md); định dạng nhập thế cờ ở
[POSITION_IMPORT.md](POSITION_IMPORT.md); thiết kế bot nhiều cấp (chưa làm) ở
[BOT_LEVELS.md](BOT_LEVELS.md). Tài liệu lịch sử nằm trong
[`old/`](../old/README.md) và không mô tả trạng thái hiện tại.

Website Production được chủ dự án xác nhận đang chạy tại cochill.vn. Source và
tài liệu trong repo không phải bằng chứng trực tiếp về VM, khả năng chịu tải
hay mức sẵn sàng vận hành.

## 1. Kiến trúc và ranh giới code

- Entry point: `python co_chill_server.py serve --port 8769`. Backend dùng
  Python standard library, WSGI và SQLite; Gunicorn chỉ là tùy chọn khi deploy
  Linux. Frontend trong `web/` không có bước build; script nạp theo đúng thứ tự
  trong `web/index.html`. Không mở `index.html` bằng `file://` khi thử tài
  khoản, đồng bộ hoặc PvP.
- Luật: `app/rules.py` và `web/xiangqi.js`, có kiểm tra đối chiếu bằng
  `tools/check_browser_rules.py`.
- Bằng chứng phân tích: `app/pikafish.py` và `web/engine-client.js`. Kiểm tra
  mọi PV hợp lệ, góc nhìn điểm, mate/cp và bound; không để LLM tự chế nước hay
  điểm.
- Học: phiên bài cơ bản ở `learning.js` + `experience.js`; bài nhiều lượt ở
  `line-practice.js`; `curriculum.js` chứa nội dung và cây đáp án.
  `web/fixtures.js` sinh bằng `python tools/export_preview_fixtures.py`, không
  sửa tay. Thế cờ mới đi qua `tools/import_positions.py` (chỉ kiểm luật, sinh
  bản nháp `line-v1` ngoài `web/`; xem POSITION_IMPORT.md). 70 bài của chủ dự
  án nằm trong `web/curriculum-pack.js`, sinh bằng
  `python tools/import_curriculum_xlsx.py --write` từ file Excel trong
  `var/import/` và bản dịch `tools/curriculum_pack_en.json`, không sửa tay;
  `curriculum.js` nối các bài này sau bài cũ, `content-en.js` dựng mục tiếng
  Anh từ đó. Frontend vẫn đọc được đáp án; reflection gate là thiết kế học, không
  phải cơ chế chống xem source.
- Persistence: luôn đi qua `save()` và cloud client; không tạo key localStorage
  chung cho mọi tài khoản. Xem bài không phải là hoàn thành hay đạt trình độ.
  Nhập tiến độ (`progress-import.js`) chỉ trả state mới qua cùng bộ sanitize
  với đồng bộ; Cài đặt hiện xem trước rồi mới `save()`.
- Lớp UI bổ sung theo thứ tự: `v5-ui.js` (tài khoản/quản trị), `online-play.js`
  (PvP), `v6-learning-ui.js`, `v6-ui.js` (trình bày), `public-profile.js` (hồ sơ
  công khai, nạp cuối để thêm vào trang đã dựng). Khi đổi render, giữ các
  lớp bảo vệ; phần học phải tôn trọng `activeGame` và guard `CCOnline`.
- PvP: server giữ phòng, ván, revision/nonce và đồng hồ; không lấy JSON của
  client làm ván chính thức. Review phải khớp `online-<gameId>` đã kết thúc trên
  server.
- Một instance, một worker: semaphore engine và vòng đời phòng gắn với process.
  Không tăng worker/replica khi chưa thiết kế lại điều phối.

## 2. Quyết định sản phẩm (V6, 25–26/10/2026)

Tóm từ câu trả lời V6 của chủ sản phẩm; không tự đổi câu trả lời của chủ dự án.

### Phạm vi và vận hành

- Chủ sản phẩm muốn UI, tài khoản, Pikafish, bài nhiều lượt và PvP cùng có;
  kho dữ liệu lớn bổ sung sau. Pilot dự kiến 5–10 người, chưa phải số người
  dùng thực.
- Google Cloud cho web/API/database/engine, cochill.vn làm tên miền. Ngân sách
  dịch vụ khác tối đa 200.000 VND/tháng, Google Cloud tính riêng.
- Chủ sản phẩm duyệt trước push/deploy, DNS, thay máy, chi phí, chuyển dữ liệu
  thật hoặc gửi email. Không khôi phục cơ chế tự duyệt cũ.

### UI và thông tin

| Quyết định | Trạng thái |
|---|---|
| Giữ logo/cover, font rõ dấu Việt, cover rộng đầu trang | Có; không thay chữ thương hiệu trong ảnh |
| Vào bằng màn tài khoản/khách, không tự vào Home | Có; chọn khách không giả tạo tài khoản server |
| Ba theme ấm/lạnh/tối, dễ tìm trong cài đặt | Có thẻ chọn/xem trước và lưu theo hồ sơ |
| Tiếng Việt trước, có chế độ tiếng Anh | Giao diện, bài học và thông báo server có tiếng Anh, được `tools/test_i18n_en.cjs` kiểm tra |
| Thêm bàn cờ/hình thay văn bản dài | Bàn cờ ví dụ, thẻ chương, icon; chưa có minh họa riêng cho mọi bài |
| Chơi giữ đối thủ, đồng hồ, ký phổ, hòa/thua | Có; PvP từ trạng thái server |
| Tự lật bàn mỗi lượt khi hai người cùng máy | Có; mặc định bật (chủ dự án chốt 19/11/2026), tắt bằng công tắc ngay dưới bàn hoặc trong Cài đặt; khi bật thì ẩn nút lật thủ công |
| Dashboard học gọn, calendar tuần; admin đầy đủ | Có dashboard và lịch tuần (thứ Hai–Chủ nhật, giờ Việt Nam: lượt đã luyện mỗi ngày, hình cần ôn từ hôm nay) trên trang Tiến độ; chưa đúng mọi bố cục đã chốt |

### Học, bài tập và engine

- 3 khóa khai/trung/tàn, 8 chương; trung cuộc có Xe, Pháo, Mã, Tốt (thêm
  20/11/2026, đứng sau Mã), an toàn Tướng và phối hợp. Người học chọn chương tự
  do. Có bản đồ chương và 9 bài hướng dẫn; bài của chương Tốt (thêm 20/11/2026)
  gồm 4 hình: hướng đi trước/sau sông, ăn quân, hàng cuối, lưới hai Tốt và mặt
  Tướng, mỗi câu đều được test đối chiếu với bộ luật.
- 12 bài cũ là bài cơ bản. Hai bài nhiều lượt thí điểm có cây quyết định hợp
  lệ, mục tiêu chiếu hết bằng chuỗi chiếu liên tục, 3–4 lượt quyết định trên
  các nhánh được duyệt; cả hai cùng một họ chiến thuật.
- 70 bài nhiều lượt do chủ dự án soạn và duyệt (nhập 20/11/2026): 35 chiếu hết,
  35 ăn quân/giành ưu thế; 50 trung cấp, 20 khó; 62 bài Đỏ đi trước, 8 bài Đen
  đi trước (bàn cờ đặt bên người học ở dưới). Quyết định của chủ dự án
  20/11/2026: trước khi giải chỉ hiện mục tiêu chuẩn sinh từ dữ liệu ("Đen đi
  trước. Chiếu hết trong 5 lượt đi của bạn."); nhận định, ý tưởng chính, vì sao
  phải hành động ngay, lý do từng nước và phản ứng cần lưu ý chỉ hiện ở phần lời
  giải, theo từng nước mẫu; tiêu đề tự sinh ("Pháo · Chiếu hết 3"); nước hợp lệ
  ngoài cây chờ kiểm chứng, không chấm sai; ở nước cuối bài chiếu hết, mọi nước
  chiếu bí ngay đều được nhận (bộ luật kiểm tra); kỹ năng: Pháo → cannon, Mã →
  horse, chiếu hết khác → safety, ăn quân khác → material; quyền `own-work`.
- Độ khó mục tiêu: cơ bản 1–2 quyết định, trung cấp 3–4, khó/nâng cao 5–7 (chủ
  dự án chốt 5–7 ngày 20/11/2026). Không kéo dài giả bằng nước vô nghĩa.
- Chỉ ba câu suy nghĩ ban đầu, sau đó chọn nước và xem phản ứng đối thủ. Sai
  giữ checkpoint; sau ba lần sai đặt lại gốc và hẹn ngày sau. Nhánh hợp lệ
  ngoài cây duyệt được giữ để kiểm chứng, không bị kết luận sai bằng máy nông.
- Lời giải mở sau suy nghĩ và nước ứng viên. Hoàn thành cả chuỗi mới ghi lần
  thử/lịch ôn; xem lời giải và có trợ giúp được ghi rõ. Có lưu nháp/khôi phục.
- Bài liên quan ưu tiên phù hợp/chưa gặp nhưng không hiển thị nhãn đã gặp/chưa
  gặp. Sau bài nhiều lượt, gợi ý trước bài cơ bản cùng kỹ năng; mỗi chương có
  khối bài cơ bản cùng kỹ năng.
- Cấp chương sau 10 bài khác nhau là quyết định chưa đủ dữ liệu để nghiệm thu.
  Không nhân bản bài để đạt 10. EXP/cấp là heuristic, không phải Elo hay ML.
- Chờ engine tối đa mong muốn 10 giây/nước. Bot máy chủ và review tài khoản
  bật `requireStrong`; API báo lỗi khả dụng nếu adapter fallback, không thay
  bằng tìm kiếm nông. Bài cơ bản có nhãn vẫn chạy local.
- 7 cấp bot và đổi cấp theo 10 ván (thua ≥6 hạ, thắng ≥7 tăng) chưa hiệu chỉnh
  hay triển khai. Không dùng độ sâu 1/2 để giả bảy cấp.
- LLM cá nhân hóa/nhận xét lập luận chưa có provider, key hay rubric. Lời giải
  hiện là mẫu dựa trên luật/cây bài, hoặc lời giải thích chủ dự án tự viết cho
  70 bài nhập từ file Excel (quyết định 19/11/2026).

### Tài khoản và dữ liệu

| Quyết định | Trạng thái |
|---|---|
| Username/password, một phiên tài khoản; social sau | Có scrypt/cookie/thu hồi phiên cũ |
| Quản trị xem người đăng ký và thống kê | Có owner TOTP và vai trò report riêng |
| Email tự khôi phục mật khẩu | Chưa có |
| Đồng bộ chơi/học, không lẫn danh tính | Có revision/conflict và phạm vi local từng người |
| Xuất/xóa dữ liệu của mình | Có; backup phải xử lý xóa riêng |
| Nhập file tiến độ cũ tự động | Có nhập file xuất của Cờ Chill trong Cài đặt: xem trước, chọn gộp hoặc thay thế, xác nhận dữ liệu của mình; vẫn có chuyển guest trong cùng origin và nhập ký phổ |
| Công khai display name/avatar; lịch sử public/private | Có hồ sơ công khai `#u/<mã ngẫu nhiên>`: tên hiển thị, tháng tham gia, thắng/thua/hòa và 20 ván online đã kết thúc (xem biên bản). Tài khoản mới công khai mặc định; tài khoản cũ riêng tư tới khi tự chọn; tên đối thủ theo cài đặt của đối thủ (chủ dự án chốt 19/11/2026). Chưa có avatar |
| Phản hồi/report lưu và xuất riêng | Có quản trị phản hồi |
| Gom ván người chơi làm dữ liệu học | Không tự bật; cần đồng ý rõ ràng; không gửi dữ liệu huấn luyện |

### PvP

- Phòng riêng/công khai; ghép theo preset thời gian, chưa theo trình độ.
- Khách có cookie phòng 24 giờ, riêng với đăng nhập học tập. Hai người cùng
  sẵn sàng trước khi đồng hồ chạy; màu đầu ngẫu nhiên, tái đấu đổi màu.
- Server kiểm tra quyền, lượt, nước, revision/nonce, đồng hồ và kết quả; client
  không tự khai thắng, FEN hay số giây. Mời hòa 15 giây, xin thua có xác nhận,
  xin đi lại cần đối thủ duyệt; có khán giả và mời khán giả rời.
- Một bên mất kết nối 30 giây khi bên kia còn hoạt động có thể thua. Cả hai mất
  hoặc server restart thì tạm dừng; cần cả hai sẵn sàng để tiếp tục.
- Chat chỉ có tin nhắn trung tính định sẵn. Chặn engine/coaching của app trong
  ván, nhưng không ngăn được thiết bị/engine ngoài. Giao hữu, không xếp hạng.

## 3. Luật và ký phổ

Nguồn đã tra cứu:
[World Xiangqi Rules 2018 (WXF)](https://www.wxf-xiangqi.org/images/wxf-rules/2018_World_XiangQi_Rules_English2018.pdf)
(Điều 3.1 H–I, 3.2 B–D, 8, 19; lặp hòa xét bốn lần xuất hiện, hai bên cùng
chiếu không suy ra bên chiếu trước thua),
[trang giới thiệu của WXF](https://www.wxf-xiangqi.org/index.php?Itemid=291&id=269&lang=en&option=com_content&view=article)
và [luật Ziga](https://zigavn.com/cotuong/luat-co-tuong) cho cách trình bày ký
phổ Việt (Tg, S, X, M, P, B; từ 04/11/2026 Tượng ghi là V; tiến `.`, thoái `/`,
bình `-`). Không sao chép hình, bộ bài hay toàn văn nguồn; ví dụ kiểm thử là
thế tự tạo. Đây không phải chứng nhận chuẩn trọng tài giải đấu.

1. Luật đi quân nằm trong `web/xiangqi.js`, có kiểm thử đối chiếu Python. Không
   module nào tạo tập nước đi riêng.
2. Ký phổ Việt sinh từ thế trước nước đi. Lộ 1–9 tính theo bên đang đi; lật
   giao diện không đổi ký phổ. Mã/Sĩ/Tượng ghi lộ đến; Xe/Pháo/Tướng/Tốt tiến
   hoặc thoái ghi khoảng cách. Quân cùng loại cùng lộ ghi `t`/`s`, hoặc
   `t`/`g`/`s` khi có ba Tốt (chi tiết: I18N_GLOSSARY mục 4).
3. Nhập ký phổ chỉ khớp tập nước hợp lệ của đúng thế hiện tại; ký hiệu mơ hồ bị
   từ chối. Không nhận tọa độ máy, chữ "tiến/thoái/bình" hay `T` cho Tượng;
   chưa hỗ trợ PGN/XQF, chữ Hán, biến phân nhánh hay chú thích xen giữa nước.
4. Biên bản hai cột: Đỏ trái, Đen phải; FEN bắt đầu lượt Đen thì ô Đỏ hàng đầu
   để trống.
5. Nước không hợp lệ chỉ báo nguyên nhân luật (cản chân/mắt, ngòi Pháo, qua
   sông, ra khỏi cung, cùng bên, tự chiếu, đối mặt Tướng); không gợi ý nước.
6. Lặp ba lần chỉ cảnh báo; lặp bốn lần xét trên toàn bàn và bên đến lượt.
7. Chiếu liên tục một bên trong ba đoạn giữa lần xuất hiện thứ nhất và thứ tư:
   bên đó thua. Triển khai hẹp, chưa có quy trình cảnh cáo/trọng tài.
8. Lặp yên tĩnh chỉ tự hòa khi không có nước chiếu và không có nước bắt quân hợp
   lệ nào của cả hai bên trong chu kỳ.
9. Hai bên cùng chiếu, chiếu xen bắt hoặc khả năng đuổi: trả
   `needsVerification: true`, không tự gán kết quả và không cộng vào thống kê.
   Mỗi nước trong chu kỳ được gắn `check`, `threat` (sau nước đó quân vừa đi
   ăn được quân, hoặc quân khác có thêm nước ăn mới) hoặc `idle`; nhãn
   `perpetual-chase-review` (một bên đe dọa mọi nước, bên kia chỉ chờ, kèm
   `chaser`), `check-chase-review`, `mutual-chase-review`,
   `idle-repetition-review` hoặc `repetition-review` chỉ giúp người duyệt, không
   phải phán quyết. Chưa xét quân được bảo vệ, căn thật/giả, ghim, ngoại lệ
   Tướng/Tốt hay Mã/Pháo đuổi Xe; phòng online trên máy chủ chưa dùng bộ phân
   loại này.
10. Không bắt quân: đếm từ các nước đã có, ăn quân thì về 0; từ 100 nửa nước chỉ
    yêu cầu kiểm chứng.
11. Chiếu hết và hết nước hợp lệ ưu tiên trước lặp thế: bên không còn nước thua.

API `web/game-tools.js` (nối vào `CC` trên trình duyệt, xuất CommonJS để test):
`notateMove`, `parseNotation`, `parseGameNotation`, `pairMoveHistory`,
`illegalMoveReason`, `repetitionStatus`. Module dựng lại từng nước bằng bộ luật,
không tin FEN do đầu vào cung cấp. Test: `node tools/test_preview_game_tools.cjs`.
Còn cần người duyệt ví dụ luật có FEN và toàn lịch sử, xác nhận phiên bản điều
lệ áp dụng và cách xử lý ván cần kiểm chứng.

## 4. Giới hạn hiện tại

### Chưa hoàn tất

- Chưa xác minh độc lập VM Google Cloud, binary/NNUE Pikafish thật, HTTPS/DNS,
  tải thực hoặc backup/restore. Thông số VM, service và lịch backup là thông tin
  do chủ dự án cung cấp.
- Chưa có email tự khôi phục mật khẩu, OAuth, avatar, chat tự do có quản trị.
  Không dùng tài khoản pilot làm kho lưu duy nhất cho dữ liệu quan trọng.
- Hồ sơ công khai chỉ có ván online do máy chủ ghi; không có tìm kiếm người
  chơi, theo dõi hay bình luận. Hồ sơ riêng tư, chưa chọn, bị khóa, quản trị hoặc
  không tồn tại đều trả cùng một lỗi 404. Ai có link đều xem được hồ sơ công
  khai; người vận hành chưa có công cụ ẩn một hồ sơ ngoài khóa tài khoản.
- Chưa có LLM chấm tư duy/cá nhân hóa, bảy cấp bot hiệu chỉnh, chính sách lên
  xuống cấp sau 10 ván hoặc hàng đợi ưu tiên bot với SLA 10 giây đã đo.
- Kho bài: 12 cơ bản, 9 hướng dẫn, 72 bài nhiều lượt (2 thí điểm + 70 bài của
  chủ dự án). Chương Khai cuộc, Xe, An toàn Tướng và Phối hợp quân đã có ít
  nhất 10 bài; Pháo, Mã, Đường thoát của Tướng có 9, Tốt có 5, nên các chương
  này chưa đủ 10 hình để đánh giá cấp. Các chương Xe, Pháo, Mã, An toàn Tướng và
  Đường thoát của Tướng gợi ý lại 12 bài cơ bản theo kỹ năng; chương Tốt và
  Khai cuộc chưa có bài cơ bản cùng kỹ năng. Hình minh họa luật chỉ được bộ luật
  kiểm tra tính hợp lệ, không phải nội dung chiến thuật được chuyên gia thẩm
  định.
- 70 bài của chủ dự án: nước đúng và nước đáp theo cây tác giả đã duyệt, có đối
  chiếu Pikafish ngoài ứng dụng (sheet `Engine_doi_chieu` không được nhập; ở 5
  bài cây chọn nước đáp khác engine và cây là chuẩn). Ứng dụng chỉ chứng minh
  luật từng nước, chiếu bí ở cuối bài chiếu hết và quân lực cuối biến hơn lúc
  đầu (thang điểm quân thô: Xe 9, Pháo 4,5, Mã 4, Sĩ/Tượng 2, Tốt 1) ở bài ăn
  quân; không chứng minh đó là nước tốt nhất hay nước đáp mạnh nhất, và không
  đo mức ưu thế (ví dụ `mid-opening-04` chỉ hơn khoảng 1,8 tốt theo engine).
  Mỗi nước đúng chỉ có một nước đáp; nước hợp lệ ngoài cây (kể cả nước dẫn tới
  chiếu bí chậm hơn) chờ kiểm chứng, nên bài mới chưa có ba lần sai/hẹn học
  tiếp. Ký pháp hiển thị do ứng dụng sinh từ UCI; trong lời giải của tác giả,
  ký pháp viết thường được đổi sang chữ hoa (x5.5 → X5.5).
- Bản tiếng Anh của 70 bài (nhận định, ý tưởng, lý do từng nước, phản ứng cần
  lưu ý) do Claude dịch ngày 20/11/2026 theo bảng thuật ngữ, chủ dự án đã duyệt
  cùng ngày; tiêu đề và mục tiêu tiếng Anh sinh từ mẫu. Cùng ngày, theo yêu cầu
  của chủ dự án, file Excel được sửa 8 ô (thiếu "Đen đi trước.", ký pháp
  "ss.5"/"b4t.1", lỗi gõ, hai câu thiếu chữ; bản gốc sao lưu trong `var/import/`).
- `tools/import_positions.py` (file JSON) chỉ kiểm luật, trùng thế và trường bắt
  buộc; không đánh giá nước tốt nhất, mục tiêu "advantage" vẫn chỉ thành bản
  nháp `line-v1-draft`. `tools/import_curriculum_xlsx.py` (file Excel của chủ dự
  án) nhận một file một lần: chạy lại thay toàn bộ `web/curriculum-pack.js`;
  đợt bài sau cần gộp vào cùng file Excel hoặc mở rộng công cụ.
- Câu trả lời bằng mũi tên và dashboard đúng thiết kế cuối chưa đầy đủ. Lịch tuần chỉ đếm
  dữ liệu trên thiết bị hoặc tài khoản đang dùng, chưa có xem tuần trước/sau.
- Chưa xác minh mọi phán quyết lặp/chiếu dai/đuổi dai theo luật giải đấu Việt
  Nam; không đưa ranked lên khi chưa làm phần này.

### Kỹ thuật và dữ liệu

- PvP polling khoảng 2 giây cho người đang chơi (ván đang chơi hoặc tạm dừng);
  người xem, phòng chờ và ván đã kết thúc khoảng 4 giây. Tab nền/mạng yếu có thể
  quá hạn 30 giây và bị coi mất kết nối. Từ 21/11/2026, một lần polling chỉ đọc
  SQLite: trạng thái "đang online" giữ trong bộ nhớ của tiến trình duy nhất và
  phòng chỉ được ghi khi ván đổi (hết giờ, mất kết nối, tạm dừng, hết hạn lời
  mời); giới hạn tần suất polling (180/phút/người) cũng trong bộ nhớ, thao tác
  ghi vẫn giới hạn trong SQLite; hàng chờ kết nối của server tăng từ 5 lên 128.
  Khởi động lại server làm mất trạng thái online, nhưng việc đó vốn đã tạm dừng
  mọi ván. Không chạy nhiều tiến trình/worker cùng lúc.
  Đo bằng `python tools/load_rooms.py` (server local riêng, database tạm, laptop
  Windows; không phải VM 2 vCPU, chưa đo trên VM; không đo production):
  trước khi sửa (20/11) 100 người p95 ~8,6 s kèm lỗi "database is locked", 200
  người có 22/100 ván bị xử thua oan; sau khi sửa (21/11) lấy trạng thái phòng
  100 người p50 ~75 ms / p95 ~0,2 s, 200 người p50 ~150 ms / p95 ~0,36 s, không
  lỗi, không ván nào bị tạm dừng hay xử thua oan. Đi nước vẫn là giao dịch ghi
  xếp hàng: 200 người p95 ~3,2 s. 400 người chưa đo được tin cậy vì chính máy
  đo bị quá tải.
- Ghép cộng đồng theo thời gian, chưa theo trình độ.
- Cookie phòng khách 24 giờ. Giữ phòng và biên bản có khách 30 ngày (chủ dự án
  chốt 19/11/2026) bằng lệnh `prune-rooms`: xem trước, chỉ xóa khi có
  `--confirm`; chưa tự chạy cho đến khi người vận hành cài cron. Backup database
  chạy hằng ngày, giữ 14 ngày (theo chủ dự án), nên bản cũ còn trong backup tới
  khi xoay vòng.
- Xóa tài khoản hoặc khách: ván đã kết thúc chung với người khác được ẩn danh
  ("Người chơi đã xóa", mã ngẫu nhiên riêng từng ván) cho đối thủ giữ lại; ván
  không còn tài khoản nào đọc được thì xóa. Phòng đang chờ/đang chơi có người đó
  vẫn bị đóng, ván dở không được ghi kết quả.
- Thống kê học do client đồng bộ, không chống gian lận.
- Nhập tiến độ chỉ nhận file xuất của Cờ Chill (`co-chill-personal-export` v1,
  `co-chill-account-export-v1`), tối đa 5 MB. Không nhập bài đang làm dở, ván
  chưa kết thúc, ván online, phản hồi, tên hồ sơ, đáp án hay quyền. File xuất cá
  nhân không có mã lượt làm bài nên mã được dựng lại; lượt trùng thời điểm bắt
  đầu và kết thúc được coi là một. Ván được bộ luật chơi lại; kết quả luật không
  tự xác định (xin thua, hết giờ, hòa thỏa thuận) lấy theo file.
- Bài cơ bản và bài nhiều lượt dùng chung một quy tắc lịch ôn: tự làm liên
  tiếp thì giãn 1/2/7/14/30 ngày, có trợ giúp thì 2 ngày và đặt lại chuỗi, bài
  cơ bản làm sai thì 1 ngày. Ngày ôn bài nhiều lượt được tính lại từ lịch sử khi
  đồng bộ. Đây là quy tắc thử nghiệm, chưa kiểm chứng hiệu quả ghi nhớ.
- Nhánh hợp lệ ngoài cây duyệt dừng chờ kiểm chứng; chưa tự chuyển engine/LLM
  chấm.
- Database, localStorage và backup chưa mã hóa ở mức ứng dụng.
- Bộ kiểm thử chạy trên source; không xác nhận Pikafish thật, VM, HTTPS/DNS,
  hai mạng Internet hay tải lớn, và không phải kiểm toán bảo mật, khả năng truy
  cập hay hiệu quả giáo dục.
- Ngày 28/10/2026 một lượt chạy từng báo 13 assertion fail trong nhóm Pikafish
  rồi tự đạt khi chạy lại. Test hợp đồng NNUE/clamp nay dùng timeout mặc định
  của adapter; điều này chỉ ổn định test. Nếu gặp lại lỗi, lưu log trước khi
  chạy lại.

## 5. Dữ liệu và quyền riêng tư

Mô tả hành vi code, không phải chứng nhận tuân thủ. Trước pilot, người vận hành
cần bổ sung liên hệ, phạm vi độ tuổi, quy trình yêu cầu xóa và thời hạn backup.

| Cách dùng | Dữ liệu |
|---|---|
| Học/chơi local với khách | localStorage: ván, nháp, lượt học, lịch ôn, sở thích |
| Khách tham gia phòng online | Server: danh tính khách, tên hiển thị, phòng, biên bản, lời nhắn mẫu; cookie phòng 24 giờ; sau 30 ngày `prune-rooms` ẩn danh hoặc xóa |
| Đăng nhập | SQLite: username, tên hiển thị, hash mật khẩu, phiên, tiến độ đồng bộ, phản hồi, nhật ký vận hành, mã hồ sơ công khai và lựa chọn công khai/riêng tư |
| Bản nháp tài khoản trên thiết bị | Cache riêng theo tài khoản; không mã hóa |

- Đăng ký không hỏi email, ngày sinh hay số điện thoại. Không tracker, không
  gửi dữ liệu người học cho AI hay để huấn luyện. Gửi phản hồi là thao tác chủ
  động.
- Mật khẩu băm scrypt có salt; token ngẫu nhiên lưu bản băm. Cookie HttpOnly,
  SameSite, Secure khi có HTTPS; một phiên mỗi tài khoản; server kiểm tra
  Origin, CSRF và vai trò. Tên, nước đi, lời nhắn trong phòng được người tham
  gia và người xem thấy; suy nghĩ sau ván không công khai. Hồ sơ công khai (nếu
  bật) cho mọi người có link thấy tên hiển thị, tháng tham gia và ván online đã
  kết thúc; không có tên đăng nhập, mã tài khoản, tiến độ học hay câu trả lời.
- Owner/report thấy thống kê và danh sách/biên bản đã lọc, không thấy mật khẩu,
  token hay câu trả lời phản ánh riêng; report không có quyền quản trị. Người có
  quyền hệ điều hành vẫn đọc được database và backup.
- Có xuất JSON cá nhân, xóa dữ liệu học trên thiết bị, xóa tài khoản (xác nhận
  mật khẩu), xóa khách phòng. File xuất không chứa khóa đáp án; có thể nhập lại
  vào tài khoản hoặc trình duyệt đang dùng sau khi xem trước và xác nhận. Có
  lệnh xem trước/xóa tài khoản không hoạt động 365 ngày và lệnh dọn phòng/khách
  sau 30 ngày (`prune-rooms`), đều chỉ xóa khi người vận hành xác nhận.
- Database và backup là hai nơi khác nhau: yêu cầu xóa phải được áp dụng lại khi
  phục hồi backup; file đã tải xuống không tự bị thu hồi.
- Dùng ván người chơi làm bộ bài chung cần đồng ý riêng.

## 6. AI, nguồn nội dung và bên thứ ba

- Codex, Claude và GitHub Copilot hỗ trợ code, kiểm thử và tài liệu; chủ dự án
  duyệt thay đổi.
- Luật Python/JavaScript quyết định nước hợp lệ. Máy cơ bản là tìm kiếm
  heuristic nông, không phải Pikafish hay ML. `app/pikafish.py` là adapter của
  dự án, không chứa binary, NNUE hay mã Pikafish; test dùng tiến trình UCI giả,
  không chứng minh sức cờ. Kiểm tra giấy phép binary, source và weights trước
  khi tải hoặc phân phối.
- Giải thích dùng template với bằng chứng luật/biến đã kiểm tra, hoặc lời của
  chủ dự án (70 bài nhập từ file Excel, nguồn ghi trong bài: ván tự đấu
  Pikafish hoặc tự dựng). Bản tiếng Anh của phần này do Claude dịch, chủ dự án
  đã duyệt (20/11/2026). Trước khi tích
  hợp LLM cần provider, sự đồng ý dữ liệu, schema bằng chứng, rubric, bộ kiểm
  thử chống bịa và phương án template khi lỗi; mọi nhận định nước/điểm/biến
  phải đối chiếu engine.
- Bài học và 12 bài cơ bản là nội dung tự dựng; không scrape kho ván hay sao
  chép chú giải/sách. Thống kê/cấp/lịch ôn là quy tắc thử nghiệm; không công bố
  Elo, số người dùng hay hiệu quả chưa đo.
- Logo và cover (`web/logo-co-chill.webp`, `web/cover-co-chill.webp`) do chủ
  sản phẩm cung cấp. Bản WebP 02/11/2026 bỏ chữ "CLB CỜ TƯỚNG"; chữ 兵 và 士
  trên ảnh bìa vẽ bằng font Ma Shan Zheng (SIL Open Font License 1.1), chỉ có
  trong ảnh. UI dùng SVG/CSS và font hệ thống, không tải font hay tracker ngoài.
- Gunicorn trong `requirements.txt` dành cho Linux production; giữ giấy phép
  dependency khi phân phối môi trường cài sẵn.
- Tham khảo: [Pikafish](https://github.com/official-pikafish/Pikafish),
  [UCI commands](https://github.com/official-pikafish/Pikafish/wiki/UCI-%26-Commands),
  [networks](https://github.com/official-pikafish/Networks),
  [WCAG](https://www.w3.org/WAI/WCAG22/quickref/). Dẫn nguồn không cấp quyền
  sao chép hay chứng nhận tuân thủ.
- Chủ dự án chưa chọn giấy phép mã nguồn; repo không có `LICENSE`. Không thêm
  license hoặc dataset bên ngoài khi chưa được duyệt.

## 7. Việc tiếp theo

1. Nghiệm thu hai tài khoản trên hai thiết bị và hai mạng thật.
2. Xác minh GCP/Pikafish: version, path, NNUE, UCI handshake, timeout, tải.
3. Email khôi phục mật khẩu: email đã xác minh, token một lần có hạn, chống dò
   tài khoản, rate limit, thu hồi phiên; cần chủ dự án duyệt dịch vụ gửi thư.
4. Nhập tiến độ: đã có xem trước, gộp/thay thế và kiểm tra theo bộ sanitize;
   còn thiếu nhập bài đang dở/ván chưa kết thúc và chưa thử với file lớn thật.
5. Bài trung/nâng cao thật: đã nhập 70 bài của chủ dự án (20/11/2026) với kết
   thúc chiếu hết hoặc hơn quân, bản tiếng Anh đã duyệt. Còn lại: quyết định có chấm "chưa đạt" nước ngoài cây khi có bằng chứng engine
   trong ứng dụng; thêm bài cho các chương chưa đủ 10.
6. LLM giải thích dựa trên schema bằng chứng, có rubric và tập kiểm thử.
7. Bot 7 cấp, hàng đợi và hạn 10 giây: đã có bản thiết kế chờ duyệt
   ([BOT_LEVELS.md](BOT_LEVELS.md)); chưa code, chưa hiệu chỉnh; không gán Elo.
8. Câu trả lời bằng mũi tên, avatar, luật
   lặp/đuổi, chat có quản trị; cài cron cho `prune-rooms` trên VM; thử tải nhỏ
   và chốt luật trước bất kỳ ranked nào.
9. PvP: đã giảm tải polling (21/11/2026, §4). Còn lại: đo trên một VM thử
   (không phải production); nếu cần hơn ~200 người cùng lúc thì giảm thời gian
   ghi của nước đi (dùng lại kết nối SQLite, `synchronous=NORMAL`) hoặc chuyển
   sang kênh đẩy (SSE/WebSocket).

## 8. Quy trình đóng góp

1. Tạo nhánh từ `codex-full`; thay đổi tập trung, thêm hoặc sửa test khi đổi
   hành vi. Sau khi sửa `web/`, chạy `python tools/stamp_static_versions.py`.
2. Chạy từ thư mục gốc: `python tools/run_checks.py` và `git diff --check`
   (Python 3.12; Node theo `.nvmrc`; không cần npm package).
3. Mở Pull Request vào `codex-full`; GitHub Actions
   (`.github/workflows/checks.yml`) phải đạt. Merge bằng merge commit rồi xóa
   nhánh; repo chỉ giữ nhánh `codex-full`.
4. Không push thẳng vào `codex-full`, không viết lại lịch sử. Chỉ chủ dự án
   deploy Production theo `deploy/DEPLOY_GCP_VI.md`.
5. Không làm yếu test, không commit secret, database, dữ liệu người học hay
   backup; giữ chức năng xuất/xóa dữ liệu.
6. Báo lỗi: hệ điều hành, phiên bản Python, commit, các bước tái hiện, kết quả
   mong đợi và thực tế. Lỗi luật kèm thế tự tạo, bên đi và nước đi. Xóa thông
   tin cá nhân khỏi log và ảnh chụp.
