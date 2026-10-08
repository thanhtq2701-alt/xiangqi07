# Câu hỏi bổ sung V4 về giao diện kiến trúc web và luật cờ tướng

Người trả lời: Trần Quốc Thanh. Ngày lập: 08 tháng 10 năm 2026. Tài liệu riêng để trả lời cùng V4 hiện có. Mục tiêu là xác định giao diện bạn thực sự muốn, hành vi từng trang, yêu cầu kỹ thuật và bộ luật có thể chuyển thành kiểm thử. Chưa có thiết kế hoặc luật mới nào được xem là đã chốt chỉ vì xuất hiện ở đây.

## Cách trả lời và gộp với V4

Giữ nguyên mã câu trong Word. Ghi quyết định, lý do và ví dụ/ảnh liên quan ngay dưới câu hỏi. Có thể ghi “Giữ V4 câu …”, “Theo đề xuất kỹ thuật”, “Chưa cần ở bản tới” hoặc “Cần tư vấn thêm”. Các câu đánh dấu ƯU TIÊN là đường trả lời nhanh trước khi đi vào chi tiết; những câu khác vẫn thuộc danh mục đầy đủ. Không cần tự chọn framework nếu bạn chỉ biết hành vi mong muốn.

V4 cũ giữ các quyết định sản phẩm nền và mã A01–N06. Bộ mới dùng mã UX01.01–UX34.08, đào sâu các quyết định đó. Nếu đổi câu cũ, ghi “Thay V4 mã … bằng …”; nếu không đổi, tham chiếu thay vì chép lại. Khi gửi, gửi V4 đã trả lời + file này đã trả lời + thư mục ảnh/ván/luật có tên khớp mã câu. Không cần gộp hai Word thủ công.

V3 vẫn là đặc tả nền đến khi câu trả lời mới được tổng hợp thành bản thay đổi có trạng thái rõ. Phân biệt bốn trạng thái: đề xuất, chủ dự án đã chốt, đã triển khai, đã kiểm chứng. Sở thích UI không thể làm thay đổi nước cờ hợp lệ; quy tắc nhà phải tách khỏi luật thi đấu và không được gắn nhãn chính thức.

## Điểm xuất phát thực tế

App hiện dùng HTML CSS JavaScript thuần, HTTP server Python, các service luật engine học tập và SQLite. Giao diện có Trang chủ, Chơi, Luyện, Tiến bộ, Sổ tay và Cài đặt; xem lại và reflection đang là trạng thái của màn bài tập. Màu hiện tại: nền #F7F8F4, chữ #203B40, xanh #244E50, vàng #BD9450, đỏ #AE4440. Không có bản Figma hoàn chỉnh, tài khoản cloud, engine mạnh hoặc LLM tích hợp. Những trang mới bên dưới là phạm vi cần quyết định, không phải tính năng đã tồn tại.

Final Pack đề xuất React Next.js TypeScript, FastAPI và PostgreSQL/Supabase; prototype hiện chọn stack nhẹ để chạy local. Câu hỏi kiến trúc bên dưới nhằm xác định lúc nào cần chuyển, không mặc định phải viết lại chỉ để đổi giao diện.

## Bản đồ các trang cần chốt

P01 Trang chủ và quay lại học; P02 Bắt đầu và đánh giá đầu vào; P03 Chọn ván; P04 Đang chơi; P05 Nhập và dựng thế; P06 Thư viện ván; P07 Tổng quan review; P08 Suy nghĩ; P09 Phân tích; P10 Thử lại; P11 Bài liên quan; P12 Bài học; P13 Tiến bộ; P14 Lịch ôn; P15 Cài đặt và dữ liệu. P16 Công cụ quản trị nội dung là lựa chọn tương lai. Mỗi trang cần chốt phiên bản desktop, điện thoại và các trạng thái, không chỉ ảnh đẹp khi có đủ dữ liệu.

## UX01 Những điểm chưa đẹp và tài liệu tham chiếu

Liên hệ V4 B và I. Bắt đầu từ vấn đề nhìn thấy, tránh sửa màu khi vấn đề thật là bố cục hoặc thông tin quá nhiều.

- Ba màn hình hiện tại bạn thấy xấu nhất là gì? Với từng màn, chỉ vùng cụ thể và chấm mức khó chịu từ 1 đến 5.
- Bạn không thích vì màu, chữ, khoảng trống, hình khối, quân cờ, nội dung dài hay cảm giác thiếu chuyên nghiệp? Xếp ba nguyên nhân chính.
- Chọn tối đa ba website/app bạn thích; gửi ảnh hoặc link và ghi chính xác phần muốn học hỏi: header, bàn cờ, sidebar hay typography.
- Gửi một ví dụ bạn không thích và giải thích điều cần tránh; không chỉ ghi “đừng giống trang này”.
- Phần nào của app hiện tại cần giữ nguyên vì đã dễ dùng, kể cả bạn chưa thích tổng thể?
- Người học cần cảm thấy bình tĩnh, tập trung, thi đấu, được hướng dẫn hay vui chơi? Xếp thứ tự, nêu cảm giác cần tránh.
- Bạn muốn mức độ thay đổi nào: chỉnh phong cách, sắp xếp lại từng trang hay thiết kế lại cấu trúc điều hướng? Vì sao?
- Bạn có ảnh chụp ở màn hình thật không? Ghi thiết bị, độ phân giải, mức zoom và chỗ phải cuộn hoặc chữ khó đọc.

## UX02 Thương hiệu và ngôn ngữ thiết kế

Liên hệ V4 B. Chốt bản sắc trước khi chọn chi tiết trang trí.

- Chọn hướng chủ đạo: câu lạc bộ cờ truyền thống, công cụ phân tích thể thao, lớp học hiện đại hay tối giản cao cấp? Có thể phối tối đa hai hướng.
- Cờ Chill là tên chính thức hay tạm? Dòng mô tả ngắn dưới logo nên nói chính xác điều gì?
- Bạn có logo gốc và quyền sử dụng không? Gửi file vector nếu có; ghi phiên bản sáng tối và kích thước nhỏ cần dùng.
- Bạn muốn biểu tượng nhận diện là quân cờ, bàn cờ, chữ viết tắt hay hình riêng? Điều gì không được dùng vì dễ nhầm thương hiệu khác?
- Giọng văn nên là HLV nghiêm túc, bạn học cùng hay trung tính? Viết một câu chào và một câu phản hồi khi người học sai.
- Thuật ngữ nào bắt buộc tiếng Việt, thuật ngữ nào chấp nhận tiếng Anh? Ví dụ review, puzzle, dashboard, engine, WHAT WHY HOW.
- Có cần mascot/nhân vật không? Nếu có, chỉ xuất hiện ở đâu và lúc nào tuyệt đối không che bàn cờ hoặc ngắt việc học?
- Giao diện có nên khác theo trình độ hay giữ một phong cách chung? Nếu khác, nêu khác về thông tin và thao tác thay vì chỉ đổi màu.

## UX03 Màu sắc và chủ đề

Liên hệ V4 B và I. Mã màu là phương án minh họa để bạn lựa chọn, chưa phải palette đã được kiểm tra tương phản.

- Chọn nền tổng thể: sáng ấm, trắng lạnh, tối hay theo hệ điều hành? Bản tới cần một hay cả hai theme?
- Màu thương hiệu chính bạn muốn là gì? Gửi HEX hoặc ảnh mẫu; có giữ xanh #244E50 hiện tại không?
- Màu phụ và màu nhấn nên dành cho thành phần nào: nút chính, liên kết, badge hay biểu đồ? Có màu nào cấm dùng?
- Màu nền bàn cờ nên là gỗ nhạt, ngà phẳng, giấy hay xanh xám? Ưu tiên ít nhiễu hay chất liệu rõ?
- Đỏ và Đen của hai bên cần sắc độ nào? Khi dùng theme tối, làm sao vẫn phân biệt quân, chữ và điểm đến?
- Chốt màu và ký hiệu bổ sung cho thành công, lỗi, cảnh báo, đang chọn, đang chiếu và nước vừa đi; những trạng thái nào không được trùng nhau?
- Bạn muốn bảng màu ít màu trung tính hay nhiều màu theo kỹ năng? Nếu mỗi kỹ năng một màu, cần tên/biểu tượng kèm theo thế nào?
- Bạn muốn xem thử ba hướng nào: xanh mực và vàng đồng; ngà và đỏ gạch; than chì và xanh ngọc? Có cần tự gửi hướng thứ tư?

## UX04 Chữ và mật độ thông tin

Liên hệ V4 B và I. Không cần biết tên font; có thể gửi ảnh minh họa.

- Chọn cảm giác chữ: sans hiện đại, serif truyền thống hay chỉ serif cho tiêu đề? Font phải hỗ trợ đầy đủ dấu tiếng Việt.
- Chữ Hán trên quân nên là kiểu thư pháp hay nét rõ tiêu chuẩn? Người không biết chữ Hán cần nhãn phụ nào?
- Bạn thấy cỡ chữ hiện tại nhỏ, lớn hay vừa? Chỉ rõ thiết bị và vùng: nội dung, ký phổ, nhãn nút hoặc lời giải.
- Muốn lời giải mặc định ngắn bao nhiêu đoạn và mở rộng chi tiết ở đâu? Có cần chế độ đọc lớn không?
- Tiêu đề trang nên rõ chức năng như “Xem lại ván” hay có câu cảm xúc? Nội dung nào cần bỏ vì dài mà không giúp thao tác?
- Ký phổ, FEN và số liệu có cần font monospace riêng? Chuỗi dài nên xuống dòng, cuộn ngang hay có nút sao chép?
- Với số liệu chưa đủ bằng chứng, muốn hiển thị dấu gạch, “Chưa đủ dữ liệu” hay ẩn thẻ? Không thay bằng số mẫu.
- Bạn thích trang nhiều thông tin nhìn cùng lúc hay ít thông tin theo bước? Nêu riêng cho màn chơi và màn học.

## UX05 Hình khối biểu tượng và hiệu ứng

Liên hệ V4 B và I. Hình thức phải giúp nhìn ra thứ tự thao tác.

- Bo góc muốn vuông, nhẹ khoảng 6–8 px, vừa 12–16 px hay tròn nhiều? Nút, thẻ và hộp nhập có dùng cùng mức không?
- Thẻ nội dung nên tách bằng viền mảnh, nền khác màu, bóng nhẹ hay chỉ khoảng trắng? Bạn ghét cách nào nhất?
- Nút chính nên đặc màu hay viền? Mỗi màn cho phép tối đa bao nhiêu nút nổi bật cạnh nhau?
- Icon nên nét mảnh, nét dày hay khối đặc? Có thay các ký tự trang trí hiện tại bằng bộ icon nhất quán không?
- Hình minh họa trang chủ nên là bàn cờ thật, vector giản lược, ảnh hay không cần? Có nguồn ảnh hợp pháp sẵn có không?
- Có dùng texture gỗ/giấy không? Độ rõ đến đâu để không làm chữ và quân khó nhìn?
- Hoạt ảnh quân đi, mở panel, tải dữ liệu nên nhanh, nhẹ hay tắt? Khi giảm chuyển động phải thay bằng tín hiệu gì?
- Âm thanh ăn quân, chiếu, hoàn thành bài và lỗi có cần riêng không? Mặc định bật/tắt và nút tắt nhanh ở đâu?

## UX06 Bố cục lưới và kích thước

Liên hệ V4 D và I. Ghi thiết bị ưu tiên trước khi chốt pixel.

- Màn hình chính bạn dùng có kích thước và độ phân giải nào? Muốn tối ưu laptop 13 inch, màn lớn hay điện thoại trước?
- Trên desktop màn học, bàn cờ chiếm khoảng 55, 65 hay 75 phần trăm vùng nội dung? Panel lời giải có chiều rộng tối thiểu nào?
- Sidebar nên luôn mở, thu gọn icon hay mở theo nhu cầu? Khi thu gọn phải giữ chữ chú thích thế nào?
- Nội dung nên có chiều rộng tối đa và căn giữa hay trải hết màn hình? Màn siêu rộng dùng khoảng trống để làm gì?
- Header cần luôn bám trên cùng không? Nó có được chiếm bớt chiều cao khiến bàn cờ phải cuộn không?
- Khoảng cách giữa các nhóm nên thoáng hay gọn? Gửi ảnh đánh dấu nơi đang thừa khoảng trắng hoặc quá chật.
- Panel ký phổ và panel lời giải được kéo đổi kích thước không? Nếu không, thứ tự ưu tiên khi thiếu chỗ là gì?
- Khi zoom trình duyệt hoặc tăng cỡ chữ, phần nào được xuống dưới và phần nào cần luôn nhìn thấy để không mất ngữ cảnh?

## UX07 Kiến trúc thông tin và điều hướng

Liên hệ V4 B. Đây là cấu trúc trang người dùng thấy, khác với cấu trúc code.

- Hãy sắp xếp thứ tự menu: Trang chủ, Chơi, Ván của tôi, Xem lại, Luyện, Bài học, Tiến bộ, Ôn tập; mục nào gộp?
- Xem lại và Ôn tập nên là trang riêng hay truy cập từ Ván của tôi/Tiến bộ? Người mới tìm được bằng cách nào?
- Mỗi trang có cần URL riêng để tải lại và quay lại đúng chỗ không? Link chia sẻ phải loại bỏ dữ liệu riêng tư nào?
- Nút Back của trình duyệt nên quay về bước trước, danh sách trước hay trang trước khi vào vòng học? Có giữ vị trí cuộn không?
- Khi rời ván đang chơi hoặc reflection chưa gửi, muốn tự lưu, hỏi xác nhận hay cả hai? Phân biệt rời trang với kết thúc ván.
- Có cần tìm kiếm toàn app theo ván, kỹ năng, bài học không? Nội dung nào được tìm trước khi lời giải được mở?
- Menu mobile nên là thanh dưới, menu kéo ra hay tab trên? Tối đa những mục nào được hiện thường trực?
- Vai trò khách, người học và người biên tập có điều hướng khác nhau thế nào? Có cần công cụ nội bộ ngay bản tới không?

## UX08 Trang chủ P01

Liên hệ V4 B H. Hiện có hero lớn, nút demo, vòng học và thẻ tiến bộ.

- Với người mới, hành động đầu tiên là chơi, demo hay tìm hiểu cách học? Chọn một nút chính và tên nút chính xác.
- Với người quay lại, ưu tiên bài đang dở, lịch ôn hay ván gần nhất? Sắp xếp khi cả ba cùng tồn tại.
- Hero hiện tại có quá lớn hoặc quá nhiều chữ không? Bạn muốn bỏ, rút gọn hay thay bằng bàn cờ có thể tương tác?
- Phần nào phải thấy trong màn đầu không cuộn: nút chơi, bài đến hạn, hướng dẫn ba bước hay tiến độ?
- Khi chưa có dữ liệu, trang nên hướng dẫn thế nào mà không tạo số liệu giả? Có cần ví dụ riêng gắn nhãn demo không?
- Có hiển thị số ngày học, thành tích hoặc chuỗi ngày không? Nếu có, làm sao tránh khiến người nghỉ vài ngày cảm thấy bị phạt?
- Bạn muốn có danh sách ván gần đây ngay trang chủ không? Hiển thị tối đa bao nhiêu và thông tin gì trên mỗi ván?
- Gửi bản phác thảo trang chủ desktop và điện thoại, đánh số các khối theo thứ tự bạn muốn mắt nhìn tới.

## UX09 Bắt đầu và đánh giá đầu vào P02

Liên hệ V4 C. Onboarding và placement đầy đủ chưa được triển khai.

- Người học cần nhập gì trước bài đầu tiên? Mỗi thông tin phải dùng để thay đổi trải nghiệm nào, hay có thể bỏ?
- Người đã biết luật có nút bỏ hướng dẫn ở đâu? Người chưa biết luật đi theo lộ trình nào mà không bị ép placement khó?
- Hướng dẫn thao tác bàn cờ nên là một bước thực hành, tooltip tại chỗ hay video tùy chọn? Khi nào được xem lại?
- Placement hiển thị số câu/thời gian dự kiến trước khi bắt đầu không? Người học được dừng và tiếp tục như thế nào?
- Khi không biết câu trả lời, chọn “Chưa biết” khác với trả lời sai hoặc bỏ dở thế nào trên giao diện?
- Kết quả đầu vào cần nói mức tạm, kỹ năng cần học và bước tiếp theo ra sao, không gắn nhãn trình độ quá chắc chắn?
- Bạn muốn hỏi mục tiêu học bằng danh sách chọn hay câu tự do? Nếu học sinh chọn nhiều mục tiêu thì ưu tiên thế nào?
- Nếu có người học nhỏ tuổi, nội dung hướng dẫn và thông báo dữ liệu cần được ai rà soát trước pilot? Không ghi danh tính trẻ trong file trả lời.

## UX10 Chọn ván và cấu hình P03

Liên hệ V4 D. Hiện có máy local, hai người cùng máy, demo và nhập biên bản.

- Bốn lựa chọn hiện tại nên thành thẻ lớn, tab hay một form? Lựa chọn mặc định nào giúp bắt đầu nhanh nhất?
- Người chơi chọn Đỏ, Đen hoặc ngẫu nhiên ở đâu? Khi review Đen chưa hỗ trợ đầy đủ, phải thông báo giới hạn trước khi bắt đầu thế nào?
- Mức máy nên được mô tả theo tốc độ/chất lượng tìm kiếm hay tên dễ hiểu? Không dùng Elo chưa được đo; bạn muốn nhãn nào?
- Ván luyện có đồng hồ không? Nếu có, chọn preset, cộng giây và tùy chỉnh ở đâu, hay để mục nâng cao?
- Tùy chọn nào phải nhớ lần trước và tùy chọn nào cần hỏi lại để tránh bắt đầu sai chế độ?
- Có cần chọn bộ luật và tóm tắt khác biệt ngay màn này không? Mặc định áp dụng bộ nào theo tài liệu bạn sẽ cung cấp?
- Khi có ván đang dở, tạo mới sẽ lưu ván cũ hay hỏi người chơi? Hai ván song song có được hỗ trợ không?
- Nút demo phải giải thích đây là ván tổng hợp ở đâu để không bị hiểu là ván người dùng thật hoặc ván chuyên nghiệp?

## UX11 Màn đang chơi P04

Liên hệ V4 D. Trong ván thật không hiển thị coaching, đánh giá hay nước tốt nhất.

- Xếp vị trí bàn cờ, tên hai bên, đồng hồ nếu có, ký phổ, nút kết thúc và nút lật bàn trên desktop.
- Chọn quân và điểm đến bằng bấm hay thêm kéo thả? Nếu kéo ra ngoài bàn thì hủy hay trả quân về bằng hiệu ứng nào?
- Chọn nhầm quân hoặc nước không hợp lệ cần báo ngay trên bàn, toast hay dòng trạng thái? Có âm thanh không?
- Nước vừa đi, quân bị ăn và tình trạng chiếu cần thể hiện thế nào mà không biến thành lời khuyên chiến thuật?
- Có được xem lại nước trước khi ván còn chạy không? Nếu có, cần nhãn “đang xem lịch sử” và nút trở về hiện tại ở đâu?
- Các hành động đầu hàng, xin hòa, dừng để học và chọn ván khác phải phân biệt thế nào về kết quả và xác nhận?
- Undo có thuộc chế độ luyện riêng không? Khi dùng, kết quả/attempt cần ghi nhãn có hỗ trợ thế nào thay vì coi như ván thi đấu?
- Khi máy timeout, tab chạy nền hoặc mất kết nối, giữ trạng thái và hiển thị hành động phục hồi thế nào để không đi trùng nước?

## UX12 Chi tiết bàn cờ và quân

Liên hệ V4 D I. Bàn cờ cần kiểm tra bằng thao tác thật, không chỉ ảnh tĩnh.

- Quân hình tròn gỗ nổi, phẳng có viền hay hình khác? Chốt chữ, vòng viền, bóng và kích thước tương đối so với khoảng lưới.
- Có tùy chọn tên quân tiếng Việt thay chữ Hán không? Nhãn nào hiện thường xuyên, khi hover và khi chạm giữ?
- Nét lưới, cung, sông và điểm đặt Pháo/Tốt cần mức đậm nào? Chữ giữa sông giữ Hán tự, đổi tiếng Việt hay bỏ?
- Tọa độ a–i và 0–9 hiện ở một hay hai phía? Khi lật bàn, tọa độ phải giữ tham chiếu cố định thế nào để không nhầm nước?
- Điểm đến hợp lệ, ô đang chọn, nước vừa đi và quân đang bị chiếu dùng viền/chấm/ký hiệu nào? Vẽ từng trạng thái riêng.
- Mũi tên phân tích chỉ xuất hiện sau reflection ở màn học thế nào? Người học có tự vẽ ý tưởng trước đáp án mà không được engine gợi không?
- Quân bị ăn hiển thị danh sách, số đếm hay không cần? Không biến chênh lệch quân thành khẳng định thắng khi chưa có phân tích.
- Kích thước bàn nhỏ nhất chấp nhận trên thiết bị thật là gì? Nếu thiếu chỗ, giảm trang trí, ẩn panel hay chuyển màn ngang trước?

## UX13 Nhập ván và dựng thế P05

Liên hệ V4 D M. Hiện chỉ nhập FEN và nước tọa độ, chưa hỗ trợ mọi file ký phổ.

- Những định dạng bạn thực sự có là gì? Gửi một file mẫu mỗi loại và tên ứng dụng xuất, không chỉ tên đuôi file.
- Màn nhập nên nhận kéo file, dán text, FEN hay chọn ảnh? Xếp thứ tự; nhận dạng ảnh là tính năng cần quyết định riêng.
- Sau khi nhập cần xem trước bàn cờ, số nước, bên đi, tên ván và nguồn trước khi xác nhận không?
- Nếu lỗi ở nước thứ 17, muốn chỉ rõ nước lỗi và thế trước đó ra sao? Có cho nhập phần hợp lệ hay bắt sửa cả ván?
- FEN cấu trúc hợp lệ nhưng không chắc đạt được trong thực chiến cần nhãn và quyền tiếp tục thế nào?
- Công cụ dựng thế bằng đặt quân có cần ngay không? Quy định nút xóa bàn, thế ban đầu, đổi lượt và kiểm tra hợp lệ.
- Nguồn/quyền dùng ván hỏi lúc nhập hay trước khi đưa vào kho bài chung? Mặc định giữ riêng hay công khai?
- Import trùng cùng một ván sẽ gộp, báo trùng hay tạo bản mới? Bạn muốn phân biệt hai bản có ghi chú khác nhau thế nào?

## UX14 Thư viện ván và trang chi tiết P06

Liên hệ V4 D H. Hiện ván gần đây nằm trong dashboard, chưa có thư viện độc lập.

- Mỗi dòng/thẻ ván cần những trường nào: ngày, màu quân, kết quả, đối thủ bí danh, số nước, trạng thái review và nguồn?
- Muốn xem dạng bảng, thẻ bàn cờ thu nhỏ hay chuyển được cả hai? Dạng nào dùng trên điện thoại?
- Các bộ lọc cần thiết nhất là gì: chưa review, đang học, đã học, bên cầm, thời gian, chủ đề hay kết quả?
- Mở ván sẽ vào nước cuối, chỗ dừng hay tổng quan review? Người dùng chọn nước cụ thể từ danh sách thế nào?
- Có cần đổi tên, gắn nhãn, đánh dấu yêu thích, ghi chú và gom theo thư mục không? Xếp thứ tự cần làm.
- Xóa ván có xóa reflection và attempt liên quan không? Người dùng phải thấy phạm vi ảnh hưởng trước khi xác nhận thế nào?
- Có xuất riêng một ván không? Định dạng và thông tin riêng tư nào phải loại bỏ khi chia sẻ?
- Khi danh sách dài, muốn phân trang hay tải thêm? Vị trí và bộ lọc có giữ khi quay lại từ một ván không?

## UX15 Tổng quan xem lại P07

Liên hệ V4 E J. Hiện chọn tối đa ba điểm trong tối đa 24 nước Đỏ gần nhất.

- Trước khi mở từng điểm, tổng quan được phép nói gì mà không lộ lời giải? Có ẩn tên chiến thuật nếu nó là gợi ý quá mạnh không?
- Một ván nên hiện một điểm ưu tiên hay danh sách ba điểm? Khi không có sai lầm rõ, muốn học từ quyết định thú vị thế nào?
- Thứ tự theo thời gian, mức ảnh hưởng hay mục tiêu học? Người học có tự chọn điểm không và có thể quay lại điểm trước không?
- Có cần timeline/đồ thị đánh giá không? Nếu có, thời điểm nào được mở để không vô tình tiết lộ đáp án trước reflection?
- Phân tích toàn ván lâu cần hiển thị tiến độ theo số thế đã xong hay từng điểm sẵn sàng? Không dùng phần trăm giả khi chưa đo được.
- Người học được hủy và quay lại sau thế nào? Phần đã tính có được giữ, và kết quả cũ phải ghi thời điểm/phiên bản nào?
- Khi kết quả engine chưa ổn định, nhãn “cần kiểm chứng” đặt ở đâu? Có cho đưa điểm đó vào bài luyện tính điểm không?
- Review cầm Đen, ván chưa xong hoặc ván dừng để học cần khác lời dẫn và phạm vi đánh giá thế nào?

## UX16 Màn suy nghĩ P08

Liên hệ V4 E F. Khóa đáp án trên server vẫn là yêu cầu bắt buộc.

- Ba câu hiện tại nên cùng một trang hay lần lượt từng câu? Trên điện thoại cần nhìn bàn cờ trong lúc gõ bằng cách nào?
- Cho người học chọn quân/nước ứng viên trên bàn rồi tự điền ký hiệu vào câu trả lời không? Có cho ghi nhiều ứng viên không?
- Mỗi câu cần ô text, lựa chọn, giọng nói hay phối hợp? Giọng nói có thể làm sau; bạn ưu tiên đầu vào nào trước?
- “Chưa biết” nên là nút riêng, lựa chọn có lý do hay cho nhập tự do? Làm sao vẫn khuyến khích quan sát trước khi mở đáp án?
- Bản nháp tự lưu tại máy hay server và báo “Đã lưu” ở đâu? Nếu lưu thất bại, người học có thể sao chép trước khi rời không?
- Ví dụ gợi cách trả lời phải dùng thế khác hay câu hỏi quan sát trung tính nào để không gợi đúng nước hiện tại?
- Sau khi gửi, cho sửa suy nghĩ không? Nếu có, giữ bản trước đáp án riêng với phần tự sửa sau đáp án thế nào?
- Mức tự tin hiển thị ba lựa chọn hay thang điểm? Thông tin này sẽ dùng để điều chỉnh lời dẫn nào thay vì chỉ thu cho đủ?

## UX17 Màn phân tích và lời giải P09

Liên hệ V4 F J K. Mọi nước/biến/đánh giá phải có căn cứ từ luật và engine.

- WHAT WHY HOW nên là ba khối, tab hay một mạch kể? Mặc định mở phần nào và phần nào có thể thu gọn?
- Khi đọc một câu mô tả, có cần bấm để bàn cờ phát biến tương ứng không? Nút trước/sau/reset đặt ở đâu?
- So sánh nước đã chơi và nước tốt nên đặt cạnh nhau, dùng tab hay một bàn có chuyển nhánh? Trên mobile dùng cách nào?
- Có nhiều nước chấp nhận được thì trình bày phương án chính và thay thế ra sao để không dạy rằng chỉ một nước là đúng?
- Điểm engine, độ sâu, phiên bản, biến kiểm chứng và cảnh báo phải hiện ngay hay trong chi tiết? Những nhãn nào luôn phải thấy?
- Khi suy nghĩ của người học đúng một phần, muốn trích lại câu nào và phản hồi theo cấu trúc nào? Không tự gán động cơ từ một nước đi.
- Nút báo sai cần chọn lỗi nước đi, lời giải, mức độ khó hay lỗi hiển thị? Có kèm vị trí/phiên bản tự động nhưng không gửi dữ liệu thừa không?
- Khi engine và người duyệt bất đồng, có tạm ẩn bài, hiển thị tranh luận hay chỉ ghi đang kiểm chứng? Ai được đóng việc xác minh?

## UX18 Thử lại và hoàn thành P10

Liên hệ V4 E F H. Lần sửa sau đáp án không được tính là lần tự giải đầu tiên.

- Trước thử lại, ẩn lời giải hay cho thu gọn? Người học phải biết việc đã xem đáp án được ghi nhận thế nào?
- Bài thử lại yêu cầu một nước, một chuỗi hoặc giải thích lại ý tưởng? Ai xác định điều kiện hoàn thành từng loại bài?
- Khi đi sai, báo đúng/sai ngay hay cho đối phương đáp rồi người học tự nhận ra? Phải dừng ở đâu để tránh kéo dài vô ích?
- Số lần thử lại có giới hạn không? Nếu nhiều lần vẫn sai, chuyển sang hướng dẫn có bước nhỏ như thế nào?
- Nếu nước khác vẫn tốt, chấp nhận và giải thích khác biệt thế nào? Nếu chưa đủ bằng chứng, không đánh sai chắc chắn ra sao?
- Màn hoàn thành cần một takeaway, so suy nghĩ trước/sau hay chỉ nút bài liên quan? Chọn thứ tự ưu tiên.
- Lời chúc mừng, hiệu ứng và âm thanh nên đến mức nào? Có thể hoàn thành mà không phá nhịp tập trung không?
- Nếu thoát sau thử lại nhưng trước bài liên quan, lần sau vào đúng bước nào và ghi tiến độ chưa hoàn thành cả vòng thế nào?

## UX19 Bài liên quan và luyện tập P11

Liên hệ V4 G H. Kho hiện có 12 bài tổng hợp, chưa có bộ bài chuyên gia duyệt.

- Danh sách chủ đề nên dùng tên kỹ năng, dạng chiến thuật hay mục tiêu như “đỡ bỏ quân”? Viết tên bạn muốn người mới hiểu.
- Trước bài, cho thấy kỹ năng và độ khó đến đâu để không lộ mẹo? Có chế độ luyện trộn không ghi chủ đề không?
- Bài liên quan sau review cần nói quan hệ với lỗi vừa học thế nào mà vẫn kiểm tra áp dụng độc lập?
- Bài mới, đã gặp, lật gương và cùng family cần nhãn phân biệt nào? Bạn chấp nhận tiêu chí “chưa gặp” cụ thể nào?
- Mỗi phiên gồm một bài hay một nhóm? Người học chọn thời lượng hay số bài, và được nghỉ giữa các bài thế nào?
- Gợi ý chia bao nhiêu mức: quan sát, ý tưởng, nước cụ thể? Trước reflection chỉ hỗ trợ thao tác hoặc cách quan sát không lộ đáp án.
- Hết bài mới thì ưu tiên ôn, đổi chủ đề hay dừng phiên? Giao diện cần nói thẳng điều gì về giới hạn kho?
- Có lưu yêu thích, bỏ qua, báo bài sai và ghi chú cá nhân không? Bỏ qua có tác động điểm/lịch thế nào cần giải thích cho người học?

## UX20 Bài học và sổ tay P12

Liên hệ V4 C G. Hiện chỉ có nội dung ngắn cho bốn kỹ năng và hướng dẫn cơ bản.

- Bài học tổ chức theo luật quân, khai trung tàn, kỹ năng tư duy hay lộ trình trình độ? Có thể tìm một luật mà không theo khóa không?
- Một bài gồm những phần nào: mục tiêu, ví dụ tương tác, lỗi thường gặp, thực hành và tóm tắt? Độ dài mong muốn?
- Cần video/âm thanh ngay không hay text và bàn cờ tương tác đã đủ? Bạn có nội dung gốc với quyền dùng không?
- Khi nhắc “cản chân Mã” hoặc “ngòi Pháo”, cần tooltip, hình minh họa hay link tới bài luật? Có quay lại đúng chỗ đang học không?
- Người đã biết có được bỏ qua bài và làm kiểm tra không? Hoàn thành bài được xác định bằng xem hết hay thực hành đạt?
- Nội dung bài học được phiên bản hóa thế nào khi sửa luật/lời giải? Người đã học có được thông báo phần thay đổi quan trọng không?
- Có cần in/tải ghi chú cá nhân hoặc tóm tắt bài không? Phần nội dung nguồn ngoài nào không được xuất lại?
- Gửi một bài mẫu theo phong cách bạn muốn và một ví dụ lời giải quá dài/khó để làm chuẩn biên tập.

## UX21 Dashboard tiến bộ P13

Liên hệ V4 H. Hiện có lần thử, bài mới đúng, kỹ năng, lịch và ván gần đây.

- Ba câu hỏi dashboard phải trả lời ngay là gì? Ví dụ hôm nay học gì, lỗi nào tái diễn, có tự giải tốt hơn không.
- Có giữ điểm 0–100 không? Nếu giữ, tên và lời giải thích nào tránh nhầm với Elo hoặc chứng nhận thành thạo?
- Biểu đồ nào thật sự giúp hành động: số lần thực hành, tỷ lệ bài mới đúng, phụ thuộc gợi ý hay tái diễn lỗi? Chọn tối đa ba trước.
- Mẫu ít, không luyện vài ngày hoặc đổi độ khó cần trình bày độ không chắc chắn thế nào? Không nối thành xu hướng chắc chắn từ quá ít điểm.
- Bộ lọc theo tuần/tháng, kỹ năng, mức khó và tự giải/có hỗ trợ có cần không? Mặc định nào ít gây hiểu nhầm nhất?
- Có muốn xem bằng chứng cụ thể dẫn đến nhận xét không? Bấm nhận xét sẽ mở các ván/bài nào?
- So với chính mình hay có bảng xếp hạng? Nếu có so người khác, bạn có mục đích học tập và dữ liệu tương đương nào để biện minh?
- Dashboard của người mới cần một hành động bắt đầu nào thay các thẻ số rỗng? Gửi bản phác thảo trạng thái có và chưa có dữ liệu.

## UX22 Lịch ôn và trở lại học P14

Liên hệ V4 H. Lịch hiện theo kỹ năng bằng quy tắc, chưa gửi nhắc tự động.

- Hiện lịch dạng danh sách hôm nay, lịch tháng hay cả hai? Người học cần quan tâm ngày chính xác hay việc tiếp theo hơn?
- Khi nhiều kỹ năng đến hạn, hiển thị bao nhiêu trong một phiên? Ai quyết định ưu tiên và có giải thích ngắn không?
- Bỏ lỡ lịch một tuần thì chia lại lịch, giữ hàng đợi hay cho chọn khởi động lại? Không phạt vì không mở app theo cách nào?
- “Ôn ngay”, “Để mai” và “Tạm nghỉ” có cần không? Thao tác trì hoãn phải khác với bằng chứng đã nhớ bài thế nào?
- Nhắc trong app, email hoặc push là phạm vi nào? Chốt giờ yên lặng, múi giờ, tần suất và cách tắt nếu triển khai.
- Một bài ôn đã gặp có được gọi là bài mới không? Bạn muốn nhãn và cách giải thích tín hiệu ghi nhớ khác chuyển giao thế nào?
- Người dùng đổi múi giờ hoặc đồng hồ máy sai thì lịch theo thời gian server hay thiết bị? Bạn cần hành vi mong muốn gì?
- Sau phiên ôn, màn kết thúc cần nói việc đã làm, lịch kế tiếp và lựa chọn nghỉ thế nào để không ép luyện vô hạn?

## UX23 Cài đặt hồ sơ và dữ liệu P15

Liên hệ V4 L. Hiện là phiên khách theo cookie, dữ liệu lưu SQLite local.

- Cài đặt chia nhóm Giao diện, Bàn cờ, Học tập, Dữ liệu và Tài khoản thế nào? Mục nào cần ngay trên màn chơi?
- Tùy chọn chữ quân, âm thanh, theme, cỡ chữ và giảm chuyển động lưu ở thiết bị hay tài khoản khi có đồng bộ?
- Khi người dùng xóa cookie và mất liên kết phiên, app cần giải thích và hướng dẫn phòng tránh ở thời điểm nào?
- Chuyển guest sang tài khoản nếu có cần gộp dữ liệu thế nào khi cả hai đã có ván? Có màn xem trước tránh ghi đè không?
- Xuất dữ liệu cần chọn loại và khoảng ngày không? File xuất chứa nguồn, phiên bản và dấu đáp án chưa mở thế nào?
- Xóa một ván, xóa lịch sử luyện và xóa toàn bộ phải tách nút ra sao? Xác nhận cần ghi đúng phạm vi và có cơ hội xuất trước không?
- Có cần trang riêng nêu engine/template/dữ liệu tổng hợp thay vì nhét nhiều cảnh báo lên mọi màn không? Nhãn tối thiểu nào vẫn phải giữ tại chỗ?
- Nếu có tài khoản sau này, quy trình đăng xuất mọi thiết bị, phục hồi và xóa tài khoản cần màn nào? Không cung cấp mật khẩu/key trong câu trả lời.

## UX24 Điện thoại cảm ứng và thiết bị yếu

Liên hệ V4 I. Chốt bằng thiết bị thật bạn hoặc người thử đang có.

- Liệt kê ba tổ hợp thiết bị/trình duyệt ưu tiên, hướng dọc/ngang và mức mạng thường dùng; không chỉ ghi “mọi điện thoại”.
- Màn học mobile nên bàn trên câu hỏi dưới, chuyển tab hay một câu mỗi bước? Khi gõ, có cần xem bàn thu nhỏ cố định không?
- Bàn phím ảo mở lên thì nút gửi và câu đang nhập không bị che bằng cách nào? Sau đóng bàn phím có giữ vị trí cuộn không?
- Chạm nhầm quân sát mép hoặc ngón tay che điểm đến được xử lý thế nào? Có cần xác nhận nước ở màn nhỏ theo tùy chọn không?
- Có cần xoay ngang để xem hai panel không? Nếu khóa hướng dọc, ký phổ và lời giải mở ở đâu?
- Khi app chuyển nền hoặc trình duyệt giải phóng tab, trở lại cần phục hồi những gì: ván, chọn quân, nháp, bước học hay bộ lọc?
- Mạng yếu cần tải phần nào trước? Có cho đọc bài đã tải và xem lịch sử offline không; thao tác ghi sẽ báo chờ đồng bộ thế nào?
- Bạn có muốn cài như PWA sau này không? Nêu lợi ích cụ thể cần như mở nhanh/offline/nhắc lịch, không chọn chỉ vì có biểu tượng app.

## UX25 Khả năng tiếp cận và thao tác thay thế

Liên hệ V4 I. Đây là yêu cầu trải nghiệm cần xác minh, không phải lời tuyên bố đã đạt chuẩn.

- Có người thử cần chữ lớn, tương phản cao, không phân biệt đỏ xanh hoặc đọc màn hình không? Ghi nhu cầu, không cần danh tính.
- Quân hai bên phân biệt thêm bằng chữ/viền/ký hiệu gì để không phụ thuộc màu?
- Bàn phím chọn ô, chọn quân, hủy chọn, đi nước và chuyển panel theo quy ước nào? Có màn trợ giúp phím tắt không?
- Trình đọc màn hình nên đọc ô, quân, bên đi, trạng thái chiếu và nước vừa đi theo thứ tự nào, tránh đọc lại cả bàn quá nhiều?
- Focus sau mở modal, lỗi form, đổi trang và hoàn thành bài phải tới đâu? Người dùng có nhận ra vị trí hiện tại không?
- Khi tăng chữ hoặc zoom, phần nào được cuộn và phần nào phải reflow? Có được mất nút hành động chính không?
- Dấu đúng/sai và biểu đồ cần mô tả text nào thay màu/âm thanh? Animation có phương án giảm chuyển động không?
- Ai sẽ kiểm tra thực tế bằng bàn phím và thiết bị hỗ trợ trước phát hành? Bạn muốn lưu checklist và lỗi truy cập ở đâu?

## UX26 Trạng thái rỗng chờ lỗi và phục hồi

Liên hệ V4 I N. Mỗi màn cần có thiết kế ngoài trạng thái thành công.

- Với từng P01–P15, hãy ghi trạng thái chưa có dữ liệu, đang tải, lỗi, thành công và hành động tiếp theo; trạng thái nào dùng chung?
- Loading ngắn dùng skeleton hay spinner? Tác vụ phân tích dài cần hiển thị đang làm gì, đã xong gì và nút hủy thế nào?
- Khi server không chạy, thông báo phải phân biệt với không có Internet như thế nào? Người dùng local cần chỉ dẫn bật server ở đâu?
- Khi request timeout nhưng server có thể đã lưu, nút thử lại cần đối chiếu trạng thái trước thế nào để tránh ghi hai attempt?
- Lỗi form đặt ngay dưới ô hay đầu trang? Có giữ toàn bộ dữ liệu và đưa focus vào ô lỗi đầu tiên không?
- Thông báo nào nên toast, inline, banner hoặc modal? Thông báo quan trọng có biến mất trước khi người dùng đọc xong không?
- Khi engine/LLM không sẵn sàng, phần nào vẫn dùng được và nhãn fallback phải nói chính xác điều gì?
- Khi cập nhật phiên bản giữa lúc học, cho hoàn thành phiên cũ, tải lại có giữ nháp hay khóa thao tác nào để tránh dữ liệu lệch?

## UX27 Kiến trúc phần mềm và ranh giới hệ thống

Liên hệ V4 J K N và Final Pack kiến trúc. Có thể trả lời “đề xuất kỹ thuật” cùng ràng buộc của bạn.

- Trong ba tháng tới cần local một máy, alpha vài người từ xa hay nhiều thiết bị một tài khoản? Chọn giai đoạn và số người đồng thời dự kiến, không coi là số đã đạt.
- Có yêu cầu bắt buộc React/Next.js/FastAPI từ mục tiêu học hoặc triển khai không, hay giữ stack hiện tại đến khi có lợi ích rõ? Ai sẽ bảo trì?
- Frontend nên chia module Board, Game, Review, Reflection, Practice, Dashboard và Settings thế nào để chỉnh UI không đụng luật?
- Dữ liệu nào server là nguồn chuẩn và dữ liệu nào chỉ là UI tạm: ván, lượt, nháp, ô chọn, lật bàn, attempt, lịch ôn? Khi lệch, bên nào thắng?
- Phân tích engine cần tác vụ nền có job ID, tiến độ và hủy không? Những việc nào được chạy đồng thời, việc nào phải theo đúng lượt?
- Adapter engine, lời giải và persistence cần thay thế độc lập ở mức nào? Thay engine có làm mất kết quả cũ hoặc phải phân tích lại không?
- Có cần cùng một board component cho chơi, review, dựng thế và bài học không? Những quyền tương tác nào khác nhau giữa các chế độ?
- Mốc nào mới chuyển SQLite sang database server hoặc tách dịch vụ? Bạn ưu tiên dễ chạy, chi phí, hiệu năng hay học stack ở giai đoạn nào?

## UX28 Hợp đồng API và tích hợp

Liên hệ V4 K. API hiện là JSON nội bộ; câu trả lời không được chứa key/token.

- Với mỗi thao tác chính, bạn cần phản hồi tức thời hay job chạy nền? Chơi nước, lưu nháp, review và tạo lời giải có ngân sách chờ khác nhau thế nào?
- Có cần chuẩn OpenAPI và phiên bản /api/v1 để frontend/backend làm độc lập không? Tích hợp ngoài nào thật sự cần hợp đồng ổn định?
- Request gửi nước cần game ID, nước, phiên bản ván và mã chống gửi trùng nào? Khi trạng thái cũ, UI sẽ tải lại và giải thích ra sao?
- Lưu reflection và attempt cần quy tắc idempotent thế nào khi double-click, retry hoặc hai tab cùng mở? Lần thử đầu phải được bảo toàn ra sao?
- API lỗi cần mã máy đọc được, thông điệp tiếng Việt, trường lỗi và mã tra cứu nào? Tránh trả stack trace/dữ liệu riêng tư cho người dùng thế nào?
- Phân tích trả engine version, độ sâu, giới hạn, biến và đánh giá với đơn vị nào? Trạng thái chiếu hết phải khác điểm vật chất như thế nào?
- Nếu có LLM, đầu vào tối thiểu là facts đã xác minh nào, đầu ra nào được phép và trường nào tuyệt đối không cho tự tạo? Kiểm tra thất bại sẽ dùng template ra sao?
- Có cần streaming, polling hay WebSocket thật không? Nêu hành vi người dùng đòi hỏi; chốt timeout, hủy, retry, quota và cách báo hết ngân sách.

## UX29 Mô hình dữ liệu và công cụ biên tập P16

Liên hệ V4 L M. Công cụ biên tập/admin chưa có trong prototype.

- Một ván cần lưu nguồn, người sở hữu, bên học, chế độ, bộ luật, trạng thái và phiên bản nào? Trường nào có thể bỏ để giảm thu dữ liệu?
- Một bài cần FEN, đáp án thay thế, cây biến, skill, family, độ khó, nguồn và trạng thái duyệt thế nào? Trường nào bắt buộc trước xuất bản?
- Reflection trước đáp án, bản sửa sau đáp án và ghi chú HLV phải tách thành dữ liệu nào để không làm sai bằng chứng học tập?
- Attempt cần ghi đúng/sai, có hỗ trợ, đã gặp, phiên bản bài/engine và thời điểm nào? Sửa đáp án sai của hệ thống sẽ xử lý attempt cũ ra sao?
- Quyền người tạo, người duyệt và người phát hành nội dung có cần tách không? Có cho tự duyệt bài của mình nhưng ghi rõ giới hạn không?
- Màn biên tập cần dựng bàn, nhập biến, thử nghiệm lời giải và preview learner như thế nào? Có khóa lời giải đúng như người học để test không?
- Lịch sử phiên bản cần ai sửa, sửa gì, lý do và cách rollback nào? Gỡ bài lỗi phải dừng gợi ý nhưng không xóa dấu vết đã học ra sao?
- Retention, export, delete và backup áp dụng cho từng loại dữ liệu thế nào? Dữ liệu đưa vào kho chung phải có đồng ý riêng nào được ghi nhận?

## UX30 Hiệu năng vận hành và đo trải nghiệm

Liên hệ V4 N. Chọn mục tiêu thực tế, sau đó đo; chưa coi mục tiêu là kết quả đã đạt.

- Mục tiêu thời gian mở trang, phản hồi chọn quân, lưu suy nghĩ và phân tích là bao nhiêu trên thiết bị/mạng cụ thể của pilot?
- Khi máy yếu hoặc engine bận, ưu tiên độ sâu, tốc độ hay tiếp tục đọc phần đã xong? Có cấu hình nhẹ/nâng cao không?
- Hosting, domain hoặc tài khoản dịch vụ nào bạn đã sở hữu? Chỉ ghi tên và người quản trị, không gửi thông tin đăng nhập.
- Mức chi cứng theo tháng và cách xử lý chạm trần là gì? Không tự bật dịch vụ trả phí sau khi quota hết.
- Cần log lỗi và metric nào để sửa app mà không ghi nguyên suy nghĩ/cookie/secret? Ai được xem và giữ bao lâu?
- Cần đo người dùng bị kẹt ở bước nào bằng sự kiện gì? Việc đo phải phân biệt demo/test với người dùng pilot thật ra sao?
- Khi phát hành lỗi, ai quyết rollback, báo cho người thử và khôi phục dữ liệu? Mức mất dữ liệu/thời gian dừng chấp nhận là bao nhiêu?
- Bạn muốn mỗi bản bàn giao có screenshot từng trang, danh sách thay đổi, test, giới hạn và hướng dẫn chạy nào để tự nghiệm thu?

## UX31 Nguồn luật và luật cơ bản

Liên hệ V4 J M. Đây là câu hỏi để bạn cung cấp luật và ví dụ; không phải xác nhận bộ luật chính thức.

- Chọn tài liệu luật gốc muốn áp dụng: tên tổ chức/tác giả, phiên bản, năm, ngôn ngữ và file/link. Nếu nhiều nguồn, nguồn nào ưu tiên khi mâu thuẫn?
- Phạm vi là cờ tướng tiêu chuẩn, biến thể địa phương hay luật nhà? Liệt kê khác biệt và cách gắn nhãn để không lẫn với luật thi đấu.
- Với Tướng, cung và đối mặt hai Tướng, hãy gửi một thế hợp lệ và một thế không hợp lệ kèm bên đi và lý do.
- Với Sĩ và Tượng, cung, sông và cản mắt, hãy gửi các trường hợp mép bàn/biên cung bạn muốn kiểm tra; phân biệt Đỏ và Đen.
- Với Mã, gửi ví dụ cản chân ở các hướng, gồm khi ô bị chặn bởi quân mình và quân đối phương; ghi nước thử và kết quả mong đợi.
- Với Xe và Pháo, gửi trường hợp đường trống, quân cản, đúng một ngòi và nhiều ngòi; phân biệt đi không ăn và đi ăn.
- Với Tốt, gửi trước/sau qua sông, sát biên và đến hàng cuối; nêu rõ hướng tiến khi bàn đang lật để tránh nhầm tọa độ.
- Với chiếu và tự chiếu, gửi ví dụ quân đang bị ghim, bắt quân chiếu, chắn chiếu và nước làm lộ Tướng; nêu các nước hợp lệ thay thế nếu biết.

## UX32 Kết thúc ván lặp thế và phán quyết

Liên hệ V4 J. Các tình huống này cần lịch sử nước, không chỉ ảnh/FEN đơn lẻ.

- Theo tài liệu bạn chọn, chiếu hết và hết nước hợp lệ được xử lý thế nào? Gửi ví dụ riêng cho mỗi trường hợp và trích mục quy định.
- Quy tắc lặp thế xác định thế giống nhau bằng những thông tin nào, đếm từ đâu và ai cần đổi nước? Gửi chuỗi nước đủ dài cùng kết quả mong đợi.
- Chiếu liên tục một bên, hai bên cùng chiếu và chuỗi vừa chiếu vừa đuổi được phân biệt ra sao theo nguồn? Gửi từng case thay vì mô tả chung.
- Khái niệm đuổi/quân bị đuổi/quân có bảo vệ và ngoại lệ nào áp dụng? Cần ví dụ dễ nhầm, nguồn điều khoản và mức chắc chắn của người duyệt.
- Các chuỗi đổi mục tiêu, xen nước chờ, bắt quân hoặc tiến Tốt có làm thay đổi cách đếm/phán quyết không? Gửi diễn biến cụ thể.
- Có giới hạn số nước không bắt quân/không tiến Tốt hoặc quy tắc hòa khác không? Đừng tự điền một con số nếu chưa có tài liệu xác nhận.
- Hết giờ, đầu hàng, thỏa thuận hòa, mất kết nối và dừng để học cho kết quả gì trong từng chế độ? Luật đồng hồ có khác với luật đi quân không?
- Khi chưa đủ dữ liệu để phân xử, app nên ghi “cần trọng tài/kiểm chứng” và dừng tính kết quả thế nào? Quy ước lặp ba lần demo hiện tại cần thay/giữ ở phạm vi nào?

## UX33 Ký phổ dữ liệu luật và bộ kiểm thử chuyên môn

Liên hệ V4 J M. Dùng mẫu LUAT ở cuối tài liệu để biến câu trả lời thành test.

- Bạn dùng ký phổ Việt, tọa độ, ký hiệu Hán hay định dạng của app nào? Gửi cùng một đoạn ván ở hai cách ghi nếu muốn hỗ trợ chuyển đổi.
- Quy tắc ghi hai quân cùng loại/cùng cột và thứ tự trước sau cần theo nguồn nào? Gửi ví dụ dễ nhập nhầm ở cả hai phía.
- FEN dùng ký tự quân nào, bên đi và trường bổ sung nào? Khi nhập biến thể ký tự, cho chuẩn hóa tự động hay báo cần xác nhận?
- Thế dựng không có lịch sử có được dùng luyện luật/chiến thuật không? Những kết luận nào phải từ chối vì thiếu lịch sử?
- Ai có thể duyệt độc lập các case luật bạn gửi? Ghi vai trò và mức xác minh, không cần thông tin cá nhân nhạy cảm.
- Với mỗi case, bạn có thể ghi tập nước hợp lệ/cấm, nước đang thử, kết quả ván và lý do không? Nếu chưa biết đáp án, đánh dấu cần kiểm chứng.
- Case nào bắt buộc trở thành regression test trước mỗi lần sửa engine/rules? Xếp lỗi gây sai kết quả ván cao hơn khác biệt trình bày.
- Nếu tài liệu luật, engine và ý kiến chuyên gia mâu thuẫn, quy trình ghi nhận/chốt thế nào? Có giữ nguyên cả các bằng chứng thay vì sửa mất lịch sử không?

## UX34 Nghiệm thu thiết kế và gói bàn giao

Liên hệ V4 N. Chốt thế nào là đạt trước khi bắt đầu thay giao diện.

- Chọn năm trang phải thiết kế lại trước và xếp thứ tự. Với mỗi trang, nêu một vấn đề quan trọng nhất và hành vi mong muốn sau sửa.
- Bạn muốn duyệt theo bước moodboard → wireframe → mockup → web chạy hay xem trực tiếp hai phương án web? Mốc nào chốt để tránh sửa lan truyền?
- Với từng trang, tiêu chí đẹp/dễ dùng quan sát được là gì: thấy nút chính, đọc rõ quân, ít cuộn, không mất nháp hay hoàn thành không hướng dẫn?
- Bạn sẽ gửi bản vẽ tay, screenshot đánh dấu, Figma hay mô tả text? Đặt tên file theo Pxx và UXxx.xx để liên kết câu trả lời thế nào?
- Thiết bị, viewport, dữ liệu thử và trạng thái nào phải có ảnh nghiệm thu? Bao gồm rỗng, chờ, lỗi và thành công thay vì chỉ happy path.
- Mức độ ưu tiên dùng Bắt buộc, Nên có, Sau này và Không làm thế nào? Khi xung đột giữa đẹp và dễ dùng, ai chốt và theo mục tiêu nào?
- Bạn muốn tôi tự quyết những chi tiết nào như spacing, component hoặc tên module, và những thay đổi nào cần đối chiếu câu trả lời trước?
- Khi gửi lại hai bộ V4, bạn muốn bảng tổng hợp quyết định gồm mã, câu trả lời, nguồn ảnh, phần thay V3/V4, trạng thái triển khai và tiêu chí kiểm thử không? Có trường nào cần thêm?

## Mẫu phác thảo trang và hình khối

Các sơ đồ dưới đây chỉ là phương án để đánh dấu/sửa. Ghi A, B hoặc C cho từng trang; không coi đây là thiết kế đã chọn. Có thể vẽ tay, chụp ảnh và đặt tên P08_mobile_v1.png. Hình chữ nhật biểu diễn vùng chức năng; màu, bo góc và typography chốt riêng.

### Phương án A cho màn học desktop

```text
HEADER tên trang và trạng thái lưu
MENU | BÀN CỜ khoảng hai phần ba | CÂU HỎI hoặc LỜI GIẢI
     | tên hai bên và công cụ   | một hành động chính
     | ký phổ thu gọn           | nguồn và chi tiết mở rộng
```

### Phương án B cho màn học điện thoại

```text
TIÊU ĐỀ và nút quay lại
BÀN CỜ vừa chiều rộng
THANH chuyển Quan sát hoặc Trả lời
MỘT CÂU HỎI và ô trả lời
NÚT lưu hoặc tiếp tục không che bàn phím
ĐIỀU HƯỚNG thu gọn khi cần tập trung
```

### Phương án C cho trang chủ quay lại

```text
LỜI CHÀO ngắn và trạng thái local
TIẾP TỤC bài đang dở với một nút
ÔN HÔM NAY | CHƠI VÁN MỚI
VÁN GẦN ĐÂY và một việc nên luyện
THÔNG TIN CHI TIẾT chỉ khi cần
```

### Phiếu thiết kế một trang để sao chép

Mã trang P… và tên: …
Người dùng và mục tiêu duy nhất của trang: …
Đi vào từ đâu và đi tiếp đến đâu: …
Các khối theo thứ tự nhìn và tỷ lệ kích thước: …
Hành động chính và hành động phụ: …
Dữ liệu được thấy trước reflection và dữ liệu chỉ sau reflection: …
Desktop và mobile khác nhau thế nào: …
Trạng thái rỗng đang chờ lỗi thành công và mất kết nối: …
Điều phải giữ khi reload hoặc quay lại: …
Ảnh/bản vẽ đính kèm và chi tiết thích/không thích: …
Tiêu chí nghiệm thu quan sát được: …

## Mẫu gửi luật cờ để chuyển thành kiểm thử

Sao chép mẫu này cho từng quy tắc/tình huống. Một case nên kiểm tra một điểm chính. Không cần tự kết luận nếu đang có bất đồng.

Mã LUAT001 và tên quy tắc: …
Bộ luật tổ chức phiên bản năm mục trang: …
File hoặc link nguồn và phạm vi quyền sử dụng: …
Phát biểu quy tắc bằng lời của bạn: …
FEN hoặc ảnh bàn cờ rõ và bên đến lượt: …
Chuỗi nước trước đó nếu liên quan lặp chiếu đuổi đồng hồ: …
Nước đang thử: …
Mong đợi hợp lệ hay không hợp lệ: …
Kết quả ván hoặc phán quyết mong đợi nếu có: …
Giải thích và ngoại lệ: …
Case gần giống nhưng kết quả ngược lại: …
Người/engine đối chiếu phiên bản và điều chưa chắc: …
Trạng thái đề xuất chủ dự án chốt đã test đã duyệt độc lập: …

## Mẫu hợp đồng một thao tác API

Sao chép nếu bạn có yêu cầu tích hợp cụ thể; có thể để tôi đề xuất phần kỹ thuật.

Thao tác và trang gọi: …
Người được phép gọi và dữ liệu được phép đọc: …
Thông tin gửi lên không chứa secrets: …
Thông tin trả về và thông tin phải giữ kín trước reflection: …
Điều kiện trước khi thực hiện: …
Kết quả lưu và ảnh hưởng lên ván attempt lịch ôn: …
Thời gian chờ timeout hủy và retry: …
Gửi trùng hoặc hai tab đồng thời xử lý thế nào: …
Mã lỗi và hành động phục hồi trên UI: …
Ví dụ đúng ví dụ sai và tiêu chí kiểm thử: …

## Cách đóng gói câu trả lời

Gửi một thư mục gồm V4 đã trả lời, Word bổ sung này đã trả lời, thư mục UI cho ảnh/bản vẽ, thư mục LUAT cho tài liệu và case, thư mục VAN_CO cho biên bản. Dùng tên Pxx_UXxx.xx cho ảnh trang và LUAT001 cho case luật. Trong Word ghi tên file tương ứng; không gửi key, mật khẩu hoặc database có dữ liệu người khác.

Đợt đầu có thể gửi câu ưu tiên, ba ảnh tham chiếu có chú thích, hai bản phác thảo màn học/trang chủ, và một nhóm case luật rõ nhất. Sau đó trả lời các câu còn lại theo từng nhóm. Mọi câu chưa trả lời cần để trạng thái chưa chốt; không tự xem im lặng là đồng ý.

Sau khi nhận đủ, đầu ra tiếp theo cần là bản quyết định hợp nhất đối chiếu V3/V4, sơ đồ trang, hệ màu/chữ/component, wireframe desktop/mobile, hợp đồng API, bộ case luật và backlog có tiêu chí nghiệm thu. Việc triển khai sẽ theo thứ tự ưu tiên bạn chốt, không mặc định thực hiện mọi tính năng tương lai được hỏi trong tài liệu này.
