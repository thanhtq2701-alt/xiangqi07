# Bàn giao backend tài khoản chơi trực tuyến và Pikafish cho V6

Ngày kiểm tra 25 tháng 10 năm 2026. Đây là kiểm tra mã nguồn và đề xuất triển khai, chưa thay đổi ứng dụng, chưa truy cập hoặc cấu hình Google Cloud, chưa triển khai website. Các đường dẫn dưới đây tính từ thư mục gốc `E:\ThanhTQ\App cờ tướng\xiangqi-ai`.

## 1 Bản gốc đã đối chiếu

Người dùng cung cấp chính xác `C:\Users\thanh\Downloads\xiangqi-ai-20261024T180855Z-1-001.zip`. ZIP có 1217 entry, SHA256 `9b42be4ab115715c54fc788861c5d64728b37a3da3907d54bf903f9306db66f5`. Không thực thi mã từ ZIP. Các file `co_chill_server.py`, `app/cloud_store.py`, `app/pikafish.py`, `online-preview/engine-client.js`, `online-preview/cloud-client.js`, `requirements.txt` và `server.py` trong ZIP trùng từng byte với thư mục hiện tại. Do đó các bằng chứng backend sau áp dụng được cho bản gốc người dùng chỉ định.

ZIP là bản chụp toàn thư mục, không phải gói an toàn để công khai. Kiểm kê tên entry thấy 3 file dạng database, 470 entry metadata Git và 19 tài liệu DOCX/PDF. Không đọc nội dung dữ liệu cá nhân hoặc khóa bí mật. Không phát hiện tên `.env` ngoài mẫu hoặc tên file khóa theo bộ lọc đơn giản; điều đó không phải chứng nhận toàn bộ ZIP không có bí mật. Claude chỉ lấy source theo allowlist, giữ backup gốc nguyên vẹn, không tải cả ZIP vào thư mục web công khai hoặc GitHub Public.

Gói `deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24.zip` chỉ là giao diện tĩnh 15 file. Gói `deliverables/Co_Chill_V5_Source_2026_10_24.zip` gồm nguồn Python đầy đủ và không kèm dữ liệu người dùng. Hai gói phục vụ hai mục đích khác nhau. `tools/build_deploy_pack.py` là công cụ tạo gói source allowlist; không đóng gói `var/`.

## 2 Kết luận hiện trạng có bằng chứng

### Tài khoản đã có code nhưng bản Site tĩnh không chạy backend

- `co_chill_server.py:32` tạo ứng dụng WSGI, mặc định phục vụ giao diện trong `online-preview/` và API cùng địa chỉ.
- `co_chill_server.py:173` cung cấp `/api/session`; từ dòng 177 xử lý đăng ký và đăng nhập; dòng 209 và 211 tải/lưu trạng thái; dòng 213 xuất dữ liệu; dòng 201 xóa tài khoản; dòng 271 và 279 cung cấp thống kê và danh sách người dùng cho vai trò được cấp.
- `app/cloud_store.py:44` băm mật khẩu bằng scrypt. `app/cloud_store.py:271` cấp phiên mới và thu hồi phiên trước của cùng người dùng. `app/cloud_store.py:317` lưu theo revision để phát hiện bản ghi cũ, không âm thầm ghi đè tiến độ mới.
- Cookie HttpOnly, SameSite Strict và Secure khi cấu hình HTTPS nằm ở `co_chill_server.py:62`; kiểm tra Host, Origin, CSRF, quyền và giới hạn request nằm từ dòng 110. Không thay các rào này bằng CORS `*` để chữa lỗi deploy.
- `online-preview/cloud-client.js:59` gọi API tương đối `/api/session`. Nếu nơi đang phục vụ giao diện không trả JSON API, client chuyển sang trạng thái không có máy chủ tài khoản. Ảnh người dùng là biểu hiện phù hợp với bản tĩnh, không chứng minh toàn bộ chức năng tài khoản chưa được viết.
- Admin có TOTP, vai trò report chỉ đọc một phần, export/delete/backup đã có. Chưa có Google OAuth, xác minh email hoặc quên mật khẩu tự phục hồi. Chỉ có một phiên hoạt động mỗi tài khoản; máy mới đăng nhập thì máy cũ bị thu hồi.
- Tiến độ được người dùng gửi lên dạng state JSON. Thống kê học tập là tổng hợp từ dữ liệu này, chưa phải bằng chứng chống sửa điểm hoặc kết quả thi đấu được máy chủ xác nhận.

### Chơi trực tuyến chưa có triển khai thực

`online-preview/app.js:67` dựng thẻ `online` ở trạng thái disabled, mô tả sẽ phát triển sau. Hiện có bot và hai người cùng một thiết bị. Tìm kiếm mã không thấy room service, WebSocket, API gửi nước đấu online, hệ thống ghép cặp hoặc rating server. Không được chỉ bật nút rồi gọi là đã có PvP.

### Pikafish có adapter gọi chương trình trên cùng máy

`app/pikafish.py:59` đọc `PIKAFISH_PATH` và `PIKAFISH_NNUE_PATH`; `app/pikafish.py:165` khởi chạy tiến trình UCI. Đây không phải HTTP client gọi máy Google Cloud từ xa. URL Console Google mà người dùng gửi là trang quản lý tài nguyên, không phải địa chỉ phân tích engine.

Chủ sản phẩm nói đã tích hợp Pikafish tại project `co-chill-lab-512513`. Ghi nhận đây là thông tin chủ sản phẩm cung cấp; lần kiểm tra này chưa xác minh VM nào, engine nào, binary/NNUE ở đâu, tài nguyên bao nhiêu, có HTTP service hay chỉ chạy UCI trong terminal. Vì vậy không hứa chỉ upload source là tự kết nối được.

Adapter hiện có kiểm tra nước/biến qua luật, bảo toàn cp/mate/bound và góc nhìn bên đến lượt; chấm riêng nước người học bằng `searchmoves` từ cùng root; một process engine mỗi Python process; hạn thời gian và dọn process. Khi cấu hình thiếu/lỗi trả fallback có nhãn. `status()` chỉ kiểm tra cấu hình/file, không khẳng định engine khỏe thật. File `tests/test_pikafish.py` có 17 test với tiến trình UCI giả do test tạo. Báo cáo 24/10 ghi 110 Python và 101 JavaScript đạt; đây là kết quả lịch sử, không phải chạy lại hôm nay hoặc chứng nhận Pikafish trên GCP.

## 3 Kiến trúc đích đơn giản nhất để tái sử dụng

Đề xuất trước tiên kiểm tra máy Google Cloud đã có. Nếu chủ sản phẩm đồng ý, VM đủ tài nguyên và có thể vận hành ổn định, đặt giao diện, Python API và Pikafish trên cùng VM; `cochill.vn` phục vụ tất cả qua HTTPS cùng origin. Đường đi là trình duyệt → reverse proxy HTTPS → Python API → SQLite trên ổ bền; API gọi Pikafish cục bộ bằng UCI. Không cần mua thêm hosting chỉ để có một tên dịch vụ nữa nếu máy sẵn có đã đáp ứng, nhưng phải kiểm tra chi phí hiện tại và xin phép trước thay đổi hạ tầng.

Giữ frontend hiện tại và WSGI trong vòng đầu. Không viết lại thành React/FastAPI chỉ để đổi framework. Đặt Python sau reverse proxy, bind nội bộ, không đưa database, binary, source riêng, Word hoặc secret vào thư mục static. Cấu hình `CO_CHILL_PUBLIC_ORIGIN=https://cochill.vn`, vị trí database bền vững, khóa TOTP ở môi trường riêng. Máy chủ có process manager để tự chạy lại, HTTPS, kiểm tra sức khỏe, sao lưu ra ngoài ổ đang dùng và diễn tập khôi phục. Cấu hình reverse proxy và nguồn IP phải đáng tin để rate limit không coi toàn bộ người dùng là cùng một IP hoặc tin header giả.

Giai đoạn pilot chỉ một instance ghi SQLite. Muốn nhiều instance, nhiều worker engine hoặc lượng PvP lớn phải có đo tải, migration và hàng đợi dùng chung trước; không tự tăng worker rồi giả định semaphore cục bộ bảo vệ cả hệ thống. Có thể chuyển sang PostgreSQL khi số lượng ghi đồng thời, vận hành hoặc scale đòi hỏi; đó là quyết định triển khai có đo đạc, không điều kiện bắt buộc để chạy pilot nhỏ.

Nếu giao diện/API buộc đặt tại Mắt Bão còn engine ở Google Cloud thì cần adapter engine từ xa mới. Trình duyệt vẫn gọi `/api/engine/analyze` của Cờ Chill; backend mới gọi dịch vụ engine đã xác thực. Không gắn key engine vào JavaScript, không gọi trực tiếp raw UCI từ browser, không mở engine ra Internet không xác thực. Không đưa URL hoặc shell command từ người dùng vào runner.

## 4 Công việc cụ thể về tài khoản và dữ liệu

1. Chạy lại bản đầy đủ bằng `co_chill_server.py`, không nhầm legacy `server.py`. Thử tài khoản mới với database kiểm thử riêng, không mang database trong ZIP lên production như dữ liệu thật.
2. Deploy giao diện và API cùng HTTPS origin. `/api/session` phải trả `application/json` với capability accounts true; hiển thị lỗi kết nối phân biệt với chưa đăng nhập. Xóa lời hứa đồng bộ ở nơi đang chạy guest hoặc ghi rõ khả năng thực.
3. Tạo owner bằng CLI và TOTP, không đặt nút tự nâng quyền trong UI. Giữ người dùng, owner và report tách vai trò. Bảng admin cần bộ lọc ngày, người dùng thử, lượt đăng ký, đăng nhập/hoạt động và số ván/bài, kèm định nghĩa chỉ số rõ.
4. Chạy thử hai thiết bị: cùng tài khoản tải đúng tiến độ; phiên cũ bị thu hồi theo chính sách hiện tại. Đồng bộ ngoại tuyến phải giữ nháp, tránh dữ liệu tài khoản A rơi vào B, không tự ghi đè khi revision xung đột.
5. Thêm quy trình phục hồi tài khoản trước public rộng. Nếu chưa có email recovery, công khai phạm vi pilot và quy trình liên hệ; không tạo mật khẩu chung hoặc gửi mật khẩu plaintext.
6. Sao lưu SQLite bằng SQLite backup API đã có, đặt lịch, giữ bản ngoài máy, thử khôi phục rồi đăng nhập/lấy tiến độ. Xóa tài khoản phải có quy trình áp dụng cả lưu trữ phụ/backup theo chính sách đã chốt.
7. Dữ liệu guest cũ thuộc origin ChatGPT Site sẽ không tự xuất hiện ở cochill.vn. Chưa có full JSON restore tin cậy; cần luồng export/preview/validate/import có xác nhận và chống ghi đè trước khi hứa chuyển toàn bộ tiến độ.

## 5 Công việc cụ thể về Pikafish

### Nhánh cùng VM được ưu tiên nếu phù hợp

Kiểm kê read-only OS, kiến trúc CPU, phiên bản engine, nguồn và checksum binary/NNUE, đường dẫn, quyền thực thi, RAM/CPU/disk. Chạy `uci` → `uciok`, `isready` → `readyok`, một thế có bestmove/PV hợp lệ và một thế bên Đen; lưu kết quả đã bỏ thông tin riêng. Cài source Python và cấu hình `PIKAFISH_PATH` là đường dẫn tuyệt đối trên chính VM. Đường dẫn máy Windows không dùng trên Linux. Kiểm tra không chọn binary có tập lệnh CPU không được VM hỗ trợ.

Dùng adapter hiện tại trước, với Threads/Hash/time thấp để đo. Ghi thời gian p50/p95, CPU, RAM, lỗi và tỷ lệ fallback trên bộ thế đã duyệt. Có nút thử lại khi bận, giữ câu trả lời; không làm học viên mất phiên học khi engine timeout. Kiểm tra các chế độ bot, review-scan, review, practice đi đúng adapter. Engine thật phải trả `fallback=false` và metadata đúng; dấu hiệu này vẫn không tự chứng minh lời giải sư phạm chính xác.

### Nhánh engine ở VM khác

Tạo `RemoteAnalysisEngine` thực hiện cùng interface `status()` và `analyze(fen, moves, selected_move, mode)`. URL engine và xác thực cấu hình phía server. Service nhận schema giới hạn: FEN gốc + lịch sử, selectedMove tùy chọn, quick/deep, requestId; budget/thread/hash do service quyết định. Response có root fingerprint, engine/NNUE version, score_type, perspective, bound, depth, nodes, elapsed, candidates và selected. Backend đối chiếu root/request và phát lại tất cả PV bằng luật trước khi cho UI dùng. Có timeout kết nối/tổng, giới hạn body/output, rate limit, concurrency quota, retry có giới hạn, circuit breaker và thông báo fallback. Dùng mạng riêng khi khả thi hoặc HTTPS có service authentication và firewall giới hạn; không công khai cổng engine trực tiếp.

### Ranh giới sự thật và học tập

Không dùng điểm heuristic của fallback như centipawn thật, không quy đổi tùy tiện thành Elo, không nói engine luôn đúng tuyệt đối. Không trừ cp với mate hoặc coi lowerbound/upperbound là điểm chính xác. Lời giải chỉ dựa trên nước hợp lệ và biến đã kiểm tra; LLM nếu bổ sung chỉ diễn đạt evidence và phải qua validator.

`co_chill_server.py:360` ghi rõ review-scan hiện gửi bằng chứng cho frontend trước reflection để UI giấu đi. State học tập do client đồng bộ cũng sửa được. Đây là cổng sư phạm, chưa chống gian lận. V6 muốn giữ đáp án kín thật cần lưu phiên học phía server, review-scan chỉ trả vị trí và gợi ý trung tính, chỉ trả lời giải sau khi server nhận reflection. Các khóa đáp án tĩnh trong JS cũng phải được tách khỏi payload gửi sớm nếu áp dụng yêu cầu này.

## 6 Chơi trực tuyến tối thiểu nhưng đúng

Đề xuất vòng đầu là phòng mời bằng mã/link, hai tài khoản, ván không xếp hạng. Ghép cặp xếp hạng, chat và giải đấu để sau khi trận online ổn định. Đây là đề xuất cần chủ sản phẩm chốt trong V6, không thay thế yêu cầu của họ.

Tái sử dụng `app.rules.Position` làm trọng tài server. Thêm mô-đun `room_store.py`, `game_service.py` và migration có version. Bảng room, seats, authoritative_games, game_moves, game_events lưu người chơi, bên, FEN gốc, thứ tự nước, đồng hồ, trạng thái/kết quả, thời điểm server, version và request ID chống gửi trùng. Không nhận whole game JSON từ client như kết quả chính thức.

API đề xuất: tạo phòng, vào phòng, xem trạng thái theo event sequence, gửi nước kèm expectedPly và requestId, xin hòa/chấp nhận hòa, đầu hàng. Đây là API cần viết mới. Mỗi lần gửi nước, server kiểm tra phiên, chỗ ngồi, lượt, ván đang chạy, luật, đồng hồ và version rồi ghi nguyên tử. Hai lần click hoặc retry mạng không tạo hai nước; stale version trả snapshot mới. Đồng hồ tính bằng thời điểm server, client chỉ hiển thị ước lượng; không nhận số giây còn lại do client khai.

Để giữ WSGI hiện tại, MVP có thể polling ngắn theo sequence với backoff/visibility, rồi nâng WebSocket khi đã đo nhu cầu. WebSocket là lựa chọn transport, không thay thế logic luật và dữ liệu. Nếu dùng WebSocket ngay phải chọn runtime thích hợp, auth/Origin, reconnect/snapshot, heartbeat, backpressure và giới hạn kết nối; không nhét WebSocket vào wsgiref rồi gọi là production.

Khi rớt mạng phải có chính sách thời gian chờ và đồng hồ rõ; khi reload lấy snapshot và các event thiếu. Kết quả ván chỉ được ghi một lần. Bài review sau ván phải lấy biên bản server để xác định điểm cần học, không tin client tự khai thắng/thua. Chưa xác minh toàn bộ luật chiếu/đuổi của giải đấu Việt Nam; hiển thị phạm vi luật thực, không mở ranked như thể đã đạt tiêu chuẩn giải đấu.

Chặn engine analysis cho người đang thi đấu online dựa trên room/game server-authoritative. Không cho giả `purpose=bot` vượt rào; bot move chỉ do service gọi cho ghế bot thật, không trả eval/PV coaching trong ván. Khóa này chỉ ngăn dùng API của Cờ Chill để gian lận, không thể bảo đảm ngăn engine ngoài hoặc thiết bị khác. Spectator nếu có phải chốt delay và dữ liệu được xem; không công khai reflection riêng.

## 7 Tiêu chí nghiệm thu bắt buộc

- Hai trình duyệt/máy thật đăng ký, login, lưu và tải đúng dữ liệu của mình; owner thấy tài khoản mới; user không gọi được API admin; report không xem nội dung riêng ngoài quyền.
- Restart/redeploy không mất dữ liệu; backup khôi phục được trong môi trường riêng; không lộ database qua URL; kiểm tra không đưa secret vào bundle hoặc log.
- Đăng nhập phiên mới, session expired, logout khi request đang bay, xung đột revision, mất mạng rồi nối lại đều giữ đúng dữ liệu và không lẫn tài khoản.
- Test UCI giả hiện có tiếp tục đạt; thêm integration test trên Pikafish thật với metadata bản đã dùng, thời gian hữu hạn, thế bên Đen, cp/mate, history, selected move, sai PV, timeout, engine bận/mất, sai NNUE. Không xóa test khi fail.
- Trước reflection không có lời giải trên màn hình; nếu V6 yêu cầu chống xem lén thì Network/API cũng chưa chứa đáp án. Sau reflection được giải thích WHAT/WHY/HOW trên biến hợp lệ, retry và bài liên quan vẫn lưu/ôn đúng.
- Hai người chơi online từ hai mạng khác nhau hoàn thành ván; gửi trùng/stale/ngoài lượt/sai luật bị xử lý đúng; reload và reconnect khớp nước/đồng hồ; timeout/đầu hàng/hòa ghi đúng một kết quả.
- Đang chơi online không mở được phân tích qua UI hoặc tự gọi API; giả mode bot không vượt rào; kết thúc ván mới vào review/reflection.
- Đo tải theo số người/engine jobs đã được chủ sản phẩm chốt. Báo p50/p95 và lỗi thực, không tự ghi số người dùng, số ván hoặc Elo không có dữ liệu.

## 8 Câu hỏi backend cần đưa vào V6

Các mục sau là thông tin chưa được bằng chứng code trả lời; không yêu cầu người dùng tự chọn framework.

1. Mục tiêu bản mở tiếp theo là tài khoản cộng đồng bộ và engine thật trước, hay bắt buộc có phòng chơi online cùng ngày? Thứ tự đề xuất: tài khoản/engine → nội dung → phòng mời online.
2. Ngân sách tối đa mỗi tháng cho toàn bộ máy chủ, lưu trữ và backup là bao nhiêu? Khoản Google Cloud đã chạy được tính trong mức này chưa? Những khoản nào phải hỏi duyệt riêng?
3. VM Google Cloud đã có tên gì, hệ điều hành, số CPU, RAM và vùng đặt? Có đang chạy dịch vụ khác phải giữ không? Chỉ cần thông tin cấu hình, không gửi mật khẩu, SSH key, token hay file service account.
4. Pikafish hiện đã chạy thử UCI trong terminal hay đã có HTTP API? Nếu có API, cung cấp tài liệu schema, health response đã che thông tin nhạy cảm và cơ chế xác thực; không gửi key thật trong Word.
5. Phiên bản/nguồn binary và NNUE, đường dẫn trên VM, quyền sử dụng/phân phối và người cài đặt là gì? Có log uci/readyok/bestmove đã bỏ thông tin riêng để đối chiếu không?
6. Có đồng ý ưu tiên chạy cả Cờ Chill API và Pikafish trên VM hiện có để giảm một lần gọi qua mạng không, nếu kiểm tra đủ tài nguyên? Nếu phải đặt web ở Mắt Bão, điều kiện nào bắt buộc?
7. Đợt thử đầu dự kiến bao nhiêu người đăng ký, bao nhiêu ván cùng lúc và bao nhiêu lượt phân tích đồng thời? Đây là mục tiêu cần kiểm thử, không phải số liệu đã đạt.
8. Muốn người chơi đăng ký bằng tên người dùng/mật khẩu hiện tại hay cần email/Google ngay? Nếu chưa có email recovery, có chấp nhận pilot giới hạn với quy trình hỗ trợ thủ công không?
9. Giữ một phiên mỗi tài khoản như hiện tại hay cho dùng cùng lúc điện thoại và máy tính? Nếu nhiều phiên, cho người dùng xem và thu hồi thiết bị nào?
10. Ai giữ owner, ai có quyền report, ai được biên tập bài? Mỗi người dùng tài khoản riêng hay chỉ một mình chủ sản phẩm trong đợt đầu?
11. Với tiến độ guest trên ChatGPT Site, cần nhập vào tài khoản mới hay chấp nhận bắt đầu lại? Có bao nhiêu người/dữ liệu cần chuyển và người đó có thể tự xuất file không?
12. Trang thống kê cần theo dõi cụ thể chỉ số nào để đưa ra quyết định: đăng ký, hoạt động theo ngày, ván hoàn tất, bài tự giải, bài dùng gợi ý, quay lại ôn? Chỉ số nào được công khai và chỉ số nào chỉ owner xem?
13. Thời gian lưu tài khoản không hoạt động, biên bản, phản hồi và backup mong muốn? Ai xử lý yêu cầu xóa và phản hồi lỗi dữ liệu?
14. PvP đầu tiên ưu tiên phòng mời bạn bè hay ghép cặp ngẫu nhiên? Có bắt buộc Elo ngay không? Đề xuất phòng mời không xếp hạng để kiểm tra nền tảng trước.
15. PvP có bắt buộc tài khoản không, có cho khách vào xem/chơi không? Có chấp nhận chưa có chat trong phiên đầu không?
16. Chốt thời gian mỗi bên, cộng giây, cách chọn bên và khi nào đồng hồ bắt đầu. Khi mất mạng bao lâu thì xử lý, đồng hồ có tiếp tục chạy không, bỏ phòng trước nước đầu có tính thua không?
17. Người chơi có được xin hòa, chơi lại, đổi bên, xin đi lại không? Với ván không xếp hạng và ván có xếp hạng cần quy tắc khác nhau thế nào?
18. Có cần khán giả/xem trực tiếp không? Nếu có, xem trễ bao lâu, có xem đồng hồ/biên bản/chat không? Phần reflection sau ván mặc định riêng tư hay có chia sẻ tự nguyện?
19. Chọn bộ luật nào cho chiếu dai/đuổi dai/lặp/hòa để kiểm chứng bằng bộ tình huống chuẩn? Ai xác nhận các ca còn tranh cãi trước mở ranked?
20. Khi engine mất/bận, muốn tiếp tục bằng máy cơ bản có nhãn, chờ hàng đợi hay chỉ cho học bài đã duyệt? Có cho fallback chấm bài nâng cao không? Đề xuất không dùng fallback nông để phán quyết bài nâng cao.
21. Mức chờ phân tích chấp nhận được cho nhanh/sâu, số ứng viên và độ dài biến hiển thị là bao nhiêu? Không tự quy đổi các mức này thành Elo.
22. Những tình huống nào cần Claude dừng xin phép: thay DNS, mở cổng firewall, tạo VM/disk trả phí, chuyển database thật, gửi email, deploy public? Giữ nguyên yêu cầu hiện tại là hỏi trước các thay đổi bên ngoài có tác động.

## 9 Nguồn và giới hạn kiểm chứng

- Code nội bộ và các đường dẫn dòng ở trên được đọc ngày 25/10/2026; chưa sửa source.
- `TEST_REPORT_CODEX.md` là bằng chứng kiểm thử lịch sử 24/10; audit này không chạy lại cả suite.
- Pikafish UCI chính thức: https://github.com/official-pikafish/Pikafish/wiki/UCI-%26-Commands
- Google Cloud cách kết nối VM Linux: https://docs.cloud.google.com/compute/docs/connect/standard-ssh
- Google Cloud firewall: https://docs.cloud.google.com/firewall/docs/firewalls

Các tài liệu chính thức được đối chiếu 25/10/2026. Tài liệu kết nối và firewall chỉ hỗ trợ cách thiết kế triển khai; không xác nhận project riêng của người dùng đang có engine hoạt động hay tài nguyên đủ tải.
