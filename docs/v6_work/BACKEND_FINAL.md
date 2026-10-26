# Backend V6: bàn giao mã nguồn ngày 26/10/2026

Tài liệu này cập nhật phần backend đã viết sau bản kiểm kê gốc trong `BACKEND_AUDIT.md`. Chỉ mô tả mã nguồn và kiểm thử cục bộ; không có thao tác xuất bản website, GitHub, Google Cloud hay DNS trong lượt này.

## Các phần hoạt động trong mã nguồn

- `co_chill_server.py` phục vụ `online-preview/` và API cùng origin. Chạy cục bộ bằng `python co_chill_server.py serve --port 8769`; `server.py` vẫn là prototype/API cũ riêng.
- `app/cloud_store.py` giữ đăng ký/đăng nhập, mật khẩu băm scrypt, phiên HttpOnly, một phiên tài khoản, đồng bộ có revision, thống kê/quản trị phân quyền và TOTP cho owner. Database nằm ở `var/` hoặc đường dẫn bền vững chỉ định qua `CO_CHILL_DB_PATH`.
- `app/online_rooms.py` giữ bàn cờ, lượt, đồng hồ, ghế, kết quả và biên bản trên server. Hai người phải sẵn sàng; client không được tự khai FEN, đồng hồ hoặc kết quả. Các thao tác gồm đi quân, hòa 15 giây, đầu hàng có xác nhận, đi lại có đồng ý, xem ván, lời nhắn định sẵn và tái đấu đổi màu. Request nước đi có revision và nonce chống áp dụng hai lần.
- API `/api/rooms/*` dùng tài khoản hoặc cookie khách riêng có hạn 24 giờ. Khách không có quyền đồng bộ học tập, engine hoặc quản trị. Host, Origin, CSRF và giới hạn tần suất được kiểm tra. Biên bản đã kết thúc của mỗi người nằm ở `/api/rooms/history`.
- Engine bị chặn cho cả người chơi và khán giả đang ở ván online sống; giả `purpose=bot` không vượt rào. Kết quả trả chậm bị bỏ nếu người đó đã vào ván online trong lúc engine tìm. Review online đối chiếu biên bản hoàn tất của server, không tin lịch sử JSON do client sửa.
- Xóa tài khoản/khách xóa cả danh tính trong phòng. Hiện xóa phòng có ghế của người đó cũng xóa biên bản chung của đối thủ; đây là giới hạn cần công bố, không phải lưu lại bản ẩn danh.

## Các sửa lỗi cuối trong lượt này

1. Thêm `requireStrong` vào `POST /api/engine/analyze`. Khi `true`, kết quả fallback không được trả cho UI: API trả HTTP 503, `code=engine_unavailable`, `Retry-After: 5`, không kèm điểm, nước hoặc biến. Chuỗi `"true"` và kiểu khác boolean bị từ chối 400. `false` hoặc bỏ trường này giữ khả năng dùng máy cơ bản có nhãn của prototype cũ. Giao diện cần bật trường này cho lựa chọn Pikafish/review mạnh; đây không phải chứng nhận chất lượng engine.
2. Cả hai ghế của ván đang chơi hoặc tạm dừng phải hoàn tất/đầu hàng trước khi rời ghế. Sửa trường hợp người không phải chủ phòng bấm rời khi tạm dừng nhưng ghế vẫn mắc lại.
3. Từ chối `preset`, `visibility`, mã chat hoặc người bị mời rời có kiểu dữ liệu không đúng bằng lỗi 400; tránh biến JSON dạng list/object thành lỗi server 500.
4. Bổ sung thống kê các lần hoàn thành nhiều lượt V6 từ `lineAttempts` và bài dở `lineSession`. Dedupe theo ID, đếm số hình riêng biệt, giữ nhãn dữ liệu do client báo cáo. Hai bài tổng hợp cùng họ chiến thuật không được trộn vào tỷ lệ trình độ độc lập của bộ bài cũ. Có test riêng cho dữ liệu trùng, thiếu completion, bài ôn và bài đang tạm gác.

## Engine và cấu hình vận hành

`app/pikafish.py` gọi UCI executable trên cùng máy với Python, qua `PIKAFISH_PATH` và tùy chọn `PIKAFISH_NNUE_PATH`. Đường dẫn Console GCP không phải API engine. `.env.example` chỉ là mẫu; chương trình không tự nạp `.env`. Không có binary, trọng số hoặc khóa dịch vụ được thêm vào pack.

Bộ kiểm thử engine dùng tiến trình UCI giả do dự án tự viết. Nó kiểm tra giao thức, biến hợp lệ, bên Đen, cp/mate/bound, nước được chọn, timeout và dọn tiến trình; không đo sức cờ Pikafish thật. Cấu hình tồn tại chỉ được ghi `configured_unverified`. Chưa truy cập VM, chạy binary thật hoặc đo tải trên Google Cloud trong lượt này.

Mô hình pilot: một máy/instance, một Gunicorn worker, nhiều thread, ổ SQLite bền vững và HTTPS cùng origin. Lệnh có sẵn trong `docs/DEPLOY_V5.md` là `gunicorn co_chill_server:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 45 --graceful-timeout 15`. Với VM dùng reverse proxy, bind Python vào loopback và cấu hình domain/HTTPS trước khi public. Không tăng worker tùy tiện: constructor phòng tạm dừng ván sau restart, semaphore engine chỉ có phạm vi một process.

Các việc vận hành còn cần nghiệm thu trên máy thật: đường dẫn/quyền binary và NNUE, metadata phiên bản, HTTPS/cookie, đăng ký hai máy, reconnect/tab nền, restart, backup/restore, tải thực với 5–10 người. Khi đặt sau proxy, kiểm tra IP phục vụ rate limit; không tin `X-Forwarded-For` tùy ý từ Internet.

## Giới hạn rõ ràng

- Ghép cặp theo thời gian chờ/preset, chưa theo Elo; không ranked hay giải đấu.
- Chỉ lời nhắn định sẵn; chưa chat tự do. Luật chiếu đuổi/lặp của giải đấu Việt Nam chưa được chứng nhận đầy đủ.
- Tab nền có thể bị trình duyệt giảm nhịp polling và bị coi là mất kết nối sau 30 giây; phải thử máy/mạng thật trước pilot rộng.
- Khách có phiên phòng 24 giờ, nhưng chưa có chính sách tự dọn mọi phòng/biên bản hết hạn. Xóa khách chủ động đã có API; không coi cookie hết hạn là xóa toàn bộ dữ liệu phòng.
- Chưa phục hồi mật khẩu bằng email/Google OAuth, chưa LLM chấm suy nghĩ và chưa calibrate bảy cấp sức cờ.
- Thống kê học tập từ state đồng bộ vẫn là dữ liệu do client gửi, chưa phải thành tích chống gian lận. Reflection là cổng học tập UI, không phải hệ thống giữ mọi khóa đáp án bí mật khỏi người xem source.

## Kiểm thử trong lượt này

Runtime: Python bundled của máy phát triển, gọi bằng đường dẫn tuyệt đối trong terminal. Lệnh có thể chạy lại bằng `python` khi máy đã cài Python phù hợp:

```text
python -m unittest discover -s tests -v
python -m unittest tests.test_online_rooms tests.test_online_http -v
python -m py_compile co_chill_server.py app/online_rooms.py tests/test_online_http.py tests/test_online_rooms.py
```

Lượt đầu trước ba test bổ sung: 141 test, 133 đạt và 8 lỗi `WinError 10013` do môi trường chặn kết nối localhost của `tests/test_http.py`. Không xóa/bỏ qua/sửa yếu test. Lượt riêng sau sửa chính: 33/33 test phòng và HTTP đạt trong 68,395 giây; sau đó thêm một test đầu vào sai kiểu. `py_compile` đạt. Kết quả chạy lại toàn bộ với quyền localhost được ghi ở phần dưới khi hoàn tất.

### Nghiệm thu tiếp tục ngày 26/10/2026

- `python -m unittest tests.test_rules tests.test_cloud tests.test_pikafish tests.test_online_rooms tests.test_online_http -v`: **102/102 đạt**, 221,966 giây. Đây là toàn bộ test thuộc pack tại lúc bắt đầu lệnh; sau đó bổ sung thêm test thống kê nhiều lượt.
- `python -m unittest tests.test_cloud.CloudTests.test_multistep_metrics_deduplicate_without_inventing_proficiency -v`: **1/1 đạt**, 1,290 giây. Tổng số test core hiện tại: **103** (30 luật + 22 cloud + 17 UCI + 21 phòng + 13 HTTP phòng).
- `python -m unittest tests.test_learning tests.test_http -v`: 34 test learning legacy đạt, 8 test HTTP legacy gặp `WinError 10013` do quyền socket của môi trường.
- Chạy lại đúng 8 test HTTP legacy bằng `python -m unittest tests.test_http -v` sau khi luồng phê duyệt cho phép localhost: **8/8 đạt**, 1,503 giây. Tổng **145 test Python** hiện có đều đã đạt qua các lượt trên; không ghi đây là một lần chạy discover liên tục. Pack chỉ chứa 103 core test; 42 test legacy cần source legacy ngoài pack.
- `python -m py_compile co_chill_server.py app/cloud_store.py app/online_rooms.py tests/test_cloud.py tests/test_online_http.py tests/test_online_rooms.py`: đạt.
- Cả hai test sửa/xuất bản nội dung cloud đều đạt ở lượt này. Lượt trước có báo một lỗi nội dung nhưng bị ngắt trước khi giữ traceback; không đủ bằng chứng xác định nguyên nhân. Không sửa yếu test hoặc khẳng định đã sửa một lỗi chưa tái hiện. Công cụ kiểm tra pack sẽ chạy lại toàn bộ core từ bản giải nén.

Không có dữ liệu tài khoản thật được mở hoặc đưa vào kiểm thử; các test dùng thư mục SQLite tạm tự tạo. Không có push/deploy/GCP trong phần kiểm thử này.
