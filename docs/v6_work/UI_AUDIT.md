# Đánh giá giao diện Cờ Chill cho bản bàn giao V6

Ngày kiểm tra 25/10/2026. Phạm vi là đọc mã và đối chiếu hai ảnh người dùng cung cấp; không sửa mã ứng dụng, không xuất bản, không thay đổi tài khoản hoặc hosting. Các đề xuất dưới đây là công việc cho vòng triển khai tiếp theo, không phải tính năng đã hoàn thành.

## 1 Nguồn đối chiếu và phạm vi xác minh

Nguồn chính mới nhất: `C:/Users/thanh/Downloads/xiangqi-ai-20261024T180855Z-1-001.zip` (117.516.268 byte, 1.217 entry). Đã đọc danh mục và so sánh từng byte, không giải nén hoặc chạy mã bất kỳ trong ZIP. Cả 16 file dưới đúng prefix `xiangqi-ai/online-preview/` (15 file runtime và README) giống hoàn toàn thư mục `online-preview/` hiện tại.

ZIP còn có các bản cũ dưới `xiangqi-ai/deliverables/Co_Chill_VSCode_2026_10_17/online-preview/` và `xiangqi-ai/var/co-chill-web-source-gon/online-preview/`. Các bản đó có `app.js`, `index.html`, `learning.js`, `experience.js` cũ hơn. Claude phải chọn đúng thư mục nguồn chính, không lấy file đầu tiên tìm thấy khi tìm đệ quy.

Gói `deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24.zip` cũng có đủ 15 file runtime và tất cả giống từng byte với nguồn chính. Đây là cơ sở kiểm tra mã bản đã bàn giao. Chưa lấy lại file trực tiếp từ máy chủ công khai trong đợt đánh giá này; ảnh người dùng là bằng chứng về lỗi hiển thị thực tế.

## 2 Lỗi chữ tiếng Việt trong ảnh tài khoản

### Những gì đã xác nhận

- `online-preview/v5-ui.js:103` chứa đúng chuỗi `Chưa kết nối máy chủ tài khoản`.
- Đã đọc UTF-8 toàn bộ file HTML/CSS/JS của `online-preview/`: tất cả đều ở dạng Unicode NFC, không có ký tự thay thế U+FFFD, không có dấu kết hợp Unicode rời. Vì vậy chưa có bằng chứng rằng lỗi này do lưu sai encoding hoặc chuỗi NFD trong mã nguồn.
- `online-preview/index.html:4` đã có charset UTF-8.
- `online-preview/style.css:21` đặt h1 bằng Georgia, Times New Roman, serif; dòng 22 đặt h2 bằng cùng nhóm font. h1 có letter-spacing âm 0,7 px; h2 không đặt letter-spacing riêng.
- Đã đọc bảng cmap trong font thực tế tại `C:/Windows/Fonts/georgia.ttf` và `georgiab.ttf` bằng Python standard library. Cả hai thiếu các ký tự ư U+01B0, ả U+1EA3, ế U+1EBF, ố U+1ED1, ủ U+1EE7 có trong câu trên. Các file Times, Arial, Segoe UI ở cùng máy có đủ ký tự của câu.

### Kết luận và giới hạn

Có vấn đề thực về độ phủ tiếng Việt của font Georgia tại môi trường local; hiện tượng chữ/dấu lệch trong ảnh phù hợp với khả năng trình duyệt phải thay font hoặc dựng tổ hợp dấu. Tuy nhiên chưa đọc được mục Rendered Fonts/computed style của đúng tab trong ảnh, nên chưa khẳng định duy nhất cơ chế browser gây lỗi. Không nên báo đã sửa chỉ bằng cách gọi normalize NFC: chuỗi hiện tại đã NFC.

### Hướng xử lý cụ thể

1. Dùng font tiêu đề có đủ tiếng Việt. Quyết định bảo trì đơn giản nhất là dùng cùng Segoe UI/Arial/sans-serif cho các tiêu đề chức năng; có thể giữ chữ thương hiệu bằng ảnh logo đã có. Nếu muốn một font serif riêng, dùng bản font có đủ Vietnamese subset, giấy phép rõ, được lưu kèm dự án thay vì phụ thuộc font cài trên máy người xem.
2. Tập trung token `--font-ui` và `--font-heading`, áp dụng h1/h2/brand có chủ đích; không thay font chữ Hán của quân cờ một cách mù quáng.
3. Chạy trang mẫu chữ `Cờ tướng — kết nối — Nguyễn — luyện tập — đường đi — quyền quản trị — tướng, sĩ, tượng, xe, pháo, mã, tốt` ở normal/bold và cả ba theme. Kiểm tra bằng ảnh thật trên Chrome/Edge Windows và Safari/iOS hoặc thiết bị tương đương có người kiểm thử.
4. Mở DevTools kiểm tra font thực được dùng và chữ còn thiếu, kiểm tra không có CSS từ extension/bản cũ xen vào. Nếu chọn font mới, lưu file license và kiểm thử khi font tải thất bại.
5. Kiểm tra độ cao dòng tiêu đề, cắt dấu phía trên/dưới, phóng to 125/200 phần trăm, tránh đặt height cố định cho vùng chữ.

Nghiệm thu: không có dấu tách, ô vuông, chữ trộn font bất thường ở các chuỗi tiếng Việt mẫu; chữ không bị cắt ở cả 3 theme; không đổi luật chơi hay ngắt trạng thái phiên học.

## 3 Trang chủ bị bó chữ thành cột hẹp

### Căn cứ trong mã

- `online-preview/style.css:67` giữ `.home-intro` căn giữa và max-width 740 px của bố cục cũ.
- `online-preview/v5.css:5` thêm padding-right 44 phần trăm vào cùng khối; dòng 6 đặt cover position absolute, width 40 phần trăm và height 260 px.
- Padding phần trăm được tính theo chiều rộng khối chứa. Kết hợp max-width cũ và padding lớn làm phần dành cho tiêu đề bị hẹp. Ảnh người dùng cho thấy đúng hậu quả: nhiều dòng ngắn và khoảng trống giữa chữ với cover.
- `style.css:269–271` thay đổi font và bỏ br ở desktop nhưng không giải quyết chỗ chứa chữ quá hẹp. `v5.css:19` chỉ chuyển về bố cục một cột khi viewport không quá 900 px, để lại nhiều độ rộng trung gian chưa tối ưu.
- Cover nguồn có tỷ lệ 1536 × 1024 nhưng đang ép object-fit cover trong ô có tỷ lệ biến đổi; nội dung ảnh có thể bị cắt khi card hẹp.

### Hướng sửa

Chuyển hero thành CSS Grid có hai phần thật: `home-copy` và `home-visual`, bỏ padding giả lập cột và absolute positioning. Desktop dùng hai cột minmax(0, 1fr), gap khoảng 24–40 px theo chiều rộng container. Mobile xếp một cột; nội dung và nút tiếp tục phải xuất hiện sớm, ảnh không đẩy thao tác chính xuống nhiều màn hình. Không tiếp tục chồng thêm media query lên quy tắc lỗi cũ.

Đề xuất copy ngắn để người dùng duyệt: tiêu đề `Chơi cờ, hiểu từng nước.`; mô tả `Chơi một ván hoặc tiếp tục bài học của bạn.`. Giữ một CTA động theo quyết định V5 đã có: tiếp tục ván đang chơi, rồi ôn đến hạn, rồi bài đang dở, rồi bắt đầu. Bốn ô chính Chơi cờ, Bài học, Ván của tôi, Ôn tập vẫn giữ; không đặt thêm nhiều CTA cạnh tranh ngang hàng trên hero.

Visual chính ưu tiên bàn cờ nhỏ từ FEN hợp lệ hoặc cover thương hiệu có tỷ lệ cố định, không dùng một ảnh to chứa lại logo với nội dung gần giống header nếu nó không giúp hiểu hành động. Ảnh trang chủ trang trí không được làm lộ đáp án bài đang dở.

Nghiệm thu: tại 1024/1280/1440/1920 CSS px, tiêu đề không bị ép thành 5–6 dòng ngắn như ảnh; không có khoảng trống do absolute image; tại 360/390/768 px và zoom 200 phần trăm, không tràn ngang, nút chính và chữ không bị ảnh che. Tối đa 2–3 dòng tiêu đề trên desktop là mục tiêu thiết kế, không ép giữ nếu người dùng phóng chữ lớn.

## 4 Ba theme đã có nhưng khó tìm

### Trạng thái thực tế

- `online-preview/experience.js:8–12`: bộ tùy chọn warm/cool/dark và kiểm tra giá trị hợp lệ.
- `online-preview/app.js:162`: Cài đặt có select Chủ đề với Sáng ấm, Trắng lạnh, Tối và nút Lưu tùy chọn.
- `online-preview/app.js:160`: áp dụng data-theme và lưu tùy chọn vào localStorage.
- `online-preview/style.css:3–11` có palette, sau đó `v5.css:15–16` lại ghi đè cool/dark. Có hai nơi định nghĩa cùng theme, dễ sửa thiếu hoặc lệch màu.
- `style.css:233–239` đã có CSS theme-picker/theme-swatch, nhưng form cài đặt hiện dùng select, không dựng ba ô xem trước tương ứng.
- `tools/test_v5_ui.cjs:74–121` có kiểm thử lưu theme và cô lập preference theo tài khoản; đây là kiểm thử logic, không thay thế thử hình ảnh/độ tương phản.

Không nên viết `chưa làm 3 theme`. Công việc đúng là tăng độ dễ tìm, đồng bộ token, sửa và nghiệm thu đủ thành phần.

### Hướng sửa

Đặt nút Giao diện có biểu tượng tại header hoặc menu avatar, dẫn tới ba ô màu có tên rõ. Trong Cài đặt hiển thị cả ba thẻ preview, trạng thái chọn có dấu tick và aria-pressed hoặc radio chuẩn; người dùng nhìn thấy kết quả ngay khi chọn. Nếu lưu cloud thất bại vẫn giữ nháp local, hiện trạng thái thật; không lẫn preference của tài khoản khác.

Gộp palette vào một nguồn định nghĩa duy nhất. Kiểm tra button, disabled/focus, input/error, board, quân Đỏ/Đen, mũi tên, bảng, modal, account status. Không đổi nghĩa màu đỏ lỗi và nước bị chiếu qua theme. Hình minh họa nên dùng SVG theo token hoặc ảnh có nền trong suốt để không tạo mảng trắng chói trên nền tối.

Nghiệm thu: từ bất kỳ trang chính, tối đa hai thao tác để thấy ba lựa chọn; đổi theme và tải lại vẫn đúng; đổi tài khoản không lấy nhầm theme; chữ và điều khiển có tương phản đủ đọc; focus không chỉ dựa vào màu.

## 5 Ít chữ hơn nhưng thông tin học vẫn đầy đủ

Ba loại hình có mục đích riêng:

1. Icon điều hướng tự dựng SVG, có nhãn chữ ngắn. Chỉ icon không có tên dễ làm người mới đoán sai.
2. Sơ đồ bàn cờ dựng từ FEN hợp lệ cho bài học, bài tập, ván cũ. Cùng một renderer với bàn chơi giúp kiểm chứng quân và vị trí; không dùng hình tạo sinh làm nguồn sự thật luật cờ.
3. Minh họa thương hiệu từ logo/cover người dùng đã cung cấp hoặc tài sản có quyền rõ. Dùng tiết chế cho trạng thái trống, chào mừng, tổng kết; không che bàn cờ.

Chia thông tin theo nhịp: trước khi làm có tên bài, mục tiêu một câu và bàn cờ; sau phản ánh mới mở lời giải; trong lời giải mỗi bước có thế trước/sau, mũi tên hợp lệ và 1–2 câu. Phần căn cứ engine, độ sâu, nguồn bài nằm trong mục Chi tiết, vẫn truy cập được khi cần. Không giấu thông tin bắt buộc như chưa lưu/engine lỗi/đang dùng fallback.

Không dùng nhãn `đã hiểu` khi người chơi chỉ bấm xem hết; không biến minh họa thành coaching trong ván trực tiếp. Thumbnail bài chưa giải không vẽ sẵn mũi tên đáp án.

## 6 Đề xuất theo từng trang

### Trang chủ

Hero grid mới, bốn card chủ chốt và một ô tiếp tục. Dùng mini-board hoặc biểu tượng theo hoạt động. Ẩn số 0 vô nghĩa với người mới, thay bằng gợi ý bắt đầu có thể thao tác. Người quay lại thấy ván/bài dở đúng trạng thái.

### Chơi

Ba lựa chọn rõ: Với máy, Cùng bạn trên thiết bị, Trực tuyến. Chỉ mở Trực tuyến khi backend PvP có thật; trước đó ghi Sắp có ở mức roadmap, không tạo nút vào trận giả. Mức máy, thời gian và màu quân gọn trong panel; bàn cờ chiếm ưu tiên. Khi chơi không hiển thị eval/hint/lời giải. Điều khiển hòa, xin thua, mất kết nối cần xác nhận đúng hành vi và không che bàn.

### Bài học và thư viện puzzle

Hiện `app.js:64` chỉ có ba tab giai đoạn và danh sách chữ; tab trung/tàn dùng lại cùng kho hình mẫu. Đổi sang card có thumbnail FEN, chủ đề, mục tiêu, độ khó tạm tính, độ dài dự kiến và trạng thái đã học. Bộ lọc nhiều chiều phải thật sự lọc dữ liệu; không chỉ đổi tiêu đề trang.

Chủ đề quân Xe/Pháo/Mã/Tốt/Sĩ/Tượng/Tướng là một chiều; chiến thuật, giai đoạn và mức khó là các chiều khác. Không ép một bài chỉ thuộc đúng một quân khi nó cần phối hợp Xe–Pháo. Đường học có bài giảng → ví dụ tương tác → bài tự làm → bài chuyển giao → ôn; số bài thực đã duyệt được hiển thị đúng.

### Hành trình học

`app.js:164` hiện bốn node dẫn tới luật, bài học, chơi, ôn; không phải curriculum. Đổi thành các chương có quan hệ tiên quyết và node kỹ năng. Mỗi node có biểu tượng/mini-board, tên, mục tiêu ngắn, số bài, tiến độ, nút tiếp tục. Trang chi tiết chương mới chứa nội dung dài. Chưa chốt ngưỡng mastery thì cho học tự do và gợi thứ tự, không khóa giả theo EXP.

### Màn học và lời giải

Giữ ba phần tự phản ánh và nước ứng viên đã chốt V5. Giảm cảm giác form dài bằng một câu hỏi chính mỗi bước hoặc nhóm câu gọn có chỉ báo 1/3, nhưng giữ được nháp và quay lại. Khi mở đáp án, có nút đi từng nước, đánh dấu thay đổi và đối chiếu suy nghĩ đầu với nguyên nhân cụ thể. Cần trả lời V6 về một màn/ba bước, không hỏi lại có phản ánh trước đáp án hay không.

### Ván của tôi và xem lại

Card ván có thế cuối hoặc điểm đáng học làm thumbnail; thông tin đối thủ, kết quả, ngày, nguồn, trạng thái phân tích. Màn replay ưu tiên bàn + timeline. Danh sách điểm đáng học dùng thumbnail và lý do ngắn, không dồn mọi PV/CP vào một trang chữ. Phân tích chưa xong phải hiển thị tiến độ và cho hủy.

### Ôn tập

Hiển thị bài đến hạn thành card ngắn, số bài còn lại, thời gian ước tính có nhãn ước tính. Bài bị hoãn sau ba lần thất bại vẫn là cần học tiếp; không mang biểu tượng đã hoàn thành. Trong bài ôn không có thumbnail gợi đáp án. Giữ mốc tính lịch từ hoàn thành theo V5.

### Tiến độ và tổng kết

Dùng biểu đồ cột kỹ năng, lịch hoạt động, node đã hoàn tất; nhãn phân biệt tự giải/có hỗ trợ. Kèm số lượt làm mẫu số thật, dữ liệu còn ít thì nói rõ. Tránh radar/Elo suy diễn chính xác từ vài bài. Cuối phiên có ô tự đánh giá đã chốt, không bắt người dùng nhập đoạn dài để thoát.

### Tài khoản

Ảnh đang hiển thị trạng thái API chưa kết nối, phù hợp bản static. Giữ trạng thái trung thực; đổi lời người dùng sang `Bạn đang dùng chế độ khách. Tiến độ được lưu trên trình duyệt này.` và CTA tiếp tục học. Chi tiết “API, máy chủ tĩnh, backend” chuyển vào hỗ trợ/chế độ kỹ thuật. Khi backend thật có sẵn, trang mới hiển thị đăng nhập/đăng ký và trạng thái lưu rõ. Không hiển thị hứa đồng bộ đa máy như đã hoạt động khi API không có.

### Cài đặt

Ba thẻ theme preview, xem trước chữ Hán/Việt trên quân, cỡ chữ có ví dụ. Dữ liệu xuất/xóa ở nhóm riêng; nút xóa có xác nhận và mô tả phạm vi. Không làm mới cả app khiến người chơi mất vị trí sau khi chọn theme.

### Luật và trợ giúp

Mỗi quân có sơ đồ nước đi, vị trí bị cản, ví dụ đúng/sai; bắt người học thử một thao tác nhỏ thay vì đọc hết bài dài. Luật chiếu/đuổi/lặp phải chờ nguồn và tình huống được duyệt, không dùng infographic đẹp để che sự chưa hoàn chỉnh. FAQ mở dần, hỗ trợ hiển thị đúng cách liên hệ đã được chủ sản phẩm xác nhận.

### Quản trị và biên tập

Tách màn dành cho chủ website khỏi học viên. Hàng bảng quản trị cần lọc/tìm kiếm/phân trang; preview bài phải dùng cùng component với học viên và cảnh báo đáp án chỉ trong preview admin. Dữ liệu bản nháp/published/version không được giấu khi giao diện rút gọn.

## 7 Danh mục tài sản cần tạo

- Một bộ icon SVG thống nhất stroke cho bốn khu vực chính và các chủ đề quân.
- Thumbnail FEN tự sinh, tái dùng renderer; lazy-load theo trang để không dựng hàng trăm bàn cùng lúc.
- Trạng thái trống có minh họa nhỏ cho chưa có ván, chưa có bài đến hạn, chưa có kết quả lọc; kèm hành động cụ thể.
- Mini storyboard ba bước cho hướng dẫn học: tự nghĩ, xem lời giải có căn cứ, luyện lại. Hình không chứa biến cờ chưa xác minh.
- Biểu đồ tiến độ dùng dữ liệu thật. Không làm ảnh tĩnh giả biểu đồ hoạt động.
- Tài sản phải lưu tên, nguồn, giấy phép/quyền, tác giả và nơi dùng. Không sao chép ảnh của website cờ khác chỉ vì đã tham khảo phong cách.

## 8 Thứ tự triển khai UI đề nghị

1. Sửa font tiếng Việt và hero layout trước; chụp so sánh đúng hai màn người dùng báo.
2. Gộp theme tokens và làm theme picker dễ tìm; kiểm thử lưu preference/cô lập tài khoản không bị hồi quy.
3. Tạo component mini-board và card nội dung; xây thêm curriculum data rồi mới dựng trang chủ đề/level, tránh UI nhiều ô rỗng.
4. Giảm chữ trên tài khoản/học/ôn theo trạng thái thực; kiểm tra gate phản ánh và không coaching ván đang chơi.
5. Thêm biểu đồ/illustration đúng dữ liệu, kiểm thử tải mạng chậm và thiết bị cảm ứng.
6. Nghiệm thu cả luồng học, đăng nhập, theme, đồng bộ và điều hướng sau deploy. Không xem 1 ảnh đẹp là đủ nghiệm thu toàn website.

## 9 Ma trận nghiệm thu giao diện

Viewport đề nghị: 360 × 800, 390 × 844, 768 × 1024, 1024 × 768, 1440 × 900 và 1920 × 1080 CSS px; thực tế phải ghi rõ viewport và tỷ lệ zoom của ảnh bằng chứng. Theme warm/cool/dark; cỡ chữ normal/large; zoom 100/125/200 phần trăm; khách, đăng nhập, offline, loading, empty/error và nhiều nội dung.

Kiểm tra: không tràn ngang toàn trang; không che focus; bàn 9 × 10 không méo; chạm được quân/ô ở màn nhỏ; popup và bàn phím ảo không che câu đang nhập; câu hỏi không mất khi đổi tab/reload; ảnh có alt phù hợp; decorative image alt rỗng; nút icon có accessible name; animation tôn trọng reduced motion; màu không phải tín hiệu duy nhất cho đúng/sai.

Cần bổ sung kiểm thử browser screenshot với các trang home/account/settings/lesson/learn/play/path, nhưng không viết snapshot chứa dữ liệu riêng người dùng. Các bài test logic hiện có vẫn phải giữ. Kết quả Unicode/font/ZIP trong báo cáo này là kiểm tra tĩnh, không được gọi là đã chạy thành công tất cả ma trận thiết bị.
