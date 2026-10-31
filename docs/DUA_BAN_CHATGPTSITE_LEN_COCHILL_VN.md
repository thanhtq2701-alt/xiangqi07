# Đưa đúng bản ChatGPT Site hiện tại lên cochill.vn

Ngày 24/10/2026. Phạm vi: **giống giao diện và chức năng của Cờ Chill đang chạy trên ChatGPT Site**, phiên bản sản phẩm V5 / phiên bản Sites 4. Không cần Python cho yêu cầu này.

> Tài liệu lịch sử về bản static ngày 24/10/2026. Production hiện dùng GCP,
> Python backend và Nginx; không làm theo các bước hosting/DNS/Vercel bên dưới.

## Gói dùng cho lần chuyển này

`deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24.zip`

ZIP có đúng 15 file web, lấy từ archive đã phát hành với source commit `748aa97d42c3437a9a36cbc9bf16e3a5c1469a3c`. Đã so từng byte với archive đó; không có `.openai`, database, khóa đăng nhập hoặc tài liệu riêng. File SHA256 nằm cạnh ZIP để đối chiếu, không cần upload file SHA256.

Giải nén ra sẽ thấy `index.html`, 9 file JavaScript, 2 file CSS, favicon và 2 ảnh. Giữ chúng cùng một thư mục. Bản source V5 55 file được gửi trước có thêm backend và kiểm thử; dùng ZIP 15 file này khi chỉ chuyển bản đang thấy trên ChatGPT Site.

## Cần ba thứ

1. **Tên miền:** đã có `cochill.vn` tại Mắt Bão.
2. **Hosting:** nơi giữ và phục vụ 15 file, hoạt động khi máy bạn tắt. Hiện chưa xác nhận tài khoản của bạn có hosting nào.
3. **DNS + HTTPS:** nối tên miền tới hosting và bật kết nối bảo mật.

Mua tên miền không đồng nghĩa đã có máy chủ. Bạn vẫn sửa code trong VS Code; không đưa code vào ô DNS.

## Nếu đã có hosting Mắt Bão

1. Đăng nhập [id.matbao.net](https://id.matbao.net/), mở dịch vụ Hosting đã mua. Xác nhận hosting cho phép phục vụ HTML/CSS/JavaScript và gắn `cochill.vn`.
2. Mở Control Panel → File Manager. Xác định **document root của cochill.vn**. Với cPanel domain chính, thường là `public_html`; domain bổ sung có thể có thư mục khác. Không đoán rồi ghi đè website khác. Mắt Bão có [hướng dẫn File Manager và upload](https://wiki.matbao.net/kb/huong-dan-quan-tri-hosting-co-ban-tren-cpanel/).
3. Nếu có web cũ, sao lưu và kiểm tra trước khi thay. Giữ thư mục hệ thống như `.well-known`. Không xóa cả hosting.
4. Upload ZIP mới vào document root rồi Extract. Kết quả phải là `DOCUMENT_ROOT/index.html`, `DOCUMENT_ROOT/app.js`… cùng cấp; không để thêm một lớp thư mục ZIP ở ngoài.
5. Nếu hosting hiện trang mặc định hoặc WordPress, nhờ hỗ trợ kiểm tra file index và rewrite đang ưu tiên. Không xóa WordPress hay file index cũ khi chưa xác nhận đó là site cần thay.
6. Trỏ tên miền về đúng hosting bằng cấu hình nhà cung cấp. Mắt Bão có mục **Tên miền → Quản lý tên miền → cochill.vn → Cấu hình tên miền về Hosting**; thao tác này chỉ có hiệu lực khi DNS được quản lý ở đó. Xem [hướng dẫn chính thức](https://wiki.matbao.net/kb/huong-dan-cau-hinh-ten-mien-ve-hosting/). Sao lưu cấu hình DNS; giữ MX/TXT email đang dùng.
7. Bật SSL/HTTPS cho `cochill.vn`, cấu hình `www.cochill.vn` chuyển về địa chỉ chính. Dùng IP/bản ghi thật của hosting, không dùng `127.0.0.1` hoặc IP tự đoán.
8. Thử `https://cochill.vn/#home` bằng điện thoại dùng 4G. Chơi, mở bài, trả lời trước lời giải, retry, tải lại để kiểm tra tiến độ.

Các bước Control Panel phụ thuộc gói thực tế. Nếu chưa thấy dịch vụ Hosting, chưa thực hiện bước upload.

## Nếu chưa có hosting: dùng Vercel cho bản tĩnh

Có thể giữ tên miền ở Mắt Bão và để Vercel phục vụ website. Không cần chuyển nhà đăng ký tên miền.

1. Giải nén ZIP vào thư mục riêng. Đưa **15 file đã giải nén** lên một repository/nhánh nguồn sạch mà bạn chọn; không upload mỗi file ZIP. Không làm mất lịch sử repo cũ.
2. Import nguồn đó vào Vercel. Chọn framework **Other**, không cần Install/Build Command. Đây là bộ file đã sẵn sàng phục vụ. Với repo chỉ chứa 15 file ở root, dùng thư mục output `.` (root), không dùng `online-preview`.
3. Deploy và thử địa chỉ `*.vercel.app` trước. Tên thật do Vercel cung cấp, không tự đoán.
4. Vào Project → **Settings → Domains**, thêm `cochill.vn` và `www.cochill.vn`; chọn domain chính và redirect domain còn lại.
5. Vercel hiển thị các bản ghi DNS cần thêm. Chép **đúng giá trị hiện trong dự án của bạn** vào bảng DNS nơi quản lý cochill.vn. Không lấy IP hoặc CNAME của dự án người khác. Chờ domain được xác minh và HTTPS sẵn sàng. [Hướng dẫn custom domain của Vercel](https://vercel.com/docs/domains/working-with-domains/add-a-domain).

Ghi chú lịch sử: cấu hình static Vercel cũ được chuyển khỏi root repository.
Production dùng GCP/Nginx và Python backend; xem `deploy/DEPLOY_GCP_VI.md`.

Xem gói dịch vụ/điều khoản trên dashboard trước khi chấp thuận thanh toán. Bản tĩnh này không đòi hỏi bạn tự quản trị VPS hoặc thuê server Python.

## Những gì sẽ giống và những gì không tự chuyển

| Nội dung | Kết quả |
|---|---|
| Bố cục, màu sắc, logo, cover và bàn cờ | Giữ đúng các file đang phát hành |
| Chơi máy cơ bản, nhập/xem lại ván, học, retry, bài liên quan, ôn | Giữ cùng chức năng trình duyệt |
| Bật/tắt máy cá nhân | Không ảnh hưởng web đã host |
| Tiến độ đang lưu ở ChatGPT Site | Không tự sang cochill.vn vì khác origin |
| Tài khoản tập trung, admin, đồng bộ giữa máy | Chưa có trên bản static, giống giới hạn Site hiện tại |
| Pikafish thật / LLM | Không được bổ sung bởi việc chuyển domain |

Có thể xuất tiến độ ở web cũ để giữ bản cá nhân; hiện chưa có nhập lại đầy đủ JSON để hứa tự chuyển tiến độ. Giao diện mới vẫn ghi chế độ khách khi không tìm thấy API. Đường dẫn `/api/session` không tồn tại trên hosting static là trạng thái được xử lý, không yêu cầu cài Python để mở trang.

Chỉ dừng web cũ sau khi bản cochill.vn hoạt động và đã giữ dữ liệu cần thiết. Việc tạo gói này chưa sửa DNS, chưa mua hosting và chưa deploy cochill.vn.

## Làm ngay một việc

Mở danh sách dịch vụ trong tài khoản Mắt Bão để xác nhận có Hosting hay chỉ có Tên miền. Có thể gửi ảnh danh sách dịch vụ để được chỉ đúng bước tiếp theo; che thông tin cá nhân, mã đăng nhập, OTP và thông tin thanh toán. Nếu chưa mua hosting, không cần mua vội để chỉ chạy bản giống ChatGPT Site.
