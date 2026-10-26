# Cờ Chill V5 — đối chiếu câu trả lời và phạm vi code

Ngày cập nhật: **24/10/2026**, giờ Việt Nam. Đây là sổ quyết định để tiếp tục phát triển, không phải chứng nhận mọi yêu cầu đã hoàn thành.

Nguồn mới đã đọc: `E:\ThanhTQ\App cờ tướng\10-23\V5.docx`, 940 đoạn, gồm câu hỏi trong bảng và 96 khối câu hỏi/trả lời. Đường dẫn `E:\ThanhTQ\App cờ tướng\10-23.docx` người dùng nhắc không tồn tại lúc kiểm tra; file đã điền tìm được nằm trong thư mục `10-23`. Hai ảnh thương hiệu do chủ sở hữu gửi được dùng ở `online-preview/logo-co-chill.png` và `online-preview/cover-co-chill.png`.

Tài liệu gốc được giữ nguyên. Câu trả lời mới rõ ràng được ưu tiên hơn phụ lục quyết định cũ. Ví dụ: số điểm đáng học sau một ván **không còn cố định tối đa ba**. Chưa điền nội dung không được xem là đã chấp thuận. Yêu cầu trong file là đầu vào sản phẩm; không tự cấp quyền mua dịch vụ, công khai dữ liệu hoặc phát hành lên hosting.

## Cách đọc trạng thái

- **Có**: phần việc nêu cụ thể đã có trong code, vẫn cần kiểm tra trên hạ tầng thực trước pilot.
- **Một phần**: có luồng chạy được, nhưng còn phạm vi quan trọng chưa làm hoặc chưa kiểm chứng.
- **Chưa**: chưa có trong bản bàn giao; không được quảng bá là đã chạy.
- **Chờ nguồn/quyết định**: không đủ bằng chứng để tự gán đáp án, quyền sử dụng hay luật chính thức.

Kết quả kiểm thử từng đợt được ghi trong `TEST_REPORT_CODEX.md`; tài liệu này chỉ đối chiếu **42 nhóm quyết định** rút từ 96 câu hỏi, không đếm nhóm “Có” thành tỷ lệ hoàn thiện toàn sản phẩm.

## 42 nhóm quyết định

| # | Câu hỏi nguồn | Quyết định và phần đã có | Trạng thái / phần cần tiếp tục |
|---:|---|---|---|
| 1 | V5-01, 02, 06, 07 | Ba phần phản ánh: quan sát/đánh giá, mục tiêu, nước đề xuất; gợi mở trước giải; giữ câu trả lời đầu. | **Một phần.** Có cấu trúc và gợi ý mẫu; chưa có bộ chấm ngữ nghĩa hoặc LLM hiểu mọi cách diễn đạt. Không chứng nhận lập luận đúng bằng từ khóa. |
| 2 | V5-03 | Ghi lượt học, phân biệt có hỗ trợ; giới hạn thử và giữ bài chưa xong để hôm sau tiếp tục. | **Một phần.** Có trạng thái dở/assisted và nháp; “đã làm đúng nước” chưa đồng nghĩa “đã hiểu”. Cần tiếp tục hoàn thiện thước đo cả câu trả lời lẫn nước đi và bài dễ thay thế. |
| 3 | V5-04, 05 | Bài có thể có các nước chấp nhận khác; giải thích theo thế cờ, lý do, cách nghĩ; bước minh họa trên bàn. | **Một phần.** Danh sách được duyệt/engine cung cấp; fallback nông không phải trọng tài về mọi nước tốt. Ảnh thế cờ trong Word chưa tự biến thành bộ bài đã duyệt. |
| 4 | V5-08, 09, 10 | Mục tiêu là luật giải quốc gia Việt Nam. Luật di chuyển và an toàn Tướng có bộ kiểm thử. | **Chờ nguồn chính thức.** Chưa xác nhận đủ luật lặp/chiếu/đuổi, mốc 50 lượt, ngoại lệ nước chiếu. Không gắn nhãn “đầy đủ luật thi đấu Việt Nam” cho bản hiện có. |
| 5 | V5-11 | Ký phổ Việt phân biệt quân trước/sau, chuyển nước thành tọa độ và phát lại kiểm tra hợp lệ. | **Một phần.** Biên bản mơ hồ phải bị từ chối; chưa có bộ nhập đủ mọi biến thể ký phổ và trường hợp nhiều Tốt cùng lộ. |
| 6 | V5-12, 14, 18 | Chưa nhận bộ ván thật/bài tập đầy đủ; dùng 12 bài tự dựng với nhãn nguồn rõ. | **Chờ dữ liệu.** Có nhập ký phổ văn bản và bộ biên tập; cần ván gốc, FEN, nước chấp nhận, căn cứ và quyền sử dụng để mở rộng. |
| 7 | V5-13, 19, 38 | Phản hồi theo bài; owner có hộp thư và bộ biên tập: nháp → xuất bản → tạm gỡ, có lịch sử phiên bản ở backend. | **Một phần.** Có kiểm tra nước/biến hợp lệ và owner duyệt. Chưa tự cách ly mọi bài bị báo hoặc thông báo lại toàn bộ người đã học; giao diện chỉnh sửa sâu còn cần hoàn thiện. |
| 8 | V5-15 | Nội dung công khai phải có nguồn và khai báo quyền; bài owner tạo cần lưu nháp trước. | **Một phần.** Chưa có cổng người học đóng góp riêng tư rồi owner duyệt. Không mặc định upload đồng nghĩa đủ quyền phát hành. |
| 9 | V5-16 | Gợi bài cùng kỹ năng, ưu tiên bài chưa gặp, ghi số lần thấy và lần đầu. | **Một phần.** Kho bài nhỏ; chưa loại trùng đầy đủ qua đối xứng/đổi màu. “Chưa gặp” là theo lịch sử ghi nhận, không khẳng định chuyển giao kỹ năng đã kiểm chứng. |
| 10 | V5-17, 18 | Chia kỹ năng, giai đoạn và mục tiêu học để có lộ trình ngắn. | **Một phần.** Chưa có giáo trình đầy đủ hay ngưỡng mở khóa được chủ sở hữu duyệt; không gán Elo từ điểm hoạt động. |
| 11 | V5-20, 21; BS-27, 28 | Giữ bố cục quen thuộc, dùng logo/cover được gửi, ba chủ đề màu, thao tác bấm quân/ô. | **Có ở bản giao diện.** Cần người dùng thử độ dễ đọc trên thiết bị thật; kéo thả không phải điều kiện bắt buộc. |
| 12 | V5-22 | Giao diện đáp ứng màn nhỏ, nhập suy nghĩ và gửi thuận tiện. | **Một phần.** Cần thử bàn phím ảo iOS/Android thật; chưa tuyên bố đã xử lý mọi cách bàn phím làm thay đổi viewport. |
| 13 | V5-23, 24 | Ngôn ngữ góp ý nhẹ nhàng; lý do nước không hợp lệ phân biệt chân Mã, mắt Tượng, lộ Tướng… | **Một phần.** Có hướng dẫn luật và phản hồi cụ thể; chưa có bộ tutorial tương tác đầy đủ cho từng lỗi. Không khen “gần đúng” khi chưa có căn cứ. |
| 14 | V5-25 | Tách hoạt động học, hỗ trợ và độc lập; không dùng số ván làm mẫu số tỷ lệ giải bài. | **Một phần.** Có thống kê với nhãn dữ liệu từ thiết bị; cổng sáu hoạt động/tỷ lệ đạt chưa là đánh giá năng lực được chuẩn hóa. |
| 15 | V5-26, 27 | Giữ bài dở, lịch học tiếp; lịch ôn gắn với thời điểm kết thúc bài, không gắn khi vừa mở. | **Một phần.** Có lịch trong app và quay lại phiên; chưa có push/email hoặc thuật toán lịch ôn được chứng minh hiệu quả. |
| 16 | V5-28 | Tài khoản tập trung, lượt chơi/học/ôn trên máy chủ; xem chi tiết người dùng đã lọc. | **Có cho pilot cùng server.** Thống kê là dữ liệu thiết bị đồng bộ, không chống gian lận hoặc tác động được kiểm định. Cần cải thiện lọc/phân trang UI khi nhiều tài khoản. |
| 17 | V5-29 | Chính sách mong muốn: một năm không hoạt động; nhắc quay lại hàng tuần. | **Một phần.** Có CLI xem số tài khoản đủ điều kiện và xóa khi `--confirm`; chưa có job tự chạy, email nhắc hoặc cam kết thời gian lưu backup. |
| 18 | V5-31 | Link chia sẻ phải mở đúng biên bản ở máy khác, không lộ câu trả lời riêng. | **Chưa.** Hiện chưa có kho snapshot công khai và quản lý link. Route có mã ván cục bộ không được coi là link chia sẻ đa máy. |
| 19 | V5-32; BS-46 | Khách dùng ngay; username/password để đồng bộ; sửa tên/mật khẩu, xuất/xóa dữ liệu. | **Có cho đăng nhập mật khẩu.** Chưa có OAuth, email xác minh, email phục hồi hoặc gộp tài khoản. Không dựng nút đăng nhập giả. |
| 20 | V5-33, 35 | Pilot dự kiến 5–10 người; ưu tiên luồng học và lỗi trọng yếu. | **Chưa có kết quả pilot.** Không bịa người dùng, số ván, tỷ lệ cải thiện. Cần chủ sở hữu tổ chức thử sau khi nghiệm thu hosting. |
| 21 | V5-37, 39, 40 | Ưu tiên dạy tốt, engine mạnh và biên tập dễ; không mua thêm dịch vụ lúc này. | **Một phần.** Có lời giải mẫu, local fallback và adapter UCI; chưa có LLM hay Pikafish binary/NNUE thật. Không chi phí dịch vụ mới. |
| 22 | V5-41 | Giữ nguyên vật liệu gốc và dữ liệu; lỗi bộ phận thì báo đúng phần bị ảnh hưởng. | **Có nền tảng.** Có draft, lỗi sync, backup CLI, trạng thái engine; vẫn cần chạy migration và diễn tập phục hồi khi đổi cấu trúc lớn. |
| 23 | V5-42; BS-30 | Owner quản trị; người hỗ trợ chỉ đọc báo cáo. | **Có.** Backend phân quyền `admin`/`report`, không tự chọn admin ở trình duyệt; màn quản trị không trả câu trả lời riêng hoặc mật khẩu. |
| 24 | V5-43 | Owner thấy người mới và số liệu mới khi mở quản trị. | **Một phần.** Có danh sách tài khoản/đếm mới và nút làm mới; chưa có push từng đăng ký hay tổng kết qua email. |
| 25 | V5-44, 45; BS-45 | Một phiên hoạt động/tài khoản; máy mới đăng nhập thu hồi máy cũ; dữ liệu từng danh tính tách riêng. | **Có nền tảng.** Có cookie HttpOnly, thu hồi phiên, local draft và CAS chống ghi đè âm thầm. Khách chỉ gửi lên khi chủ động chọn; không bí mật lưu server. |
| 26 | V5-46 | Khóa phải có lý do và thời hạn; quyền sửa/xóa tài khoản. | **Có phần thao tác.** Owner khóa có hạn, thu hồi phiên; người dùng xuất/xóa tài khoản thường. Chưa có cổng kháng nghị riêng/email hỗ trợ cấu hình sẵn; owner deletion cần bàn giao quyền qua vận hành. |
| 27 | BS-01, 02 | Home ưu tiên ván đang chơi rồi ôn/bài dở; muốn chặn ván mới khi còn ôn. | **Một phần.** Home ưu tiên ván đang chạy và bài đến hạn. Chưa khóa bắt buộc theo ngưỡng backlog chưa chốt; tránh khóa vô hạn bởi bài chưa duyệt hoặc không thể giải. |
| 28 | BS-03, 04, 05 | Tutorial, đánh giá đầu vào tiếp tục được, mục tiêu học có thứ tự và chỉnh được. | **Một phần.** Có hướng dẫn/tùy chọn học cơ bản; chưa có bài đánh giá đầu vào đủ chuẩn và lộ trình thích nghi đã hiệu chỉnh. |
| 29 | BS-06, 07 | Không giới hạn giờ là một lựa chọn; hòa hai bên xác nhận trong 15 giây. | **Một phần.** Có không giới hạn giờ và hòa trên một thiết bị. Chưa tự tính thua sau 30 giây offline; chưa có hòa với bot được duyệt theo vật chất/lịch sử. |
| 30 | BS-08, 09 | Nhập toàn bộ biên bản để xem lại; thế đơn thuộc phân tích/biên tập, không suy ra kết quả ván. | **Một phần.** Import kiểm tra từng nước và người gửi xác nhận đủ biên bản; chương trình không chứng minh họ đã gửi mọi nước. Luật tranh chấp còn cần nguồn chính thức. |
| 31 | BS-10, 11, 12 | Tránh ván trùng; giữ ván cũ, yêu thích và phân trang. | **Một phần.** Có so thế đầu + chuỗi nước để tìm trùng; không cắt âm thầm danh sách ván. Chưa có hệ thư mục cá nhân/note/nhánh biến hoàn chỉnh. |
| 32 | BS-13 | Số điểm cần học biến đổi theo ván; không tự bịa lỗi khi không thấy. | **Một phần.** Phân tích vẫn giới hạn tài nguyên; không dùng “không tìm thấy” làm kết luận ván hoàn hảo. Cần kiểm thử bộ ván và chất lượng engine thật. |
| 33 | BS-14, 15, 17 | Một nước ứng viên, tự nghĩ trước giải, giữ suy nghĩ đầu; xem lịch sử khi review. | **Có luồng chính.** Chưa có mũi tên/đánh dấu riêng hoặc mọi kiểu chỉnh sửa và replay tiền cảnh. Cổng phản ánh là cổng học tập, không hệ chống sửa dữ liệu trên máy người dùng. |
| 34 | BS-16, 18, 19, 20 | Giải thích từng bước, thử lại, bài liên quan; tự đánh giá là tùy chọn. | **Một phần.** Có chuỗi học và tiếp tục bài; chưa có hai bàn đồng thời hoặc hệ ghi chú riêng hoàn chỉnh. Xem lời giải không được coi là độc lập giải được. |
| 35 | BS-21…26 | Tiến độ/EXP thể hiện hoạt động; Home, âm thanh, trợ giúp, empty/error state rõ. | **Một phần.** Có cấu phần giao diện và thống kê; chưa có hệ EXP/lộ trình được chốt hoàn chỉnh. Không quảng bá cấp hoạt động là khả năng thi đấu. |
| 36 | BS-29 | Đăng nhập/lấy lại phiên quay về việc đang làm. | **Có cơ chế route và draft.** Xung đột dữ liệu cần người dùng chọn bản; không tự trộn bài riêng của hai tài khoản trên máy chung. |
| 37 | BS-31, 33, 34 | Engine mạnh, chi tiết độ sâu và độ khó bot phù hợp. | **Một phần.** Adapter UCI kiểm tra PV/điểm, local fallback rõ nhãn, bot cơ bản có mức tìm kiếm. Chưa có binary thật được nghiệm thu, Elo hay tự điều chỉnh độ khó theo thua liên tiếp. |
| 38 | BS-32 | Engine và trọng số cần quyền hợp lệ. | **Chờ engine được phép sử dụng.** Không tải/gài binary chưa rõ nguồn; không dùng bí mật khi thiếu quyền; không suy quyền NNUE từ giấy phép mã nguồn. |
| 39 | BS-35…38 | Phân tích nhanh/rồi sâu; rời trang bỏ kết quả trễ; lỗi engine không làm người chơi thua oan. | **Một phần.** Có client hủy/bỏ kết quả trễ, timeout và trạng thái kỹ thuật; engine server có thể vẫn chạy tới hạn. Chưa có lưu nhánh phân tích thủ công đầy đủ. |
| 40 | BS-39…41 | Giới hạn tải engine, không gửi dữ liệu đến LLM, có backup. | **Có nền tảng.** API hạn tần suất, một UCI process mỗi worker, backup API. Chưa có queue công bằng nhiều máy, lịch backup hay SLA phục hồi; LLM tắt/chưa cấu hình. |
| 41 | BS-42, 43 | Chuẩn bị chuyển hosting, giờ Việt Nam. | **Có tài liệu và cấu hình static Vercel.** Hiển thị Asia/Ho_Chi_Minh; bản đầy đủ ưu tiên server cùng origin với lưu bền vững. Chưa deploy, tắt site cũ hoặc mua tên miền. |
| 42 | BS-44, 47…50 | Admin xác thực thêm; repo gốc; API cho chính web; user xem trước công khai. | **Có nền tảng pilot.** TOTP owner, kiểm tra origin/CSRF/role; chưa có audit bảo mật độc lập hoặc chính sách riêng đầy đủ cho từng nhóm tuổi. Không tự công khai repo/dịch vụ. |

## Các quyết định quan trọng cần giữ khi làm tiếp

1. **Xóa là xóa thật.** Trả lời V5-30 đề nghị chỉ ẩn ở dashboard nhưng giữ server để huấn luyện không được dùng làm hành vi ẩn. Bản hiện tại xóa dữ liệu tài khoản ở database hoạt động; backup/export cần quy trình người vận hành riêng. Nếu muốn đóng góp dữ liệu, phải có thao tác đồng ý rõ ràng, phạm vi cụ thể, nguồn/quyền và cách rút lại.
2. **Không bịa trí thông minh.** Chưa có LLM chấm ngữ nghĩa, chưa huấn luyện mô hình, chưa có bộ dữ liệu người thật đã được cấp quyền. Engine quyết định nước hợp lệ/đánh giá theo phạm vi tìm kiếm; lời giải mẫu không được tự thêm biến không kiểm tra.
3. **Engine thật cần kiểm thử thật.** Có adapter không đồng nghĩa Pikafish đã chạy. `configured_unverified` chỉ nói đường dẫn/cấu hình tồn tại; phải đo trên binary/NNUE đúng quyền, đúng hệ điều hành và bộ thế duyệt.
4. **Không chốt luật từ lời kể.** Nguồn quốc gia, năm/phiên bản và ví dụ phân xử chiếu/đuổi/lặp cần được cung cấp hoặc đối chiếu. Giữ giới hạn rõ thay vì gọi mọi mốc đã có là chuẩn giải chính thức.
5. **Tài khoản chỉ bền khi máy chủ bền.** Cookie/session và SQLite đã có code, nhưng hosting ephemeral sẽ làm mất database. Static Vercel không tạo backend tài khoản. Hướng dẫn triển khai hiện hành nằm trong `docs/DEPLOY_GCP_V6.md`; chưa deploy hoặc mời người dùng khi chưa được chủ dự án chấp thuận.
6. **Không dùng dữ liệu tự báo cáo làm chứng cứ hiệu quả.** Mẫu số độc lập, lượt có hỗ trợ, tài khoản thử và người thật phải phân biệt. Thang level/EXP cần ghi đúng là hoạt động/heuristic khi chưa hiệu chuẩn.

## Những thông tin thực sự còn thiếu để nâng chất lượng tiếp

- Bộ ván thật có đầy đủ biên bản, bên cần phân tích, kết quả và nguồn/quyền sử dụng.
- Bộ thế đã được người biết cờ duyệt: FEN, bên đi, một hoặc nhiều nước chấp nhận, biến minh họa hợp lệ, mục tiêu, lý do và mức khó. Ảnh Word cần được dựng lại, xác minh quân/bên đi trước.
- Nguồn luật quốc gia cụ thể cho chiếu dai, đuổi dai, lặp và không ăn quân; không chỉ tên luật chung.
- Rubric chấm ba phần câu trả lời: ví dụ đạt/chưa đủ/mâu thuẫn và cách gợi mở. Điều này mới giúp đánh giá lời giải tự do có căn cứ khi tích hợp provider sau.
- Quyết định vận hành: hosting/database bền, ngân sách bạn chấp nhận, người giữ TOTP/backup, địa chỉ hỗ trợ thật, chính sách tài khoản thử và độ tuổi pilot.
- Kết quả thử usability trên máy tính và điện thoại, đặc biệt thao tác bàn cờ, bàn phím ảo, sync khi mất mạng và quay lại bài dở.

Không cần trả lời lại toàn bộ V5 để chạy bản local. Những mục trên là đầu vào cho vòng nghiệm thu chất lượng tiếp, không phải lý do chặn các phần có thể chạy hiện tại.
