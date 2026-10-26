# Nguồn và quyền sử dụng trong bản V5 — 24/10/2026

Vật liệu sản phẩm mới: `E:\ThanhTQ\App cờ tướng\10-23\V5.docx`; vật liệu V3/V4/UI UX + Luật và Final Pack được giữ nguyên để đối chiếu. Các câu trả lời riêng không phải tài nguyên public của website. Việc một tài liệu có trong repo local không tự cho phép công khai nó.

Hai ảnh thương hiệu được chủ sản phẩm cung cấp để dùng cho website:

- `E:\ThanhTQ\CLB Cờ tướng\Ava.png` → `online-preview/logo-co-chill.png` (đã có ảnh tương ứng).
- `E:\ThanhTQ\CLB Cờ tướng\Cover.png` → `online-preview/cover-co-chill.png`.

Nguồn cung cấp là chủ sản phẩm; chưa có giấy phép độc lập được kiểm toán. Không tự suy rằng mọi yếu tố trong hình hoặc tài liệu của bên thứ ba đều được phép tái phân phối. Bốn ảnh thế cờ trong Word gồm hình có dấu nguồn/video/trích sách chưa đủ thông tin xác minh; không đưa chúng vào bộ bài public. Các bài đang chạy là 12 bài tổng hợp của dự án, chưa là bộ chú giải chuyên gia.

`app/pikafish.py` là mã adapter do dự án viết, không kèm engine binary, NNUE hoặc mã nguồn Pikafish sao chép. Bộ kiểm thử dùng tiến trình giả do dự án tạo. Tài liệu [PIKAFISH_SETUP_V5.md](docs/PIKAFISH_SETUP_V5.md) dẫn nguồn chính thức; cần kiểm tra quyền của đúng binary và trọng số trước khi dùng/phân phối. Không tự coi giấy phép mã nguồn là giấy phép của mọi file trọng số.

Local dùng Python standard library và JavaScript thuần. `requirements.txt` bổ sung Gunicorn cho máy chủ Linux/UNIX; không bắt buộc cho Windows local. Các cấu hình triển khai không mua dịch vụ hoặc tự cấp quyền phân phối code. Dự án vẫn cần chủ sở hữu chọn giấy phép cho code của mình trước khi quảng bá quyền tái sử dụng; một repo Public không đồng nghĩa ai cũng được cấp mọi quyền.

Không scrape kho ván/bài, không chép hình hoặc code của đối thủ, không nhập nội dung sách chỉ vì sách đã cũ. Nguồn hosting/engine đã dùng trong hướng dẫn được dẫn tại [DEPLOY_V5.md](docs/DEPLOY_V5.md) và [PIKAFISH_SETUP_V5.md](docs/PIKAFISH_SETUP_V5.md). Đây là ghi nhận nguồn, không phải tư vấn pháp lý hay chứng nhận toàn bộ quyền sử dụng.

## Ghi nhận nguồn của các phiên bản trước

Nhận định không có ảnh bên ngoài bên dưới thuộc thời điểm bản gốc; V5 dùng hai ảnh chủ sản phẩm cung cấp như ghi rõ phía trên.

# Sources and notices

No external chess implementation, engine binary, NNUE weights, book puzzles, annotations, images or puzzle database has been copied into this implementation. UI graphics are original SVG/CSS; fonts use the user's system fonts. Python's standard library supplies HTTP, SQLite and tests. The project owner has not selected a public redistribution license for the project's own code.

Product sources are the owner-provided Word files and Final Pack, whose original text is retained locally; raw personal discovery documents are excluded from Git. `docs/spec/` contains the finalized owner specification unchanged.

Reference sources checked on 8 October 2026:

- World Xiangqi Federation, [World Xiangqi Rules](https://www.wxf-xiangqi.org/images/wxf-rules/2018_World_XiangQi_Rules_English2018.pdf): reference for future complete rule adjudication; no tournament compliance claim.
- [Official Pikafish repository](https://github.com/official-pikafish/Pikafish): candidate replacement engine. It is a Xiangqi UCI engine; its repository describes GPLv3 distribution obligations. Review the exact release, code and weights terms before bundling. Nothing from Pikafish is currently distributed.
- [W3C WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/): future accessibility acceptance checklist; not a certification.
- [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview): beginner API reading.
- [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): future security review reference.

These references are for verification/learning, not authorization to import copyrighted datasets. Public visibility is not a data license. Document permissions for every future data source, and do not reuse user games for shared training without an appropriate consent process.
