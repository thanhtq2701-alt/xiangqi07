# Sổ tay hiện trạng Cờ Chill AI

Cập nhật 12/10/2026: repo đã được push lên `https://github.com/thanhtq2701-alt/xiangqi07`, nhánh mặc định `codex-full`; có launcher `Mo_Co_Chill.cmd` chạy độc lập với ChatGPT. Các nhận xét “chưa có remote” trong snapshot 08/10 là lịch sử. Đánh giá chuẩn bị công khai mới nằm trong `PUBLIC_READINESS_VI.md`; vẫn chờ chủ dự án quyết định Public. Inventory/HTML cũ có ngày snapshot riêng, không phải kết quả quét mới.

Bản diễn giải do người phát triển cập nhật, đối chiếu ngày 08/10/2026. Danh mục file tự động nằm trong `PROJECT_INVENTORY_VI.md`; bản HTML tổng hợp nằm trong `deliverables/Co_Chill_So_tay_hien_trang.html`. Đây là sổ nhớ dự án, không phải đặc tả thay thế V3 và không phải cam kết mọi ý tưởng đã được triển khai.

## 1. Bạn đang có sản phẩm ở bước nào?

Bạn có một prototype web chạy trên máy cá nhân, có code, luật cờ, máy tìm nước đơn giản, cơ sở dữ liệu và bài kiểm thử. Vòng học đã được triển khai xuyên suốt: chơi/nhập ván → xem lại → trả lời suy nghĩ trước lời giải → phân tích có nước hợp lệ → thử lại → bài liên quan → ghi lần thử → lịch ôn → dashboard. Chưa có website công khai hoặc sản phẩm production. Đường dẫn localhost chỉ dùng trên máy đang chạy server.

Đã qua bước ý tưởng, đặc tả và xây prototype. Bước tiếp theo là kiểm chứng chất lượng cờ và chất lượng dạy học, trả lời quyết định V4, rồi cải thiện engine và trải nghiệm dựa trên bằng chứng. Không cần mua API để chạy bản hiện tại.

## 2. Các nơi lưu thông tin và thứ tự ưu tiên

- `xiangqi-ai/XiangqiAI_V3_Final_Pack.zip`: đặc tả V3 đã chốt; 18 tài liệu Markdown và manifest. `docs/spec/` là bản sao đặc tả trong Git. Đây là nguồn yêu cầu; không đồng nghĩa đã hoàn thành tất cả.
- `General/Answer V3.docx` và `xiangqi-ai/Answer V3.docx`: câu trả lời, ý định sản phẩm của bạn. So SHA-256 trong danh mục để biết có trùng nguyên byte không.
- `General/V3.docx`: bộ câu hỏi khám phá cũ, giữ làm lịch sử, không tự coi là câu trả lời đã chốt.
- `xiangqi-ai/Codex.docx`: hướng dẫn thực thi cho tác nhân. Chỉ là tài liệu đầu vào; yêu cầu trực tiếp hiện tại của bạn được ưu tiên khi có mâu thuẫn.
- `10-07/XiangqiAI_V3_Final_Pack/`: một bản giải nén ngoài Git của repo. `docs/materials/` chứa bản giải nén và text trích xuất phục vụ đọc, bị Git bỏ qua.
- `10-08/Co_Chill_V4_Tien_do_va_Bo_sung_Thong_tin.docx` và `xiangqi-ai/deliverables/Co_Chill_V4_Tien_do_va_Bo_sung_Thong_tin.docx`: bộ 84 câu hỏi V4, gồm 12 câu P0; chưa phải đặc tả V4 được bạn phê duyệt. Khi sửa một bản, các bản khác không tự đồng bộ. Chọn một bản để trả lời và ghi rõ bản đó khi gửi lại.
- `Failing/10-08/1.png`, `22.png`: ảnh lỗi nhập extension/history của trình duyệt. Đã xem ảnh; không thể suy ra ứng dụng cờ tướng bị lỗi từ hai ảnh này.
- File `~$...docx`: file khóa/tạm do Word tạo, không phải bản tài liệu đầy đủ và không chứng minh tài liệu gốc cùng tên vẫn tồn tại.

## 3. Kiến trúc và từng nhóm code

Trình duyệt `web/` → JSON HTTP `server.py` → nghiệp vụ `app/service.py` → luật/engine/học tập → SQLite `app/storage.py`. Backend quyết định nước hợp lệ và khóa đáp án; frontend chỉ hiển thị và gửi thao tác.

| File | Hiện có gì và dùng để làm gì |
| --- | --- |
| server.py | Điểm khởi động. HTTP server Python, route GET/POST, cookie khách, giới hạn request, kiểm tra Host/Origin, chỉ phục vụ 4 tài nguyên web công khai. Mặc định port 8000; hướng dẫn demo dùng 8765. |
| app/rules.py | Bàn cờ 9×10, FEN, tọa độ, luật 7 quân, nước hợp lệ, tự chiếu/lộ Tướng, chiếu hết và hết nước. |
| app/engine.py | EngineAdapter và LocalEngine: tìm tối đa 2 ply, giới hạn thời gian, cache, đánh giá đơn giản và xác minh biến đi. Chưa có engine mạnh bên ngoài. |
| app/learning.py | 4 kỹ năng, nội dung bài học ngắn, chẩn đoán đơn giản, chọn bài, lịch ôn, ExplanationProvider và TemplateProvider. |
| app/puzzles.py | Sinh 12 thế cờ tổng hợp, nhóm chủ đề/family; không phải tập ván đấu thật hoặc dữ liệu đã được chuyên gia duyệt. |
| app/service.py | Tạo/nhập ván, nước người/máy, review, reflection, hint, attempt, practice, dashboard, feedback và export. |
| app/storage.py | Lưu JSON trong bảng SQLite records; tách dữ liệu theo phiên khách; giao dịch, xuất, xóa. |
| app/__init__.py | Đánh dấu package Python của ứng dụng. |
| web/index.html | Khung HTML, điều hướng và điểm gắn giao diện. |
| web/app.js | Render các màn hình, bàn cờ, gọi API, nhập ván, suy nghĩ, lời giải, thử lại, dashboard và cài đặt. |
| web/style.css | Màu sắc, bố cục, bàn cờ, responsive và trạng thái tương tác. |
| web/favicon.svg | Biểu tượng tab trình duyệt. |
| tests/test_rules.py | Kiểm thử luật, FEN, tọa độ, chiếu/hết nước và đếm cây nước. |
| tests/test_learning.py | Engine, bài mẫu, service, khóa đáp án, lịch ôn, lần thử đầu, dữ liệu và fallback. |
| tests/test_http.py | Kiểm thử server tạm, route, assets, bảo vệ tài nguyên, phiên khách và flow HTTP. |
| tests/__init__.py | Đánh dấu package kiểm thử. |
| tools/create_v4_document.py | Sinh Word câu hỏi V4. Cần python-docx ở môi trường tạo tài liệu; app không cần thư viện này. |
| tools/update_inventory.py | Sinh danh mục, hash, bản HTML tổng hợp và so thay đổi với lần kiểm kê trước. Chỉ dùng thư viện chuẩn Python; không sửa code hoặc tự commit. |

## 4. UI/UX thực sự đã có

- Trang chủ và hành trình demo 60 giây; bàn cờ có chọn quân/nước, đổi hướng nhìn.
- Chơi với máy hoặc hai người cùng thiết bị; nhập FEN + nước tọa độ; xem lịch sử ván.
- Màn xem lại điểm cần học; 3 ô suy nghĩ bắt buộc trước lời giải; WHAT/WHY/HOW; thử lại và gợi ý có ghi nhận hỗ trợ.
- Luyện bài liên quan, bài học ngắn, tiến bộ và lịch ôn; cài đặt xuất/xóa dữ liệu; góp ý lưu cục bộ.
- Cập nhật 09/10: giao diện có nhãn quân tiếng Việt tùy chọn, phím mũi tên/Enter/Esc, tự lưu bản nháp reflection lên server local, tiếp tục bài từ trang chủ và phục hồi bài/ván khi reload. Chưa audit WCAG đầy đủ hoặc kéo thả; nháp chưa lưu xong vẫn có thể mất khi đóng cưỡng bức, chưa giải quyết xung đột nhiều tab.

## 5. API hiện có — nội bộ, không phải dịch vụ trả phí

| Phương thức và đường dẫn | Chức năng |
| --- | --- |
| GET /api/bootstrap | Dữ liệu khởi tạo: dashboard, kỹ năng, bài học, nhãn engine/LLM/lưu trữ. |
| GET /api/dashboard | Lần thử, kỹ năng, lịch đến hạn, bài review và ván gần đây. |
| GET /api/game?id=… | Đọc ván thuộc phiên khách hiện tại. |
| GET /api/exercise?id=… | Đọc bài, ẩn phân tích nếu chưa được mở. |
| GET /api/export | Xuất dữ liệu phiên; không lộ lời giải chưa mở. |
| POST /api/game | Tạo ván, demo hoặc nhập ván. |
| POST /api/move | Gửi nước người chơi. |
| POST /api/bot | Yêu cầu nước máy. |
| POST /api/review | Tạo/đọc điểm cần xem lại của ván. |
| POST /api/reflect | Lưu suy nghĩ và xử lý mở lời giải theo loại bài. |
| POST /api/draft | Lưu nháp suy nghĩ; không mở đáp án hoặc ghi điểm. |
| POST /api/attempt | Thử nước tại bài học; ghi lần thử và cập nhật học tập. |
| POST /api/practice | Chọn bài liên quan hoặc ôn tập. |
| POST /api/hint | Gợi ý; đánh dấu có hỗ trợ. |
| POST /api/feedback | Lưu góp ý tại máy, chưa gửi cho chủ dự án. |
| POST /api/delete | Xóa dữ liệu phiên khi confirmation là DELETE. |

POST dùng JSON, cùng Origin localhost và cookie khách; giới hạn payload 32 KB. Chưa có OpenAPI, API versioning, OAuth, khóa API đối tác, hàng đợi tác vụ hoặc rate limit production. Interface engine/giải thích đã có nhưng không tự bảo đảm tích hợp provider bất kỳ sẽ hoạt động; provider chưa được chấp nhận sẽ trở về template chuẩn.

## 6. Dữ liệu, AI và nguồn

- `var/chill.sqlite3`: dữ liệu thật được ứng dụng lưu tại máy, bảng records gồm id/owner/kind/data/created. Kiểm kê chỉ đọc số bản ghi theo loại, không đưa cookie, định danh phiên hoặc suy nghĩ người học vào báo cáo.
- Các bản ghi có thể gồm thao tác kiểm thử/demo và thao tác của bạn; không diễn giải chúng thành số người dùng thật hoặc hiệu quả học tập.
- Ngân hàng 12 bài, 4 chủ đề; máy shallow search và giải thích template. Không có LLM, API trả phí, neural network, ML training hay tập dữ liệu lớn.
- Lịch ôn theo quy tắc 1/2/7/14/30 ngày; điểm tiến bộ là heuristic, không phải Elo hay năng lực được kiểm định. Không có gửi nhắc lịch.
- `data/sources.csv` theo dõi 2 nguồn: fixture tổng hợp và yêu cầu chủ dự án. Chưa chọn license phát hành dự án. Tham chiếu tài liệu luật/engine không có nghĩa đã tích hợp hoặc có quyền phân phối mọi dữ liệu ngoài.
- Git không lưu database, raw Word đầu vào, ZIP, ảnh artifacts hoặc text materials. Sao lưu Git đơn thuần sẽ không khôi phục toàn bộ thư mục của bạn.

## 7. Tài liệu bàn giao và nên đọc gì

| Tài liệu | Cách dùng |
| --- | --- |
| README.md | Điểm bắt đầu, cách chạy, flow, cấu trúc và giới hạn chính. |
| RUN_AND_DEMO_CODEX.md | Hướng dẫn demo ngắn và vận hành local. |
| IMPLEMENTATION_REPORT_CODEX.md | Chi tiết đã xây, quyết định kiến trúc, lệnh, dữ liệu, real/fallback và khái niệm cần học. |
| TEST_REPORT_CODEX.md | Bằng chứng 65 test và kiểm tra browser ở lần bàn giao trước; không tự cập nhật mỗi lần chạy. |
| KNOWN_LIMITATIONS.md | Những giới hạn đã biết, cần đọc trước khi mô tả sản phẩm cho người khác. |
| AI_USAGE.md | Phần AI hỗ trợ tạo code và trạng thái AI lúc chạy. |
| PRIVACY.md | Phiên khách, dữ liệu cục bộ, xuất/xóa và giới hạn riêng tư. |
| THIRD_PARTY_NOTICES.md | Nguồn, phụ thuộc và lưu ý giấy phép. |
| BEGINNER_LEARNING_GUIDE_CODEX.md | Thứ tự học kỹ thuật và các file để lần theo code. |
| DEVELOPMENT_JOURNAL.md | Nhật ký thay đổi theo đợt; bổ sung khi thay đổi hành vi. |
| AGENTS.md | Quy tắc làm việc trong repo cho tác nhân coding. |
| .gitignore | Quy định thứ gì không vào Git; không phải cơ chế sao lưu. |
| PROJECT_MEMORY_VI.md | Bản diễn giải này; cập nhật thủ công khi tính năng/trạng thái thay đổi. |
| PROJECT_INVENTORY_VI.md | Danh sách file, archive, Word, bản trùng, Git và lần kiểm kê mới nhất. |
| inventory/manifest.json | Snapshot máy đọc được để so file thêm/sửa/xóa giữa hai lần cập nhật. |

Thứ tự đọc đề nghị: sổ tay này → README → chạy demo → KNOWN_LIMITATIONS → 12 câu P0 trong Word V4 → báo cáo triển khai → hướng dẫn học code. Bạn chưa cần nghiên cứu ML sâu hoặc đăng ký dịch vụ cloud để kiểm tra prototype.

## 8. Cái gì còn thiếu và nên làm tiếp

Đợt 09/10 đã khảo sát nguồn chính thức của 11 dịch vụ cờ tướng, ghi nhận 3 nơi chưa truy cập được và cải thiện khả dụng từ yêu cầu có sẵn. Báo cáo đầy đủ: `RESEARCH_AND_IMPROVEMENTS_2026_10_09.md`. Bộ kiểm thử mới nhất có 72 test pass; đây là bằng chứng kỹ thuật, không phải hiệu quả học thực tế.

Bổ sung ngày 08/10/2026: `deliverables/Co_Chill_V4_Bo_sung_UI_UX_Kien_truc_Luat.docx` có 272 câu trong 34 nhóm, 20 câu ưu tiên, mã UX01.01–UX34.08. Trả lời cùng Word V4 cũ, kèm ảnh/bản vẽ theo mã trang P01–P16 và case luật theo mã LUAT001. Nguồn nội dung ở `docs/V4_BO_SUNG_UI_UX_KIEN_TRUC_LUAT.md`; generator là `tools/create_v4_ui_supplement.py`. Đây là bộ thu thập yêu cầu, chưa phải thiết kế UI mới hoặc luật đã triển khai.

1. Trả lời 12 câu P0 trong V4; xác định người học mục tiêu, mục tiêu pilot, engine/luật, quyền dữ liệu và tiêu chí chấp nhận. Trả lời các nhóm UI/UX/API còn lại theo mẫu; chưa quyết định có thể ghi “dùng mặc định đề xuất”.
2. Chuẩn bị một nhóm nhỏ thế cờ có quyền sử dụng: FEN, bên đi, lời giải chấp nhận, biến giải thích, mức người học và nguồn. Nhờ người hiểu cờ duyệt; đối chiếu engine mạnh trước khi đưa ra tuyên bố độ chính xác.
3. Kiểm thử bằng một ván của chính bạn; ghi màn hình/bước tái hiện lỗi và kỳ vọng. Hai ảnh lỗi extension hiện có không đủ để sửa lỗi gameplay.
4. Ưu tiên nâng chất lượng phân tích và xử lý tác vụ nền. Nháp reflection, độ rõ bàn cờ và thông báo chờ đã cải thiện ngày 09/10; review vẫn có thể mất khoảng 48 giây với 24 thế chưa cache vì search đồng bộ.
5. Sau khi vòng học được kiểm chứng, mới quyết định engine mạnh, hosting, đăng nhập, đồng bộ, backup và provider LLM. Chưa có PvP online, đồng hồ, placement thực, import ký phổ nâng cao, luật chiếu dai/đuổi dai đầy đủ hoặc kết quả pilot.

## 9. Cách chạy và cập nhật sổ nhớ mỗi đợt

Chạy web từ thư mục repo: `python server.py --port 8765`, mở http://127.0.0.1:8765/ và giữ terminal. Dừng bằng Ctrl+C. App chỉ cần Python 3.10+; không cần npm build hoặc API key.

Sau khi sửa: chạy `python -m unittest discover -s tests -v`; cập nhật nội dung mục liên quan trong sổ tay này và DEVELOPMENT_JOURNAL.md; chạy `python tools/update_inventory.py`. Mở bản HTML để đọc, xem `git diff`, rồi commit các file code/tài liệu cần thiết cùng bản kiểm kê. Không dùng git add toàn bộ dữ liệu riêng tư ngoài ý muốn.

Snapshot ghi HEAD tại lúc quét, tức commit nền trước commit chứa snapshot, không phải hash của chính commit tương lai. Không cần cập nhật vòng lặp chỉ để chèn hash chính nó. Lần sau chạy lại sẽ ghi HEAD mới và báo file thêm/sửa/xóa. Chương trình tự cập nhật metadata, không tự xác nhận tính năng đúng hoặc tự chạy tests.

Trước khi di chuyển máy: sao lưu toàn bộ thư mục App cờ tướng vào nơi bạn kiểm soát, gồm General/10-07/10-08 và database nếu muốn giữ tiến độ. Đóng server trước khi chép database; giữ dữ liệu riêng tư ngoài repo công khai. Tại lần kiểm tra này chưa cấu hình remote Git; commit hiện mới là lịch sử trên máy.
