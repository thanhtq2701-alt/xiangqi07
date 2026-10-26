# Đưa Cờ Chill lên cochill.vn — hướng dẫn cho người mới

Cập nhật: **24/10/2026**. Đọc theo thứ tự, làm xong một bước rồi mới chuyển bước tiếp theo.

**Bạn đã mua tên miền `cochill.vn` tại Mắt Bão. Chưa xác nhận được bạn đã mua hosting nào.** Ảnh email bạn gửi xác nhận đăng ký tên miền ngày 23/10/2026, hết hạn 23/10/2027; email yêu cầu hoàn tất hồ sơ trước **02/11/2026**. Kiểm tra và thực hiện việc này trong tài khoản Mắt Bão của bạn. Đây là thông tin trong email, không phải xác nhận rằng hosting hoặc website đã hoạt động.

Gói source được chuẩn bị ở `deliverables/Co_Chill_V5_Source_2026_10_24.zip`. Gói chứa mã chạy V5 cùng công cụ/tài liệu cần thiết; **không mang theo tài khoản, tiến độ, mật khẩu, khóa quản trị hoặc database của máy này**. Việc tạo gói không tự đăng tải website.

## 1. Hiểu sáu phần trước khi thao tác

| Khái niệm | Hiểu đơn giản | Trong dự án này |
|---|---|---|
| Tên miền | Địa chỉ người khác gõ vào | `cochill.vn` |
| Hosting/máy chủ | Máy tính trên Internet chạy website | Cần chọn dịch vụ chạy được Python |
| DNS | Chỉ dẫn tên miền tìm tới máy chủ nào | Cấu hình tại nơi đang quản lý DNS |
| HTTPS | Kết nối được mã hóa, có chứng chỉ cho tên miền | Cần bật trên hosting |
| GitHub | Nơi lưu phiên bản mã nguồn | Repository `xiangqi07` của bạn |
| VS Code | Nơi bạn đọc, sửa và kiểm tra code | Vẫn dùng trên máy của bạn |

Luồng làm việc sau này là **VS Code → GitHub → hosting → người dùng mở cochill.vn**. DNS nối tên miền tới hosting; nó không phải nơi upload code. Mua tên miền không tự mua máy chủ, không tự tạo tài khoản người chơi và không làm engine mạnh hơn.

`localhost`/`127.0.0.1` là máy đang mở trình duyệt. Vì vậy gửi link localhost cho người khác không đưa họ tới máy của bạn. ChatGPT Site là bản xem thử online khác: phần chơi/học lưu trên trình duyệt chạy được; server Python và tài khoản V5 không chạy trong gói static đó.

## 2. Việc cần làm ngay: xem mình có hosting chưa

1. Tự mở [trang quản lý Mắt Bão](https://id.matbao.net/) và đăng nhập tài khoản của bạn.
2. Tìm **Cloud Hosting/Email**, **Cloud Hosting**, **WordPress** hoặc **Cloud Server** trong danh sách dịch vụ. Tên mục có thể khác theo phiên bản giao diện.
3. Nếu có dịch vụ, mở chi tiết và ghi lại **tên gói, hệ điều hành, control panel, ngày hết hạn**. Không gửi mật khẩu, mã OTP, khóa SSH hoặc thông tin thanh toán.
4. Nếu chỉ thấy `cochill.vn` trong mục Tên miền, hiện mới xác nhận được tên miền. Không cần mua thêm ngay; xác minh khả năng chạy ứng dụng trước.

Mắt Bão hướng dẫn quản lý dịch vụ tại ID Portal và có danh sách Hosting/Email riêng. Một số thao tác “Kích hoạt” có thể đồng thời trỏ DNS: ở bước kiểm kê này, chỉ xem thông tin, chưa cần kích hoạt hoặc thay bản ghi. [Quản lý tài khoản](https://wiki.matbao.net/kb/lam-the-nao-de-dang-nhap-vao-trang-quan-ly-dich-vu/), [hướng dẫn kích hoạt và thay DNS](https://wiki.matbao.net/kb/huong-dan-kich-hoat-dich-vu-hosting-email-tren-trang-id-portal/).

Bạn có thể tự gửi nội dung sau cho bộ phận hỗ trợ Mắt Bão:

> Tôi sở hữu cochill.vn và muốn triển khai ứng dụng Python 3.12 trở lên, giao diện HTML/CSS/JavaScript. Ứng dụng dùng WSGI, entry point `co_chill_server:application`, lưu SQLite ở thư mục ghi được và nằm ngoài thư mục web công khai. Tôi cần HTTPS, biến môi trường, cách khởi động lại ứng dụng, và terminal/Shell để tạo tài khoản quản trị. Xin xác nhận gói hiện tại của tôi có đáp ứng không, tên gói cụ thể, cách deploy Python và nơi lưu dữ liệu bền sau restart/redeploy. Nếu không đáp ứng, xin tư vấn phương án phù hợp và chi phí trước khi thay đổi dịch vụ. Tôi chưa cần WordPress.

Đừng suy ra “có Hosting Linux/cPanel” là chắc chạy được bản này. Nhà cung cấp cần xác nhận phiên bản Python, WSGI và quyền lưu dữ liệu. Chỉ upload vào `public_html` có thể hiện giao diện nhưng không tạo được API tài khoản.

## 3. Gói nào cần đưa lên, gói nào giữ riêng?

Giải nén ZIP vào **thư mục mới**, tránh chép đè hoặc xóa repository đang làm việc.

| Thành phần | Vai trò | Nếu thiếu |
|---|---|---|
| `co_chill_server.py` | Chạy website và API V5 | Không có server tài khoản/đồng bộ |
| Các module `app/` trong gói | Luật, engine, dữ liệu, xác thực, nội dung | Server thiếu phần xử lý hoặc không khởi động |
| `online-preview/` | Toàn bộ HTML, CSS, JavaScript, ảnh | Thiếu màn hình, bàn cờ hoặc hành vi học |
| `requirements.txt` | Cài máy chủ Gunicorn khi chạy Linux | Thiếu tiến trình phục vụ production |
| `.env.example` | Mẫu tên biến cấu hình | Vẫn chạy được nhưng khó cấu hình đúng |
| `.gitignore`, README, tài liệu, tests/tools | Bảo trì, hướng dẫn, kiểm tra | Không nhất thiết chặn chạy, nhưng nên giữ |
| Manifest SHA-256 đi kèm gói | Danh sách file và dấu kiểm tra nội dung | Khó đối chiếu bản đã bàn giao |

Không upload `.git/`, `var/`, `.env` thật, file SQLite/backup, Word trả lời, tài liệu riêng hoặc khóa TOTP lên GitHub hay thư mục web. ZIP source không phải bản sao lưu người chơi. Những file nằm ngoài gói vẫn giữ nguyên trong dự án gốc; không cần xóa chúng để deploy.

## 4. Kiểm tra source trên máy trước

Mở **thư mục đã giải nén** bằng VS Code, mở Terminal tại nơi có `co_chill_server.py`, chạy:

```powershell
python co_chill_server.py serve --port 8770
```

Mở `http://127.0.0.1:8770/#home`. Cổng 8770 giúp tránh trùng bản cũ ở 8769. Nếu dùng Python Launcher, thay `python` bằng `py -3.12`. Giữ terminal mở; `Ctrl+C` để dừng. Python 3.12 là phiên bản đã dùng kiểm tra đợt V5. Không cần npm hoặc API key để chạy local.

Các bài kiểm tra V5 trong gói:

```powershell
python -m unittest tests.test_rules tests.test_cloud tests.test_pikafish -v
node tools/test_cloud_client.cjs
node tools/test_engine_client.cjs
node tools/test_v5_ui.cjs
```

Node chỉ dùng khi chạy kiểm thử JavaScript. Kết quả kiểm thử của bản source trước khi đóng gói nằm trong báo cáo; chưa chứng minh hosting của bạn đã hoạt động.

## 5. Chọn cách chạy bản có tài khoản

Ưu tiên **một máy chủ phục vụ cả giao diện và API**, kèm chỗ lưu SQLite bền. Đây là cách ít thay đổi code hiện tại nhất. Nếu gói Mắt Bão đáp ứng, làm theo cấu hình Python do họ cung cấp. Nếu chưa có gói phù hợp, một phương án là Render Python Web Service kèm persistent disk; bạn xem và chấp thuận chi phí trước khi tạo. Render chỉ hỗ trợ persistent disk cho dịch vụ trả phí, và chỉ dữ liệu dưới đường dẫn mount được giữ. [Persistent disks](https://render.com/docs/disks).

**Không cần tách Vercel frontend + backend lúc này.** Cấu hình Vercel hiện có chỉ phục vụ bản khách. Tách hai nơi cần thêm xử lý cookie/origin/CSRF và kiểm thử; không phải chỉ đổi một URL.

Với Render, hướng dẫn đầy đủ ở [DEPLOY_V5.md](DEPLOY_V5.md). Các ô chính:

| Ô cấu hình | Điền |
|---|---|
| Runtime | Python 3 |
| Root directory | Thư mục chứa `co_chill_server.py`; để trống nếu file ở root repo |
| Build command | `pip install -r requirements.txt` |
| Start command | Dòng Gunicorn bên dưới |
| Auto-deploy | Tắt trong giai đoạn đầu để bạn chủ động phát hành |

```sh
gunicorn co_chill_server:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 45 --graceful-timeout 15
```

Đưa **file đã giải nén** vào repository/nhánh triển khai sau khi xem danh sách thay đổi; không upload mỗi ZIP rồi mong hosting tự chạy. Không ghi đè lịch sử Git hoặc xóa nhánh cũ. Nếu cập nhật repo hiện có, dùng một nhánh để review trước khi merge.

## 6. Cấu hình tên miền và dữ liệu cho ứng dụng

Các biến được nhập trong bảng Environment của hosting hoặc cơ chế môi trường do nhà cung cấp hướng dẫn. `.env.example` chỉ là mẫu: ứng dụng không tự đọc `.env`.

```text
CO_CHILL_PUBLIC_ORIGIN=https://cochill.vn
CO_CHILL_DB_PATH=/DUONG_DAN_LUU_BEN/co_chill_accounts.sqlite3
CO_CHILL_ADMIN_TOTP_SECRET=KHOA_RIENG_CUA_BAN
```

Hai giá trị viết hoa sau dấu `=` là chỗ thay thế, không chép nguyên. Với Render gắn disk ở `/var/data`, đường dẫn database là `/var/data/co_chill_accounts.sqlite3`. Với hosting khác, dùng đường dẫn được xác nhận. Không đặt database trong `online-preview/` hoặc `public_html`.

Chỉ dùng **một địa chỉ chính**: `https://cochill.vn`, không thêm dấu `/`, `#home` hoặc `/api`. Nếu đang thử bằng URL tạm do hosting cấp, dùng chính URL đó làm `CO_CHILL_PUBLIC_ORIGIN`; khi chuyển tên miền thì đổi sang `https://cochill.vn` và restart/deploy lại. Code hiện kiểm tra đúng Host/origin, nên URL phụ có thể trả 403 — không tắt kiểm tra này để chữa lỗi.

Render có thể dùng một domain đã xác minh làm Host khi kiểm tra HTTP. Trong giai đoạn chuyển tên miền, để kiểm tra TCP mặc định/Health Check Path trống để tránh Host chưa khớp. Sau đó kiểm tra `https://cochill.vn/api/health` và chỉ bật HTTP health check khi Host kiểm tra phù hợp. TCP qua chỉ nói server mở cổng, chưa chứng minh ứng dụng đầy đủ. [Health checks của Render](https://render.com/docs/health-checks).

## 7. Trỏ cochill.vn tới hosting

Chỉ thực hiện sau khi có dịch vụ và hướng dẫn DNS chính xác:

1. Trong hosting, thêm custom domain **cochill.vn**. Ghi lại bản ghi mà hosting yêu cầu.
2. Trong Mắt Bão, mở **Tên miền → Quản lý tên miền → cochill.vn**; xem Nameserver hiện do ai quản lý. Nếu DNS đang ở nhà cung cấp khác, sửa tại nơi đó. [Hướng dẫn Mắt Bão](https://wiki.matbao.net/kb/huong-dan-cau-hinh-ten-mien-ve-hosting/).
3. Sao lưu/chụp cấu hình DNS hiện tại trước khi sửa. Không xóa tất cả bản ghi; giữ các bản ghi email MX/TXT đang dùng.
4. Điền bản ghi cho website theo bảng dưới, thay mục mẫu bằng giá trị hosting cấp.

| Tên | Loại | Giá trị |
|---|---|---|
| `@` hoặc để trống theo panel | A hoặc ALIAS/ANAME | IP/hostname chính xác hosting yêu cầu |
| `www` | Thường là CNAME | Hostname đích do hosting hướng dẫn |
| Bản ghi xác minh | Theo hosting | Giá trị xác minh chính xác, nếu được yêu cầu |

Không điền `127.0.0.1`, đường dẫn ổ E:, URL có `https://` vào ô IP, hay IP tự đoán. Với Render, loại bản ghi root tùy khả năng DNS; subdomain thường dùng CNAME. Kiểm tra bản ghi AAAA cũ của chính hostname đang chuyển vì Render hướng dẫn dùng IPv4. [Cấu hình DNS Render](https://render.com/docs/configure-other-dns).

5. Trở lại hosting, xác minh domain và chờ chứng chỉ HTTPS. Nếu dùng Render, hệ thống cấp/gia hạn TLS; thêm root domain sẽ kèm chuyển hướng `www` về root. Hosting khác cần cấu hình chuyển hướng tại proxy/control panel. [Custom domains](https://render.com/docs/custom-domains).
6. Khi DNS/TLS sẵn sàng, áp dụng origin `https://cochill.vn`, mở web bằng địa chỉ này và kiểm tra lại. Thay DNS có thể cần thời gian lan truyền; không đổi liên tục qua nhiều IP khi chưa xác định lỗi.

## 8. Tài khoản quản trị và chuyển dữ liệu cũ

Trên Shell **của máy chủ thật**, tạo khóa TOTP bằng `python co_chill_server.py generate-admin-totp`. Tự thêm khóa vào ứng dụng authenticator và Environment của hosting; không gửi khóa cho AI. Sau đó chạy `python co_chill_server.py create-admin --username owner`, tự nhập mật khẩu được hỏi ẩn. Chi tiết cách đăng nhập/backup ở [DEPLOY_V5.md](DEPLOY_V5.md). Không tạo admin trong Build Command và không có mật khẩu quản trị mặc định.

Có hai loại dữ liệu cần phân biệt:

- **Khách trên localhost/ChatGPT Site:** localStorage thuộc từng origin và trình duyệt. Chuyển sang cochill.vn không tự chuyển tiến độ. Có xuất JSON để giữ bản cá nhân, nhưng bản hiện tại chưa có công cụ nhập lại đầy đủ JSON đó; không hứa “xuất rồi nhập là xong”.
- **Tài khoản V5:** nằm trong SQLite của server. Muốn giữ, dùng lệnh backup tạo bản nhất quán rồi chuyển riêng qua kênh quản trị bảo mật. Không đưa database vào source ZIP/GitHub. Không chép mù database đang ghi, và không ghi đè database production đã có người dùng.

Nếu chỉ có dữ liệu demo, có thể chọn bắt đầu database mới và giữ backup cũ riêng. Nếu có người dùng thật, cần kế hoạch dừng ghi, backup, chuyển, kiểm tra, đổi đường dẫn và quay lại khi lỗi. Người dùng phải đăng nhập lại tại domain mới. Chưa có công cụ tự hợp nhất hai database.

## 9. Kiểm tra trước khi gửi link cho mọi người

- [ ] Mở HTTPS trên máy khác hoặc điện thoại dùng 4G; không cần bật máy cá nhân.
- [ ] Vào Home, chơi, học, trả lời trước giải, retry và bài liên quan.
- [ ] Đăng ký tài khoản thử, đợi “Đã đồng bộ”, đăng nhập từ trình duyệt thứ hai thấy tiến độ; phiên cũ bị thu hồi theo thiết kế.
- [ ] Owner thấy thống kê; người thường không vào được quyền quản trị.
- [ ] Restart/redeploy xong tài khoản và tiến độ vẫn còn.
- [ ] Có backup riêng, biết cách khôi phục; xuất/xóa tài khoản thử hoạt động.
- [ ] `www` chuyển về domain chính; API không bị lỗi 403.

| Hiện tượng | Kiểm tra đầu tiên |
|---|---|
| Refused to connect ở localhost | Server trên máy chưa chạy/đã tắt |
| cochill.vn không mở | DNS, domain verification và trạng thái hosting |
| Có giao diện nhưng không đăng nhập | Đang chạy static hay Python API thật? |
| 403 địa chỉ máy chủ/origin | `CO_CHILL_PUBLIC_ORIGIN` có đúng hostname và HTTPS không? |
| 502/503 | Log khởi động, Start Command, Python và cổng hosting |
| Mất tài khoản sau deploy | Database có nằm trên vùng lưu bền không? |

## 10. Cập nhật hằng ngày

Sửa code trong VS Code → chạy local/tests → xem diff → commit các file đã chọn → push nhánh → review → **chủ động deploy** → thử lại luồng chính → ghi nhật ký. DNS thường chỉ cấu hình một lần; không đổi DNS mỗi lần sửa nút hoặc bài học. Render có thể tự deploy theo commit, nhưng cũng cho tắt để chọn phát hành thủ công. [Quản lý deploy](https://render.com/docs/deploys).

Việc cần quyết định tiếp theo là **xác nhận tên gói hosting và khả năng chạy Python/SQLite**. Bạn không cần điền lại V5 hoặc viết lại toàn bộ web chỉ vì đổi địa chỉ. Domain mới vẫn dùng cùng code và cùng giới hạn hiện tại: engine local có nhãn, chưa cài Pikafish/NNUE thật, chưa có LLM chấm lập luận.
