# Chạy và triển khai Cờ Chill V5 — 24/10/2026

**Code hiện có hai cách chạy.** Bản đầy đủ dùng Python phục vụ cả giao diện và API trên cùng một địa chỉ. Bản tĩnh đưa lên Vercel chạy vòng chơi/học ở trình duyệt, nhưng không có máy chủ tài khoản, quản trị hoặc Pikafish. Repository chưa được triển khai bởi tài liệu này.

## 1. Chọn đúng phương án

| Cách chạy | Người khác mở được? | Tài khoản, đồng bộ, quản trị | Dữ liệu nằm ở đâu? |
|---|---|---|---|
| `python co_chill_server.py serve` trên máy bạn | Chỉ máy bạn với mặc định loopback | Có, để kiểm thử | SQLite trên máy bạn; khách ở trình duyệt |
| Vercel static với `vercel.json` đã kèm | Có, sau khi bạn tự Deploy | Không; giao diện báo chưa có API | localStorage của từng trình duyệt |
| Render Python + **ổ lưu bền vững** | Có, sau khi bạn tự Deploy | Có | SQLite trên volume của một instance |
| Render Free Python + SQLite trên filesystem mặc định | Có, để thử tạm | API có thể chạy, nhưng không đáng tin để giữ tài khoản thật | Có thể mất dữ liệu khi restart, redeploy hoặc ngủ |

Render ghi rõ filesystem mặc định là tạm thời; Free không gắn persistent disk và ngủ sau 15 phút không có truy cập. Vì vậy **không mời người dùng tạo tài khoản thật trên Render Free với SQLite mặc định**. [Giới hạn Render Free](https://render.com/docs/free)

Phương án ít thay đổi code nhất cho pilot có tài khoản là **một Render Web Service, một persistent disk, giao diện và API cùng origin**. Persistent disk yêu cầu dịch vụ trả phí; bạn cần tự xem giá và chấp thuận trước khi chọn. Không kèm `render.yaml` tự chọn gói trả phí. Nếu cần backend không trả phí, phải chọn dịch vụ database bền vững phù hợp và bổ sung adapter; code hiện tại chưa dùng Postgres. [Persistent disks của Render](https://render.com/docs/disks)

## 2. Chạy bản đầy đủ ở Windows

Yêu cầu Python 3.12. Bộ kiểm thử đợt này dùng Python 3.12.14. Mở PowerShell tại thư mục repo:

```powershell
Set-Location -LiteralPath 'E:\ThanhTQ\App cờ tướng\xiangqi-ai'
python co_chill_server.py serve --port 8769
```

Mở [Cờ Chill local](http://127.0.0.1:8769/#home). Giữ cửa sổ server đang chạy. Đóng server hoặc tắt máy thì localhost dừng; đây không phải lỗi trình duyệt. Nếu `python` không được nhận nhưng đã cài Python Launcher, dùng `py -3.12` thay `python`.

Không cần Node, npm, React hoặc API key để chạy bản này. Không chạy `server.py` nếu muốn kiểm tra V5 tài khoản: đó là server legacy, dùng giao diện/API khác. Không mở trực tiếp `index.html` bằng `file://` để kiểm tra tài khoản.

File SQLite mặc định là `var/co_chill_accounts.sqlite3`. Biến `CO_CHILL_DB_PATH` cho phép đổi vị trí. `.env.example` chỉ là tài liệu mẫu: ứng dụng **không tự nạp `.env`**.

## 3. Tạo tài khoản quản trị riêng

Tài khoản thường đăng ký ở mục **Tài khoản**. Tài khoản admin chỉ được tạo bằng dòng lệnh trên máy chủ, không có nút tự nâng quyền trên web.

1. Tạo khóa TOTP trong terminal riêng của bạn:

   ```powershell
   python co_chill_server.py generate-admin-totp
   ```

2. Lưu khóa vừa hiện ở nơi riêng an toàn. Thêm khóa thủ công vào ứng dụng authenticator: TOTP, SHA-1, 6 chữ số, chu kỳ 30 giây. Đặt **chính khóa đó** làm biến môi trường trong terminal sẽ chạy server:

   ```powershell
   $env:CO_CHILL_ADMIN_TOTP_SECRET = 'DAN_KHOA_BASE32_CUA_BAN_O_DAY'
   python co_chill_server.py create-admin --username owner
   ```

   Dòng trên chứa placeholder, không phải khóa thật. Không gửi khóa, ảnh QR hoặc mật khẩu cho người khác; không commit vào Git. Mật khẩu được hỏi ẩn hai lần, tối thiểu 10 ký tự. Lệnh không tạo thêm owner khi đã có owner.

3. Khởi động hoặc khởi động lại server trong môi trường có cùng biến. Đăng nhập tên `owner`, mật khẩu đã đặt, mã TOTP hiện tại. Mở **Quản trị**. Đồng hồ máy chủ và điện thoại cần đúng giờ.

4. Nếu muốn cấp người hỗ trợ quyền chỉ đọc, chạy `python co_chill_server.py create-report --username ten_bao_cao`. Vai trò `report` xem thống kê và biên bản đã lọc, không khóa người dùng hoặc sửa nội dung. Không cấp chung tài khoản owner.

Chưa có email khôi phục, passkey hoặc mã dự phòng. Mất mật khẩu/khóa TOTP cần người vận hành xử lý trên máy chủ sau xác minh danh tính; chưa có quy trình phục hồi tự động. Giữ bản sao khóa riêng an toàn trước khi mở pilot.

## 4. Render: bản đầy đủ cùng một địa chỉ

Các bước dưới đây là hướng dẫn để **bạn** thao tác sau khi đã xem bản local. Không có dịch vụ hay phí nào được tạo tự động.

1. Đẩy code đã kiểm tra vào repository của bạn. Không đẩy `.env`, `var/`, database, backup, engine binary hoặc tài liệu câu trả lời riêng tư. GitHub repository không cần chuyển Public chỉ để kết nối dịch vụ deploy hỗ trợ repo riêng tư.
2. Tạo **Web Service**, runtime **Python 3**, root directory là thư mục chứa `co_chill_server.py`. Nếu repo Git chính là `xiangqi-ai`, để Root Directory trống.
3. Chọn phiên bản Python bằng biến `PYTHON_VERSION=3.12.14`. Build command:

   ```sh
   pip install -r requirements.txt
   ```

4. Start command:

   ```sh
   gunicorn co_chill_server:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 45 --graceful-timeout 15
   ```

   Một worker giữ giới hạn engine trong một process; bốn thread giúp API nhẹ không phải chờ một lượt engine. Không tăng worker hoặc scale nhiều instance khi chưa thiết kế lại cơ sở dữ liệu/queue. Gunicorn phục vụ WSGI trên UNIX; Windows local dùng lệnh `serve`, không dùng Gunicorn. [Gunicorn](https://gunicorn.org/), [mẫu triển khai Python của Render](https://render.com/docs/deploy-flask)

5. Sau khi **bạn chấp nhận chi phí**, gắn persistent disk ở `/var/data`. Đặt biến:

   | Biến | Giá trị |
   |---|---|
   | `CO_CHILL_DB_PATH` | `/var/data/co_chill_accounts.sqlite3` |
   | `CO_CHILL_PUBLIC_ORIGIN` | `https://TEN-DICH-VU-CUA-BAN.onrender.com` — thay bằng địa chỉ thật |
   | `CO_CHILL_ADMIN_TOTP_SECRET` | Khóa TOTP thật, nhập trong secret environment của Render |
   | `PYTHON_VERSION` | `3.12.14` |

   `CO_CHILL_PUBLIC_ORIGIN` phải đúng **một origin**: gồm `https://` và hostname, không có `/#home`, `/api`, dấu `/` cuối, user/password hoặc query. Thiếu biến này thì ứng dụng chỉ chấp nhận localhost. Sai origin có thể gây 403 dù build thành công. Chọn một tên miền chính; khi chuyển sang domain riêng phải cập nhật biến này và dùng nhất quán tên miền đó.

6. Health check path: `/api/health`. Endpoint này xác nhận server/SQLite khởi tạo được; không chứng minh Pikafish, email hay mọi tính năng đã sẵn sàng.
7. Deploy. Sau khi máy chủ chạy và disk đã mount, dùng Shell của dịch vụ để tạo owner bằng `python co_chill_server.py create-admin --username owner`. Đừng tạo database/admin trong **Build Command**: build không phải môi trường giữ dữ liệu runtime.
8. Mở URL HTTPS, tạo tài khoản thử, chơi/học, đợi “Đã đồng bộ”. Đăng nhập từ trình duyệt thứ hai: phải nhận tiến độ cũ, phiên thứ nhất bị thu hồi. Kiểm tra owner thấy tài khoản; tài khoản thường không mở được API quản trị.
9. Thử redeploy rồi đăng nhập lại. Nếu dữ liệu biến mất, dừng mời người dùng và kiểm tra volume/đường dẫn trước. Xuất dữ liệu và sao lưu định kỳ.

Mặc định không có Pikafish thật. Tùy chọn máy chủ có thể trả engine local dự phòng với nhãn rõ. Muốn engine mạnh, đọc [PIKAFISH_SETUP_V5.md](PIKAFISH_SETUP_V5.md), cài binary Linux và trọng số hợp lệ ngoài thư mục static. Không đưa Windows `.exe` lên Linux rồi kỳ vọng chạy được.

## 5. Vercel: bản tĩnh để xem/chơi thử

`vercel.json` chỉ xuất bản thư mục `online-preview`, framework `Other`/`null`, không cần install/build. Import Git repository vào Vercel, Root Directory để tại thư mục chứa `vercel.json`, kiểm tra Output Directory `online-preview`, rồi tự Deploy. [Cấu hình Vercel](https://vercel.com/docs/project-configuration/vercel-json#outputdirectory)

Link nhận được dạng `https://ten-ban.vercel.app`. Các route dùng hash (`/#home`, `/#lessons`) nên không cần rewrite mọi đường dẫn về HTML. `server.py`, database và tài liệu trong repo không nằm trong output static này.

Trong cấu hình hiện có, đăng ký/đăng nhập, đồng bộ giữa máy, quản trị, gửi phản hồi tới chủ web và engine server **không hoạt động trên Vercel static**; giao diện báo thiếu API. Chơi/học với máy cơ bản, lịch ôn và tiến độ khách vẫn chạy trên trình duyệt. Đổi máy hoặc xóa localStorage không mang theo dữ liệu khách.

Muốn Vercel frontend + Render backend là một bước tích hợp riêng: cần thiết kế origin/cookie/proxy/CSRF phù hợp và kiểm thử lại. Chỉ thêm URL Render vào JavaScript không đủ, vì phiên bản này chủ ý chỉ chấp nhận cùng origin. Không dùng SQLite cục bộ như một database bền vững cho serverless Vercel.

## 6. Backup, khôi phục và xóa dữ liệu

Lệnh backup dùng SQLite backup API, không sao chép mù file đang mở. Đích phải là **file mới**; lệnh không ghi đè backup cũ:

```powershell
python co_chill_server.py backup --output var/backups/co-chill-2026-10-24.sqlite3
```

Backup có tài khoản, dữ liệu và mật khẩu đã băm; cần bảo vệ như dữ liệu riêng. Không đặt backup trong `online-preview/` và không commit. Giữ bản sao ngoài máy/disk đang chạy; backup trên cùng disk không bảo vệ khỏi mất disk. Chưa có lịch backup tự động hoặc cam kết thời gian phục hồi.

Để diễn tập khôi phục **không đè database đang dùng**, chạy một server khác trỏ tới bản backup:

```powershell
python co_chill_server.py serve --db var/backups/co-chill-2026-10-24.sqlite3 --port 8770
```

Chỉ làm local với `CO_CHILL_PUBLIC_ORIGIN` trống hoặc phù hợp loopback. Bản backup dùng để thử có thể thay đổi khi đăng nhập/lưu; giữ một bản gốc riêng. Trước khôi phục production, dừng ghi, tạo backup hiện trạng, chọn bản cần phục hồi và thay `CO_CHILL_DB_PATH` sang file phục hồi; không xóa database cũ trong lúc đang chạy. Sau phục hồi phải áp dụng lại các yêu cầu xóa tài khoản phát sinh sau thời điểm backup.

CLI kiểm tra tài khoản không hoạt động 365 ngày:

```powershell
python co_chill_server.py prune-inactive
```

Lệnh trên chỉ thống kê. Chỉ khi chủ vận hành đã xem danh sách/quy trình lưu trữ và xác nhận mới dùng `--confirm` để xóa; owner bị loại khỏi quy tắc này. Chưa có job định kỳ tự chạy. Xóa trong web xóa bản hoạt động trên server; bản xuất và backup do người vận hành giữ cần được xử lý riêng, không bí mật giữ để huấn luyện.

## 7. Kiểm tra trước khi mở pilot

Chạy tại root repo:

```powershell
python -m unittest discover -s tests -v
node tools/test_preview_learning.cjs
node tools/test_preview_game_tools.cjs
node tools/test_preview_experience.cjs
node tools/test_cloud_client.cjs
node tools/test_engine_client.cjs
node tools/test_v5_ui.cjs
python tools/check_online_preview.py
python tools/check_browser_rules.py
```

Node chỉ cần cho kiểm thử JavaScript, không cần để phục vụ web. Kết quả thực của đợt kiểm thử nằm ở `TEST_REPORT_CODEX.md`; không hiểu lệnh được liệt kê ở đây là bằng chứng mọi hosting đã được chạy thử.

Kiểm tra thủ công: đăng ký → học và tự phản ánh trước lời giải → thử lại → bài liên quan → ôn/progress; tải lại giữa phiên; mất mạng/đồng bộ lại; chuyển thiết bị; owner xem thống kê/nháp bài; tài khoản thường không có quyền owner; xuất và xóa tài khoản thử. Sau deploy kiểm tra thêm HTTPS, TOTP, backup/restore và dữ liệu còn sau restart.

Nguồn và giới hạn hosting được đối chiếu ngày **24/10/2026**. Giá/gói có thể thay đổi; xem dashboard trước khi tạo dịch vụ. Chưa mua hạ tầng, đăng ký tên miền, push GitHub hoặc thay site cũ trong đợt chuẩn bị code này.
