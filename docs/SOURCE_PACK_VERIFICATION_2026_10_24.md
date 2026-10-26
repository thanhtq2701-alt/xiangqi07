# Kiểm tra gói source V5 — 24/10/2026

Gói: `deliverables/Co_Chill_V5_Source_2026_10_24.zip` (3.399.587 byte, 55 file).

SHA-256: `660473546130376131e7a3e2f672d589918c2835434a250202a1eff50082deac`.

Đã kiểm tra ZIP không lỗi, hash từng file khớp `MANIFEST_SHA256.json`, chỉ chứa allowlist. Không có `var/`, `.git/`, `.env` thật, SQLite, Word riêng, dữ liệu người chơi hoặc engine binary. Các hằng password/TOTP trong tests là fixture công khai dành riêng cho kiểm thử.

Đã giải nén sang thư mục mới trong `var/` và chạy từ chính thư mục đó:

- 33 kiểm thử Python đạt trong 9.174 giây: 30 luật, static/private-file isolation, account sync/revision và fallback không có binary.
- 10/10 hồi quy điều phối UI V5 đạt.
- 12 bài synthetic khớp dữ liệu/luật từ checker.

Không chạy lại toàn bộ 68 kiểm thử Python được đóng gói: bộ đầy đủ ở repository gốc đã đạt 110/110 trong đợt trước; gói lược bỏ legacy nên giữ 68. Không có deploy lên cochill.vn, chỉnh DNS hoặc đọc/chuyển database thật. Đây là gói source mới, không phải database migration.

Tạo lại bằng `python tools/build_deploy_pack.py --output deliverables/TEN_MOI.zip`. Lệnh dùng allowlist, xác minh hash và từ chối ghi đè ZIP đã có. Gói hiện tại giữ README riêng để tránh nhầm server legacy. Repo gốc không bị dọn/xóa.
