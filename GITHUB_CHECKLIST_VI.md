# Cờ Chill — toàn bộ checklist đưa lên GitHub và commit hằng ngày

Ngày lập: **12/10/2026 (Asia/Bangkok)**. Đây là hướng dẫn thao tác và danh mục bàn giao, không phải xác nhận đã push.

**Cập nhật sau lần push đầu:** đã nối `origin` với `https://github.com/thanhtq2701-alt/xiangqi07.git`, đẩy 7 commit đến `1eec2db`, xác nhận mã local/remote trùng nhau và nhánh mặc định `codex-full`. Bạn đã hoàn thành bước 5; từ nay dùng mục 6 cho công việc hằng ngày. Các dòng “chưa có remote” bên dưới mô tả snapshot trước lần push đầu, không phải trạng thái hiện tại. Không chạy lại `remote add` hoặc tạo repo mới. Chuẩn bị Public được ghi trong `PUBLIC_READINESS_VI.md`; chưa đổi visibility.

## 1. Trạng thái đã kiểm tra

- Thư mục đúng: `E:\ThanhTQ\App cờ tướng\xiangqi-ai`. Chỉ dùng thư mục này làm repo, không lấy cả thư mục cha `App cờ tướng`.
- Đã có Git, phiên bản 2.52.0.windows.1; không cần `git init` lại.
- Nhánh đang dùng: `codex-full`; 6 commit trước lần bổ sung checklist này. Commit nền gần nhất: `aa78421` (launcher Windows).
- Chưa có remote GitHub. Chưa xác minh tài khoản GitHub/đăng nhập của bạn. Không thấy GitHub CLI `gh` trong PATH; hướng dẫn chính chỉ cần Git.
- Working tree sạch trước thay đổi tài liệu này. Không có file `var/`, `artifacts/`, `docs/materials/` đang được Git theo dõi. Kiểm tra lịch sử đường dẫn `.env` và `var` không có kết quả.
- Quét mẫu token/private key phổ biến trong file văn bản hiện tại không thấy kết quả. Đây không phải kiểm toán đầy đủ lịch sử Git hoặc nội dung nhị phân Word.
- Tài liệu kiểm thử trước đây ghi 72 test đạt; không chạy lại bộ test trong lần tạo checklist. Launcher đã được kiểm tra khởi động/dùng lại và HTTP 200 ngày 12/10.

## 2. Bạn cần chuẩn bị gì ngay hôm nay

- [ ] Tài khoản GitHub của chính bạn và quyền tạo repository.
- [ ] Tên repo đề xuất: `xiangqi-ai` hoặc `co-chill`.
- [ ] Chọn **Private** cho lần đầu. Repo có đặc tả, câu hỏi Word, thông tin tác giả và inventory đường dẫn máy. Nếu muốn Public, rà soát cả lịch sử và Word trước khi đổi.
- [ ] Email dùng cho commit: email đã xác minh trên GitHub hoặc địa chỉ noreply mà GitHub cung cấp trong Settings → Emails. Không tự đoán địa chỉ noreply.
- [ ] URL repo thực tế, dạng `https://github.com/TEN_TAI_KHOAN/TEN_REPO.git`.
- [ ] Đăng nhập bằng luồng trình duyệt của Git Credential Manager nếu Git yêu cầu. Không gửi mật khẩu/token vào chat, không nhúng token vào URL.
- [ ] Chưa cần domain, hosting, API key, database cloud, thanh toán hay đổi framework để push code.

## 3. Những gì cần đưa lên

| Nhóm | File/thư mục | Mục đích |
|---|---|---|
| Server | `server.py` | HTTP API và phục vụ web local |
| Logic | `app/` | Luật cờ, engine local, học, dữ liệu và persistence |
| Giao diện | `web/` | HTML, CSS, JavaScript, favicon |
| Kiểm thử | `tests/` | Luật, học, HTTP và tính toàn vẹn |
| Mở web | `Mo_Co_Chill.cmd`, `tools/start_local.ps1` | Bật server nền trên Windows |
| Hướng dẫn | `README.md`, `RUN_AND_DEMO_CODEX.md` | Cài/chạy và demo |
| Báo cáo | `IMPLEMENTATION_REPORT_CODEX.md`, `TEST_REPORT_CODEX.md`, `KNOWN_LIMITATIONS.md`, `AI_USAGE.md` | Thực trạng, test và giới hạn |
| Quy tắc | `AGENTS.md`, `.gitignore`, `PRIVACY.md`, `THIRD_PARTY_NOTICES.md` | Quy tắc phát triển, riêng tư và nguồn |
| Đặc tả | `docs/spec/` | 18 tài liệu Final Pack gốc; không tự sửa yêu cầu |
| Nguồn bài | `data/sources.csv` | Ghi nguồn/quyền sử dụng; bài tổng hợp nằm trong code |
| Bộ nhớ dự án | `PROJECT_MEMORY_VI.md`, `PROJECT_INVENTORY_VI.md`, `inventory/`, `DEVELOPMENT_JOURNAL.md` | Theo dõi tiến độ và kiểm kê |
| Tài liệu V4 | `deliverables/`, `docs/V4_BO_SUNG_UI_UX_KIEN_TRUC_LUAT.md` | Hai Word câu hỏi và sổ tay HTML; chưa coi là câu trả lời đã chốt |
| Công cụ tài liệu | `tools/create_v4_document.py`, `tools/create_v4_ui_supplement.py`, `tools/update_inventory.py` | Tái tạo tài liệu/kiểm kê, không cần để chạy game |
| Tham khảo | `RESEARCH_AND_IMPROVEMENTS_2026_10_09.md`, `BEGINNER_LEARNING_GUIDE_CODEX.md` | Khảo sát và kiến thức cần học |
| Checklist này | `GITHUB_CHECKLIST_VI.md` | Hướng dẫn push và làm việc mỗi ngày |

Ứng dụng chạy bằng Python standard library; không cần tự tạo `package.json`, `requirements.txt` hay thư mục `node_modules` để đủ bộ. Công cụ tạo Word cần thư viện riêng; đó không phải dependency của server.

## 4. Những gì KHÔNG đưa lên repo

- `var/`: SQLite chứa tiến độ, suy nghĩ, phiên khách, log. GitHub lưu code không đồng nghĩa sao lưu dữ liệu học. Nếu cần giữ tiến độ, sao lưu riêng file SQLite khi server đã dừng và giữ cookie trình duyệt.
- `.env`, `.env.*`, mật khẩu, access token, SSH private key, credential và cookie xuất ra.
- Cache `__pycache__/`, `*.pyc`, `.venv/`, `node_modules/`.
- `artifacts/`: ảnh kiểm thử cục bộ có thể chứa dữ liệu học.
- `docs/materials/`, `Answer V3.docx`, `Codex.docx`, `XiangqiAI_V3_Final_Pack.zip`: bản gốc đang được giữ local và ignore. Đặc tả cần dùng đã có trong `docs/spec/`; không cần đẩy ZIP để app chạy.
- File Word tạm `~$...`, database `*.sqlite3`, WAL/SHM. Đã bổ sung ignore dự phòng trong lần này.
- Thư mục `.git` không tải lên bằng giao diện upload file; lệnh `git push` tự truyền lịch sử cần thiết.

Hai Word trong `deliverables/` được cho phép theo dõi. Khi điền câu trả lời cá nhân vào chúng, phải xem lại trước commit. `.gitignore` không xóa file đã từng commit; nếu lỡ commit secret, cần thu hồi secret và xử lý lịch sử riêng, không chỉ xóa file ở commit sau.

## 5. Đẩy lần đầu — thực hiện theo thứ tự

### Bước A — tạo repo rỗng trên GitHub

Đăng nhập GitHub → New repository → đặt tên → **Private** → không tạo thêm README, .gitignore hoặc LICENSE → Create repository. Repo local đã có README và lịch sử. Chưa chọn giấy phép phát hành công khai; không tự thêm MIT/GPL khi chưa quyết định.

### Bước B — mở PowerShell đúng thư mục và kiểm tra danh tính

```powershell
cd "E:\ThanhTQ\App cờ tướng\xiangqi-ai"
git status
git branch --show-current
git log -6 --oneline
git config user.name
git config user.email
```

Nếu tên/email chưa đúng, thay hai giá trị mẫu sau rồi chạy. Cấu hình này chỉ áp dụng repo hiện tại:

```powershell
git config user.name "TEN_HIEN_THI_CUA_BAN"
git config user.email "EMAIL_DA_XAC_MINH_HOAC_NOREPLY_CUA_BAN"
```

Đổi cấu hình không thay tác giả/email commit cũ. Nếu cần bảo vệ email lịch sử, kiểm tra trước khi Public; không sửa lịch sử chỉ để làm đẹp biểu đồ đóng góp.

### Bước C — kiểm tra và commit thay đổi còn lại, nếu có

```powershell
git status --short
git diff --stat
git diff --check
```

Nếu sạch thì bỏ qua commit. Nếu có thay đổi, chỉ stage file bạn đã xem; không chạy `git add .` một cách mù quáng. Ví dụ nếu checklist chưa được commit:

```powershell
git add GITHUB_CHECKLIST_VI.md .gitignore
git diff --cached --stat
git diff --cached
git commit -m "docs: prepare GitHub handoff and daily workflow"
```

### Bước D — nối remote và push

Thay `TEN_TAI_KHOAN` và `TEN_REPO` bằng giá trị thật. Những lệnh này dành cho repo GitHub **rỗng**:

```powershell
git remote -v
git remote add origin https://github.com/TEN_TAI_KHOAN/TEN_REPO.git
git remote -v
git push -u origin codex-full
```

Giữ nhánh hiện tại để không đổi quy trình đang chạy. Sau push, kiểm tra Settings → Branches/Default branch trên GitHub và chọn `codex-full` làm nhánh mặc định nếu chưa đúng. Không bắt buộc nhánh phải tên `main`.

Nếu `origin` đã tồn tại, không chạy lại `remote add`; kiểm tra URL. Chỉ khi xác nhận URL cũ sai mới dùng `git remote set-url origin URL_DUNG`. Nếu repo đích đã có commit, dừng quy trình repo rỗng này và đối chiếu lịch sử; không force-push hoặc tự gộp lịch sử không liên quan.

### Bước E — xác nhận đã lên đúng

```powershell
git status -sb
git rev-parse HEAD
git ls-remote origin refs/heads/codex-full
```

Hai mã commit cuối cần trùng nhau. Mở GitHub và kiểm tra README, server.py, app, web, tests và lịch sử commit. Kiểm tra không có var, .env hoặc file Word tạm. Nếu chỉ thấy một ZIP thì chưa đẩy source đúng cách.

## 6. Commit mỗi ngày từ 12/10/2026

**Đầu buổi**, sau khi đã nối remote và working tree sạch:

```powershell
git status -sb
git pull --ff-only
```

Nếu có thay đổi chưa commit hoặc báo diverged/conflict, đọc thông báo và xử lý trước, không dùng reset --hard/force để vượt lỗi.

**Trong buổi:** sửa từng việc có ý nghĩa; ghi việc làm thật, test thật và việc còn thiếu trong `DEVELOPMENT_JOURNAL.md`. Cập nhật README khi cách chạy đổi, báo cáo/giới hạn khi hành vi đổi. Commit theo nhóm logic, không cần dồn mọi thứ cuối ngày.

**Trước commit code**, chạy kiểm tra tương ứng:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app server.py tests
git diff --check
```

Nếu thay frontend và có Node hiện đại: `node --check web/app.js`. Không dùng Node cổ chỉ vì máy có sẵn. Với tài liệu thuần, kiểm tra nội dung/link/diff; không cần tuyên bố chạy lại test game nếu chưa chạy. Chạy demo phản tư → xem giải thích → thử lại → bài liên quan → tiến độ khi thay core flow.

Cập nhật inventory khi cấu trúc/tính năng có thay đổi: `python tools/update_inventory.py`. Tool quét cả thư mục cha để ghi danh mục, nên xem lại metadata trước push; không cần chạy mỗi commit nhỏ.

**Cuối mỗi nhóm việc**, dùng đường dẫn file thật thay ví dụ:

```powershell
git status --short
git diff
git add README.md DEVELOPMENT_JOURNAL.md
git diff --cached --stat
git diff --cached
git commit -m "docs: record verified progress for 2026-10-12"
git push
git status -sb
```

Ví dụ message khác: `fix: preserve reflection draft on reload`, `feat: add related exercise filter`, `test: cover cannon capture edge case`. Không backdate hoặc tạo commit rỗng để giả tiến độ. Push hôm nay giữ nguyên ngày của các commit cũ; biểu đồ đóng góp phụ thuộc email liên kết và nhánh mặc định, không chỉ số lần push.

Mẫu nhật ký mỗi ngày:

```text
Ngày:
Mục tiêu:
Thực sự đã làm:
File/nhóm thay đổi:
Lệnh kiểm tra và kết quả:
Lỗi/giới hạn còn lại:
Việc tiếp theo:
Commit/PR liên quan:
```

## 7. Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| Nothing to commit | Không có thay đổi mới; push commit đã có nếu chưa push |
| Remote origin already exists | Xem git remote -v; chỉ đổi URL khi xác nhận sai |
| Repository not found / 403 | Kiểm tra tài khoản, URL, quyền repo; đăng nhập đúng tài khoản |
| Authentication failed | Dùng luồng đăng nhập Git Credential Manager; không dùng mật khẩu GitHub như token |
| Non-fast-forward | Fetch và xem lịch sử; không force push; repo mới nên rỗng |
| Git không nhận danh tính | Cấu hình user.name/user.email local ở bước B |
| File đáng lẽ ignore vẫn hiện staged | Dừng commit, kiểm tra file có được theo dõi từ trước không; .gitignore không tác động hồi tố |
| Web GitHub Pages chỉ hiện HTML/lỗi API | Pages không chạy server Python/SQLite; cần triển khai backend riêng |
| Web 127.0.0.1 không mở | Chạy Mo_Co_Chill.cmd; push GitHub không bật server local |

## 8. GitHub không thay thế hosting hoặc backup dữ liệu

Push repo giúp lưu code/lịch sử và cộng tác. Website hiện tại vẫn chạy local bằng `Mo_Co_Chill.cmd` hoặc `python server.py --port 8765`. GitHub Pages phục vụ web tĩnh, không chạy Python server của dự án. Muốn chia sẻ một URL app chạy thật là công việc triển khai riêng: cần host backend, lưu trữ bền vững, HTTPS, cấu hình và rà soát quyền truy cập. Không đổi server sang public chỉ để đẩy code.

Không cần thêm paid LLM, auth sản xuất hay dataset lớn để hoàn thành bước GitHub hôm nay. CI GitHub Actions là cải tiến tiếp theo có thể thêm sau; hiện chưa cấu hình hay tuyên bố CI đã đạt.

## 9. Nguồn hướng dẫn chính thức đã đối chiếu

- GitHub, đưa repository local lên GitHub: https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
- GitHub Pages là hosting tĩnh: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- Pages không hỗ trợ server-side Python: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site

## 10. Danh sách file Git theo dõi tại thời điểm chuẩn bị

Danh sách bên dưới là source và tài liệu cần được push cùng lịch sử. Có thể xem danh sách sống bằng `git ls-files`. Checklist này và thay đổi .gitignore sẽ nằm trong commit chuẩn bị GitHub.

```text
.gitignore
AGENTS.md
AI_USAGE.md
BEGINNER_LEARNING_GUIDE_CODEX.md
DEVELOPMENT_JOURNAL.md
IMPLEMENTATION_REPORT_CODEX.md
KNOWN_LIMITATIONS.md
Mo_Co_Chill.cmd
PRIVACY.md
PROJECT_INVENTORY_VI.md
PROJECT_MEMORY_VI.md
README.md
RESEARCH_AND_IMPROVEMENTS_2026_10_09.md
RUN_AND_DEMO_CODEX.md
TEST_REPORT_CODEX.md
THIRD_PARTY_NOTICES.md
app/__init__.py
app/engine.py
app/learning.py
app/puzzles.py
app/rules.py
app/service.py
app/storage.py
data/sources.csv
deliverables/Co_Chill_So_tay_hien_trang.html
deliverables/Co_Chill_V4_Bo_sung_UI_UX_Kien_truc_Luat.docx
deliverables/Co_Chill_V4_Tien_do_va_Bo_sung_Thong_tin.docx
docs/V4_BO_SUNG_UI_UX_KIEN_TRUC_LUAT.md
docs/spec/00_START_HERE.md
docs/spec/01_PRODUCT_SPEC.md
docs/spec/02_FEEDBACK_AND_CORRECTIONS.md
docs/spec/03_ARCHITECTURE.md
docs/spec/04_PROTOTYPE_7_DAY.md
docs/spec/05_MILESTONES.md
docs/spec/06_ROADMAP.md
docs/spec/07_LEARNING_MODEL_SPACED_REPETITION.md
docs/spec/08_AI_ML_PLAN.md
docs/spec/09_DATA_LICENSE_SOURCES.md
docs/spec/10_README_VI_DRAFT.md
docs/spec/11_DAILY_UPDATE_TEMPLATE.md
docs/spec/12_SETUP_CHECKLIST.md
docs/spec/13_CLAUDE_TRACK.md
docs/spec/14_CODEX_TRACK.md
docs/spec/15_PARALLEL_COMPARISON_SCORECARD.md
docs/spec/16_FUTURE_FEATURE_BACKLOG.md
docs/spec/17_ACTION_ITEMS_BEFORE_CODE.md
inventory/VERIFICATION_VI.md
inventory/manifest.json
server.py
tests/__init__.py
tests/test_http.py
tests/test_learning.py
tests/test_rules.py
tools/create_v4_document.py
tools/create_v4_ui_supplement.py
tools/start_local.ps1
tools/update_inventory.py
web/app.js
web/favicon.svg
web/index.html
web/style.css
GITHUB_CHECKLIST_VI.md
```
