# Bàn giao code Cờ Chill V5 — 24/10/2026

**Cập nhật sau bàn giao local:** giao diện V5 đã được phát hành lên ChatGPT Site, phiên bản Sites 4, theo yêu cầu mở online. Server Python chưa deploy; xem [biên bản phát hành](docs/SITES_V5_RELEASE_2026_10_24.md) và [hướng dẫn cochill.vn](docs/COCHILL_VN_CHO_NGUOI_MOI.md). Các đoạn “chưa phát hành” bên dưới mô tả thời điểm bàn giao local trước yêu cầu mới.

**Đã triển khai các phần có thể chạy của V5 trong repository local:** vòng học có bước suy nghĩ trước lời giải, giữ bài dở, lịch ôn, tài khoản và đồng bộ cùng server, quản trị, biên tập nội dung, giao diện theo thương hiệu và adapter engine. **Chưa triển khai hết mọi mong muốn trong V5; chưa đưa bản code này lên hosting.** Bản ChatGPT Site đã phát hành trước đây không tự đổi theo source local.

Phạm vi thực tế được đối chiếu theo [42 nhóm yêu cầu V5](docs/V5_DECISIONS_2026_10_24.md). Trạng thái kiểm thử cuối đợt nằm ở [TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md); không lấy số test của các mục lịch sử bên dưới làm kết quả của bản mới.

## 1. Đầu vào đã dùng

- File được tìm thấy và đọc toàn bộ: `E:\ThanhTQ\App cờ tướng\10-23\V5.docx`, gồm 940 đoạn và 96 khối câu hỏi/trả lời. Đường dẫn người dùng nhắc `E:\ThanhTQ\App cờ tướng\10-23.docx` không có tại lúc kiểm tra.
- Giữ nguyên tài liệu gốc và `docs/spec/`; đối chiếu yêu cầu mới với kiến trúc/code đang có, không xây lại toàn bộ.
- Dùng logo/cover do chủ sản phẩm gửi. Logo đã có bản tương ứng; thêm cover vào tài nguyên giao diện.
- Xem bốn ảnh thế cờ trong Word nhưng chưa đưa vào bài công khai vì cần xác minh thế, bên đi, đáp án và quyền sử dụng.
- Không coi câu trả lời trong file là quyền tự mua dịch vụ, phát hành công khai hoặc bí mật giữ dữ liệu để huấn luyện. Xóa tài khoản ở bản này xóa dữ liệu hoạt động thực sự.

## 2. Những gì đã xây

### Vòng học

Người học quan sát thế, trả lời ba câu và chọn một nước ứng viên trước khi mở lời giải. Bỏ trống trường bắt buộc không tạo lượt thử. Lời giải theo cấu trúc điều gì xảy ra, vì sao và cách suy nghĩ tiếp; nước/biến phải có căn cứ luật và kết quả đã có. Sau đó người học thử lại, nhận bài cùng kỹ năng ưu tiên chưa gặp, hoàn thành và thấy lịch ôn/tiến độ.

Giữ nháp và bước học khi tải lại. Sau ba lần gửi câu trả lời đầy đủ nhưng nước chưa được chấp nhận, bài chuyển sang tạm dừng để tiếp tục ngày sau; không tự tính là đã hoàn thành hoặc tăng lịch ôn. Lượt có hỗ trợ được ghi riêng, không gọi là đã độc lập nắm vững. Tự đánh giá cuối phiên là tùy chọn. Lịch ôn dựa trên thời điểm hoàn thành, hiển thị theo giờ Việt Nam.

### Chơi và xem lại

Có máy cơ bản trong trình duyệt, hai người cùng máy, đồng hồ/tùy chọn không giới hạn và nhập biên bản kiểm tra nước đi. Import toàn ván yêu cầu thế xuất phát và xác nhận đã gửi đủ biên bản; chương trình không thể chứng minh người gửi không bỏ phần cuối. Có nhận diện biên bản trùng và không cắt âm thầm danh sách ván cũ chỉ vì vượt 200 ván.

Review không cố định ba điểm đáng học: quét có giới hạn tối đa 20 lượt gần nhất của bên người học, hiển thị tiến độ thực, hỗ trợ hủy/bỏ kết quả trễ. Không thấy điểm cần xem lại không được diễn đạt thành ván hoàn hảo. Có lựa chọn phân tích nhanh/sâu qua API và trạng thái lỗi kỹ thuật; lỗi engine không tự làm người chơi thua do đồng hồ tiếp tục chạy trong lúc chờ bot server. Không đưa coaching trong ván đang diễn ra.

### Tài khoản, đồng bộ và quản trị

Đăng ký/đăng nhập username/password là chức năng thật với SQLite, không phải màn hình giả. Mật khẩu băm scrypt có salt; token phiên ngẫu nhiên chỉ lưu bản băm ở server; cookie HttpOnly/SameSite, Secure khi cấu hình HTTPS. API thay đổi dữ liệu có kiểm tra origin, CSRF, giới hạn kích thước/tần suất và quyền. Đăng nhập ở phiên mới thu hồi phiên cũ theo yêu cầu một phiên hoạt động.

Dữ liệu học đồng bộ có số phiên bản. Nếu server có bản mới, client báo xung đột để chọn, không ghi đè âm thầm. Cache theo từng tài khoản; bản khách chỉ nhập khi người dùng chủ động chọn. Giữ nháp khi mạng lỗi; trạng thái “Đã đồng bộ” khác với “Đã lưu trên thiết bị”. Khi đang lấy dữ liệu tài khoản, giao diện chờ để tránh ghi trạng thái khách/phiên cũ sang tài khoản mới.

Owner được tạo bằng CLI và cần TOTP để đăng nhập. Vai trò `report` xem thống kê/danh sách/biên bản đã lọc; không xem phản hồi riêng hoặc bản nháp nội dung. Owner xử lý phản hồi, khóa tài khoản với lý do/thời hạn, tạo/sửa nháp bài và xuất bản/tạm gỡ. Bộ nội dung kiểm tra nước hợp lệ, nguồn, phiên bản và xung đột cập nhật. Nếu bài đang học đã đổi phiên bản, dừng chấm theo đáp án cũ và cho người học giữ bản nháp trước khi bắt đầu lại.

Có sửa thông tin/mật khẩu, xuất dữ liệu và xóa tài khoản thường; backup SQLite và kiểm tra tài khoản không hoạt động qua CLI. Chưa có email phục hồi/OAuth, job backup hoặc dọn tài khoản tự động. Thống kê quản trị là dữ liệu do thiết bị gửi, không chứng nhận Elo, khả năng chống gian lận hay tác động học tập.

### Giao diện và triển khai

Giữ bố cục chính đã thống nhất, bổ sung cover, ba chủ đề màu, màn tài khoản/quản trị/trợ giúp, thông báo trạng thái kết nối và bố cục màn nhỏ. Chưa có kiểm toán khả năng tiếp cận hoặc thử đầy đủ iOS/Android. Chuẩn bị `vercel.json` cho bản tĩnh và hướng dẫn Render cho bản có server, không tự tạo dịch vụ trả phí.

## 3. Kiến trúc hiện tại, đọc từ ngoài vào trong

```text
Trình duyệt: online-preview/
  giao diện → luật/nước đi → trạng thái học và cache trên thiết bị
        │
        ├─ cloud-client.js → API cùng địa chỉ → SQLite tài khoản/nội dung
        └─ engine-client.js → API kiểm tra ngữ cảnh → adapter UCI/local engine

co_chill_server.py
  ├─ app/cloud_store.py: xác thực, phiên, đồng bộ, số liệu, xóa/backup
  ├─ app/content_store.py: nháp, xuất bản, phiên bản, kiểm tra bài
  └─ app/pikafish.py → app/rules.py kiểm tra nước; app/engine.py dự phòng
```

**Cùng địa chỉ** nghĩa là HTML và `/api/...` được phục vụ từ cùng một server/origin. Cách này giảm cấu hình cookie/CORS khi deploy. Nó không phải Vercel frontend tự gọi một backend bất kỳ: tách hai địa chỉ cần một vòng thiết kế và kiểm thử riêng.

`server.py` + `web/` + `app/service.py` là ứng dụng legacy còn được giữ để tránh làm mất code/tests cũ. Nó không dùng API tài khoản mới. Không trộn lệnh chạy hoặc database của hai bản. `var/chill.sqlite3` là dữ liệu cũ; `var/co_chill_accounts.sqlite3` là dữ liệu tài khoản V5.

## 4. File thêm/sửa trong đợt V5

Các đường dẫn dưới đây tính từ `E:\ThanhTQ\App cờ tướng\xiangqi-ai`.

| File/nhóm | Thay đổi và vai trò |
|---|---|
| `co_chill_server.py` | Entry point WSGI/CLI, static website, API session/account/state/admin/content/engine/feedback/health |
| `app/cloud_store.py` | SQLite, hash mật khẩu/token, TOTP, đồng bộ có revision, thống kê đã lọc, export/xóa |
| `app/content_store.py` | Lưu bài nháp/công khai, kiểm tra luật và nguồn, phiên bản nội dung |
| `app/pikafish.py` | Giao thức UCI, timeout, giới hạn process/output, kiểm tra PV, fallback rõ nguồn |
| `online-preview/app.js` | Tích hợp trạng thái học V5, import/review, bot server, resume và tài khoản |
| `online-preview/learning.js` | Lượt độc lập/hỗ trợ, tạm dừng, hoàn thành, ngày ôn, khôi phục trạng thái |
| `online-preview/experience.js` | Sở thích/trải nghiệm, thời gian và các kiểm tra trạng thái liên quan |
| `online-preview/cloud-client.js` | Session, lấy/lưu trạng thái, xử lý 409, offline và kết quả trễ |
| `online-preview/engine-client.js` | Yêu cầu phân tích, bỏ kết quả trễ, xác minh nước/biến/đơn vị điểm |
| `online-preview/v5-ui.js` | Tài khoản, quản trị, phản hồi, biên tập bài, riêng tư/trợ giúp |
| `online-preview/index.html`, `v5.css`, `cover-co-chill.png` | Nạp thành phần V5, bố cục/theme/ảnh cover |
| `tests/test_cloud.py`, `tests/test_pikafish.py` | Xác thực, phân quyền, đồng bộ, nội dung, engine giả và đường lỗi |
| `tools/test_cloud_client.cjs`, `test_engine_client.cjs`, `test_v5_ui.cjs` | Hồi quy client, race/expiry, điểm engine và điều phối UI |
| `tools/test_preview_learning.cjs`, `test_preview_experience.cjs` | Bổ sung ca học/tạm dừng/lịch và trải nghiệm |
| `.env.example`, `requirements.txt`, `vercel.json` | Mẫu cấu hình, Gunicorn cho UNIX, output static Vercel |
| `Mo_Co_Chill_V5.cmd` | Launcher Windows gọi Python từ PATH, giữ server trong cửa sổ trực tiếp; không tự bật trình duyệt |
| `docs/DEPLOY_V5.md`, `PIKAFISH_SETUP_V5.md`, `V5_DECISIONS_2026_10_24.md` | Chạy/deploy, tích hợp engine, đối chiếu toàn bộ đầu vào V5 |
| `README.md`, báo cáo test, báo cáo này, `AI_USAGE.md`, `KNOWN_LIMITATIONS.md`, `PRIVACY.md`, `THIRD_PARTY_NOTICES.md` | Bàn giao và phân biệt hiện tại với lịch sử |

Những Word bàn giao hoặc thay đổi tài liệu đã có từ các đợt trước không được tính là code mới của đợt này. Dữ liệu QA và văn bản trích xuất nằm trong `var/` bị Git bỏ qua. Không sửa tài liệu nguồn, không gộp nhầm toàn bộ file untracked thành một commit.

## 5. Phần thật và phần dự phòng

| Thành phần | Trạng thái chính xác |
|---|---|
| Luật di chuyển, lưu ván, nhập/phát lại | Có code thực và kiểm thử; không chứng nhận mọi luật giải đấu |
| Phản ánh, retry, gợi bài, lịch ôn, progress | Thực thi trong ứng dụng; gợi ý/lịch là heuristic, chưa có kiểm chứng hiệu quả |
| Tài khoản, sync, admin, biên tập | Backend SQLite thật khi chạy `co_chill_server.py`; không hoạt động trên hosting chỉ phục vụ file tĩnh |
| Pikafish | Adapter có; chưa có binary/NNUE thật hoặc kết quả đo sức mạnh |
| Engine fallback | Tìm kiếm local giới hạn, có nhãn; không ngang engine mạnh |
| Giải thích | Mẫu có căn cứ nước/biến; không phải LLM hiểu lập luận |
| Bài tập | 12 bài tự dựng và công cụ thêm bài đã kiểm tra luật; chưa là giáo trình chuyên gia |
| Người dùng/số ván | Tài khoản QA là dữ liệu thử; chưa có số liệu người dùng/impact được xác nhận |
| Hosting | Có code/cấu hình/hướng dẫn; chưa deploy, mua hạ tầng, đổi domain hoặc thay site cũ |

Các ranh giới engine, client phân tích, store và nội dung được tách để thay thế sau này. Có interface không đồng nghĩa phần thay thế đã được tích hợp hoặc nghiệm thu.

## 6. Lệnh kiểm tra và bằng chứng

Quá trình đã đọc file Word qua ZIP/XML, kiểm kê file/Git, kiểm tra JavaScript, chạy Python/Node suites và dùng trình duyệt kiểm tra luồng. Báo cáo kết quả cuối cùng, số ca và giới hạn môi trường nằm ở [TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md). Các lệnh tái kiểm tra:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app co_chill_server.py server.py tests
node tools/test_preview_learning.cjs
node tools/test_preview_experience.cjs
node tools/test_preview_game_tools.cjs
node tools/test_cloud_client.cjs
node tools/test_engine_client.cjs
node tools/test_v5_ui.cjs
python tools/check_online_preview.py
node --check online-preview/app.js
node --check online-preview/v5-ui.js
git diff --check
```

Node chỉ cần cho kiểm thử, không bắt buộc để phục vụ web. Không có TypeScript/typecheck hay bundler: frontend là JavaScript thuần nên không có bước build biên dịch để báo “đã build”. HTTP tests cần quyền mở socket local; môi trường hạn quyền có thể chặn thao tác này trước khi ứng dụng chạy.

Đã kiểm tra thủ công chuỗi phản ánh → chọn nước → lời giải → retry → bài liên quan, cùng việc tải lại giữ bước học và trạng thái đồng bộ bằng tài khoản thử ở lượt kiểm tra trình duyệt trước trong cùng đợt phát triển. Lượt chốt cuối chưa lặp lại kiểm tra trình duyệt do công cụ điều khiển không xác minh được địa chỉ tab; các thay đổi sau đó được kiểm tra bằng test tự động. Launcher mới chưa được thử nhấp đúp. Bằng chứng hiện có không thay thế thử hosting HTTPS, thiết bị thật, phục hồi backup hoặc kiểm thử với binary Pikafish thật. Những lỗi phát hiện trong đồng bộ/khởi tạo đã được sửa và có kiểm thử hồi quy; các giới hạn chưa xử lý được liệt kê riêng, không xóa test để che lỗi.

## 7. Ngày mai chạy như thế nào

```powershell
Set-Location -LiteralPath 'E:\ThanhTQ\App cờ tướng\xiangqi-ai'
python co_chill_server.py serve --port 8769
```

Nếu lệnh Python chưa có trên PATH nhưng máy có Python Launcher, dùng `py -3.12 co_chill_server.py serve --port 8769`. Mở [http://127.0.0.1:8769/#home](http://127.0.0.1:8769/#home). Giữ cửa sổ terminal; `Ctrl+C` để dừng. Sau khi tắt máy cần chạy lại. Không cần key API hoặc cài Node để mở web local.

Muốn owner: làm theo [hướng dẫn TOTP và tạo admin](docs/DEPLOY_V5.md#3-tạo-tài-khoản-quản-trị-riêng). Không có mật khẩu admin mặc định; không đưa tài khoản kiểm thử vào bản dùng thật. Muốn deploy: chọn bản tĩnh Vercel hay bản có API và ổ dữ liệu bền ở Render theo [DEPLOY_V5.md](docs/DEPLOY_V5.md). Không xem một lần deploy thành công là bằng chứng dữ liệu còn sau redeploy; cần thử lưu/đăng nhập/restart trên hạ tầng chọn.

## 8. Demo khoảng 60 giây

1. Mở Home để thấy nhận diện Cờ Chill và các lối vào chính; đăng ký/đăng nhập một tài khoản thử nếu muốn minh họa sync.
2. Mở Học, chọn bài đầu; chỉ vào ba câu hỏi và bàn cờ để giải thích rằng người học phải tự nghĩ trước.
3. Nhập suy nghĩ ngắn, chọn nước trên bàn, gửi. Đọc phần điều gì/vì sao/cách nghĩ và nhãn giới hạn nguồn phân tích.
4. Thử lại thế cờ; hoàn thành bước để sang bài liên quan. Nhấn mạnh hệ thống ưu tiên bài chưa gặp, không đảm bảo kho luôn còn bài mới.
5. Mở phần ôn/tiến độ và tải lại trang: cho thấy trạng thái/lịch được lưu. Nếu đăng nhập, đợi “Đã đồng bộ” trước khi đóng.

Đây là demo cơ chế, không phải bằng chứng người học thật đã hiểu trong 60 giây. Dùng dữ liệu thử riêng; không tính demo thành kết quả người dùng.

## 9. Năm khái niệm nên học từ implementation

1. **Frontend và backend:** HTML/CSS/JS là màn hình và tương tác; Python xác nhận phiên/quyền và lưu dữ liệu. File giao diện đẹp không tự tạo tài khoản tập trung.
2. **State machine:** một phiên có bước phản ánh, lời giải, retry, bài liên quan, tạm dừng, hoàn thành. Kiểm tra bước chuyển giúp tránh lộ đáp án sớm hoặc cộng lượt hai lần khi reload.
3. **Xác thực và phân quyền:** đăng nhập trả lời “bạn là ai”; backend quyết định “bạn được làm gì”. Ẩn một nút admin ở giao diện không phải biện pháp phân quyền.
4. **Đồng bộ có revision:** hai bản dữ liệu có thể cùng thay đổi. Gửi số phiên bản giúp phát hiện bản cũ và yêu cầu chọn, thay vì âm thầm làm mất công việc; cache local và server là hai nơi lưu khác nhau.
5. **Luật, engine, lời giải là ba lớp:** luật kiểm tra nước đi; engine tìm và đánh giá trong giới hạn; phần dạy diễn giải những dữ kiện đó. LLM về sau không được tự tạo nước/điểm/biến ngoài căn cứ đã kiểm tra.

## 10. Phần còn lại và rủi ro cần biết

Chưa có engine mạnh thật, LLM chấm ngữ nghĩa, dữ liệu bài/luật đã được chuyên gia duyệt toàn diện, PvP, OAuth/phục hồi email, sharing đa máy công khai, RAG sách, giáo trình thích nghi, nhắc ngoài ứng dụng hoặc vận hành nhiều server. Nền tảng tài khoản chưa được audit độc lập hay thử tải production. Backup/retention cần chủ vận hành thực hiện. Chi tiết ở [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

Không có push/commit/phát hành mới được ghi nhận trong đợt bàn giao này. Quyền ghi `.git` bị hạn chế trong môi trường làm việc; code và tài liệu nằm ở working tree để chủ dự án xem và commit. Các commit và site được nhắc bên dưới là lịch sử trước ngày 24/10/2026, không phải thao tác mới.

---

## Lịch sử triển khai trước V5 24/10/2026

Các số test, branch, URL và lệnh dưới đây mô tả từng thời điểm cũ. Đọc phần V5 ở trên để chọn entry point và trạng thái hiện tại.

# Cập nhật phát hành ngày 16/10/2026

Đã triển khai và phát hành Site phiên bản 3 dựa trên UI UX + Luật, UX35. [Báo cáo đầy đủ](BAO_CAO_UIUX_V5_2026_10_16.md) ghi file thay đổi, kiến trúc, lệnh, kiểm thử, trạng thái engine/LLM, dữ liệu, quyền, giới hạn và demo. Các phần bên dưới được giữ làm lịch sử các đợt trước.

# Implementation report

## Update 9 October 2026

Added server-owned reflection drafts (`POST /api/draft`), pending learning summaries in dashboard, home resume entry, hash-based reload recovery, Vietnamese piece labels, keyboard board navigation, responsive/readability polish and clearer request/error handling. Files changed: app/service.py, web/app.js, web/index.html, web/style.css, tests/test_learning.py, tests/test_http.py and handoff documentation. JSON storage avoids a migration; drafts stay private to the guest, export/delete with other records, do not open answers or score, and cannot overwrite submitted reflections.

Verified 72 tests (64.517s), Python compileall, Node --check, browser draft/reload/full learning flow and a 390×844 layout. No new build system, external engine, LLM, dataset or paid service. Engine and scoring remain the original prototype. Drafts lack durable offline support and multi-tab conflict resolution; full browser history routing and screen-reader audit remain outstanding. Run command stays `python server.py --port 8765`.

Research and complete change report: RESEARCH_AND_IMPROVEMENTS_2026_10_09.md, with official sources for 11 inspected services and 3 inaccessible targets. No owner answers from the new V4 questionnaire were used. Earlier evidence below describes the initial implementation.

## Outcome and evidence

Built a working Vietnamese-first local Xiangqi learning prototype from an empty application baseline. The complete loop was exercised in the browser: load synthetic game, open critical moment, answer three reflection questions, reveal grounded analysis, retry a2a7, receive a different related exercise, solve h2h7, record both attempts, schedule a 14-day review, view progress and reload with persistence intact. These are QA records, not real learner-impact results.

Final automated run: **65 tests passed in 39.380 seconds**, including rules, engine lines, 20 successive bot positions, learning services, SQLite persistence and real HTTP integration. Python compilation, modern Node JavaScript syntax check and Git whitespace check also passed. No TypeScript/typecheck or bundler is configured; the application intentionally has no dependency installation or frontend build step.

## Input audit

Read both supplied Word documents completely by extracting all text-bearing document parts, and read all 18 Markdown files plus manifest in the Final Pack. Long output was re-read in bounded chunks after truncation. The entire parent `App cờ tướng` folder contained only the supplied materials, an older discovery-question document, a temporary Word lock file and a duplicate ZIP. Hash comparison confirmed `10-07.zip` equals the Final Pack. No source code, dependency manifest, tests, engine binary or Git repository was present. There was no existing application to run or preserve.

The current user request and autonomous Codex.docx supersede the archive's older audit-only/stop instructions. The original spec files are copied unchanged to `docs/spec/`. Raw discovery text and source attachments remain local and ignored by Git. No other project directories were modified.

Local Git branch: `codex-full`. First implementation commit: `6cd4f79` (`feat: implement local Xiangqi learning loop with rules and persistence`). Documentation and the requested V4 document are recorded separately. No remote was configured or push performed.

## Architecture actually used

- Browser: semantic HTML, CSS and JavaScript without a framework; SVG/CSS board with clickable accessible cell labels.
- HTTP: Python standard-library loopback server with JSON requests, static-file allowlist, Host/Origin checks, request size limit, security headers and HttpOnly/SameSite guest cookie.
- Domain: immutable board state and deterministic legal move generation; bounded local search behind `EngineAdapter`; application services enforce the learning state machine.
- Teaching: `ExplanationProvider` interface and canonical Vietnamese `TemplateProvider`. Unverified provider output falls back. No model API exists at runtime.
- Learning: theme recommendation prioritizes unseen families; first-attempt-only evidence; assisted/independent outcomes are separate; transparent date scheduler.
- Persistence: SQLite repository with owner-scoped JSON records, transactional writes, explicit connection closure, local export and deletion.

The suggested Next.js/FastAPI/Supabase stack was not an existing implementation. Choosing Python standard library + plain JS + SQLite removes install/API/auth barriers and keeps the loop runnable. The domain boundaries are portable to FastAPI/PostgreSQL and a richer frontend later. This is a documented prototype deviation, not a claim of production readiness.

## Main files and behavior

| File | Responsibility |
|---|---|
| `app/rules.py` | FEN validation, coordinates, all seven piece movements, blocking, self-check, flying general, terminal states |
| `app/engine.py` | Cached uniform-depth root ranking, legal PVs, bounded search and disclosed timeout fallback |
| `app/puzzles.py` | Twelve original synthetic fixtures, four skills, source/family/solution metadata |
| `app/learning.py` | Grounded WHAT/WHY/HOW, tentative skill tags, recommendation and 1/2/7/14/30-day scheduling |
| `app/service.py` | Games, move history, review, reflection gate, hints, retry, progress, export gate |
| `app/storage.py` | SQLite ownership and transaction repository; connections close on context exit |
| `server.py` | Local HTTP entry point and session boundaries; only four public static assets |
| `web/` | Home, board, import, review, practice, lessons, dashboard, data controls |
| `tests/` | 65 automated tests across rules, search, services and HTTP |
| `docs/spec/` | Unchanged finalized specifications |
| `data/sources.csv` | Current provenance register |
| `tools/create_v4_document.py` | Reproducible owner-requested V4 questionnaire builder |

Also created README, RUN_AND_DEMO_CODEX, TEST_REPORT_CODEX, BEGINNER_LEARNING_GUIDE_CODEX, AI_USAGE, KNOWN_LIMITATIONS, PRIVACY, THIRD_PARTY_NOTICES and DEVELOPMENT_JOURNAL.

## Real versus fallback

**Real execution:** legal move generation, bot search, game history, imported move validation, critical selection, server-side reflection gate, legal candidate lines, retries, recommendations, first attempts, dates, feedback storage, dashboard, guest isolation and SQLite persistence.

**Fallbacks and simplifications:** shallow material-oriented local engine instead of Pikafish; deterministic template instead of LLM; elementary synthetic fixtures instead of an expert gold set; local guest instead of cloud auth; heuristic score/schedule instead of validated mastery/ML. Imported FEN is structurally validated but historical reachability is not proven. Review currently focuses Red and the latest 24 Red plies.

Engine status: `chill-local-1.0`, maximum depth 2 plies, a 2-second per-position search deadline, LRU cache up to 512 entries. An unfinished iteration is discarded, preserving common comparison depth. Legal PV validation follows search. Bot strength is low; strategic coaching beyond the horizon is not supported. No engine binary, NNUE weights or external dataset was installed.

LLM status: none. The provider boundary is ready for future work, but the current verifier intentionally permits only canonical grounded template output. A real LLM needs evaluation and stronger fact constraints before enabling arbitrary prose. Reflection text is stored, not semantically graded.

## Commands and material failures

| Commands or checks | Result and purpose |
|---|---|
| `Get-ChildItem`, `rg --files --hidden`, ZIP/XML extraction | Inventoried all local materials; read complete specifications |
| `git status --short` initially | Reported no Git repository; truthful empty-baseline finding |
| `node --version`, `python --version`, `git --version` | Found system Node 6.14, Python 3.14, Git 2.52; app needs only Python |
| Puzzle-bank analysis script | All 12 authored solutions match depth-2 local search |
| `python -m unittest discover -s tests -v` | Final 65/65 passed; HTTP tests require loopback socket permission |
| `python -m compileall -q app server.py tests` | Passed |
| Bundled modern `node.exe --check web/app.js` | Passed; no dependency/bundler build required |
| `git diff --check` | Passed |
| `python server.py` / `python server.py --port 8765` | Started; final browser-accessible server uses 8765 outside socket-restricted sandbox |
| Browser actions in Codex | Complete flow, reload persistence and responsive layout inspected |
| `git init -b codex-full`, `git add`, `git commit` | Created local history; `.git` writes required sandbox escalation |
| Bundled Word builder and structural QA | Valid DOCX; 84 unique questions and all 12 P0 IDs verified |
| `render_docx.py ... --emit_pdf` | Blocked: LibreOffice `soffice.exe` is not available in the runtime; retry outside sandbox confirmed missing renderer |

Early failures fixed: invalid synthetic black-pawn placement; test positions with an unintended friendly blocker or surviving pawn; SQLite context manager not closing connections on Windows. Assertions were preserved, test fixtures corrected to represent the intended rules. Windows sandbox socket error 10013 was resolved by running local HTTP checks/server outside the sandbox, without changing application networking safeguards.

## Manual verification and code review

Verified the normal demo loop including a new unseen exercise and persisted results. Observed no solution in review before reflection. Checked source/API paths so the JSON export also omits unrevealed analysis. Reviewed legal movement, local turn ownership, first-attempt idempotence, failure retention, same-skill unseen selection, late-study due dates, source disclosure, and public static-path restrictions. Browser test data remains clearly demonstration evidence; no claim of real user learning is made.

Full screen-reader/mobile-device accessibility certification, tournament adjudication, production load testing, public deployment and expert content validation remain open. See KNOWN_LIMITATIONS for the complete list. The V4 Word file is structurally checked but not visually paginated/rendered because the required renderer is absent; do not claim the explicit page breaks prove its actual Word page count.

## Run tomorrow

```powershell
cd "E:\ThanhTQ\App cờ tướng\xiangqi-ai"
python server.py --port 8765
```

Open http://127.0.0.1:8765/. No package install or API key. Keep the terminal open; Ctrl+C stops it. Use the same browser/hostname for the guest session.

60-second demo: home demo → review → answer 3 prompts → reveal → retry a2a7 → related unseen puzzle → reflect → h2h7 on a fresh session → dashboard. See RUN_AND_DEMO_CODEX for alternatives and later-session behavior.

## Five concepts for the owner

1. Legal moves and move quality are different questions; rules are deterministic, search estimates quality.
2. A learning state machine protects reflection before revelation and distinguishes first attempts from retries.
3. An API is a data contract; it does not automatically mean a paid AI service.
4. Transactions and ownership keep saved progress coherent and sessions separate.
5. Automated tests establish specific evidence, while expert review and real pilot observations answer different questions.

Next highest-value work: owner-reviewed diverse positions plus a grounded explanation rubric, followed by a stronger engine adapter and independent benchmark before widening usage.

## 12 October 2026 — independent Windows launcher

Added `Mo_Co_Chill.cmd` and `tools/start_local.ps1`: discover Python 3.10+, start hidden server outside the chat lifecycle, wait for HTTP readiness, reuse an existing responsive app, and open the default browser. Failure messages point to ignored local logs; occupied ports are not killed. README explains reboot behavior and browser-cookie continuity. Commands verified: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/start_local.ps1 -NoBrowser` twice and HTTP GET `/` (200). Server remains reachable after launcher exits. No game logic or database migration changed; no new external services. Automatic Windows startup and hosting are not installed.

## 12 October 2026 — repository presentation

Polished README for fresh clones, added contribution guidance and owner-reviewed public-readiness report, corrected GitHub status and journal ordering. Rechecked 72 tests, Python/JS syntax, and 97 historical blobs including two DOCX XML payloads. No runtime, engine, data, original specification, visibility or history changes. Details and pending privacy/license decisions: PUBLIC_READINESS_VI.md.

## 12 October 2026 — public static preview and tomorrow plan

Added KE_HOACH_TU_13_10_2026.md with prioritized owner tasks, V4, UI/UX, games/rules, hosting, daily Git workflow and a proposed seven-day plan. Added online-preview/ source mirror and tools/check_online_preview.py. A separate Sites deployment publishes only four selected static assets: two fixture exercises, reflection, explanation, retry, related fixture and local completion/review markers. Existing Python app and SQLite are unchanged. No server-side gate or online engine in this preview. Browser flow, persistence, mobile width and fixture integrity checked.


## Cập nhật ChatGPT Site V4 ngày 15 tháng 10 năm 2026

Bản public đã được nâng từ demo hai bài lên prototype trình duyệt có luật, chơi máy/hai người, review, 12 bài, resume, lịch ôn và tự đánh giá. Xem [báo cáo đầy đủ](BAO_CAO_CHATGPTSITE_V4_2026_10_15.md) để biết kiểm thử, phần thật/giới hạn và các mục V4 chưa làm. Ứng dụng Python local vẫn là triển khai riêng.
