# Đối chiếu luật và ký phổ cho đợt UI/UX ngày 15/10/2026

Nguồn yêu cầu: `UI UX + Luat.docx`, nhóm UX31–33, và UX35. Bản Word gốc được giữ nguyên. Đây là ghi chú kỹ thuật cho bản thử, không phải tuyên bố đã đạt chuẩn trọng tài giải đấu.

## Nguồn đã tra cứu

- [World Xiangqi Rules 2018 — PDF do WXF phát hành](https://www.wxf-xiangqi.org/images/wxf-rules/2018_World_XiangQi_Rules_English2018.pdf): Điều 3.1 H–I về chiếu/lặp nước cấm; 3.2 B–D về lặp thế, hành vi hai bên và nước tự nhiên; Điều 8 về xác minh số nước; 19 về định nghĩa. Lặp hòa thông thường xét **bốn lần xuất hiện** và điều kiện không vi phạm, không chỉ đếm ba lần. Ngưỡng không bắt quân cần đối chiếu cách đếm và xác minh. Hai bên cùng chiếu không thể suy ra bên chiếu trước thua. Đây là bản chính thức tìm được; chưa xác nhận có phiên bản mới hơn áp dụng cho mọi giải.
- [Trang giới thiệu World Xiangqi Rules của WXF](https://www.wxf-xiangqi.org/index.php?Itemid=291&id=269&lang=en&option=com_content&view=article): xác nhận nguồn tổ chức của tài liệu, không lấy nhãn của website khác làm chứng cứ luật chính thức.
- [Trang luật Ziga do chủ dự án gửi](https://zigavn.com/cotuong/luat-co-tuong): tham khảo cách trình bày ký phổ Việt: Tg, S, T, X, M, P, B; tiến `.`, thoái `/`, bình `-`. Trang tự ghi nội dung là tóm lược, cần đối chiếu điều lệ. Không coi tiêu đề “chính thức” của bài là chứng nhận cho ứng dụng.

Không sao chép hình ảnh, bộ bài tập hay toàn văn nguồn vào sản phẩm. Các ví dụ kiểm thử bên dưới là thế tự tạo.

## Quyết định triển khai thực tế

1. **Luật đi quân giữ nguồn hiện tại** trong `online-preview/xiangqi.js`, đã có kiểm thử đối chiếu Python. Module mới không tạo tập nước đi riêng và không thay đánh giá bằng nội dung giải thích.
2. **Ký phổ Việt** được sinh từ thế trước nước đi. Lộ 1–9 tính theo bên đang đi; lật giao diện không thay ký phổ. Mã/Sĩ/Tượng đi chéo ghi lộ đến; Xe/Pháo/Tướng/Tốt tiến hoặc thoái ghi khoảng cách. Khi quân cùng loại cùng lộ, dùng `trước`/`sau`, hoặc `giữa` khi có ba quân. Với các cụm Tốt phức tạp, thêm lộ và `[thứ tự]` để tránh đoán quân; đây là phần mở rộng minh thị của prototype cần chủ dự án duyệt.
3. **Nhập ký phổ** chỉ khớp với tập nước hợp lệ của đúng thế hiện tại. Ký hiệu mơ hồ bị từ chối; không tự chọn phương án đầu tiên. Hỗ trợ cả tọa độ a0–i9, số thứ tự nước và biên bản Việt. Chưa hỗ trợ PGN/XQF, chữ Hán, biến phân nhánh, nhận ảnh hoặc chú thích xen giữa các nước. Toàn chuỗi phải hợp lệ mới chuyển cho ứng dụng lưu.
4. **Biên bản hai cột** luôn Đỏ bên trái, Đen bên phải. Nếu FEN bắt đầu ở lượt Đen, ô Đỏ của hàng đầu để trống; không dịch nhầm bên đi.
5. **Nước không hợp lệ** chỉ thông báo nguyên nhân luật: cản chân/mắt, ngòi Pháo, qua sông, ra khỏi cung, cùng bên, tự chiếu, đối mặt hai Tướng. Không đưa nước thay thế, điểm đánh giá hoặc nước tốt nhất trong ván.
6. **Lặp ba lần** chỉ cảnh báo. **Lặp bốn lần** được xét trên toàn bàn cờ và bên đến lượt; nội dung lời giải, đồng hồ và người dùng không thuộc khóa thế cờ.
7. **Chiếu liên tục một bên**: nếu mọi nước của đúng một bên trong ba đoạn từ lần xuất hiện thứ nhất đến thứ tư đều chiếu, ứng dụng kết thúc với bên đó thua. Đối thủ có nước chiếu xen kẽ không tự làm bên chiếu liên tục hết trách nhiệm. Đây là triển khai hẹp, chưa có trọn quy trình cảnh cáo/yêu cầu trọng tài của giải đấu.
8. **Lặp yên tĩnh**: chỉ tự hòa nếu không nước chiếu và không phát hiện bất kỳ nước bắt quân hợp lệ nào của cả hai bên trong chu kỳ. Kiểm tra thận trọng này có thể đưa nhiều chu kỳ thực ra hòa sang diện cần kiểm chứng.
9. **Hai bên cùng chiếu, chiếu xen bắt hoặc khả năng đuổi**: trả `needsVerification: true`, không tự gán thắng/thua/hòa. Chưa có phân loại căn thật/căn giả, đuổi theo danh tính quân, đổi mục tiêu, đuổi Tốt, ghim hoặc ngoại lệ Mã/Pháo đuổi Xe. Không coi một nước chờ bất kỳ là luôn xóa mọi trách nhiệm lặp.
10. **Không bắt quân**: đếm từ các nước đã có, đặt lại 0 sau ăn quân; Tốt tiến không ăn không đặt lại. Từ 100 nửa nước chỉ yêu cầu kiểm chứng. Không tuyên bố thuật toán đã thực hiện đầy đủ quy trình “50 nước mỗi bên”. FEN đơn lẻ không chứa lịch sử đủ để phán quyết các mục này.
11. **Chiếu hết và hết nước hợp lệ** có ưu tiên trước lặp thế: dùng kết quả từ bộ luật hiện tại, đều là thua cho bên không còn nước hợp lệ.

## API của module mới

`online-preview/game-tools.js` nối vào `CC` trên trình duyệt, xuất CommonJS để kiểm thử. Tải sau `xiangqi.js`; không cần thư viện bên ngoài.

| Hàm | Dữ liệu và kết quả |
|---|---|
| `notateMove(positionOrFen, move)` | Nước tọa độ hợp lệ → ký phổ Việt; nước sai bị từ chối. |
| `parseNotation(positionOrFen, text)` | Ký phổ Việt/tọa độ → đúng một nước tọa độ hợp lệ. |
| `parseGameNotation(initialFen, text, maxPlies = 200)` | Trả `{moves, positions}`; positions gồm FEN đầu và sau mỗi nước. |
| `pairMoveHistory(initialFen, history)` | Trả các hàng `{number, red, black}`. Mỗi ô có `move, notation, ply, before, side`. |
| `illegalMoveReason(positionOrFen, move)` | Trả chuỗi rỗng khi hợp lệ, hoặc lý do bằng tiếng Việt. |
| `repetitionStatus(initialFen, history)` | Trả `over, winner, reason, needsVerification, code, occurrences, quietPlies`. |

`history` chấp nhận mảng tọa độ hoặc mảng đối tượng có `move` như dữ liệu app hiện tại. Không tin FEN `before/after` do đối tượng đầu vào cung cấp: module dựng lại từng nước bằng bộ luật. `needsVerification` không phải một kết quả hòa và không được cộng vào thống kê thắng/thua.

## Kiểm thử và phần cần V5

Lệnh: `node tools/test_preview_game_tools.cjs` (dùng Node runtime của workspace nếu Node hệ thống quá cũ).

- Ký phổ từng loại quân, cả Đỏ/Đen; vòng khứ hồi hơn 4.000 nước hợp lệ trên 100 thế từ chuỗi ván xác định.
- Tách trước/sau, Tốt nhiều cụm, từ chối ký hiệu mơ hồ; nhập biên bản đánh số và nước sai giữa chuỗi.
- Biên bản bắt đầu lượt Đen; nguyên nhân nước cấm; ghim và đối mặt Tướng.
- Chiếu lặp ở cả hai phía với ngưỡng bốn; lặp yên tĩnh; không xử hòa nhầm khi có khả năng đuổi; đếm không bắt quân và ngưỡng cần kiểm chứng.

V5 cần một người duyệt các ví dụ luật có FEN + toàn lịch sử và điều khoản; xác nhận bộ luật/phiên bản cụ thể; duyệt ký phổ khi nhiều Tốt cùng lộ; quyết định cách trình bày và xử lý ván cần kiểm chứng. Không thể thay các dữ liệu này bằng câu xác nhận chung “theo luật tiêu chuẩn”.
