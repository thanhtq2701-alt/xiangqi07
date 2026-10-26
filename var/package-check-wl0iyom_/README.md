# Cờ Chill V5 — gói source để bàn giao/deploy

Đọc trước: [Hướng dẫn cochill.vn cho người mới](docs/COCHILL_VN_CHO_NGUOI_MOI.md).

Đây là bản sao các file V5 cần để chạy và tiếp tục phát triển. Giải nén vào thư
mục mới. Không có database, người chơi, mật khẩu thật, khóa TOTP, Word riêng,
Git history hoặc engine binary. Không xóa thư mục dự án gốc.

## Chạy local

Python 3.12 trở lên; mở terminal ngay tại thư mục chứa README này:

```powershell
python co_chill_server.py serve --port 8770
```

Mở http://127.0.0.1:8770/#home và giữ terminal chạy. Dùng `py -3.12` thay
`python` nếu có Python Launcher. SQLite mới ở `var/co_chill_accounts.sqlite3`.
Không cần Node hay API key để chạy. File `Mo_Co_Chill_V5.cmd` dùng cổng 8769.

## Deploy

Hosting phải hỗ trợ Python WSGI, HTTPS và SQLite trên vùng lưu bền. Không chỉ
upload toàn bộ gói vào public_html: source/API không phải toàn bộ là file public.
`co_chill_server.py` chỉ phục vụ tài nguyên từ `online-preview/`.

Lệnh Linux production (Gunicorn):

```sh
pip install -r requirements.txt
gunicorn co_chill_server:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 45 --graceful-timeout 15
```

Xem [DEPLOY_V5.md](docs/DEPLOY_V5.md) về origin, disk, tạo owner và backup.
`vercel.json` chỉ deploy giao diện khách; không tạo backend tài khoản.
`.env.example` là mẫu; ứng dụng không tự nạp `.env`.

## Cấu trúc

- `co_chill_server.py`: server/API/CLI V5.
- `app/`: luật, engine dự phòng, adapter UCI, dữ liệu, tài khoản và bài.
- `online-preview/`: toàn bộ giao diện và tài nguyên trình duyệt.
- `tests/`, `tools/`: kiểm thử V5 và tạo gói.
- `docs/` và các báo cáo: hướng dẫn, giới hạn, quyết định sản phẩm.
- `MANIFEST_SHA256.json`: danh sách, kích thước và hash của từng file (trừ manifest).

Gói bỏ ứng dụng legacy `server.py`/`web/`, tài liệu trả lời và các công cụ tạo
Word. Chúng còn trong dự án gốc nhưng không cần để chạy server V5.

## Kiểm tra gói độc lập

```powershell
python -m unittest discover -s tests -v
python tools/check_online_preview.py
python tools/check_browser_rules.py
node tools/test_preview_learning.cjs
node tools/test_preview_experience.cjs
node tools/test_preview_game_tools.cjs
node tools/test_cloud_client.cjs
node tools/test_engine_client.cjs
node tools/test_v5_ui.cjs
```

Có 68 kiểm thử Python V5/luật trong gói ở thời điểm tạo; 110 test trong báo
cáo dự án đầy đủ gồm thêm legacy không đóng gói. 101 test JavaScript được giữ.
Node chỉ cần khi chạy các kiểm thử JS. Adapter Pikafish được thử bằng UCI giả;
chưa có binary/NNUE thật. Lời giải hiện theo mẫu, chưa có LLM/ML huấn luyện.

## Cập nhật

Sửa code → test → xem diff → commit/push các file được chọn → deploy khi bạn
quyết định. Sau khi đã giải nén và chạy, `var/` có thể chứa dữ liệu riêng:
không upload toàn bộ thư mục một cách mù quáng. Chạy lại
`python tools/build_deploy_pack.py --output deliverables/BAN_MOI.zip` để tạo
gói allowlist mới. Lệnh từ chối ghi đè ZIP cũ. Database cần backup/chuyển riêng.
