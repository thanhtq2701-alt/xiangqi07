# old/ — lưu trữ lịch sử

Mọi thứ trong thư mục này **không còn được dùng** và không mô tả trạng thái hiện
tại. Không chạy, không sửa, không dựa vào đây khi làm tính năng mới. Trạng thái
hiện hành nằm ở [README](../README.md) và [docs/PROJECT.md](../docs/PROJECT.md).

| Mục | Nội dung |
|---|---|
| `SPEC_V0.1.md` | Bộ đặc tả V0.1 ban đầu (Final Pack 00–17, 18 tệp gộp nguyên văn): kế hoạch, kiến trúc đề xuất, lộ trình. Quyết định hiện hành ở docs/PROJECT.md. |
| `HISTORY.md` | 8 tài liệu tháng 10/2026 gộp nguyên văn theo thời gian: tóm lược V3–V5, audit học tập và giao diện, ghi chú chuẩn bị GCP, bàn giao Claude V6, báo cáo triển khai/kiểm thử Codex, sổ tay hiện trạng. Vận hành hiện tại: deploy/DEPLOY_GCP_VI.md. |
| `legacy/` | Ứng dụng local-only đời đầu (`server.py`, `web/`), các module chỉ nó dùng (`app/service.py`, `storage.py`, `learning.py`) và test của chúng. Đã thay bằng `co_chill_server.py` + `web/`. |
| `tools/` | Công cụ đóng/kiểm tra gói ZIP source; không còn dùng vì code chia sẻ qua GitHub. |
| `data/` | `sources.csv` mẫu nguồn dữ liệu theo đặc tả cũ; chưa từng được code đọc. |

Liên kết bên trong hai tệp gộp trỏ tới vị trí cũ nên có thể không mở được; tệp gốc vẫn xem được trong lịch sử Git.

Lịch sử chi tiết của từng tệp vẫn xem được bằng `git log --follow`.
