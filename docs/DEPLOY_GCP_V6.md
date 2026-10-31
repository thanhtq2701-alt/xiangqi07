# Chuẩn bị đưa V6 lên Google Cloud và cochill.vn

Ngày 26/10/2026. Tài liệu chuẩn bị; chưa đăng nhập, thay máy, DNS, firewall,
dịch vụ trả phí hoặc deploy trong lượt này. Chủ sản phẩm phải duyệt trước.
Không cần mua tên miền lần nữa. Tên miền là địa chỉ; Python cần máy chủ chạy
liên tục, ảnh/code cần được lưu và database cần ổ bền.

Nếu bạn mới deploy lần đầu, hãy đọc thêm
[hướng dẫn từng bước cho người mới](../deliverables/CO_CHILL_PVP_DEPLOYMENT_GUIDE_NEWBIE_2026_10_30.txt).
Hướng dẫn đó giải thích thuật ngữ, kiểm tra PvP qua hai mạng, backup/restore và
cảnh báo bảo mật; nó không thay thế phê duyệt chi phí, máy chủ hoặc DNS.

## Kiến trúc pilot đã chọn

Một VM Linux chạy HTTPS reverse proxy → Gunicorn một worker nhiều thread →
`co_chill_server:application`, database SQLite trên ổ lưu bền, Pikafish UCI
chạy trên cùng VM. Frontend và API cùng `https://cochill.vn`. Không đưa
database hay toàn bộ source vào thư mục public của proxy; Python chỉ phục
vụ `online-preview/` và các API có kiểm tra quyền.

Không tăng nhiều worker/instance: điều phối engine và trạng thái restart phòng
hiện chỉ an toàn trong mô hình một process. Không dùng SQLite trên filesystem
tạm thời. Cổng Python chỉ bind loopback; public đi qua HTTPS.

## Chủ máy cần kiểm tra trước khi làm

1. VM thực, OS/CPU/RAM/disk, các dịch vụ khác đang chạy, IP công khai và cách
   truy cập được cấp quyền. Không gửi private key/password trong chat.
2. Pikafish executable tương thích Linux/CPU, đường dẫn, quyền chạy và NNUE
   tương ứng. Đọc `docs/PIKAFISH_SETUP_V5.md`; ghi metadata version và nguồn.
3. Tên miền đã hoàn tất đăng ký, quyền sửa DNS, dịch vụ HTTPS đã chọn; không
   sửa record email hoặc dịch vụ khác một cách mù quáng.
4. Nơi giữ backup riêng, hạn giữ và người có quyền khôi phục. Mục tiêu 12 giờ
   trong V6 cần chốt/đo riêng thời gian mất dữ liệu và thời gian khôi phục.

## Lệnh chuẩn bị trên Linux (ví dụ, chưa chạy)

Upload hoặc clone source sạch vào `/opt/co-chill/app` bằng tài khoản vận hành
có quyền. Không clone đè database đang chạy. Tạo virtual environment, cài
dependency đã khóa và chạy tests trước khi bật public:

```sh
cd /opt/co-chill/app
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python tools/run_checks.py
```

Lệnh tests cần Node.js 24.22.1 (phiên bản chuẩn trong `.nvmrc`).
Chương trình chạy không cần Node. Biến môi trường:

```sh
export CO_CHILL_DB_PATH=/var/lib/co-chill/accounts.sqlite3
export CO_CHILL_PUBLIC_ORIGIN=https://cochill.vn
export PIKAFISH_PATH=/opt/pikafish/pikafish
export PIKAFISH_NNUE_PATH=/opt/pikafish/pikafish.nnue
gunicorn co_chill_server:application --bind 127.0.0.1:8769 --workers 1 --threads 4 --timeout 45 --graceful-timeout 15
```

Đường dẫn là ví dụ, phải thay bằng đường dẫn có thật. Tài khoản dịch vụ cần
quyền đọc source/engine, ghi thư mục database; không chạy app bằng root.
`.env.example` chỉ hướng dẫn; app không tự đọc `.env`. Thiết lập biến qua
dịch vụ systemd hoặc môi trường vận hành, không nhét secret vào Git.

Owner cần TOTP. Lệnh sau in secret mới để **chủ máy tự giữ kín**, không sao
chép kết quả vào báo cáo, log công khai hoặc chat:

```sh
python co_chill_server.py generate-admin-totp
# Cấu hình CO_CHILL_ADMIN_TOTP_SECRET riêng và đăng ký cùng secret vào authenticator.
python co_chill_server.py create-admin --username OWNER_NAME
```

CLI hỏi mật khẩu kín. Tạo owner trước khi mời người khác. Cấu hình reverse
proxy giữ Host đúng, HTTPS, giới hạn request body; không tin IP trong header
do client tùy ý gửi. Kiểm tra rate limit sau proxy: nếu mọi client thành một
IP nội bộ thì giới hạn dùng chung có thể quá chặt. Chưa có cấu hình proxy
riêng đã nghiệm thu trên VM của bạn.

## Backup và cập nhật

```sh
python co_chill_server.py backup --output /PRIVATE_BACKUP_DIR/co-chill-NEW.sqlite3
```

Output phải là file mới, có quyền riêng. Đây là bản chứa dữ liệu người chơi;
không commit. Thử restore vào database thử riêng rồi khởi chạy instance
thử ở cổng khác; không ghi đè database thật để "thử". Backup/retention định
kỳ chưa tự cài. Cần giữ bản source V5 và V6 trước cập nhật, không xóa V4 tự động.

## Nghiệm thu trước mời 5–10 người

- HTTPS/cookie Secure hoạt động, đăng ký hai tài khoản không lẫn dữ liệu,
  owner xem được thống kê, người thường không gọi được admin.
- Pikafish trả nước/PV hợp lệ cho hai bên; tắt/mất/bận engine thì UI báo lỗi,
  không coi máy nông là kết quả mạnh; không trừ thời gian người chơi do lỗi máy.
- Hai máy ở hai mạng chơi phòng đến kết thúc; kiểm tra ready, clocks, reload,
  reconnect, hòa/thua/đi lại/tái đấu và khán giả không mở được engine trong ván.
- Reflection trước lời giải, thử lại/related, hoàn thành mới đặt lịch ôn,
  reload và đăng nhập lại giữ đúng nháp/tiến độ.
- Restart app giữ database, ván live tạm dừng đúng; backup/restore thực sự
  thành công, log không chứa password/token/câu trả lời riêng.
- Đo lỗi và độ trễ trên VM. Chưa có số liệu chịu tải hoặc SLA được chứng minh.

Khi đạt và được chủ sản phẩm duyệt, mới trỏ record cochill.vn đến IP máy đang
phục vụ HTTPS. Push GitHub không tự làm các bước deploy/DNS này.
