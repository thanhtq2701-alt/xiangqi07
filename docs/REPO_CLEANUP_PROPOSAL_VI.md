# Đề xuất dọn repo — chỉ báo cáo

## Phạm vi và nguyên tắc

Đây là ảnh chụp các file Git đang theo dõi trong `var/`, `artifacts/` và
`deliverables/` tại nhánh làm việc hiện tại. Báo cáo không xóa, di chuyển,
đổi tên hay sửa nội dung trong ba thư mục đó. Dung lượng là byte của file
trong worktree tại thời điểm kiểm kê; số liệu có thể đổi nếu file được cập
nhật.

| Thư mục | File tracked | Dung lượng |
|---|---:|---:|
| `var/` | 581 | 111,948,945 B (106.76 MiB) |
| `artifacts/` | 8 | 673,654 B (0.64 MiB) |
| `deliverables/` | 49 | 14,858,692 B (14.17 MiB) |

Khuyến nghị bên dưới chỉ là đề xuất cho một đợt dọn riêng sau khi chủ repo
duyệt. “Archive” nghĩa là bảo toàn bản sao rồi mới cân nhắc đưa ra khỏi repo;
“bỏ khỏi Git” không đồng nghĩa xóa dữ liệu khỏi mọi nơi.

## `var/` — dữ liệu, nguồn lịch sử và đầu ra kiểm tra

Các hàng có dấu `/` cuối là nhóm prefix: số lượng và dung lượng gồm toàn bộ
file tracked ở bên dưới nhóm đó. Các file nằm ngay trong `var/` được liệt kê
riêng.

| Nhóm/file tracked | Số file | Byte | Đề xuất |
|---|---:|---:|---|
| `var/build_clean_web_package.py` | 1 | 8,859 | Archive như script lịch sử; không có tham chiếu runtime hiện tại |
| `var/co-chill-preview.tar.gz` | 1 | 7,619 | Archive bản preview cũ |
| `var/co-chill-sites-v5-2026-10-24.tar.gz` | 1 | 3,257,014 | Archive gói V5 cũ |
| `var/co-chill-uiux-v5.tar.gz` | 1 | 773,646 | Archive gói UI/UX cũ |
| `var/co-chill-v4-preview.tar.gz` | 1 | 32,318 | Archive preview V4 |
| `var/co-chill-web-source-gon/` | 24 | 1,016,634 | Archive bản source gọn lịch sử |
| `var/code-manual-2026-10-18/` | 154 | 40,951,488 | Archive nguyên trạng tài liệu/bản làm việc; rà quyền và trùng lặp trước |
| `var/finish_uiux_app.py` | 1 | 27,797 | Archive script chỉnh UI/UX một lần |
| `var/merge_v5_accounts.py` | 1 | 15,267 | Archive script migration V5; không chạy trên Production nếu chưa kiểm tra |
| `var/migration-2026-10-17/` | 25 | 3,596,430 | Archive bằng chứng và đầu vào migration cũ |
| `var/package-check-wl0iyom_/` | 55 | 3,878,609 | Giữ bản sao kiểm chứng cần thiết rồi đề xuất bỏ bản giải nén tạm khỏi Git |
| `var/questionnaire-2026-10-21/` | 144 | 13,119,339 | Archive nội dung câu hỏi/bản làm việc; không xóa nguồn gốc |
| `var/reading-guide-2026-10-20/` | 36 | 8,420,179 | Archive tài liệu đọc/bản làm việc |
| `var/review-v4/` | 6 | 589,734 | Archive ảnh/bằng chứng review cũ |
| `var/review-web-design/` | 13 | 2,008,327 | Archive bản review thiết kế cũ |
| `var/server-error.log` | 1 | 0 | Đề xuất bỏ log rỗng khỏi Git sau khi xác nhận không phải fixture |
| `var/server-output.log` | 1 | 60 | Đề xuất bỏ log sinh ra khỏi Git; chuyển log cần giữ sang nơi lưu phù hợp |
| `var/site-preview/` | 16 | 3,480,774 | Archive bản preview lịch sử |
| `var/uiux-review/` | 76 | 29,741,469 | Archive bản review UI/UX lịch sử |
| `var/update_uiux_app.py` | 1 | 23,238 | Archive script chỉnh UI/UX một lần |
| `var/v5-2026-10-23/` | 15 | 845,991 | Archive snapshot V5 |
| `var/v6/` | 3 | 133,431 | Giữ bằng chứng test hiện được `TEST_REPORT_CODEX.md` nêu; chuyển có kiểm soát trước khi bỏ khỏi Git |
| `var/v6_build_proof.cjs` | 1 | 3,197 | Archive script kiểm chứng build lịch sử nếu không còn được tái sử dụng |
| `var/v6_find_lines.cjs` | 1 | 2,259 | Archive script nghiên cứu lịch sử |
| `var/v6_found_lines.json` | 1 | 1,131 | Archive dữ liệu nghiên cứu lịch sử |
| `var/v6_line_exercises.json` | 1 | 14,135 | Giữ/archive như dữ liệu bài tập nghiên cứu; chưa thấy code runtime hiện tại tham chiếu trực tiếp |

### Các đường dẫn runtime cần giữ an toàn

**Không xóa hoặc `git rm` database đang chạy, database local, hay SQLite
sidecar trong lúc service có thể đang hoạt động.** Các đường dẫn dưới đây có
vai trò khác nhau; không có database chuẩn nào trong danh sách tracked ở trên.

| Đường dẫn | Dẫn chứng và cách dùng | Xử lý |
|---|---|---|
| Giá trị `CO_CHILL_DB_PATH` trong `/etc/cochill.env` — Production hiện trỏ tới `/var/www/html/var/co_chill_accounts.sqlite3` theo thông tin vận hành | `co_chill_server.py` dùng biến này khi tạo `CloudStore` và làm mặc định cho CLI (`co_chill_server.py:41,623`); `deploy/DEPLOY_GCP_VI.md` mô tả đường dẫn DB Production | Dữ liệu bền của người dùng; tuyệt đối không xóa/ghi đè. File env chứa secret, không đưa vào Git hoặc in ra |
| `var/co_chill_accounts.sqlite3` | Đường dẫn mặc định local trong `co_chill_server.py:41,623`; thư mục cha được tạo bởi `app/cloud_store.py:184` | Giữ DB nếu tồn tại; không đưa DB vào Git |
| `var/co_chill_accounts.sqlite3-wal` và `var/co_chill_accounts.sqlite3-shm` (hoặc cùng hậu tố cạnh đường dẫn DB do cấu hình) | `app/cloud_store.py:192` bật `journal_mode=WAL`; SQLite dùng các sidecar khi cần | Không xóa khi service/connection đang chạy; không coi là cache có thể xóa tùy ý |
| `var/chill.sqlite3` | Mặc định của `app/storage.py:17`; `tools/update_inventory.py:124` mở DB này chỉ đọc nếu có | Module storage này không được entry point V6 hiện tại import, nhưng tool kiểm kê còn đọc. Không xóa trước khi xác minh mọi workflow local đã ngừng dùng |
| `var/tests/` và các file tạm bên trong | Các test như `tests/test_cloud.py`, `tests/test_pikafish.py`, `tests/test_online_rooms.py`, `tests/test_online_http.py`, `tests/test_learning.py` tạo thư mục này và dùng `TemporaryDirectory` | Scratch của test, không phải DB Production; không dọn trong khi test đang chạy |

Chưa tìm thấy code ứng dụng hiện tại ghi upload/cache/lock dạng file vào
`var/`. SQLite là dữ liệu file bền. Engine có cache LRU trong bộ nhớ
(`app/engine.py:2,42`) và server có `Lock` trong bộ nhớ
(`co_chill_server.py:595,602`); không nhầm chúng với file có thể dọn. Kết luận
này chỉ áp dụng cho code đã rà trong repo, không thay thế kiểm tra cấu hình
hay dữ liệu thực trên VM.

`tools/update_inventory.py` duyệt cây dự án và phân loại `var/` là dữ liệu
local nhạy cảm (`tools/update_inventory.py:43,97`); nó không phải luồng ghi
runtime của ứng dụng. Báo cáo kiểm thử hiện nhắc bằng chứng local dưới
`var/v6/`. Các nhóm lịch sử còn lại không được entry point, test hoặc tool
hiện tại nêu đích danh; chúng vẫn có thể chứa tư liệu cần lưu trữ.

## `artifacts/` — ảnh và file UI/UX cũ

| File tracked | Byte | Dấu vết tham chiếu | Đề xuất |
|---|---:|---|---|
| `artifacts/co-chill-2026-10-09.png` | 135,026 | Không được app/test dùng | Archive ảnh lịch sử |
| `artifacts/co-chill-home.png` | 31,274 | Không được app/test dùng | Archive nếu còn giá trị so sánh |
| `artifacts/co-chill-public-live.png` | 190,298 | Không được app/test dùng | Archive ảnh kiểm tra cũ |
| `artifacts/co-chill-public-preview.png` | 191,042 | Không được app/test dùng | Archive ảnh preview |
| `artifacts/co-chill-uiux-v5-live.png` | 66,989 | Được nhắc trong báo cáo UI/UX lịch sử | Giữ cùng báo cáo hoặc archive cả cặp |
| `artifacts/co-chill-v4-live.png` | 52,874 | Không được app/test dùng | Archive ảnh V4 |
| `artifacts/improve_ui.py` | 3,074 | Không được code/test/tool hiện tại gọi | Archive script cũ; chuyển sang `tools/` chỉ nếu còn nhu cầu |
| `artifacts/polish.css` | 3,077 | Không được app hiện tại nạp | Archive stylesheet cũ |

`tools/update_inventory.py` có nhánh phân loại đường dẫn `artifacts/` là ảnh/
bằng chứng (`tools/update_inventory.py:47`), không phải consumer chạy ảnh.
Một số báo cáo lịch sử có nhắc hoặc dẫn ảnh; vì vậy nên giữ ảnh và tài liệu
liên quan cùng nhau trước khi cân nhắc bỏ khỏi Git.

## `deliverables/` — tài liệu và các gói nguồn cũ

| File/nhóm tracked | Số file | Byte | Đề xuất |
|---|---:|---:|---|
| `deliverables/CO_CHILL_HANDOFF_AND_PRODUCT_QUESTIONS_2026_10_27.txt` | 1 | 19,326 | Archive bàn giao/đầu vào lịch sử |
| `deliverables/CO_CHILL_SYSTEM_ISSUES_FIX_CYCLES_2026_10_27.txt` | 1 | 10,448 | Archive nhật ký xử lý lịch sử |
| `deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24.zip` | 1 | 3,255,480 | Archive; không phải gói deploy hiện tại |
| `deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24_SHA256.json` | 1 | 2,595 | Giữ cạnh ZIP tương ứng trong archive |
| `deliverables/Co_Chill_Giai_thich_tung_file_va_nhom_code_2026_10_18.docx` | 1 | 111,564 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_Huong_dan_review_va_update_2026_10_20.docx` | 1 | 58,014 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_So_tay_Code_VSCode_2026_10_17.docx` | 1 | 56,243 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_So_tay_hien_trang.html` | 1 | 51,728 | Giữ nếu còn chạy `tools/update_inventory.py`; tool hiện ghi file này (`tools/update_inventory.py:186`) |
| `deliverables/Co_Chill_V4_Bo_sung_UI_UX_Kien_truc_Luat.docx` | 1 | 60,402 | Archive; được script tạo tài liệu V4 ghi ra (`tools/create_v4_ui_supplement.py:11`) |
| `deliverables/Co_Chill_V4_Tien_do_va_Bo_sung_Thong_tin.docx` | 1 | 56,440 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_V5_Cap_nhat_Tai_khoan.docx` | 1 | 54,376 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_V5_Cau_hoi_hoan_thien.docx` | 1 | 51,446 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_V5_Source_2026_10_24.zip` | 1 | 3,399,587 | Archive; không thay thế source entry point hiện tại |
| `deliverables/Co_Chill_V5_Tong_hop_cau_hoi_phat_trien_2026_10_21.docx` | 1 | 259,668 | Archive tài liệu lịch sử |
| `deliverables/Co_Chill_VSCode_2026_10_17.zip` | 1 | 813,826 | Archive cùng thư mục giải nén bên dưới |
| `deliverables/Co_Chill_VSCode_2026_10_17/` | 29 | 1,039,124 | Archive source snapshot cũ; không dùng làm entry point |
| `deliverables/Co_Chill_Web_Source_Gon.zip` | 1 | 804,312 | Archive gói nguồn lịch sử |
| `deliverables/HUONG_DAN_CODE_VA_BAN_GIAO_CHAT_MOI.txt` | 1 | 36,379 | Archive tài liệu bàn giao |
| `deliverables/Lỗi typo.docx` | 1 | 1,256,315 | Archive/kiểm tra chủ sở hữu trước khi bỏ khỏi Git; không được app/test hiện tại tham chiếu |
| `deliverables/xiangqi-ai_V6_2026-10-26.sha256.txt` | 1 | 96 | Giữ cùng ZIP V6 cho đến khi phát hành gói thay thế |
| `deliverables/xiangqi-ai_V6_2026-10-26.zip` | 1 | 3,461,323 | Giữ như bản phát hành V6 đã ghi nhận; không ghi đè |

Các file trong bảng là 20 file độc lập và 29 file thuộc source snapshot, tổng
cộng 48 file. Không thấy ứng dụng hoặc test runtime đọc các deliverable này.
README hướng dẫn tạo gói mới trong `deliverables/`; builder nhận đường dẫn
output do người chạy chọn (`README.md:68-69`,
`tools/build_deploy_pack.py:103`). Các tài liệu kiểm kê cũ liệt kê file trong
thư mục, nhưng điều đó không làm chúng thành dependency runtime.

## Dẫn chứng và hậu quả khi triển khai

- Database Production được cấu hình ngoài repo qua `/etc/cochill.env`; script
  deploy chỉ lấy đúng `CO_CHILL_DB_PATH`, sao lưu trước fetch và không tự
  restore DB. Secret không được đưa vào báo cáo này.
- `git pull` chỉ cập nhật working tree theo commit mới. Nếu commit tương lai
  chứa `git rm` một file tracked trong các nhóm trên, Git sẽ xóa file đó khỏi
  `/var/www/html` khi cập nhật thành công. Nếu file tracked đang sửa tại VM,
  pull có thể bị từ chối; không dựa vào đó như cơ chế lưu trữ.
- File untracked/ignored thường không bị Git pull xóa, nhưng có thể gây xung
  đột nếu trùng đường dẫn với file mới được thêm vào Git. Backup database
  không phải backup thay thế cho ảnh, tài liệu hay archive.
- Trước một đợt dọn thật: tạo và xác minh bản archive ngoài working tree,
  rà references lần cuối, đề xuất danh sách `git rm` riêng, kiểm tra kế hoạch
  trên bản clone/VM thử, rồi mới xin duyệt Production. Báo cáo này không thực
  hiện bước nào trong số đó.
