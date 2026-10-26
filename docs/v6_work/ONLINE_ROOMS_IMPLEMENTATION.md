# Phòng cờ trực tuyến V6

Ngày 25 tháng 10 năm 2026. Mô-đun mới `app/online_rooms.py` và kiểm thử `tests/test_online_rooms.py` được viết sau khi chủ sản phẩm trả lời V6. Các mô tả chưa có PvP trong `BACKEND_AUDIT.md` mô tả bản gốc 24/10, không mô tả mô-đun mới này.

## Giao diện để tích hợp

Khởi tạo một lần `OnlineRooms(db_path)` khi ứng dụng khởi động, dùng cùng đường dẫn SQLite của CloudStore. Một instance ứng dụng và một Gunicorn worker cho pilot; các thread gọi độc lập được bảo vệ bằng SQLite transaction. Constructor tạm dừng ván đang chạy do không phân biệt thời gian máy chủ dừng với người chơi mất mạng; hai ghế xác nhận sẵn sàng mới tiếp tục. Không khởi tạo lại đối tượng mỗi request.

Tất cả phương thức nhận `user` từ session đã được server xác minh. `user.id` không được lấy từ JSON client. Người chơi khách cũng cần server-issued session có ID ổn định. Mỗi phương thức tự mở transaction ngắn trên SQLite; không gọi trong transaction ghi CloudStore đang giữ lock.

| Phương thức | Input | Output |
| --- | --- | --- |
| `create(user, data)` | preset bullet/blitz/rapid/untimed; visibility private/public; optional seconds và increment giới hạn | Snapshot phòng |
| `list_public(user)` | Session hợp lệ | rooms công cộng, mine, chatOptions |
| `match(user, data)` | preset | Ghép phòng công cộng cùng thời gian hoặc tạo phòng chờ; chưa bắt đầu cho đến cả hai ready |
| `join(user, code, spectator=False)` | Mã phòng đúng, xem hoặc chơi | Snapshot theo vai trò |
| `snapshot(user, code)` | Thành viên đã vào phòng | Cập nhật presence, đồng hồ và snapshot |
| `action(user, code, action, data)` | Các thao tác bên dưới | Snapshot mới hoặc APIError |
| `history(user)` | Session hợp lệ | Biên bản hoàn tất của chính người chơi, có màu riêng, không reflection của đối thủ |
| `has_live_context(user)` | Session hợp lệ | True khi người đó đang chơi hoặc xem ván đang chạy/tạm dừng |
| `delete_identity(user_id)` | Chỉ gọi khi xóa tài khoản đã xác thực | Xóa dữ liệu phòng/kết quả có danh tính đó |

Thao tác: `ready`; `move` với `move`, `expectedRevision`, `nonce`; `resign` với `confirm: true`; `draw`, `draw-accept`, `draw-decline`; `takeback`, `takeback-accept`, `takeback-decline`; `chat` với `message` là mã trong chatOptions; `kick` với `userId` của khán giả; `leave`; `rematch`.

Snapshot chứa code, gameId, ownerId, players, spectators, side, status, revision, options, ready, fen, initialFen, moves dạng chuỗi, clock theo millisecond, serverNow theo epoch seconds, result, drawOffer, takebackOffer, pauseReason, messages, rematch, chatOptions. Không chứa engine eval/PV, reflection, private learner state, nonce cache hoặc lịch presence đầy đủ.

## Hành vi đã thực hiện

Mã phòng 10 ký tự hex ngẫu nhiên. Phòng riêng không hiện trong danh sách; phải vào phòng bằng mã trước xem snapshot. Hai ghế ngẫu nhiên màu lần đầu, đổi bên khi cả hai xin tái đấu; mỗi ván có ID riêng và biên bản cũ giữ nguyên. Một danh tính chỉ chiếm một ghế đang chờ/chơi/tạm dừng. Đồng hồ chỉ bắt đầu sau hai xác nhận và tính bằng giờ máy chủ. Không tin FEN, màu, thời gian còn lại hoặc kết quả do client gửi. Nước được kiểm tra bằng `app.rules.Position`.

Move kiểm tra revision và nonce; request trùng không áp dụng thêm nước, hai request cạnh tranh không ghi đè. Người xem không được đi quân; chủ phòng đuổi người xem có hiệu lực trong phòng đó. Lời mời hòa hết hạn 15 giây. Xin đi lại phải được đối thủ đồng ý trước nước tiếp theo của người xin; lịch sự kiện còn giữ những nước đã rút. Đầu hàng cần xác nhận. Result lưu một lần trong bảng riêng.

Nếu một ghế không heartbeat 30 giây trong khi ghế còn lại vẫn có hoạt động, server xử thua mất kết nối. Nếu cả hai đều vắng hoặc server vừa khởi động lại, ván được tạm dừng để tránh ghi thắng/thua tùy tiện. Các deadline đồng hồ/mất mạng được so thứ tự. Polling snapshot phải chạy đều khi ở phòng; đừng gắn nó chỉ với hành động đi quân. HTTP tab nền có thể bị trình duyệt giảm nhịp, vì vậy trước public rộng phải kiểm thử hành vi tab nền và độ trễ mạng thật; API này không tuyên bố phát hiện mạng hoàn hảo.

## Giới hạn cần ghi đúng

- Ghép cộng đồng theo preset và phòng chờ, chưa ghép theo sức cờ thật. Level học không phải Elo.
- Chỉ chat bằng lời nhắn trung tính đã định sẵn. Chưa có chat tự do với cơ chế điều hành đủ để ngăn gợi nước; không gọi là chat tự do hoàn chỉnh.
- Không có rating, ranked hoặc giải đấu. Luật chiếu/đuổi/lặp giải đấu Việt Nam chưa được chứng nhận đầy đủ.
- Cần tích hợp route, guest/auth, UI và review. Chỉ unit test mô-đun đạt không chứng minh hai người đã chơi được trên Internet.
- API engine phải gọi `has_live_context` và chặn cả người chơi lẫn khán giả của ván sống, kể cả request giả purpose bot. Rào state client trước V6 không đủ để làm điều đó.
- Sau ván, mỗi người lấy history rồi lưu review riêng. Không chứa hoặc chia sẻ suy nghĩ riêng trong bảng phòng.
- Xóa danh tính hiện xóa phòng/biên bản có người đó, gồm bản có đối thủ. Cần công bố phạm vi và cân nhắc tách bản ẩn danh của đối thủ ở phiên bản sau; không giữ danh tính ẩn sau xóa.

## Kiểm chứng

`python -m unittest tests.test_online_rooms -v`: 19/19 đạt ngày 25/10/2026, 2.074 giây trong lượt chạy trước chỉnh vệ sinh nonce khi xóa danh tính. Các ca bao gồm private membership, public matching, cả hai ready, luật/lượt, revision, nonce, hai request đồng thời, đồng hồ, hết giờ, hòa 15 giây, offline 30 giây, hai người mất mạng, restart, spectator/kick/chat, đi lại có đồng ý, tái đấu đổi màu, biên bản riêng, xóa dữ liệu. Lượt cuối sẽ được báo trong tổng hợp kiểm thử của root sau tích hợp.
