# Kiểm thử bản code V5 — 24/10/2026

**Phát hành frontend sau đợt test:** native Sites xác nhận phiên bản 4 thành công. Không thay backend; không có lượt browser QA mới. [Bằng chứng và phạm vi phát hành](docs/SITES_V5_RELEASE_2026_10_24.md).

**Kết quả chốt: 110/110 kiểm thử Python và 101/101 kiểm thử JavaScript đạt.** Đây là kiểm thử code local, không phải chứng nhận production, sức mạnh Pikafish hoặc hiệu quả học tập. Môi trường: Windows, Python 3.12.14 và Node trong runtime đi kèm; dữ liệu thử tách khỏi dữ liệu người dùng.

## Kết quả chạy thực tế

| Lệnh/nhóm | Kết quả |
|---|---|
| `python -m unittest discover -s tests -v` | 110 đạt, 139.067 giây: 72 kiểm thử legacy, 21 account/content/cloud, 17 adapter Pikafish |
| `node tools/test_cloud_client.cjs` | 21 đạt |
| `node tools/test_engine_client.cjs` | 10 đạt |
| `node tools/test_preview_learning.cjs` | 26 đạt |
| `node tools/test_preview_experience.cjs` | 20 đạt |
| `node tools/test_preview_game_tools.cjs` | 14 đạt, gồm 4.054 vòng ký phổ/nước đi hợp lệ |
| `node tools/test_v5_ui.cjs` | 10 đạt |
| `python tools/check_browser_rules.py --node PATH_TO_NODE` | 205 thế, 5.468 thế con, 25 ca FEN, perft độ sâu 2 = 1.920, 10 nhóm đầu vào sai; engine 12 thế/153 biến: PASS |
| `python tools/check_online_preview.py` | 12 bài tổng hợp, lời giải mẫu, provenance và đầy đủ tập nước hợp lệ khớp code luật |
| `python -m compileall -q app co_chill_server.py server.py tests` | Qua |
| `node --check` cho 9 file JavaScript trong `online-preview/` | Qua; `v5-ui.js` kiểm tra lại sau bản sửa cuối |
| `git diff --check` | Qua; chỉ thông báo chuyển LF/CRLF của Git |

Đã bật `python co_chill_server.py serve --port 8769` và đọc HTTP thật: `/api/health`, `/api/session`, `/`, `app.js`, `v5-ui.js`, `cloud-client.js`, `engine-client.js`, `v5.css`, `cover-co-chill.png` đều trả **200**, MIME đúng. Đây là kiểm tra phục vụ trang/tài nguyên, không thay thế việc thao tác mọi màn hình.

Các lệnh dùng `python`/`node` trên đây được chạy bằng đường dẫn runtime tương ứng khi chúng chưa có trên PATH. Kiểm thử HTTP và đọc localhost ban đầu bị Windows chặn socket trong môi trường hạn quyền (`WinError 10013`); đã chạy lại với quyền được cấp và đạt, không bỏ hoặc làm yếu test. Không có TypeScript, external linter hay bundler được cấu hình; không báo giả rằng typecheck/lint/build đã chạy. Vercel static không cần bước biên dịch.

## Các hành vi quan trọng được kiểm tra

- Luật các quân, chiếu/hết nước, tính toàn vẹn ván, nhập nước sai không làm hỏng lịch sử; browser/Python khớp trên bộ thế nêu trên. Sự khớp này không thay thế trọng tài độc lập về luật giải đấu.
- Phản ánh bắt buộc trước giải; bỏ trống không ghi lượt; ba lần chưa đúng tạm dừng sang ngày sau; lượt có hỗ trợ không thành độc lập; lịch ôn từ lúc hoàn thành; giữ bước bài liên quan khi reload.
- Password hash và nâng cấp hash cũ, TOTP/chống dùng lại mã, session hết hạn/đăng nhập mới, CSRF/origin/Host, kích thước JSON, giới hạn tần suất, phân quyền và rollback.
- Đồng bộ theo revision, xung đột, hai tài khoản tách cache, phiên cũ không hồi sinh từ request trễ; tùy chọn giao diện được khôi phục và không kế thừa nhầm tài khoản trước.
- Xuất dữ liệu giữ câu trả lời/lịch sử/lịch ôn nhưng bỏ khóa đáp án nội bộ; xóa tài khoản thật; report không thấy feedback riêng hoặc nháp bài; backup có thể mở để khôi phục dữ liệu thử.
- Bài nháp → xuất bản → sửa → duyệt lại → gỡ; phiên bản cũ không được âm thầm xuất bản/ghi đè. Đổi FEN hoặc nước mẫu bỏ biến minh họa cũ nếu không gửi biến thay thế; biến cung cấp sai bị từ chối.
- Adapter UCI giới hạn timeout/output, dọn process con, kiểm tra PV hợp lệ, score đúng góc nhìn/đơn vị, không trộn cp và mate hoặc coi bound là điểm chính xác. **17 bài adapter dùng engine UCI giả lập do test tạo, không phải Pikafish thật.**

## Kiểm tra giao diện và giới hạn bằng chứng

Trong lượt kiểm tra trình duyệt trước của cùng đợt V5: đã tạo tài khoản thử trên database QA riêng; đi qua ba câu phản ánh → chọn nước a2a7 → lời giải → retry → bài liên quan; trạng thái đồng bộ và bước bài liên quan giữ sau reload. Đã quan sát Home/cover ở panel hẹp. Không ghi nhận lỗi/warning console ở lượt đó. Các tài khoản và lượt này không phải người dùng thật hoặc chứng cứ tác động.

Lượt cuối, công cụ Computer Use tự dừng vì không xác định chắc URL trình duyệt để thực thi chính sách. Đã dừng thao tác UI; không tuyên bố đã chạy lại tất cả màn hình sau bản sửa cuối. Những sửa cuối có kiểm thử tự động nêu trên. Chưa thử nhấp đúp launcher mới, admin/content end-to-end bằng UI, mọi thiết bị di động, HTTPS trên hosting, Vercel/Render thực tế, sức tải hoặc binary/NNUE thật. Cần nghiệm thu các phần đó trên môi trường deploy trước khi mở pilot.

Không deploy, push GitHub, thay site cũ hoặc tạo dịch vụ trả phí trong đợt chốt này. Xem [báo cáo triển khai](IMPLEMENTATION_REPORT_CODEX.md) và [hướng dẫn deploy](docs/DEPLOY_V5.md).

---

# Lịch sử kiểm thử — các kết quả bên dưới thuộc bản/ngày trước

# Kiểm thử phát hành UI UX ngày 16/10/2026

- Python unittest: 72/72 qua, 43.521 giây; chạy lại ngoài sandbox sau lỗi quyền HTTP socket, không sửa yếu kiểm thử.
- Browser learning state: 19/19; experience/app handlers: 18/18; notation/rule extensions: 14/14. Tổng 51 kiểm thử Node qua.
- Browser/Python parity: 205 thế, 5.468 thế con; perft 2 = 1.920; 25 FEN, 10 nhóm lỗi; engine 12 thế/153 biến.
- Fixture validation: 12/12. JavaScript syntax qua; static package Sites thành công.
- Manual: phản hồi trước đáp án, trợ giúp có chờ quan sát, retry, bài liên quan, tự đánh giá, tiến độ; timed local game/ký phổ/lật bàn/xin thua; nhập ván và phân tích; theme tối/chữ lớn/quân Việt; laptop 1366×900 và mobile 390×844 không tràn ngang. Không có console error ghi nhận. Public Site v3 mở được với UI mới.

Xem [báo cáo](BAO_CAO_UIUX_V5_2026_10_16.md) để biết lệnh, giới hạn và các lỗi hiển thị còn lại. Những kết quả bên dưới thuộc các lượt trước.

# Test report

## Latest update 9 October 2026

`python -m unittest discover -s tests -v`: **72 passed in 64.517 seconds**, outside sandbox for localhost access. Seven new tests cover draft persistence without answer reveal/scoring, ownership and validation, late autosave after submission, unfinished practice resume/completion, draft export/delete, required HTTP fields and HTTP draft/resume gating. Existing 65 tests unchanged except additions. Python compileall and bundled Node syntax check pass.

Browser: draft saved, navigation home showed resume, reload restored text without answer, Vietnamese pieces preserved reflection, keyboard selected a2 and moved to a7, related b3g3 solved, progress persisted. Viewport 390×844 measured client/scroll widths 375/375 on home and exercise; board about 329 px. Initial viewport attempt affected another tab; final measurements were from the visible mobile test tab. Error/warning logs empty at final check. Screenshot: artifacts/co-chill-2026-10-09.png. Not a full accessibility audit or real learner study.

## Original handoff evidence

Date: 8 October 2026. Environment: Windows, Python 3.14, bundled modern Node for syntax verification.

Final command `python -m unittest discover -s tests -v`: **65 passed, 39.380 seconds**. No failing tests were deleted or weakened.

Coverage includes all seven pieces, horse legs in eight directions, elephant eyes/river, exact cannon screens, general palace, flying general, self-check, pawn direction/crossing, capture, invalid FEN/moves, state immutability, checkmate and stalemate loss. Initial move count 44 and depth-2 perft 1920 pass.

Engine coverage: all 12 puzzle solutions checked; 20 successive bot positions with legal moves and PV replay; timeout legal fallback; cache; invalid line rejection. Local self-consistency is not independent expert validation.

Learning coverage: full demo → reflection → retry → unseen related exercise → schedule → dashboard; required fields; pre-reflection hint/attempt rejection; idempotent retries/review; failed first attempt retained; hint assistance; no false mistake required; due queue; guest ownership; local export/delete; persistence after repository reopen; atomic invalid import; provider failure/invention fallback.

HTTP coverage: all public assets, security headers, secret/source/database path denial, Host/Origin checks, cookie flags, cross-guest record rejection, full reflection/retry flow and export answer gate, invalid request responses.

Additional checks: Python compileall passed; modern Node `--check web/app.js` passed; Git diff whitespace check passed. No framework build, TypeScript typecheck or external linter is configured; these were not represented as passing.

Manual browser smoke: demo loaded, history visible; critical moment had no answer before reflection; three answers saved; explanation shown; a2a7 retried; related h2h7 exercise solved after its own reflection; dashboard showed two first attempts, one independent transfer success and a 14-day skill schedule; reload preserved records. A final new bot game accepted b0c2 and returned a legal Black reply. Layout inspected at desktop, narrow panel and a phone-sized viewport; document scrollWidth equaled clientWidth (375 px), with no horizontal overflow. Browser error/warning log was empty at the final check. No public users or impact metrics inferred.

Failures diagnosed during development:

- Black pawn on an impossible pre-river odd file: corrected synthetic fixture before delivery.
- Three rules-test fixtures were misconstructed (own piece on intended horse destination; spare pawn preventing stalemate; undefended checking pawn). Corrected setup while preserving the intended assertions.
- SQLite `with connection` commits but does not close: introduced ClosingConnection to fix Windows file handles.
- Sandbox blocked temporary SQLite locations and loopback sockets: tests use workspace temp directory; HTTP checks run with approved outside-sandbox permission.
- In-app browser could not reach the initial sandbox server: restarted loopback server outside sandbox on 8765; browser flow then passed.

V4 document checks: valid DOCX ZIP/XML, 84 unique A01–N06 questions, 12 prioritized P0 IDs and all intended sections. Rendering attempted twice; runtime lacks LibreOffice. No page-by-page visual verification or rendered-page count claimed.

12 October 2026 launcher validation: Windows PowerShell `tools/start_local.ps1 -NoBrowser` started the server successfully and exited 0; a second invocation reused it and exited 0; subsequent GET `/` returned HTTP 200. `git diff --check` passed. Browser auto-opening, Windows reboot and actual ChatGPT closure were not exercised. Earlier 72-test suite results remain historical; game logic is unchanged by this launcher-only update.

## 12 October 2026 — public-readiness recheck

72/72 tests passed in 42.073s. Python compileall and modern Node --check web/app.js passed. Documentation-only changes; no fresh browser demo claimed. Historical blob scan and its limits are recorded in PUBLIC_READINESS_VI.md.

12 October 2026 public preview: both guided fixtures completed in browser; progress 2/2 survived reload, explanation hidden before new reflection; viewport 390x844 measured client/scroll width 375/375. No browser console errors observed. Modern Node syntax passed; python tools/check_online_preview.py verifies exported positions, both solutions and complete legal-move sets against app/rules.py. Full local 72-test suite was passed earlier today; local runtime is unchanged.


## Cập nhật ChatGPT Site V4 ngày 15 tháng 10 năm 2026

Bản public đã được nâng từ demo hai bài lên prototype trình duyệt có luật, chơi máy/hai người, review, 12 bài, resume, lịch ôn và tự đánh giá. Xem [báo cáo đầy đủ](BAO_CAO_CHATGPTSITE_V4_2026_10_15.md) để biết kiểm thử, phần thật/giới hạn và các mục V4 chưa làm. Ứng dụng Python local vẫn là triển khai riêng.
