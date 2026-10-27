# Cờ Chill V6 — source để đưa lên GitHub, 26/10/2026

Web học cờ tướng: **chơi/nhập ván → chọn điểm đáng học → tự suy nghĩ → giải thích có căn cứ → thử lại → bài liên quan → lịch ôn → tiến độ**.

Bản này là source bàn giao. **Chưa deploy V6 lên Internet**; ChatGPT Site cũ không tự cập nhật. Tài khoản/PvP cần Python phục vụ cả giao diện và API.

## Chạy ngay

Python 3.12 trở lên. Giải nén, mở cả thư mục bằng VS Code, mở Terminal tại nơi có README:

```powershell
python co_chill_server.py serve --port 8769
```

Mở **http://127.0.0.1:8769/**. Giữ terminal chạy; Ctrl+C để dừng. Windows có thể dùng `py -3.12` hoặc launcher `Mo_Co_Chill_V5.cmd` (tên cũ, gọi đúng server). Linux/macOS dùng `python3`. Không cần Node/npm/API key để chạy.

SQLite tự tạo ở `var/co_chill_accounts.sqlite3`. Copy source không chuyển tài khoản sang máy khác. Các thiết bị phải đăng nhập vào cùng một server đã deploy để đồng bộ. Không commit database.

## Những gì có trong source

- Giao diện Việt, EN cho các chuỗi giao diện đã dịch; nội dung học vẫn Việt. Cover, font không chân, ba theme xem trước, màn chọn tài khoản/khách.
- Máy cơ bản, hai người cùng máy, nhập/phát lại ký phổ; suy nghĩ trước lời giải, retry, bài liên quan, ôn và lưu nháp.
- Tài khoản scrypt/cookie, đồng bộ phát hiện xung đột, owner TOTP, quyền báo cáo, quản trị nội dung/phản hồi.
- PvP riêng/công khai, ghép theo thể thức thời gian, khách/tài khoản; server giữ luật/đồng hồ; hòa, đi lại có đồng ý, đầu hàng, đổi bên ván sau, khán giả và tin nhắn định sẵn. Pilot không xếp hạng.
- Hành trình 3 khóa/7 chương, 8 bài hướng dẫn và 2 bài nhiều lượt có cây đáp án kiểm tra luật, bên cạnh 12 bài cơ bản.
- Adapter UCI Pikafish; chế độ yêu cầu engine mạnh báo chưa sẵn sàng khi thiếu engine, không giả Pikafish bằng máy nông.

Chưa kiểm tra Pikafish/NNUE trên Google Cloud. Chưa có email tự khôi phục mật khẩu, LLM cá nhân hóa, 7 cấp bot hiệu chỉnh hoặc đầy đủ luật giải đấu. Xem [giới hạn](KNOWN_LIMITATIONS.md).

## Kiến trúc

```text
online-preview/ (HTML/CSS/JavaScript)
        │ HTTP cùng origin, cookie + CSRF
        ▼
co_chill_server.py
        ├── app/cloud_store.py → SQLite tài khoản/tiến độ
        ├── app/online_rooms.py → luật, phòng, đồng hồ PvP
        ├── app/content_store.py → nội dung có phiên bản
        └── app/pikafish.py → tiến trình UCI khi cấu hình
```

| File/nhóm trong online-preview | Vai trò |
|---|---|
| index.html, style.css, v5.css, v6.css | Khung, thứ tự script, bố cục, màu |
| app.js | Bàn cờ và vòng chơi/học cốt lõi |
| xiangqi.js, game-tools.js | Luật, máy cơ bản, ký phổ/phát lại |
| learning.js, experience.js, fixtures.js | Phiên học, bản nháp, lịch ôn, bài cơ bản |
| curriculum.js, line-practice.js, v6-learning-ui.js | Chương học, bài nhiều lượt và màn học |
| cloud-client.js, engine-client.js, v5-ui.js | API, đồng bộ, bằng chứng engine, tài khoản/quản trị |
| online-play.js, v6-ui.js | Phòng PvP; màn vào, ngôn ngữ, cover, theme |
| logo-co-chill.png, cover-co-chill.png, favicon.svg | Hình thương hiệu |

Giữ toàn bộ thư mục `online-preview/`, không copy riêng app.js. Các lớp bổ sung bọc app cũ để tái dùng code; thứ tự script quan trọng. Prototype từ thế hệ trước không phải entrypoint V6 và không nằm trong source pack.

## Kiểm tra và đóng gói

Cần Node.js LTS để test JavaScript, không cần khi chạy app. Bộ checks đã được xác nhận với Node.js 22.23.4; Node.js 6.14.0 quá cũ. Nếu máy có nhiều bản Node hoặc bản đang dùng không nằm trong PATH, chỉ rõ đường dẫn:

```powershell
python tools/run_checks.py --node "C:\path\to\node.exe"
python tools/build_v6_pack.py --output deliverables/xiangqi-ai-v6-new.zip
python tools/verify_source_pack.py deliverables/xiangqi-ai-v6-new.zip
```

Không có bundler/build hay TypeScript typecheck. Checks gồm syntax, nghiệp vụ, bộ bài và parity luật. Builder chỉ lấy danh sách file cho phép, không ghi đè ZIP cũ, kèm `MANIFEST_SHA256.json`.

Lần kiểm tra tại workspace C ngày 26/10/2026 dùng Python 3.14.2 và Node.js 22.23.4: 104 bài kiểm thử Python, kiểm tra fixture/parity và toàn bộ kiểm tra JavaScript đều đạt. Đây là kiểm tra local; không xác nhận Pikafish/NNUE, GCP hoặc cochill.vn. Xem [báo cáo tests](TEST_REPORT_CODEX.md) để biết phạm vi và giới hạn.

## Đọc tiếp

1. [Đưa lên GitHub cho người mới](docs/GITHUB_V6_CHO_NGUOI_MOI.md).
2. [Bàn giao Claude](docs/CLAUDE_HANDOFF_V6.md).
3. [Quyết định V6](docs/V6_DECISIONS.md).
4. [Chuẩn bị Google Cloud/cochill.vn](docs/DEPLOY_GCP_V6.md).
5. [Triển khai](IMPLEMENTATION_REPORT_CODEX.md), [kiểm thử](TEST_REPORT_CODEX.md), [giới hạn](KNOWN_LIMITATIONS.md), [AI](AI_USAGE.md), [riêng tư](PRIVACY.md).
6. [Tóm lược lịch sử trước V6](V6_PREVIOUS.md).

`.env.example` chỉ là mẫu; chương trình không tự nạp `.env`. Không gửi khóa, cookie, backup hoặc database cho AI/GitHub. Chưa có giấy phép mã nguồn chung do chủ dự án chọn; xem `THIRD_PARTY_NOTICES.md` trước khi công bố open source.
