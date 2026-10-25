# Sổ quyết định UI UX và Luật tiếp nhận ngày 15 tháng 10 năm 2026

Hoàn thiện đối chiếu và bộ V5 ngày 16 tháng 10 năm 2026.

**Quyết định mới cùng ngày, thay ưu tiên trước:** chủ sản phẩm yêu cầu chính đợt nâng cấp V5 có tài khoản thật, dữ liệu tập trung, đồng bộ nhiều thiết bị và trang quản trị để xem đăng ký mới/thống kê toàn hệ thống. Phần phía dưới nói để tài khoản sang sau là bối cảnh của Site v3, không còn là phạm vi ưu tiên của V5. Chưa triển khai tính năng này. Phạm vi, câu hỏi còn thiếu và tiêu chí nghiệm thu: mục 13 trong [file bàn giao](../deliverables/HUONG_DAN_CODE_VA_BAN_GIAO_CHAT_MOI.txt). V5 32 trong bản Word mới đã đổi sang câu hỏi phương thức đăng nhập; V5 40 đã tính backend/tài khoản. V5 cập nhật có 46 câu, thêm 42–46; người dùng chỉ điền Word mới, file TXT là bàn giao để đọc. PvP, engine mạnh và LLM không tự được thêm vào phạm vi.

## Phạm vi và nguồn

Nguồn mới: `E:\ThanhTQ\App cờ tướng\10-13\UI UX + Luat.docx`, gồm các nhóm UX01–UX34, phần UX35 trả lời câu hỏi bổ sung, 22 ảnh tham chiếu và các mẫu cuối tài liệu. File gốc được giữ nguyên. Đã đọc đầy đủ văn bản và xem đủ 22 ảnh. Bản trích XML phục vụ đối chiếu ở `var/uiux-review/full-text.txt`; các nhãn `~p` trong đó chỉ là page break lưu trong XML, không phải số trang đã kiểm chứng.

Kiểm tra phân trang: renderer đóng gói không có LibreOffice trên Windows; đã xuất PDF bằng Microsoft Word ẩn, mở nguồn chỉ đọc, không lưu sửa nguồn. Bản xuất có 50 trang. Đã xem ảnh trang 46 và 47: UX35 nằm ở trang 46 trong bản xuất này, trang 47 là mẫu phác thảo. Phân trang có thể đổi theo môi trường nên dùng mã UX35 để liên kết phần người dùng gọi là trang 47.

Nguồn nền: Final Pack trong `docs/spec/`, V4 đã trả lời, bản phác trang và các quyết định trực tiếp trong cuộc trò chuyện. Báo cáo `BAO_CAO_CHATGPTSITE_V4_2026_10_15.md` ghi trạng thái phiên bản Site trước đợt cập nhật này. Khi tài liệu hướng dẫn cũ hỏi về tính năng, câu hỏi đó không tự trở thành quyết định đã chốt.

Sổ này tách **ý định đã nhận**, **trạng thái đã có**, **phần đang làm trong đợt này** và **việc cần chốt**. Báo cáo phát hành của đợt mới là nơi ghi kết quả kiểm thử và deploy thực tế; không suy từ “đã chốt” thành “đã hoạt động”.

## Quyết định phạm vi ưu tiên

UX35 chốt vòng học công khai chạy được: chơi/nạp ván → điểm cần học → phản hồi trước → giải thích có căn cứ → thử lại → bài liên quan → kết quả → lịch ôn và tiến độ, có resume và giao diện mobile. PvP trực tuyến, tài khoản đồng bộ nhiều thiết bị và AI huấn luyện riêng để sau. Quyết định này làm rõ phạm vi trước mắt của các mong muốn tài khoản, nhiều thiết bị, ghép trận, xếp hạng và dịch vụ thời gian thực ở các nhóm trước.

Giữ stack nhẹ ở Site hiện tại: HTML/CSS/JavaScript, luật và tìm kiếm trong trình duyệt, localStorage. App Python/SQLite vẫn là phần riêng trong repository. Không giả lập tài khoản, đồng bộ server, Pikafish, LLM hay ML bằng nhãn giao diện. Dữ liệu nháp lưu local phải nói là local; đóng/mở lại cùng browser khác với đồng bộ thiết bị.

Người dùng yêu cầu deploy bản ChatGPT Site mới ở tin nhắn này; quyền đó không bao gồm mua dịch vụ, tăng ngân sách, đổi quyền GitHub hoặc tự chuyển sang Vercel. Nguyên tắc hỏi trước các hành động cần quyền vẫn áp dụng.

## Đối chiếu từng nhóm yêu cầu

| Nguồn | Ý định được nhận | Hướng xử lý trong đợt này và phần còn lại |
|---|---|---|
| UX01 | Trang có điều hướng riêng, chữ rõ hơn, phong cách bình tĩnh; tham khảo lộ trình Duolingo và bàn TTTK | Dùng route và sidebar, thiết kế bố cục riêng; không sao chép hình hoặc mã của ứng dụng tham khảo. Lỗi cụ thể tiếp tục thu qua V5 21. |
| UX02 | Tên Cờ Chill, trung tính hoặc bạn học, Việt hóa, không in WHAT WHY HOW | Sửa nhãn và cấu trúc lời dẫn; logo đã có trong ảnh 7 của Word, V5 20 chỉ chốt palette/biến thể nhỏ và file tốt hơn nếu có. Chấm lập luận linh hoạt còn thiếu bộ chấm và ví dụ. |
| UX03 | Ba theme sáng ấm, trắng lạnh, tối; màu xanh hiện tại tạm giữ | Thêm lựa chọn theme; kiểm tra tương phản các trạng thái. Màu thương hiệu cuối cùng còn chờ chốt palette và biến thể logo đã cung cấp. |
| UX04 | Chữ rõ, lời giải ngắn có chi tiết, ký phổ Đỏ Đen, không dồn quá nhiều nội dung | Chỉnh typography và phân nhóm; thống kê ít mẫu hiển thị Chưa đủ dữ liệu thay số giả. Mẫu văn phong ở V5 05. |
| UX05 | Bo góc, gỗ sáng, icon nhất quán, âm ngắn có tắt nhanh | Dùng CSS/asset tự tạo; không dùng âm hoặc texture lấy từ game khác. Không kéo hoạt ảnh thành trễ thao tác; tôn trọng giảm chuyển động. |
| UX06 | Laptop trước, bàn trái 50–55%, panel phải, sidebar thu gọn, giữ bàn và câu hỏi khi zoom | Cải thiện layout đáp ứng; panel kéo đổi kích thước chưa ưu tiên. Cần nghiệm thu thiết bị thực. |
| UX07 | Trang riêng, Ván của tôi chứa xem lại, Ôn tập chứa tiến bộ, thêm lộ trình, mobile có menu dưới | Bổ sung điều hướng; link trang hoạt động không có nghĩa chia sẻ được ván local. Công cụ biên tập để giai đoạn sau. |
| UX08 | Bắt đầu chơi/demo/cách học, ưu tiên bài đang dở và lịch đến hạn, không nhét ván gần đây ở home | Thêm trang Cách học và CTA theo dữ liệu thật. Chuỗi ngày nếu có là chỉ số hoạt động, không chứng minh kỹ năng. |
| UX09 | Tự khai mức, bỏ hướng dẫn khi đã biết, chưa biết thì hỏi nhỏ hơn, giữ chỗ dở | Cấu hình mức hướng dẫn và scaffold; chưa có placement/xếp hạng đã hiệu chuẩn. Không lấy thắng máy nông để chứng nhận trình độ. |
| UX10 | Chọn màu, preset thời gian cộng giây, một ván hoạt động, luật chặt | Thêm preset và increment, giữ hạn chế một ván; engine nông phải có nhãn. Luật giải đấu nâng cao cần đối chiếu riêng. |
| UX11 | Click quân/đích, đồng hồ, ký phổ, lật bàn, không xem lại/coaching trong ván, đầu hàng là thua | Cải thiện tương tác và kết thúc ván rõ nghĩa; không chèn lời khuyên. Online mất mạng và ghép trận chưa thuộc bản browser. |
| UX12 | Quân Hán mặc định, tùy chọn Việt, không chấm đích hợp lệ, vòng chọn/nước gần nhất, chiếu có dấu, danh sách quân bị ăn | Cập nhật board cùng agent luật; ký phổ phải ổn định khi lật. Không sao chép bộ quân TTTK. |
| UX13 | Dán/file/ảnh ký phổ, lỗi dừng đúng nước, bài do chủ sở hữu nhập vào kho chung | Định dạng thật cần file mẫu V5 12; không nhận dạng ảnh giả. Quyền chia sẻ không tự có chỉ vì chủ sở hữu tải lên, V5 15. |
| UX14 | Thư viện ván có metadata, bộ lọc, yêu thích, phân trang 20 x 10, xuất riêng | Ván lưu có sẵn trong bản trước; hoàn thiện thư viện theo đợt. Không giữ ngầm dữ liệu riêng sau khi xóa. |
| UX15 | Tối đa ba điểm theo thời gian; trước suy nghĩ không lộ mẹo; tiến độ thật và resume | Tiếp tục review nông có giới hạn. Kết quả chưa chắc chỉ là ứng viên học; không chấm chính thức hoặc khen chắc “không sai” vì engine không tìm thấy. |
| UX16 | Câu hỏi text cùng trang, chưa biết hỏi nhỏ hơn, nháp, không sửa bản trước đáp án | Bổ sung gợi mở theo câu; lưu nháp local được ghi rõ. Chờ 10 giây và điều kiện mở lời giải cần V5 02. |
| UX17 | Giải thích theo tình huống, biến tương tác, nhiều nước hợp lý, chi tiết engine, chỉ ra đúng/sai từng ý | Làm rõ nhãn và phần chi tiết có căn cứ. Chưa giả chấm ý bằng keyword; không khai engine đạt sâu 5–6 khi mới 2 ply. V5 04–07. |
| UX18 | Giải thích rồi nước đúng mới đủ, tối đa ba lần, sai hỏi nhỏ hơn, giữ bước related | Tách hoàn tất hoạt động/có hỗ trợ/tự giải. Chưa chứng minh hiểu chỉ bằng từ khóa hoặc ô tích. Trạng thái sau lần ba cần V5 03 và V5 26. |
| UX19 | Chủ đề theo mục tiêu, bài thêm ưu tiên chưa gặp, ba tầng gợi ý, hết kho nói thật | Bài cùng chủ đề có thể mới; cùng nhóm tương đương hoặc lật gương không tự trở thành bằng chứng chuyển giao. V5 16. |
| UX20 | Bài theo giai đoạn/kỹ năng/mức; text và bàn trước video; luật có minh họa và quay lại | Lộ trình phải ghi nội dung thực có; không tạo giáo trình giả. Kho trước có 12 bài tổng hợp, chưa chuyên gia duyệt. V5 14–18. |
| UX21 | Dashboard hoạt động và tỷ lệ bài mới; chỉ từ sáu mẫu; ranking/EXP mong muốn | Giữ Chưa đủ dữ liệu khi dưới sáu mẫu, tách trợ giúp. Chưa có Elo/ML/xếp hạng thực. V5 25 và V5 28. |
| UX22 | Ngày/tháng, hàng đợi quá hạn, nhắc ngoài 22–7 giờ mỗi sáu giờ, nhắc nghỉ 30 phút | Giữ lịch local và hàng đợi; email/push/server time chưa tồn tại. Thời gian học phải loại tab nền khi đo; V5 26–27. |
| UX23 | Cài đặt chia nhóm, tài khoản giữ dữ liệu, export không lộ đáp án, xóa tách phạm vi | Thêm settings và export chia sẻ an toàn. UX35 để tài khoản sau; không nói xóa cookie vẫn giữ dữ liệu trên Site hiện tại. V5 29–32. |
| UX24 | Laptop trước, bàn trên câu hỏi dưới trên mobile, giữ chỗ, offline/PWA sau | Cải thiện responsive và kiểm tra viewport; thiết bị bàn phím ảo thực cần pilot. Không tuyên bố offline toàn diện. |
| UX25 | Chữ/đọc màn hình, thông báo có text, chủ sở hữu và bạn bè kiểm tra | Giữ điều khiển bàn phím như phương án bổ sung, không bắt người dùng đổi khỏi chuột; focus/contrast là việc kỹ thuật tự làm. |
| UX26 | Lỗi inline, trạng thái chờ rõ, không mất nháp, cập nhật cuối phiên | Không dùng “server đang xử lý” thay cho server ngừng hoạt động hoặc mạng lỗi. Không phần trăm giả. Bản tĩnh không giả request server. |
| UX27 | Module tách luật/UI, engine thay được, ưu tiên Pikafish, dễ chạy/chi phí thấp | Chưa đổi stack chỉ để đổi giao diện. Engine browser và Python riêng; Pikafish cần giai đoạn tích hợp/nguồn giấy phép riêng. |
| UX28 | Phản hồi sớm, chống gửi trùng, lỗi Việt, API version sau, LLM dựa facts | Giữ idempotence trạng thái học; chưa có cloud API/stream/WebSocket. Mate có trạng thái riêng, không làm người học nhầm điểm vật chất 32k. |
| UX29 | Chủ sở hữu biên tập/duyệt/phát hành, family và metadata đủ, lưu phiên bản | Chưa có trang admin thật. V5 19 chốt công việc ưu tiên; giữ ownership và dữ liệu trước/sau lời giải riêng. |
| UX30 | 100k mong muốn/200k trần, phản hồi nhanh, log riêng, 12h xử lý lỗi | Không hứa 0,1 ms. Không biến test thành người dùng thật từ bài thứ sáu. Cần pilot, chỉ số, ngân sách và kế hoạch vận hành V5 33–38. |
| UX31 | Bảy quân tiêu chuẩn, nguồn tham khảo Ziga/Wikipedia | Luật đi quân đã có test; ảnh nguồn phải đối chiếu từng quân. Nguồn phổ thông không thay thế phiên bản luật giải cho tình huống nâng cao. |
| UX32 | Hết nước là thua, lặp/chiếu/đuổi, 50 nước không ăn, kết quả đồng hồ | Tình huống lịch sử cần bộ luật xác định; chưa áp mốc 50 như luật chính thức. Chiếu/đuổi liên tục không được xử bằng phỏng đoán đơn giản. V5 08–10. |
| UX33 | Ký phổ Việt, chủ sở hữu duyệt, giữ bằng chứng | Thêm ký pháp với kiểm thử; tình huống cùng cột cần mẫu. Giữ negative tests để kiểm tra nước cấm dù UI không cho đi. |
| UX34 | Xem web chạy và phản hồi, bàn rõ/nút rõ, báo thay đổi/test/giới hạn | Thực hiện bản thử rồi ghi kết quả thật. V5 không lặp nguyên 272 câu; tập trung vào thiếu dữ kiện và tiêu chí nghiệm thu. |
| UX35 | Core loop trước; bạn bè intermediate; tổng ngân sách; giữ dữ liệu một năm; câu trả lời dựa ý chính | Core loop là phạm vi trước mắt. “Giữ để train sau khi xóa” xung đột nguyên tắc dự án; hiện không dùng dữ liệu người học để train. V5 29–30 yêu cầu chốt chính sách cụ thể. |

## Những điểm không tự biến thành tính năng thật

1. “Đã hoàn thành bài” hiện phải nói rõ hoàn tất thao tác hay tự giải được nước; chưa có bằng chứng hệ thống chấm đúng hiểu biết tự do.
2. “Tôi chưa biết” cần gợi mở, không giả delay xử lý. Thời gian chờ mang tính phạt có thể làm người học đoán bừa; hỏi V5 02 trước khi áp dụng cứng.
3. Đúng từ khóa không chứng minh quan hệ lập luận đúng. Bản hiện tại không tự tô xanh/đỏ câu trả lời theo khớp từ đơn giản.
4. Một nước có điểm cao hơn ở thế sau khi đổi bên đi không tự tốt hơn. So phương án phải cùng thế, cùng phía đánh giá, cùng giới hạn tìm kiếm; mate là trạng thái riêng.
5. Mẫu sáu lần chỉ là ngưỡng UI, không đủ để khẳng định hiệu quả, trình độ hoặc xu hướng ổn định.
6. Bài mới phải xét cả vị trí và nhóm tương đương. Hình cùng chủ đề có thể khác thật; hình lật gương không tự là thử nghiệm chuyển giao độc lập.
7. Khách/local không phải tài khoản cloud. Share URL trang không tự share dữ liệu local; xuất dữ liệu không đồng nghĩa nhập khôi phục đã có.
8. Xóa dữ liệu không được hiểu là chỉ giấu giao diện rồi giữ để train. Chưa có sự đồng ý riêng của người học cho mục đích đó và dự án hiện cấm thu để huấn luyện.
9. Ván/ảnh/lời bình do chủ sở hữu nhập chưa chắc có quyền xuất bản. Không sao chép tài sản của TTTK, Ziga hay website tham khảo.
10. Bộ luật giải đấu cần nguồn và phiên bản. Mốc 50 nước, 3–4 lần lặp, hai bên cùng chiếu và đuổi quân có ngoại lệ không được nhận là đầy đủ chỉ từ mô tả ngắn.

## Bộ V5 và cách cập nhật

`docs/CO_CHILL_V5_QUESTIONS.md` là nguồn nội dung chỉnh được. `deliverables/Co_Chill_V5_Cau_hoi_hoan_thien.docx` là bản điền 41 câu, gồm 7 câu về dạy học, 6 câu luật/ký phổ, 6 câu nội dung, 5 câu UI, 4 câu tiến bộ, 4 câu dữ liệu, 6 câu pilot/vận hành và 3 câu giai đoạn tiếp theo. Không dùng số câu cố định cho mỗi nhóm.

Sau mỗi lần nhận câu trả lời, bổ sung ngày, mã V5, quyết định mới, phần thay quyết định cũ, commit thực hiện và bằng chứng kiểm thử. Chỉ ghi đã phát hành khi tool deploy báo thành công và link công khai đã được kiểm tra. Giữ báo cáo cũ để thấy lịch sử thay đổi; không sửa hồi tố trạng thái đã xác minh của phiên bản trước.

## Kết quả phát hành ngày 16 tháng 10 năm 2026

Site phiên bản 3 đã phát hành thành công. Trạng thái triển khai thực, kết quả kiểm thử và giới hạn được ghi tại [báo cáo phát hành](../BAO_CAO_UIUX_V5_2026_10_16.md); bảng phía trên giữ vai trò đối chiếu ý định, không phải lời tuyên bố mọi mục đã hoàn tất.

## Bản Word V5 hợp nhất phần tài khoản

Bản hiện dùng để trả lời là `deliverables/Co_Chill_V5_Cap_nhat_Tai_khoan.docx`: 46 câu trong 9 nhóm. Giữ mã cũ; cập nhật câu 25, 28, 32, 37, 39, 40 và thêm 42–46. Nguồn Markdown và builder đã cập nhật. Word 41 câu trước đó giữ nguyên để đối chiếu, không cần điền thêm file TXT.
