# Cờ Chill — tất cả việc cần làm từ ngày 13/10/2026

Lập ngày 12/10/2026. Đây là kế hoạch hành động đề xuất, không tự động chốt những câu trả lời V4 bạn chưa cung cấp. Mục tiêu tuần đầu: một vòng học dễ hiểu, chạy được, có nội dung cờ đã kiểm tra; tránh mở rộng quá nhiều tính năng.

## 0. Tối nay đã có gì / ngày mai bắt đầu từ đâu

- App đầy đủ chạy local: chơi/nhập ván → review → phản tư → phân tích → thử lại → bài liên quan → lịch ôn → tiến độ.
- Source nằm trong repo `thanhtq2701-alt/xiangqi07`, nhánh `codex-full`; AI đã commit/push. Không cần tạo repo khác hoặc đổi Public để hosting hoạt động.
- Kiểm tra gần nhất: 72/72 test đạt ngày 12/10. Engine local tối đa 2 ply; lời giải template; 12 bài tổng hợp chưa phải bộ chuyên gia duyệt.
- Bản web công khai được chuẩn bị riêng trong đợt này: giới thiệu và hai bài học tương tác từ fixture đã kiểm tra, lưu trên trình duyệt. Nó không chạy backend Python và không đồng bộ SQLite local.
- Hai Word phải trả lời nằm trong deliverables: `Co_Chill_V4_Tien_do_va_Bo_sung_Thong_tin.docx` (84 câu) và `Co_Chill_V4_Bo_sung_UI_UX_Kien_truc_Luat.docx` (272 câu). Câu trùng chỉ cần dẫn mã; chưa biết kỹ thuật thì ghi “đề xuất giúp tôi”.

## 1. Ngày mai 13/10 — lịch tập trung đề xuất

Không bắt buộc giờ cố định. Chia thành các phiên; nghỉ giữa phiên. Nếu thiếu thời gian, hoàn thành ba đầu ra: câu P0, một vòng demo được ghi lỗi, và vài ván có nguồn rõ ràng.

| Phiên | Bạn làm | Đầu ra |
| --- | --- | --- |
| 1 · 30 phút | Đọc README, PUBLIC_READINESS_VI.md; mở bản web; chạy local bằng Mo_Co_Chill.cmd | Hiểu phần thật, phần demo và giới hạn |
| 2 · 60–90 phút | Trả lời 12 câu P0 trong V4 chính | File Word đã trả lời, không cần văn phong đẹp |
| 3 · 60 phút | Trả lời nhóm UI quan trọng: người học, màu/chữ, trang chủ, chơi, phản tư, mobile | 3–5 hình tham khảo kèm điều thích/không thích; không sao chép tài sản |
| 4 · 45–60 phút | Chạy trọn vòng học, ghi lỗi theo mẫu ở mục 5 | 5 vấn đề quan trọng nhất, không cần 50 lỗi nhỏ |
| 5 · 60 phút | Gom ván/position và nguồn luật theo mục 4 | Đợt đầu 3–5 ván hoặc 5–10 thế đủ thông tin |
| 6 · 20 phút | Gửi tài liệu và chọn 3 ưu tiên ngày tiếp theo | Một tin nhắn giao việc rõ ràng; AI tổng hợp và triển khai |

12 câu P0: A01, A02, C03, E02, F01, F04, G02, J01, K01, L02, M01, N01. Trong bộ UI bổ sung, ưu tiên câu đầu của nhóm 1, 2, 3, 6, 7, 8, 10, 11, 12, 15, 16, 17, 19, 21, 24, 27, 28, 31, 32, 34. Các câu còn lại hoàn thành dần; không cần chặn sửa lỗi quan trọng để chờ đủ 356 câu.

## 2. Checklist toàn bộ thông tin bạn cần cung cấp

### Sản phẩm và người dùng

- [ ] Ai học trước: mới biết luật, người chơi phong trào hay nhóm khác?
- [ ] Một phiên học dài bao lâu, dùng điện thoại hay máy tính là chính?
- [ ] Người học thường sai gì; khi nào họ thấy phản tư hữu ích thay vì phiền?
- [ ] Tiêu chí bản đầu thành công: hoàn tất vòng học, hiểu một lỗi, quay lại ôn; không tự nhận cải thiện trình độ nếu chưa đo.
- [ ] Ba việc bắt buộc và ba việc để sau; đề xuất để sau: PvP, 3D, premium, neural network.

### UI/UX và nội dung từng trang

- [ ] Tên sản phẩm, giọng văn, chữ quân Việt/Hán, màu chủ đạo, font, hình khối và độ tương phản.
- [ ] 3–5 website/hình tham khảo: ghi chính xác thích bố cục, màu hay tương tác nào, không chỉ gửi ảnh.
- [ ] Trang chủ: nút chính là chơi, tiếp tục bài hay học từ lỗi?
- [ ] Chơi/nhập ván: kích thước bàn cờ, lịch sử nước, đổi hướng, bàn phím, điện thoại.
- [ ] Review: cách chọn tình huống, số điểm cần xem mỗi ván, thông tin nào nên ẩn.
- [ ] Phản tư: câu hỏi, gợi ý khi “không biết”, tối thiểu cần nhập, khi nào cho xem lời giải.
- [ ] Giải thích: WHAT/WHY/HOW, độ dài, biến minh họa, cách đánh dấu điều chưa chắc chắn.
- [ ] Thử lại/bài liên quan: phản hồi khi sai, gợi ý, tiêu chí bài mới và xử lý đã gặp.
- [ ] Lịch ôn/dashboard: mục tiêu, trạng thái đến hạn, cách tránh tạo cảm giác thành tích giả.
- [ ] Cài đặt/riêng tư: xuất/xóa dữ liệu, thông báo mất phiên, nội dung dễ hiểu.
- [ ] Các trạng thái: trống, đang tải, lỗi mạng, lưu thành công, mất kết nối, mobile, focus bàn phím.

### Luật, engine và chất lượng dạy học

- [ ] Nguồn luật/bộ luật mong muốn, phiên bản và link tài liệu.
- [ ] Những tình huống gây tranh cãi: lặp thế, chiếu dai, đuổi dai, hết nước; cung cấp biên bản cụ thể.
- [ ] Người hoặc phương pháp duyệt lời giải; phân biệt nước hợp lệ với nước tốt nhất.
- [ ] Điều chấp nhận ở prototype: engine nông/template; yêu cầu nào cần engine mạnh mới đạt.
- [ ] Nội dung không được thu thập/dùng lại; quyền sử dụng từng nguồn ván.

### Hosting, API và tài khoản

- [ ] Muốn link demo hay bản lưu tiến độ lâu dài; số người dự kiến thử ban đầu, không coi là số người thật.
- [ ] Ngân sách hosting tối đa nếu có; không tự đăng ký trả phí khi chưa quyết định.
- [ ] Tài khoản hosting để triển khai backend; kết nối qua đăng nhập chính thức, không gửi token/mật khẩu trong chat.
- [ ] Có cần đăng nhập/khôi phục tài khoản hay chấp nhận guest trong giai đoạn đầu?
- [ ] Có cần đồng bộ nhiều thiết bị? Nếu có, cookie guest hiện tại chưa đủ.
- [ ] Khi nào muốn domain riêng? Không bắt buộc mua để có URL thật.
- [ ] Nếu cân nhắc LLM: chỉ dùng để diễn giải dữ kiện engine; không bắt buộc mua API.

## 3. Việc AI có thể làm thay bạn

- Rà soát hai Word, hợp nhất câu trả lời thành V4 rõ ràng và ghi câu còn mâu thuẫn.
- Thiết kế/sửa UI theo quyết định đã chốt, ưu tiên cùng hệ thống thay vì vá từng màu riêng.
- Sửa code, viết test logic quan trọng, chạy kiểm tra và báo cáo phần chưa kiểm chứng.
- Chuẩn bị hosting/backend và database bền vững; bạn kiểm soát đăng nhập, thanh toán và việc công khai.
- Commit/push từng nhóm việc sau kiểm tra; không backdate hoặc tạo tiến độ giả.
- Cập nhật README, báo cáo, AI usage, limitations và kế hoạch này theo từng đợt.

Bạn không phải tự sửa mọi file. Giao yêu cầu bằng hành vi mong muốn và tiêu chí đạt; AI chọn file phù hợp. AI không tự làm việc mỗi ngày khi không có phiên/schedule được thiết lập. Lịch bên dưới chưa tạo automation.

## 4. Gửi ván cờ như thế nào

Số lượng đề xuất để khởi động, không phải yêu cầu dataset đã được kiểm chứng: đợt đầu 3–5 ván hoặc 5–10 thế; sau duyệt định dạng tăng dần đến khoảng 20–30 thế đa dạng. Chất lượng và quyền sử dụng quan trọng hơn số lượng.

Với mỗi ván/thế, điền:

```text
ID:
Nguồn / người sở hữu / quyền sử dụng:
Ván thật hay thế tự dựng:
Mức người chơi (nếu biết, không đoán):
FEN ban đầu và bên đi:
Danh sách nước tọa độ, hoặc biên bản/ảnh có đủ thứ tự:
Nước/tình huống cần học:
Người chơi lúc đó nghĩ gì (nếu có):
Nước được cho là tốt / các lựa chọn chấp nhận:
Ai/engine nào kiểm tra, phiên bản/depth nếu có:
Giải thích WHAT / WHY / HOW:
Luật/điểm chưa thống nhất:
Có cho phép công khai không:
```

Không cần tự chuyển FEN nếu chưa biết: gửi bàn cờ rõ, vị trí đầy đủ, bên đi và thứ tự nước; AI chuyển rồi bạn xác nhận. Không lấy hàng loạt ván/sách/bài từ website chỉ vì xem được miễn phí. Không gửi thông tin cá nhân đối thủ nếu không cần.

## 5. Mẫu phản hồi một lỗi hoặc yêu cầu UI

```text
Trang và thiết bị:
Commit hoặc URL đang thử:
Bước 1 / 2 / 3:
Kỳ vọng:
Thực tế:
Ảnh/video (che dữ liệu riêng):
Mức độ: chặn sử dụng / khó hiểu / trang trí
Tiêu chí hoàn thành:
```

Ví dụ tiêu chí: “Ở màn phản tư trên điện thoại, ô nhập không bị bàn phím che; đóng/mở bài còn bản nháp đã lưu; chưa bấm gửi thì chưa thấy đáp án.”

## 6. Lộ trình 7 ngày đề xuất, không phải cam kết deadline

| Ngày | Trọng tâm | Điều kiện hoàn thành |
| --- | --- | --- |
| 13/10 | Quyết định P0, UI tham khảo, dữ liệu đợt đầu | Có bộ đầu vào rõ ràng |
| 14/10 | Hợp nhất V4, chốt phạm vi và bản vẽ các trang chính | Bạn duyệt flow, AI ghi acceptance criteria |
| 15/10 | Sửa UI trang chủ/chơi/phản tư | Mobile và desktop dùng được, không lộ lời giải sớm |
| 16/10 | Duyệt thế cờ/lời giải và cải tiến phân tích | Có bộ case hợp lệ và nguồn rõ |
| 17/10 | Backend online + persistence nếu đã có hosting | URL thật, dữ liệu giữ qua restart, guest cách ly |
| 18/10 | Thử với nhóm nhỏ có đồng ý | Ghi quan sát thật và lỗi ưu tiên |
| 19/10 | Sửa lỗi, báo cáo và quyết định mốc tiếp | Test qua, demo qua, tài liệu đúng hiện trạng |

Nếu đầu vào/hosting chưa sẵn sàng, dịch mốc tương ứng; không tuyên bố đã hoàn thành cho kịp lịch.

## 7. File nào chỉnh khi làm thêm

| Nhu cầu | File |
| --- | --- |
| Màu/font/mobile | web/style.css |
| Khung/menu | web/index.html |
| Màn hình, tương tác bàn cờ | web/app.js |
| API/hosting | server.py |
| Luồng học | app/service.py |
| Luật | app/rules.py |
| Phân tích | app/engine.py |
| Giải thích/lịch ôn | app/learning.py |
| Fixture | app/puzzles.py |
| Persistence | app/storage.py |
| Test | tests/ |
| Bản xem trước online riêng | online-preview/; không đồng bộ backend tự động |

## 8. Checklist trước mỗi commit và phát hành

- [ ] Đọc git status/diff, chỉ stage file đã xem.
- [ ] Thay logic thì chạy test tương ứng; core flow cần giữ đầy đủ kiểm tra.
- [ ] Kiểm tra cú pháp Python/JS và diff; ghi test thật, không chép kết quả cũ như mới.
- [ ] Thử manual đường đi bị thay đổi, cả lỗi/mất mạng nếu liên quan.
- [ ] Không đưa database, secret, reflection cá nhân hay tài liệu chưa được phép ra public.
- [ ] Commit nhóm việc rõ; push rồi đối chiếu remote.
- [ ] Nếu hosting tự deploy, kiểm tra URL sau deploy và có cách quay lại bản trước.

```powershell
git status -sb
python -m unittest discover -s tests -v
python -m compileall -q app server.py tests
git diff --check
```

Sau khi AI hoàn thành, báo cáo nên có: đã sửa gì, file nào, test nào, thực/fallback, commit, URL và lỗi còn lại. Bạn không cần mua API hoặc chuyển repo Public để tiếp tục.

## 9. Riêng tư, public và sao lưu

- Repo GitHub giữ nguyên audience cho đến khi bạn duyệt PUBLIC_READINESS_VI.md. Website demo công khai chỉ chứa nội dung được tuyển chọn, không chứa Word/đặc tả/đường dẫn máy/email Git.
- Backend local còn lưu ở var/chill.sqlite3; sao lưu khi server dừng. GitHub không sao lưu dữ liệu này.
- Bản xem trước lưu tiến độ demo trên browser, không tài khoản/đồng bộ; xóa dữ liệu trình duyệt sẽ mất. Không dùng nó làm bằng chứng đã triển khai persistence server.
- Duyệt email lịch sử, thông tin tác giả, Word và giấy phép trước Public source.
- Domain riêng, payment, PvP, app mobile native và ML để sau khi vòng học được kiểm chứng.

## 10. Tin nhắn bạn gửi tôi ngày mai

“Bắt đầu ngày 13/10. Đây là hai file V4 tôi đã trả lời [đính kèm], các ván/thế [đính kèm], 3 ưu tiên hôm nay là […]. Hãy kiểm tra mâu thuẫn, triển khai theo thứ tự, chạy test, commit/push và báo cáo điều đã làm thật. Những câu chưa biết hãy đề xuất phương án, không tự coi là tôi đã chốt.”

Bạn có thể gửi từng phần; không phải đợi trả lời hết mới bắt đầu sửa.

## Link đã xuất bản tối 12/10

https://co-chill-ngay-mai.cosmicanole32.chatgpt.site — bản xem trước public, người khác có link có thể mở; không cần bật máy cá nhân. Đã xác nhận deployment succeeded và mở trang thật. Đây là demo tĩnh hai bài, không phải toàn bộ app local. Kế hoạch này không nằm trong các file public của Site.
