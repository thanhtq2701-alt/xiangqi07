# Báo cáo triển khai V6 — 26/10/2026

## Kết quả thực tế

Gói source tiếp tục từ repository V5 và ZIP chủ sản phẩm gửi ngày24/10.
Không rewrite toàn bộ, không deploy ChatGPT Site/cochill.vn, không push GitHub,
không thay DNS hoặc tạo hạ tầng trả phí. Gói để chủ sản phẩm cập nhật repository
và tiếp tục với Claude. Phần chưa đáp ứng V6 ghi ở KNOWN_LIMITATIONS.md và
docs/V6_DECISIONS.md; hoàn thiện pack không có nghĩa hoàn tất toàn bộ roadmap.

## Đã xây/cập nhật

- Giao diện: font không chân, cover rộng, chọn tài khoản/khách, thẻ3 theme,
  hỗ trợ English một phần giao diện. Giữ ảnh do chủ sản phẩm cung cấp.
- Nội dung: 3 khóa/7 chương,8 bài hướng dẫn và2 bài nhiều lượt bổ sung cho12 bài cơ
  bản. Bài có bàn cờ ví dụ/phát lại, provenance và giới hạn rõ.
- Hoàn thiện local nội dung: thêm ví dụ luật Xe bị quân chắn, ngòi Pháo đổi,
  chân Mã bị chắn và cách chắn đường chiếu; nối chương theo kỹ năng với puzzle
  cơ bản đã có. Sau bài nhiều lượt, đề xuất puzzle cơ bản cùng kỹ năng trước
  khi quay lại một bài nhiều lượt có cùng họ; reflection gate vẫn giữ nguyên.
- Nhiều lượt:3suy nghĩ ban đầu, nước ứng viên, phản ứng đối thủ từ cây kiểm
  tra luật, retry,3 lần sai hẹn lại, nhánh ngoài cây chưa chấm sai, explanation,
  hoàn thành một lần, bài liên quan, lịch ôn và self-report. Lưu/khôi phục nháp
  theo tài khoản, không coi xem bài là mastery.
- PvP: backend giữ trạng thái/luật/đồng hồ; guest hoặc account tạo/join/watch,
  phòng công khai/riêng và match theo preset,ready,hòa,đi lại,đầu hàng,tái đấu,
  khán giả/chat mẫu, history riêng. UI polling và nối đầy đủ API.
- Account V5 được giữ: scrypt,cookie,CSRF,role,TOTP,revision/conflict.
  Sửa transfer guest để không bỏ sót hoặc ghi đè tiến độ chỉ có bài nhiều lượt.
  Admin metrics bổ sung bài nhiều lượt, dedupe, không nâng proficiency giả.
- Sửa test TOTP phụ thuộc đồng hồ thật: giữ đúng mã phát lại và thêm ca mã
  mới ở bước thời gian kế tiếp; giữ nguyên bảo vệ xác thực production.
- Engine: thêm requireStrong để lỗi Pikafish không thành kết quả heuristic
  giả mạnh. Bot server/review tài khoản dùng chế độ này. Guest intermediate
  được hướng dẫn đăng nhập/dùng bài kiểm chứng thay phân tích nông.
- Công cụ: run_checks.py, builder V6 allowlist, verifier manifest/path/hash;
  hướng dẫn GitHub/Claude/GCP và báo cáo cập nhật.

## Kiến trúc

Frontend HTML/CSS/JavaScript không bundler; Python WSGI + SQLite cho API.
Luật hai phía có test parity. Browser phân lớp app cũ + UI mở rộng, shared
save/cloud boundary. Server chỉ phục vụ assets trong online-preview.
Pikafish qua subprocess UCI cùng máy; không nhận lệnh shell/path từ client.
Một worker nhiều thread cho pilot; không tự mở rộng đa process.

## File thay đổi chính

- online-preview/index.html,app.js,v5-ui.js,learning.js,experience.js,
  engine-client.js: nối modules, guard, lưu dữ liệu, export và engine.
- online-preview/v6-ui.js,v6.css: presentation/theme/language.
- online-preview/curriculum.js,line-practice.js,v6-learning-ui.js,app.js:
  chương, ví dụ luật, liên kết puzzle cơ bản và màn học.
- online-preview/online-play.js: lobby/phòng/chơi/xem/history.
- co_chill_server.py,app/online_rooms.py,app/cloud_store.py: API/PvP/metrics.
- tests/test_online_rooms.py,test_online_http.py,test_cloud.py: regression.
- tools/test_v6_*.cjs,test_engine_client.cjs,test_v5_ui.cjs: test UI/learning.
- tools/run_checks.py,build_v6_pack.py,verify_source_pack.py: kiểm tra/đóng gói.
- README,AGENTS,CLAUDE,docs và các báo cáo: cấu trúc/run/handoff/quyết định.

Manifest trong ZIP là danh sách chính xác từng file/byte/hash. Không có DB,
log,secret,.git,node_modules,tài liệu trả lời cá nhân hoặc ZIP cũ lồng bên trong.
Repository gốc vẫn giữ tài liệu lịch sử và prototype legacy, không xóa chúng.

## Kiểm thử và lệnh

Chi tiết kết quả ở TEST_REPORT_CODEX.md. Các lệnh thực hiện gồm:
python -m unittest (bộ core và legacy), Python compile, node --check,
tools/check_online_preview.py,tools/check_browser_rules.py,các test JS,
tools/run_checks.py,browser Chrome với database thử riêng,build_v6_pack và
verify_source_pack. Browser E2E đi qua cả học4 quyết định và PvP2 cửa sổ.
Môi trường hạn chế socket phải cấp quyền local cho kiểm thử; không yếu test.

Không có eslint/tsc/npm build vì dự án chưa dùng các hệ đó. Syntax và hành
vi được kiểm tra bằng công cụ được đóng trong pack; không báo lint giả.

## Real / fallback / pending

| Phần | Trạng thái |
|---|---|
| Luật, API tài khoản, SQLite, PvP | Code chạy/test local thật; chưa nghiệm thu Internet |
| UCI adapter | Có; test protocol bằng tiến trình giả |
| Pikafish VM của chủ sản phẩm | Chưa kiểm tra binary/NNUE/kết nối thật |
| Máy cơ bản | Tìm kiếm heuristic có nhãn, không Elo/ML |
| Explanation | Template có căn cứ, chưa LLM |
| Bài/cây đáp án | Tự dựng, kiểm tra luật/mục tiêu hữu hạn; chưa chuyên gia duyệt |
| Thống kê và ôn | Quy tắc/client state, không bằng chứng hiệu quả giáo dục |

Nguồn dữ liệu: đặc tả/câu trả lời chủ sản phẩm, ảnh thương hiệu chủ sản phẩm,
các thế cờ synthetic của dự án. Không scrape, không dùng ván người chơi để
huấn luyện. Quyền ảnh/tài liệu và license code cần chủ sản phẩm xác nhận;
Pikafish/weights không được phân phối kèm.

## Chạy ngày mai và demo

Trong thư mục giải nén: `python co_chill_server.py serve --port 8769`.
Mở http://127.0.0.1:8769. Giữ terminal. Tests: `python tools/run_checks.py`
(cần Node). GitHub: docs/GITHUB_V6_CHO_NGUOI_MOI.md.

Demo60 giây: vào khách → Hành trình → bài nhiều lượt → trả lời3 câu và chọn
nước → đối thủ đáp → hoàn tất → explanation/phát lại → ghi nhận → lịch ôn.
Có thể chọn bài cơ bản nếu chưa giải được; không bật đáp án trước suy nghĩ.
PvP dùng hai cửa sổ/hồ sơ tách biệt trên cùng server để tạo/join/ready/chơi.
Chạy Internet cần triển khai và nghiệm thu GCP riêng.

## 5 khái niệm nên học

1. Frontend hiển thị/thao tác; backend kiểm quyền và giữ sự thật dùng chung.
2. Database khác source; Git giữ code, không nên giữ dữ liệu người chơi.
3. State machine giữ các bước suy nghĩ/practice/explain/finish không bị nhảy.
4. Engine/rules cung cấp bằng chứng; LLM nếu thêm chỉ giải thích bằng chứng.
5. Test + version control + deploy là ba việc riêng: test đạt không tự
   publish, push không tự tạo server và copy source không copy tài khoản.
