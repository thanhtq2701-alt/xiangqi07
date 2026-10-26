# Cờ Chill — báo cáo chuẩn bị công khai

> **Báo cáo lịch sử ngày 12/10/2026, không phải trạng thái phát hành V6.**
> Dùng [README](README.md), [TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md),
> [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) và
> [GITHUB_CHECKLIST_VI.md](GITHUB_CHECKLIST_VI.md) để biết hướng dẫn/trạng thái
> hiện hành. Các lệnh và kết quả bên dưới chỉ ghi bằng chứng của snapshot này.

Đối chiếu **12/10/2026**, từ commit nền `1eec2db`. Chủ dự án đã chọn: **chuẩn bị chỉn chu, báo cáo trước, quyết định Public sau**. Không thay visibility, triển khai hosting hoặc viết lại lịch sử trong đợt này.

## Khi nào có thể Public?

Có thể công khai source dưới nhãn **prototype** sau khi chủ dự án duyệt thông tin được công bố. Không cần chờ hoàn thiện tất cả tính năng. Tuy nhiên, hiện chưa đủ cơ sở quảng bá thành dịch vụ học cờ hoàn chỉnh đã được kiểm chứng.

| Mốc | Hiện trạng | Việc tiếp theo |
| --- | --- | --- |
| Repo dễ đọc và chạy | Có quick start, launcher, demo, kiến trúc, test và giới hạn | Đọc bản giới thiệu mới |
| Thông tin có thể công khai | Đã quét mẫu secret và đường dẫn dữ liệu trong lịch sử | Duyệt email, tên tác giả, inventory, đặc tả và Word |
| Công khai source | Chưa thay visibility | Chủ dự án quyết định sau báo cáo |
| Giấy phép | Chưa chọn LICENSE | Chốt quyền sử dụng trước khi giới thiệu là mã nguồn mở cho phép tái sử dụng |
| Website online | Chưa triển khai | Hosting/backend, HTTPS, persistence và quyền truy cập là công việc riêng |
| Sản phẩm hoàn thiện | Engine nông, bài tổng hợp, lời giải template | Chốt V4, duyệt nội dung và cải tiến trải nghiệm |

## Đã chỉnh những gì

1. README: trạng thái trung thực, bảng công nghệ, lệnh clone đúng repo, bỏ đường dẫn máy cá nhân khỏi quick start, sơ đồ thư mục và đường dẫn đọc tiếp.
2. Thêm CONTRIBUTING.md: quy trình sửa, test, báo lỗi và nguyên tắc bảo vệ vòng học.
3. Cập nhật checklist GitHub và sổ tay: đã push, không chạy lại bước tạo remote; phân biệt snapshot cũ và trạng thái mới.
4. Bổ sung launcher trong hướng dẫn chạy, sửa mục nhật ký bị đặt sai vị trí.
5. Chạy lại test và kiểm tra cú pháp; quét blob lịch sử Git, gồm XML của hai Word.
6. Lập báo cáo này để bạn quyết định công khai dựa trên bằng chứng.

Đây là đợt chỉnh **repo và tài liệu bàn giao**. Chưa thiết kế lại toàn bộ UI, thay engine, hoàn thành V4 hay cài CI. Không tự suy đoán câu trả lời V4 còn chờ.

## Kiểm tra thực tế

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m unittest discover -s tests -v` | 72/72 đạt, 42.073 giây trên Windows; gồm luật, HTTP, reflection gating, draft, review, scheduling, recommendation, persistence |
| `python -m compileall -q app server.py tests` | Đạt |
| Node hiện đại `--check web/app.js` | Đạt; dùng runtime đi kèm môi trường phát triển |
| Lịch sử Git trước đợt này | 97 blob đã quét; gồm 2 blob DOCX giải nén XML |
| Mẫu secret | Không thấy mẫu token ghp_, github_pat_, sk- dài hoặc header private key đã kiểm tra |
| Đường dẫn nhạy cảm | Không thấy var/, .env/.env.*, file .sqlite3 hoặc Word tạm trong lịch sử blob theo mẫu kiểm tra |
| Email commit | 1 địa chỉ phân biệt, không phải noreply; không chép email vào báo cáo |
| Word metadata | Hai Word deliverables có docProps/core.xml; cần duyệt metadata và nội dung |

Quét mẫu không chứng minh tuyệt đối không có secret/thông tin cá nhân: không bao phủ mọi kiểu token, ảnh, file nhị phân nhúng hoặc ngữ nghĩa tài liệu. Không chạy lại browser demo thủ công vì không đổi runtime/UI; bằng chứng demo trước ở báo cáo 09/10. Test không chứng minh chất lượng sư phạm hay sức mạnh engine.

## Bạn cần duyệt trước khi quyết định Public

- [ ] **Email commit cũ:** đồng ý công bố email lịch sử. Đổi git config chỉ đổi commit mới; không tự rewrite lịch sử.
- [ ] **Tên tác giả:** đồng ý công bố tên trong README, tài liệu và Word.
- [ ] **Inventory/sổ tay:** manifest, danh mục và HTML có đường dẫn máy, tên file ngoài repo, hash, timestamp, số lượng record local. Không chứa nội dung database nhưng vẫn là metadata cần cân nhắc.
- [ ] **Hai Word V4:** đồng ý công bố nội dung và metadata; kiểm tra câu trả lời riêng tư/comments nếu bổ sung sau này. Không sửa bản gốc trong đợt này.
- [ ] **Đặc tả:** đồng ý công bố kế hoạch trong docs/spec. Đã push Private không có nghĩa đã đồng ý công bố.
- [ ] **Giấy phép:** chốt có cho người khác dùng/sửa/phân phối code theo giấy phép nào hay chỉ chia sẻ để xem; chưa tự thêm LICENSE.
- [ ] **Lời giới thiệu:** dùng nhãn prototype local, engine tối đa 2 ply, template và bài tổng hợp; không tuyên bố trained ML/người dùng thật/hiệu quả chưa có bằng chứng.

Nếu không muốn công khai một mục, xóa ở commit mới không loại bỏ bản cũ khỏi lịch sử. Có thể tiếp tục giữ repo hiện tại riêng tư hoặc quyết định tạo một repo phát hành source đã tuyển chọn. Không force-push hay sửa lịch sử khi chưa được yêu cầu rõ ràng.

## Thứ tự cải thiện sản phẩm tiếp theo

1. Trả lời hai bộ V4, chốt người học, phong cách UI và tiêu chí vòng học thành công.
2. Duyệt thế cờ/lời giải: FEN, bên đi, nước chấp nhận, mục tiêu học, nguồn và quyền sử dụng; kiểm tra bằng engine sâu hơn.
3. Chỉnh từng trang theo hệ thống màu, chữ, spacing, loading/error và mobile chung; kiểm thử vòng học chính trước mở rộng tính năng.
4. Thay engine qua interface có sẵn, benchmark bằng thế đã duyệt. Nếu thêm LLM, chỉ diễn giải dữ kiện engine được kiểm soát.
5. Pilot nhỏ có đồng ý phù hợp; quan sát và báo cáo kết quả thực tế.
6. Nếu cần URL app online, làm đợt triển khai riêng; không đưa thẳng local server ra Internet.

## File của đợt này

README.md, CONTRIBUTING.md, PUBLIC_READINESS_VI.md, GITHUB_CHECKLIST_VI.md, PROJECT_MEMORY_VI.md, RUN_AND_DEMO_CODEX.md, DEVELOPMENT_JOURNAL.md, TEST_REPORT_CODEX.md, IMPLEMENTATION_REPORT_CODEX.md, AI_USAGE.md.

Inventory cũ giữ ngày snapshot 09/10; không tuyên bố quét lại toàn thư mục hoặc tự thêm metadata máy vào bản chuẩn bị công khai.
