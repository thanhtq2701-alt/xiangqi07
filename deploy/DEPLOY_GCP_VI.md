# Triển khai Cờ Chill trên VM GCP

Hướng dẫn này khớp cấu hình Production đã được chủ dự án cung cấp: Ubuntu
24.04, Python 3.12, code tại `/var/www/html`, venv tại
`/var/www/html/.venv`, systemd service `cochill.service`, Nginx HTTPS và
SQLite trên cùng VM. Tên miền chính thức là `cochill.vn`.

> Không đưa secret, mã TOTP, mật khẩu, database hoặc backup vào Git/chat.
> Thao tác khôi phục/cập nhật Production cần cửa sổ bảo trì và backup riêng.

## 1. Những gì đang chạy

- Ứng dụng: `/var/www/html/co_chill_server.py serve --host 127.0.0.1 --port 8000`
- Service: `cochill.service`, chạy dưới `thanhtq2701`
- Biến bí mật/cấu hình: `/etc/cochill.env` (quyền đọc hạn chế)
- Database: `/var/www/html/var/co_chill_accounts.sqlite3`
- Nginx công khai HTTPS; Python chỉ nghe loopback.
- Sao lưu hằng ngày vào `~/backups`, giữ 14 ngày.

`cochill.service` và `nginx-cochill.conf` trong thư mục này là mẫu để đối
chiếu/cài lại, không phải lệnh tự động sửa VM. Đọc kỹ trước khi thay cấu hình
đang hoạt động.

## 2. Thiết lập ban đầu

1. Cài Ubuntu 24.04, Git, Python 3.12/venv, Nginx và Certbot; mở firewall
   chỉ các cổng cần thiết (SSH, HTTP/HTTPS). Trỏ cả `cochill.vn` và
   `www.cochill.vn` theo quyết định DNS đã duyệt.
2. Clone repository vào `/var/www/html` hoặc triển khai source đã duyệt. Đảm
   bảo thư mục này thuộc đúng tài khoản vận hành; không đặt database trong
   web root được Nginx phục vụ trực tiếp.
3. Tạo venv và cài requirements của repo:

   ```sh
   cd /var/www/html
   python3.12 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

4. Tạo `/etc/cochill.env` từ mẫu `deploy/cochill.env.example`. Điền:
   `CO_CHILL_PUBLIC_ORIGIN=https://cochill.vn`,
   `CO_CHILL_DB_PATH=/var/www/html/var/co_chill_accounts.sqlite3`,
   `CO_CHILL_ADMIN_TOTP_SECRET` và đường dẫn Pikafish/NNUE đã được kiểm tra.
   Đặt `CO_CHILL_TRUSTED_PROXIES=127.0.0.1` chỉ khi Nginx cùng VM kết nối
   từ loopback và ghi đè `X-Real-IP` bằng `$remote_addr`. Bỏ biến này/để
   trống nếu proxy không phải proxy tin cậy; khi trống, throttle dùng
   `REMOTE_ADDR`.
5. Hạn chế quyền file môi trường (ví dụ `root` sở hữu, nhóm service chỉ đọc,
   mode `640`; hoặc quyền `600` nếu owner là tài khoản service). Không ghi
   secret vào shell history, log hay repo.
6. Cấp chứng chỉ Let's Encrypt cho `cochill.vn` và `www.cochill.vn`. Mẫu
   Nginx cuối dùng certificate tại
   `/etc/letsencrypt/live/cochill.vn/`. Nếu chứng chỉ chưa tồn tại, dùng
   cấu hình HTTP tạm thời để Certbot cấp chứng chỉ trước khi cài mẫu HTTPS.
7. Cài `deploy/cochill.service` thành
   `/etc/systemd/system/cochill.service`. Cài ba server block trong
   `deploy/nginx-cochill.conf` vào sites-available, bật site, rồi kiểm tra
   `sudo nginx -t` trước khi reload.
8. Chạy `sudo systemctl daemon-reload`,
   `sudo systemctl enable --now cochill.service`; sau đó
   `sudo systemctl restart nginx`. Kiểm tra
   `curl -fsS https://cochill.vn/api/health`.

Mẫu Nginx đặt `client_max_body_size 3m`: API giới hạn body ở 2 MiB state cộng
64 KiB overhead; 3 MiB cho khoảng đệm giao thức mà không vượt mức API.
Proxy đặt `X-Real-IP` bằng địa chỉ TCP thực `$remote_addr`, không tin giá trị
client gửi. Ứng dụng không dùng `X-Forwarded-For`.

## 3. Cập nhật code

### Cập nhật bằng một lệnh

Từ tài khoản `thanhtq2701`, chạy tại `/var/www/html` trên nhánh
`codex-full`:

```sh
cd /var/www/html
./deploy/update.sh
```

Script kiểm tra nhánh và các thay đổi ở file được Git theo dõi (file
untracked được phép), tạo backup bằng lệnh `backup` của ứng dụng trước khi
fetch, rồi hiển thị commit/diffstat và chờ xác nhận. Dùng
`./deploy/update.sh --yes` chỉ khi đã xem xét trước thay đổi sắp kéo về.
Script chỉ đọc dòng `CO_CHILL_DB_PATH` cần thiết từ `/etc/cochill.env`;
không in hay sửa file môi trường. Nó chỉ cài lại requirements khi file đó
thay đổi, kiểm tra cú pháp Python trước restart và chờ health check tối đa
30 giây.

Nếu triển khai lỗi sau khi kéo code, script in lệnh quay lại commit trước,
restart service và đường dẫn backup. Lệnh đó không khôi phục database tự
động; việc restore database là thao tác riêng cần được cân nhắc/duyệt.
Script không thay đổi `/etc/cochill.env`, Nginx, Certbot hay cron.

### Hướng dẫn thủ công dự phòng

Trước khi cập nhật, xác nhận đây là branch/revision đã duyệt để chạy Production,
worktree sạch và backup gần nhất dùng được. Không kéo branch thử nghiệm hoặc
chép đè database.

```sh
cd /var/www/html
git status --short
git branch --show-current
git pull --ff-only origin codex-full
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/run_checks.py
sudo systemctl restart cochill.service
sudo systemctl status cochill.service --no-pager
curl -fsS https://cochill.vn/api/health
```

`git pull --ff-only` sẽ dừng nếu cần merge; không tự giải quyết conflict trên
Production. Với thay đổi requirements, chỉ cài đúng dependencies đã được
duyệt. Nếu health check hoặc log báo lỗi, dừng triển khai tiếp và khôi phục
phiên bản code trước theo quy trình vận hành đã kiểm tra.

## 4. Xem trạng thái và log

```sh
sudo systemctl status cochill.service --no-pager
sudo journalctl -u cochill.service -n 100 --no-pager
sudo journalctl -u cochill.service -f
sudo nginx -t
sudo systemctl status nginx --no-pager
```

Không gửi log chưa rà soát ra ngoài; không bật log request body, cookie, mật
khẩu hoặc nội dung học riêng.

## 5. Sao lưu và khôi phục SQLite

Tạo backup mới (đường dẫn không được tồn tại) bằng tài khoản service hoặc
tài khoản có quyền đọc DB và ghi thư mục backup:

```sh
sudo -u thanhtq2701 mkdir -p /home/thanhtq2701/backups
sudo -u thanhtq2701 /var/www/html/.venv/bin/python \
  /var/www/html/co_chill_server.py backup \
  --db /var/www/html/var/co_chill_accounts.sqlite3 \
  --output /home/thanhtq2701/backups/co-chill-YYYYMMDD-HHMMSS.sqlite3
```

Backup chứa dữ liệu tài khoản/người học. Cron Production hiện giữ 14 ngày;
kiểm tra quyền thư mục, dung lượng, kết quả chạy và thử khôi phục định kỳ trên
bản sao/thư mục thử riêng.

Khôi phục **ghi đè dữ liệu hiện tại**. Trước khi làm, xác nhận đúng file backup
và lịch bảo trì:

1. Dừng service: `sudo systemctl stop cochill.service`.
2. Giữ database hiện tại trong thư mục dự phòng riêng. Nếu có file
   `co_chill_accounts.sqlite3-wal` hoặc `co_chill_accounts.sqlite3-shm`, cũng
   giữ chúng cùng bản database hiện tại.
3. Đưa các file `-wal`/`-shm` cũ ra khỏi thư mục database đang hoạt động (giữ
   bản sao ở thư mục dự phòng); không để WAL cũ nằm cạnh database restore.
4. Chép backup đã chọn vào
   `/var/www/html/var/co_chill_accounts.sqlite3`, đặt owner phù hợp với
   `thanhtq2701`, và kiểm tra quyền truy cập.
5. Khởi động service, kiểm tra `systemctl status`,
   `journalctl -u cochill.service` và `/api/health`.
6. Nếu xác minh thất bại, dừng service rồi phục hồi bản database và sidecar
   vừa giữ.

Không khôi phục database trong khi service đang ghi; không đưa backup vào repo.

## 6. Gia hạn chứng chỉ

Certbot đã được cấu hình tự gia hạn. Kiểm tra và mô phỏng gia hạn:

```sh
sudo certbot certificates
sudo certbot renew --dry-run
systemctl list-timers --all | grep -i certbot
```

Sau gia hạn thật, hook Certbot thường reload Nginx. Nếu cần, chạy
`sudo systemctl reload nginx` rồi kiểm tra HTTPS. Không chạy phát hành chứng
chỉ lặp lại khi certbot báo còn quota/rate-limit.

## 7. Tạo lại TOTP cho owner admin

`CO_CHILL_ADMIN_TOTP_SECRET` là secret chung cấu hình phía server. Đổi secret
không tự tạo một tài khoản admin mới và không thay schema/database.

1. Vào máy qua kênh quản trị riêng. Sinh secret mới bằng
   `/var/www/html/.venv/bin/python /var/www/html/co_chill_server.py generate-admin-totp`;
   chỉ nhập secret vào authenticator riêng và `/etc/cochill.env`.
2. Cập nhật `CO_CHILL_ADMIN_TOTP_SECRET` trong file môi trường, giữ quyền
   hạn chế; không lưu output vào file tạm hoặc terminal log.
3. Khởi động lại `cochill.service`, đăng nhập tài khoản admin hiện có với mã
   mới và xác nhận trang quản trị hoạt động.
4. Nếu cần tạo tài khoản owner mới do database/mất tài khoản, trước tiên
   backup database và xác nhận chưa có admin hiện hữu; sau đó dùng
   lệnh tương tác với EnvironmentFile riêng của systemd:

   ```sh
   sudo systemd-run --wait --pty \
     --property=EnvironmentFile=/etc/cochill.env \
     --property=WorkingDirectory=/var/www/html \
     --property=User=thanhtq2701 \
     /var/www/html/.venv/bin/python /var/www/html/co_chill_server.py \
     create-admin --username TEN_DANG_NHAP
   ```

   Lệnh từ chối tạo admin thứ hai. Không xóa database để vượt kiểm tra này.

## 8. Chuyển tùy chọn sang Gunicorn

Mặc định tiếp tục dùng `cochill.service` đang chạy `serve`. Nếu chủ vận hành
chọn Gunicorn, trước hết cài vào đúng venv:

```sh
cd /var/www/html
.venv/bin/pip install gunicorn
```

Đối chiếu `deploy/cochill-gunicorn.service.example`, dừng `cochill.service`,
cài unit thay thế với tên service đã thống nhất, `daemon-reload`, rồi chỉ bật
một trong hai service. Cấu hình mẫu dùng một worker/bốn threads, bind
`127.0.0.1:8000`, timeout 45 giây. Không chạy đồng thời cả hai trên cùng port.
Không tăng worker/replica: room state và semaphore Pikafish có scope process,
còn SQLite là một instance. Kiểm tra room pause/restart, log, health và tải
thực trước khi coi chuyển đổi hoàn tất. Không thêm Gunicorn vào
`requirements.txt` khi chưa duyệt.
