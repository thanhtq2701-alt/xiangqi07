# Lịch sử báo cáo, audit và bàn giao (10/2026)

Lưu trữ lịch sử, gộp nguyên văn theo thứ tự thời gian. Số liệu và trạng thái trong đây là của thời điểm viết, không phải trạng thái hiện tại; xem README và docs/PROJECT.md. Mỗi mục dưới đây là một tệp gốc, tiêu đề hạ một cấp.

## Mục lục

- `reports/V6_PREVIOUS.md`
- `reports/v6_work/LEARNING_AUDIT.md`
- `reports/v6_work/UI_AUDIT.md`
- `docs/DEPLOY_GCP_V6.md`
- `docs/CLAUDE_HANDOFF_V6.md`
- `reports/IMPLEMENTATION_REPORT_CODEX.md`
- `reports/TEST_REPORT_CODEX.md`
- `reports/PROJECT_MEMORY_VI.md`

---

<!-- nguồn: reports/V6_PREVIOUS.md -->

## V6 Previous

Tóm lược các ý tưởng và quyết định V3–V5 đã được hợp nhất hoặc thay thế. Đây
là ghi chú lịch sử, không phải đặc tả hay hướng dẫn vận hành hiện hành. Nếu có
khác biệt, dùng [README](README.md), [quyết định V6](docs/V6_DECISIONS.md) và
[giới hạn](KNOWN_LIMITATIONS.md).

### Ý tưởng được giữ lại

- Dạy cách suy nghĩ và lý do đằng sau nước đi, không chỉ đưa đáp án; ưu tiên
  vòng chơi/nhập ván → chọn thời điểm đáng học → tự suy nghĩ → giải thích có
  căn cứ → thử lại → bài liên quan → ôn → tiến độ.
- Làm UI tiếng Việt dễ đọc, hỗ trợ người mới nhưng có đường học sâu hơn; ưu
  tiên bàn cờ, thao tác bàn phím/cảm ứng, trạng thái lưu và khôi phục.
- Luật và engine làm nguồn sự thật. Ký phổ, nhập/phát lại ván và phán quyết
  luật phải kiểm tra được; tình huống chưa đủ căn cứ cần được ghi rõ, không
  tự đoán. Ghi chú luật cũ dùng WXF 2018 để đối chiếu; vẫn cần lịch sử ván và
  người duyệt cho trường hợp lặp, chiếu/đuổi dai và luật giải đấu.
- Giữ ranh giới thay thế được giữa giao diện, server, persistence và engine.
  Ghi nhãn trung thực cho máy heuristic, bài tổng hợp, lịch ôn và giải thích
  mẫu; không tuyên bố có ML được huấn luyện hay hiệu quả học đã được chứng minh.
- Bảo vệ dữ liệu người học, hỗ trợ xuất/xóa, không scrape nội dung hoặc dùng
  dữ liệu người chơi để huấn luyện khi chưa có quyền và sự đồng ý.
- Tách bài giảng xem trước khỏi bài thực hành; xem lời giải không phải mastery.
  Một lần thử gồm suy nghĩ và nước đi; bài dở phải giữ đúng chỗ để học tiếp.
- Ghi riêng bài gốc, biến thể cùng ý, bài liên quan và trạng thái có trợ giúp.
  Chỉ tính nội dung mới khi mục tiêu hoặc cấu trúc thực sự khác; lịch ôn bắt
  đầu từ lúc hoàn thành từng bài, tự đánh giá không thay kết quả thực hành.
- Độ khó dựa vào quyết định cần đưa ra, phản ứng quan trọng và phương án gây
  nhiễu, không chỉ độ dài biến hay độ sâu engine. Nhãn trình độ chưa hiệu
  chỉnh không phải Elo hoặc bằng chứng mastery.
- Nội dung chia sẻ cần nguồn/quyền dùng và duyệt; bài gửi của người học không
  tự vào kho chung. Nước hợp lệ khác với nước tối ưu; nếu ngoài cây đáp án hoặc
  bằng chứng chưa đủ thì giữ trạng thái chưa xác định, không tự chấm sai.

### Ý tưởng đã được nâng cấp hoặc thay thế

- Các prototype V3–V5, web tĩnh và hướng dẫn hosting cũ không phải entry point
  hiện tại. Chạy V6 theo lệnh trong README; không dùng hướng dẫn Sites/Vercel,
  DNS hoặc server cũ để kết luận V6 đã được triển khai.
- Các câu hỏi UI, tài khoản, luật, nội dung và kế hoạch theo ngày đã được thay
  bằng code hiện có, quyết định V6 và giới hạn được ghi nhận. Câu trả lời trong
  tài liệu cũ không tự chứng minh tính năng đã hoạt động.
- Màu sắc, hình thức, scope PvP, tài khoản và engine đã được cập nhật qua các
  vòng chủ sản phẩm duyệt. Chi tiết đúng hiện nay nằm trong V6, không lấy mức
  ưu tiên/ngân sách hoặc kế hoạch phát hành cũ làm chỉ thị mới.
- Báo cáo, inventory, ảnh chụp và gói source V3–V5 là snapshot lịch sử; không
  thay cho kiểm thử V6 hoặc trạng thái repository hiện tại.

### Ý tưởng vẫn chưa được xác nhận hoàn tất

Kho bài nâng cao đã được chuyên gia duyệt; chấm tự do bằng LLM; cấp bot được
hiệu chỉnh; phục hồi mật khẩu qua email; luật giải đấu đầy đủ; và vận hành
Pikafish/Google Cloud, tải, backup, HTTPS hay DNS thực tế. Chỉ coi là hoàn tất
khi có bằng chứng mới trong [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) và
[TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md).

### Tài liệu nguồn

Các ghi chú, kế hoạch, báo cáo, câu hỏi và bản bàn giao V3–V5 đã được rút gọn
ở đây; bản gốc không còn cần cho việc chạy web. Riêng tài liệu Final Pack gốc
trong `docs/spec/` và `docs/materials/` được giữ nguyên theo quy ước dự án.

---

<!-- nguồn: reports/v6_work/LEARNING_AUDIT.md -->

## Kiểm tra kho bài và thiết kế học tập cho V6

> Tài liệu lịch sử ngày 25/10/2026, dựa trên snapshot source lúc đó; không
> dùng làm kiểm kê hiện tại.

Ngày kiểm tra 25 tháng 10 năm 2026. Phạm vi chỉ đọc mã nguồn và tài liệu; không thay đổi chức năng, không sinh thêm bài chưa kiểm chứng. Các số lượng đề xuất bên dưới là mục tiêu xây dựng, không phải nội dung đã tồn tại.

### Đối chiếu đúng gói ZIP người dùng vừa cung cấp

Baseline bổ sung là gói source do chủ sản phẩm cung cấp ngày 24/10/2026, gồm 1217 entry. Chỉ đọc danh mục và các file mã liên quan; không thực thi mã trong ZIP, không mở hoặc xuất dữ liệu tài khoản riêng.

Năm file dưới thư mục gốc `xiangqi-ai/` trong ZIP đều giống từng byte với bản local đã dùng cho báo cáo này:

| File tương đối từ gốc dự án | Kết quả đối chiếu ZIP với local |
| --- | --- |
| `online-preview/fixtures.js` | Giống hoàn toàn, 506 dòng |
| `online-preview/learning.js` | Giống hoàn toàn, 475 dòng |
| `online-preview/experience.js` | Giống hoàn toàn, 71 dòng |
| `app/content_store.py` | Giống hoàn toàn, 144 dòng |
| `online-preview/app.js` | Giống hoàn toàn, 233 dòng |

Vì vậy số lượng và các kết luận học tập bên dưới không đổi: 12 bài một nước mẫu, 4 minh họa khai cuộc và hành trình 4 liên kết. Đây không phải suy đoán từ tên ZIP; đã phân tích nội dung `fixtures.js` trong đúng gói mới.

Trong cùng ZIP còn có các bản sao cũ ở `deliverables/Co_Chill_VSCode_2026_10_17/`, `var/site-preview/dist/` và `var/co-chill-web-source-gon/`. `learning.js`, `experience.js` và `app.js` tại các bản sao này có kích thước khác bản gốc hiện tại; không lấy nhầm chúng làm baseline V6 và không đếm các bản sao fixture thành bài mới. Đường dẫn deliverables mô tả nội dung ZIP được kiểm tra, không còn là thư mục trong repository sau khi gộp tài liệu lịch sử vào `V6_PREVIOUS.md`. Việc năm file trên giống nhau không phải khẳng định toàn bộ 1217 entry giống repo hiện tại.

### Kết luận hiện trạng đã kiểm chứng

- `online-preview/fixtures.js` có đúng 12 bài, chia đều 3 bài cho mỗi nhóm `material`, `cannon`, `horse`, `safety`. Toàn bộ mang nguồn `synthetic-codex-v1`, đều gắn `phase=end`. Không bài nào trong 12 bài có trường `difficulty` hoặc chuỗi `pv`.
- Mỗi bài hiện có một nước `solution`; vài hình ăn quân trực tiếp, vài hình cứu Tướng. Đây chủ yếu là luyện quan sát và luật ở một quyết định, không phải bộ chiến thuật nhiều nước. Tên nội bộ `horse-fork` không biến bài thành một bài đòn đôi đã được chứng minh.
- Đã đọc ZIP `deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24.zip`: `fixtures.js` trong ZIP giống từng byte với file local. Nhận xét trên áp dụng cho gói bản tĩnh đã đóng ngày 24 tháng 10.
- `online-preview/app.js:65` có 4 mục khai cuộc Pháo đầu, Phi tượng, Tiên nhân chỉ lộ, Sĩ giác pháo. Mỗi mục minh họa đúng một nước; không phải 4 khóa khai cuộc, không có kiểm tra vận dụng riêng cho từng mục.
- `online-preview/app.js:64` dùng cùng `puzzleBank()` cho tab Trung cuộc và Tàn cuộc, lọc theo skill chứ chưa lọc `phase`. Vì vậy hai tab chưa đại diện hai kho bài độc lập. Không được cộng 12 bài hai lần thành 24.
- `online-preview/app.js:164` dựng Hành trình học bằng 4 liên kết cố định: luật, bài học, chơi và nhìn lại, ôn tập. Chưa có chương, điều kiện trước, ma trận kỹ năng, kiểm tra kết thúc chương hoặc lộ trình Xe Pháo Mã thật.
- `app/content_store.py:53` hỗ trợ nhãn `unrated/beginner/intermediate/advanced`; đó là nhãn biên tập, chưa có bằng chứng chuẩn hóa độ khó. Bộ 12 bài đóng gói chưa gắn nhãn này.
- `app/content_store.py:67` có thể lưu một PV hợp lệ dài 1 đến 30 nửa nước, phải bắt đầu bằng `solution`. Validator kiểm tra luật chứ không chứng nhận phương án tối ưu hay giá trị sư phạm. `online-preview/app.js:59` vẫn chỉ hiển thị `pos.play(p.solution)` khi xem minh họa. Lưu PV dài không đồng nghĩa người học giải được bài nhiều lượt.
- `online-preview/learning.js:84` snapshot phiên học không mang cây biến hay con trỏ bước. `createSession` tại dòng 97 giữ một `candidate` cho cả hình. Cần nâng mô hình dữ liệu trước khi thêm bài nhiều nước.
- `online-preview/experience.js:28` chỉ kiểm tra đủ ba câu trả lời và nước ứng viên khớp mẫu/alternatives. Hệ thống không chấm đúng sai lập luận tự do. Không được gắn nhãn đã hiểu chỉ vì nước đi trùng mẫu.
- `online-preview/learning.js:309` đề xuất bài cùng skill, ưu tiên ID chưa gặp rồi hình xem lâu nhất. Chưa xét mức khó, chủ đề phụ, mục tiêu cá nhân, độ tương đương hình hoặc lịch sử cùng family. Dù fixture có `family`, từng bài đang tự dùng ID của chính nó làm family.

### Những quyết định cũ cần giữ

Đã đối chiếu `var/v5-2026-10-23/answers_full.txt`, các đoạn P0165–P0197, P0232–P0240, P0509–P0521 và P0622–P0632. Đây là câu trả lời đã có, không nên bắt chủ sản phẩm trả lời lại toàn bộ.

- Người học tự quan sát, trả lời và đề xuất nước trước khi mở đáp án. Không coaching trong ván đang chơi.
- Một lượt thử là gửi cả bộ suy nghĩ và nước đi. Sau ba lần chưa đạt thì giữ hình chưa hoàn thành để học tiếp; không tính thành công.
- Phần giảng được xem trước; bài thực hành mới sau đó mới áp dụng reflection. Đã xem không đồng nghĩa đã học được.
- Bài gốc và bài liên quan có trạng thái riêng. Bỏ qua bài liên quan phải giữ chỗ để lần sau quay lại.
- Lịch ôn neo vào thời điểm hoàn thành từng hình. Tự đánh giá cuối phiên được lưu riêng.
- Người dùng đã chấp nhận độ khó phụ thuộc cả số lựa chọn gây nhiễu và yêu cầu nhìn thấy ý tưởng, không chỉ chiều dài lời giải.
- V5 đã chọn nội dung mới ưu tiên thêm hình, sửa hình lỗi; bài do người học gửi trước hết ở kho riêng, qua duyệt mới vào kho chung. Việc tải file lên không tự chứng minh quyền tái xuất bản tài liệu của bên khác; phải giữ nguồn và căn cứ quyền dùng.
- V5 cho phép hình chưa gặp có nhãn Bài mới, nhưng thống kê cần tách biến thể cùng ý và bài chuyển giao thật; chỉ đổi màu không được coi là nội dung mới độc lập.
- V5 có mong muốn khóa bước khi đủ kỹ năng và điểm, nhưng chưa định nghĩa tiêu chí. EXP là điểm hoạt động, không phải bằng chứng trình độ; cần hỏi V6 ngưỡng chuyển bước có căn cứ thay vì tự quyết dùng EXP.
- Chưa có bộ hình khó mẫu kèm đáp án do chủ sản phẩm cung cấp trong V5. Không được nói đã có bộ thẩm định từ chuyên gia. Nhịp duyệt từng được nêu khoảng 10 thế mỗi tuần, cần xác nhận khả năng thực tế trước khi hứa ra hàng trăm bài.

### Phân biệt bài giảng và bài luyện

Một lesson nên dạy đúng một mục tiêu bằng bàn cờ và câu hỏi ngắn: mở đầu nêu tình huống, một minh họa có thể bước tới/lùi, một ví dụ dễ nhầm có thể bật tắt quân chắn, rồi bài thực hành khác vị trí. Không biến mọi lesson thành đoạn văn dài. Một puzzle kiểm tra một hoặc nhiều quyết định của người học, có mục tiêu, phản ứng đối thủ và điều kiện kết thúc rõ.

Ví dụ mục tiêu bài Pháo là nhận ra khi nào quân ngòi di chuyển khiến đòn ăn quân không còn tồn tại. Hình minh họa có thể đánh dấu ngòi trong phần giảng; hình kiểm tra sau đó không được tự đánh dấu ngòi hay mũi tên đáp án trước khi người học suy nghĩ. Đồ họa phải biểu diễn đúng một trạng thái luật sinh ra từ FEN, không dùng ảnh trang trí vẽ tùy ý để khẳng định vị trí chiến thuật.

### Mô hình bài nhiều lượt cần triển khai

Tạo schema `exercise-v2`, giữ bộ đọc v1 để các lượt cũ không mất. Các trường tối thiểu:

- Danh tính: `id`, `version`, `status`, `contentType`, `familyId`, `createdBy`, `reviewedBy`, `reviewedAt`.
- Bàn gốc: `initialFen`, `rulesetId`, lịch sử cần cho các luật lặp nếu có; không kết luận lặp chỉ từ một FEN.
- Mục tiêu: `goalType` như thắng vật chất, chống đòn, chiếu hết hoặc cải thiện vị trí; `goalDescription`, điều kiện đạt cụ thể và giới hạn kết luận.
- Phân loại: `pieceTags`, `motifTags`, `phase`, `prerequisites`, `difficultyLabel`, `difficultyStatus=provisional/empirical`, các lý do xếp mức.
- Cây quyết định: mỗi node có `nodeId`, bên đi, băm trạng thái, câu hỏi hoặc chỉ dẫn, các cạnh `move`, `nextNodeId`, loại cạnh của người học hay đối thủ, trạng thái chấp nhận và lý do. Node kết thúc phải có tiêu chí đạt hoặc chưa kết luận.
- Bằng chứng: tên/phiên bản engine, cấu hình tìm kiếm, thời gian hoặc nodes, MultiPV, score có chiều nhìn thống nhất, PV đã phát lại qua luật, ngày xác minh, dấu duyệt người biên tập. Thiếu bằng chứng thì giữ nháp/cần kiểm chứng.
- Nguồn: tự dựng, ván người dùng cho phép, nguồn công khai có giấy phép, người cấp quyền, URL/file và phạm vi được dùng. Bài dẫn xuất phải lưu quan hệ với ván hoặc tài liệu gốc.
- Gợi ý và giải thích: gợi ý theo mức, phần WHAT/WHY/HOW gắn với node hoặc bằng chứng, minh họa chỉ được mở ở giai đoạn cho phép. Không cho nhà cung cấp lời giải tự tạo thêm nước ngoài cây đã duyệt.

PV đơn tuyến chỉ là một đường engine tính. Nó không đủ để chấm một bài có nhiều phản ứng hợp lý. Ban đầu cây nhỏ do biên tập viên duyệt dễ bảo trì hơn việc tính vô hạn khi người học đi bất kỳ nước nào. Khi gặp nước hợp lệ ngoài cây, hệ thống phải hoặc kiểm tra qua engine theo chính sách đã duyệt, hoặc báo chưa đủ căn cứ và cho giữ nháp; không tự chấm sai vì khác chuỗi duy nhất.

Phiên học v2 cần `exerciseVersion`, `currentNodeId`, `moveHistory`, `answersByNode`, `branchId`, lần gửi, mức gợi ý, trạng thái độc lập/có hỗ trợ, thời điểm bắt đầu/hoàn thành. Lưu sau mỗi bước. Bên đối thủ đi theo nhánh đã duyệt; mọi nước đều qua cùng bộ luật. Người học phải thực hiện các quyết định tiếp theo; không tính hoàn thành ngay sau nước đầu nếu bài yêu cầu cả chuỗi.

Reflection đầu hình giữ ba ý đã chốt; không bắt nhập lại ba đoạn văn giống nhau ở mỗi nửa nước. Ở điểm quyết định tiếp theo có thể hỏi ngắn Bạn nghĩ đối thủ đang đe dọa gì hoặc Bạn tiếp tục kế hoạch thế nào. Quyết định số lần hỏi cần chủ sản phẩm chốt theo V6. Khi mở đáp án hoặc khám phá biến, toàn lượt chuyển sang có hỗ trợ; lần đầu được giữ nguyên để thống kê.

Retry phải đưa về đúng nút gốc hoặc checkpoint đã định nghĩa, không ghi đè câu trả lời đầu. Khi engine/content được sửa, pin version cũ để truy vết; bài bị rút vì đáp án sai phải dừng chấm, giữ nháp, đánh dấu kết quả bị ảnh hưởng và cho người vận hành xem trước cách sửa thống kê.

### Lộ trình chủ đề có thể mở rộng

Tách ba trục độc lập để tránh nhân bản bài: quân cờ, ý tưởng, giai đoạn. Một bài phối hợp Xe Pháo có thể được tìm qua cả hai quân, nhưng chỉ có một ID và một lịch sử học.

1. Nền tảng cho người mới: cả bảy loại quân, chiếu và thoát chiếu, chân Mã, mắt Tượng, ngòi Pháo, mặt Tướng. Dùng thử thao tác trên bàn; cho người đã biết luật bỏ qua với nhãn tự khai.
2. Quan sát và phòng mất quân: quân không bảo vệ, quân bị tấn công, đổi quân và phản công sau khi ăn. Đây là điều kiện nền cho nhánh chiến thuật.
3. Xe: đường mở và đường bị cản, bảo vệ quân, tấn công hàng/cột, phối hợp hai Xe, đòn ghim/xiên khi vị trí cụ thể được kiểm chứng.
4. Pháo: tạo và phá ngòi, thay đổi ngòi sau chuỗi trao đổi, phối hợp Xe Pháo, tìm phản ứng phòng thủ. Không chỉ ba bài ăn Xe qua một ngòi.
5. Mã: chân Mã và đường vào, kiểm tra hai mục tiêu, bị cản sau phản ứng đối thủ, phối hợp Mã Pháo/Xe Mã. Đòn đôi phải được chứng minh trên bàn cụ thể.
6. Tốt và bộ phòng thủ: Tốt qua sông, đường thoát Tướng, Sĩ Tượng, đổi quân có lợi khi phòng thủ, chống sát. Chỉ gắn nhãn thắng/hòa khi có căn cứ và bộ luật đủ phạm vi.
7. Phối hợp và tính biến: lựa chọn nước ứng viên, dự đoán đáp trả mạnh nhất, so sánh hai kế hoạch và chống đòn. Đây là nơi các bài nhiều lượt và nhiều nhánh có ý nghĩa.
8. Khai cuộc và tàn cuộc theo mục tiêu: khai cuộc dạy phát triển và phản ứng cụ thể, tránh học thuộc một tuyến duy nhất; tàn cuộc dạy kỹ thuật chuyển ưu thế/chống thua qua một đoạn có điều kiện kết thúc. Chưa có bộ kết luận tàn cuộc chuẩn thì ghi rõ phạm vi.

Hành trình học nên hiện thẻ quân lớn Xe, Pháo, Mã, Bảo vệ Tướng, Phối hợp và các nhánh khác khi có nội dung. Trong nhánh: mục tiêu nhỏ → minh họa → luyện độc lập → bài vận dụng chưa gặp → ôn. Mỗi thẻ hiện số bài thực tế đã duyệt, tiến độ hoàn thành và một hành động Tiếp tục. Nhánh chưa có bài phải ghi Đang chuẩn bị, không tạo hàng loạt nút rỗng.

### Độ khó và quy mô đề xuất

Không nâng level bằng cách đổi tên bài dễ thành nâng cao. Độ dài là số nửa nước hoặc số quyết định của người học, phải ghi rõ; một nước của Đỏ cộng một nước của Đen là hai nửa nước. Không đánh đồng độ sâu tìm kiếm của Pikafish với độ khó bài.

- Mức nhập môn: nhận diện luật và một mục tiêu rõ, ít nhiễu, thường một quyết định. Vẫn giữ để phục vụ người mới.
- Mức cơ bản: dự đoán một phản ứng, có phương án hấp dẫn nhưng không đạt, khoảng hai quyết định của người học khi nội dung phù hợp.
- Mức trung cấp: nhiều nước ứng viên hợp lý, hai đến ba quyết định, phải trả lời phản ứng đối thủ và phối hợp quân.
- Mức nâng cao: cây biến có nhiều phòng thủ quan trọng, ba quyết định trở lên hoặc kế hoạch vị trí khó nhận ra; không bắt buộc cứ dài mới khó.

Các khoảng trên là khung biên tập tạm, không phải thang đã đo. Xếp mức theo số quyết định, số nhánh có ý nghĩa, độ nổi bật của đe dọa, kiến thức cần biết, mức phức tạp giải thích và dữ liệu người học sau này. Hiển thị Dự kiến khi chưa có mẫu; không gán Elo giả. Một bài một nước vẫn có thể khó nếu nước yên lặng hoặc nhiều nhiễu, nhưng phải được duyệt cụ thể.

Lộ trình số lượng để chủ sở hữu duyệt:

- Đợt kiểm chứng bộ chạy nhiều lượt: 6 lesson và 24 puzzle đã duyệt, tập trung Xe Pháo Mã. Mỗi quân có 2 lesson và 8 hình, gồm minh họa/luyện có hỗ trợ, bài chưa gặp và bài vận dụng riêng. Đây là tổng mục tiêu mới cần biên soạn, không cộng biến thể đổi màu vào thành tích.
- Đợt mở rộng: 12–18 lesson và 60–90 puzzle thật sự khác mục tiêu hoặc cấu trúc, thêm an toàn Tướng, phối hợp, khai/tàn. Chỉ tăng khi pipeline duyệt chạy và chủ sở hữu đủ thời gian review.
- Đợt sau: tăng theo lỗ hổng taxonomy và số lượt dùng thật; không đặt số lượng trang trí. Báo số nháp, số qua luật, số qua engine, số qua người duyệt và số đã phát hành riêng nhau.

Không thể chứng nhận 24 hay 90 bài chất lượng bằng cách tự tạo hàng loạt và chỉ kiểm tra nước hợp lệ. Tốc độ phát hành phụ thuộc nguồn có quyền, thời gian engine thực, người biên tập và kiểm thử trên người dùng. Chưa có nguồn cũng vẫn xây được schema, editor, renderer và bài demo gắn nhãn; không được giả vờ kho nội dung đã đủ.

### Quy trình kiểm chứng nội dung

1. Nhập nháp có nguồn và quyền dùng. Lưu file gốc riêng, không tự chuyển ván cá nhân vào kho chung.
2. Kiểm tra FEN/bên đi, số quân, Tướng, mọi cạnh hợp lệ, trạng thái sau mỗi nước và điều kiện kết thúc. Loại cây hỏng, node mồ côi, vòng lặp không kiểm soát.
3. Phân tích bằng engine đúng phiên bản đang phục vụ, so các nước ứng viên và phản ứng phòng thủ cần thiết. Giới hạn thời gian/nodes, xác minh không timeout hoặc score bound bị hiểu thành kết luận chắc chắn. Ghi lại bằng chứng; không gọi hợp lệ là tối ưu.
4. Người biên tập duyệt mục tiêu, chấp nhận các phương án tương đương có căn cứ, xem lời giải có bám vào bằng chứng không; kiểm tra câu hỏi không vô tình tiết lộ đáp án.
5. Xem trước toàn vòng: reflection, chuỗi nước, lời giải, retry, bài liên quan, lịch ôn. Cần thao tác trên cả màn hình nhỏ.
6. Xuất bản version bất biến có log. Có nút báo vấn đề; bài sai bị rút khỏi chấm ngay, giữ lịch sử phục vụ sửa lỗi.

### Lịch ôn và đánh giá vận dụng

Giữ nguyên mốc 1/2/7/14/30 ngày đang được kiểm thử như lịch heuristic. `learning.js:181` quyết định lịch theo thành công và hỗ trợ; bài chưa hoàn thành có lịch học tiếp riêng. Không gọi đây là mô hình ML hay chứng minh hiệu quả nhớ lâu.

Với bài nhiều lượt, chỉ ghi hoàn thành sau khi đạt điều kiện cuối cây và kết thúc hình; nhấp hoàn thành lặp lại không được đẩy lịch thêm. Hình chuyển giao có completionAt riêng, không phụ thuộc bài gốc hoặc màn tự đánh giá. Pause giữ node/câu trả lời/lượt gửi. V6 phải chốt ba lần chưa đạt áp dụng cả hình hay từng checkpoint; không tự đổi quy tắc cũ mà không hỏi.

Nên bổ sung `familyId` và phân loại firstExposure: hình chưa gặp, biến thể cùng family, đã xem đáp án, luyện lại, ôn, chuyển giao. Các biến thể lật gương/đổi màu không được dùng để thổi phồng tỷ lệ vận dụng. Related recommendation ưu tiên cùng kỹ năng, đúng mức phù hợp và family mới; hết bài phải nói rõ thay vì gọi bài cũ là mới.

Dashboard nên tách hoạt động, thành công nước đi độc lập, có hỗ trợ, khả năng nhớ lại sau thời gian và kết quả trên hình khác. Ngưỡng 6 mẫu trong code là điều kiện hiển thị tạm, không phải độ tin cậy thống kê được xác thực. Không cộng ván chơi, lesson đã xem và puzzle đã giải thành một tỷ lệ thành thạo. Chỉ tự khai trình độ phải ghi tự khai; thay đổi level bằng bài thực tế cần chính sách minh bạch.

### Danh sách nghiệm thu cần giao Claude

- Migration v1 sang v2 giữ ID, version, câu trả lời cũ, nguồn và completionAt; rollback không mất bản gốc.
- Một bài ít nhất 3 quyết định của người học và 2 nhánh phòng thủ thật: hai nhánh đều chơi được đến cuối, mọi nước hợp lệ; không hoàn thành ngay sau quyết định đầu.
- Hai nước tương đương đã duyệt đều được chấp nhận; nước hợp lệ ngoài cây không bị tự kết luận sai chắc chắn.
- Reflection chặn lời giải/mũi tên/PV/điểm gợi ý trước khi gửi hoặc chủ động nhận hỗ trợ; bài giảng minh họa và bài kiểm tra tách rõ. Chế độ server không gửi đáp án bí mật trước gate nếu yêu cầu chống xem nguồn; static vốn chỉ bảo vệ luồng UI, không giữ bí mật khỏi người đọc JS.
- Refresh/mất mạng/đổi thiết bị sau bước 2 khôi phục đúng nhánh và trạng thái; không lặp nước đối thủ hay ghi hai attempt.
- Tạm gỡ hoặc sửa bài đang làm giữ nháp và ngừng chấm, không lặng lẽ đổi đáp án; bản đã học truy vết được.
- Bỏ qua bài liên quan rồi quay lại mở đúng hình đó; không thay thế bằng một hình khác mà mất chỗ học.
- Mốc ôn bám thời điểm hoàn thành từng hình; bài chưa xong không tạo completion; hint/retry không đi vào tỷ lệ tự giải mới.
- Lọc Xe/Pháo/Mã, khai/trung/tàn, mức khó, đã học/chưa gặp không nhân đôi một nội dung. Mọi số đếm là số thực trong bộ đã duyệt.
- Kiểm tra family: đổi màu/lật gương không thành bằng chứng chuyển giao độc lập; hết kho có trạng thái trung thực.
- Không mở phần luyện/phân tích hỗ trợ trong ván live. Ván đã kết thúc mới dẫn sang điểm học.
- Chạy lại `tools/test_preview_learning.cjs`, `tools/test_preview_experience.cjs`, `tests/test_cloud.py` và bổ sung test cây biến, migration, schema, provenance, scheduling; không sửa yếu test cũ để bỏ reflection hoặc chống mất dữ liệu.

### Câu hỏi V6 bổ sung để chủ sở hữu trả lời

Đây là câu hỏi mới hoặc phần V5 còn chưa đủ cụ thể. Số câu mỗi nhóm theo nhu cầu, không cố định tám câu. Có thể trả lời Đồng ý đề xuất để đội phát triển tự xử lý chi tiết kỹ thuật.

#### Nhánh học và thứ tự ưu tiên

L01. Trong đợt kế tiếp, ba nhánh cần làm sâu nhất là Xe, Pháo, Mã hay muốn thay một nhánh bằng chống mất quân/bảo vệ Tướng/phối hợp? Xếp thứ tự và nêu nhóm người học chính của từng nhánh.

L02. Trong nhánh Xe đầu tiên, chọn ba mục tiêu muốn người học tự làm được sau học: tìm đường mở, bảo vệ quân, tính ăn rồi bị ăn lại, phối hợp hai Xe, hay mục tiêu khác. Với Pháo và Mã có thể ghi tương tự, không cần tự tạo FEN.

L03. Hành trình nên là bản đồ mở cho chọn mọi bài, hay có khóa chương? Nếu khóa, có chấp nhận dùng bài vận dụng độc lập làm điều kiện, còn EXP chỉ để động viên? Đề xuất cho làm bài vượt cấp thay vì bắt người biết chơi học lại luật.

L04. Người học đi theo một nhánh Xe tới hết rồi sang Pháo, hay xen kẽ theo điểm yếu và lịch ôn? Đề xuất nhánh chính do người học chọn, hệ thống chen bài ôn đến hạn và đề nghị chuyển nhánh khi cần.

L05. Một phiên học mong muốn kéo dài khoảng bao lâu và tối đa bao nhiêu hình nhiều lượt? Có ưu tiên thời gian 5 phút, 10–15 phút hay không giới hạn?

L06. Những chương nào cần xuất hiện ngay nhưng mang nhãn Đang chuẩn bị, và chương nào nên ẩn cho tới khi có bài thật? Đề xuất chỉ hiện số bài đã duyệt và không tạo nút học rỗng.

#### Độ khó

L07. Bạn muốn người dùng nhìn thấy mấy mức và tên gì? Có đồng ý khung Nhập môn, Cơ bản, Trung cấp, Nâng cao kèm nhãn dự kiến trước khi có dữ liệu thật?

L08. Cung cấp một hình bạn coi là trung cấp và một hình nâng cao, hoặc cho phép người biên tập đề xuất để bạn duyệt. Nêu vì sao khó; có thể ghi chưa biết đáp án để engine kiểm chứng, không cần đoán.

L09. Tỷ lệ bài giữ ở mức một quyết định cho người mới nên khoảng bao nhiêu? Đề xuất vẫn giữ nền tảng nhưng phần người đã biết luật ưu tiên tính phản ứng và phối hợp nhiều lượt.

L10. Khi một người liên tiếp chưa đạt một mức, hệ thống tự hạ bài, hỏi trước khi hạ, hay giữ mức nhưng thêm gợi ý? V5 đã có tự giảm mức chơi máy; câu này chỉ hỏi mức bài học để không nhập hai khái niệm làm một.

L11. Bạn muốn hiển thị mức khó trên từng bài hay chỉ theo chương? Có cho người học tự chọn bài khó hơn khuyến nghị với nhãn thử thách không?

#### Bài nhiều lượt và nhánh

L12. Ở quyết định thứ hai và các bước sau, người học chỉ chọn nước, trả lời một câu ngắn, hay lặp lại cả bộ reflection? Đề xuất một câu ở các điểm thay đổi kế hoạch, tránh bắt viết lại ba đoạn giống nhau.

L13. Ba lần thử chưa đạt áp dụng cho cả hình hay mỗi checkpoint? Sau khi dùng hết, giữ đúng nhánh đang dở hay quay lại gốc hôm sau? Đề xuất giữ nhánh để không mất phần đã làm, nhưng không tính hoàn thành hình.

L14. Đối thủ trong bài nên luôn đáp nước phòng thủ mạnh nhất, đi nhánh đã biên soạn để dạy mục tiêu, hay cho người học chọn nhánh sau lời giải? Đề xuất lúc chấm dùng nhánh đã duyệt, lúc học thêm có thể khám phá.

L15. Với một nước hợp lệ ngoài cây mà engine chưa kết luận kịp, bạn muốn chờ phân tích, tạm lưu để người duyệt xem, hay thử lại phương án khác? Đề xuất không chấm sai chắc chắn khi chưa có căn cứ.

L16. Điểm kết thúc bài muốn là đạt vật chất/mục tiêu, chiếu hết, hay đánh tới hết ván? Nêu riêng cho bài chiến thuật, kế hoạch vị trí và tàn cuộc.

L17. Khi sai ở bước cuối nhưng đã làm đúng các bước đầu, có ghi nhận từng phần trên dashboard không? Đề xuất lưu từng quyết định nhưng chỉ gắn Hoàn thành hình khi đạt điều kiện cuối.

L18. Retry sau lời giải nên bắt giải lại toàn hình hay chỉ checkpoint chưa hiểu? Đề xuất có cả hai nhưng đều mang nhãn luyện lại có hỗ trợ; không thay kết quả lần đầu.

#### Nguồn bài và duyệt

L19. Đợt nội dung đầu tiên bạn muốn chốt ở 6 lesson/24 puzzle tập trung Xe Pháo Mã, hay số khác? Đây là mục tiêu biên soạn mới, có thể giảm để duyệt kỹ hơn.

L20. Bạn có thể cung cấp bao nhiêu ván/hình có quyền dùng trong tuần đầu? Với mỗi nguồn chỉ cần mô tả loại file, số lượng, chủ đề, người cho phép và hạn gửi; đáp án chưa biết được để trống.

L21. Ai sẽ duyệt nhận định chiến thuật và lời giải trước khi xuất bản? Nếu chỉ mình bạn, nhịp khoảng 10 thế mỗi tuần trong V5 còn phù hợp không?

L22. Có chấp nhận bài tự dựng được ghi rõ nguồn và chờ duyệt để lấp các nhóm còn thiếu không? Điều kiện tối thiểu đề xuất là qua luật, engine có log và người biên tập duyệt.

L23. Bài do người chơi đóng góp cần được xin phép chia sẻ riêng ở thời điểm nào: khi gửi ván, khi đề nghị lấy một thế, hay trước lúc xuất bản? Đề xuất kho riêng mặc định, xin phép trước khi đưa lên kho chung.

L24. Bạn muốn tự biên tập bằng đặt quân trên bàn, dán FEN/biên bản, hay cả hai? Chọn thao tác ưu tiên cho bản đầu: nhập nguồn, đặt câu hỏi, sửa nhánh, preview, gỡ bài.

#### Ôn và thống kê

L25. Với một bài nhiều lượt, bài ôn yêu cầu giải lại cả cây, một nhánh được chọn hay chỉ điểm từng vướng? Đề xuất một nhánh có ý nghĩa, xoay nhánh giữa các lần ôn và ghi rõ mức đã kiểm tra.

L26. Khi hết bài cùng chủ đề chưa gặp, ưu tiên đề nghị chủ đề khác, tạo hình từ ván của người học sau xác minh, hay luyện lại? V5 đã muốn nói rõ hết bài; câu này cần xếp thứ tự để recommendation thực hiện nhất quán.

L27. Trong dashboard, ba thông tin nào bạn muốn nhìn đầu tiên: bài đến hạn, nhánh đang học, tự giải hình mới, nhớ lại sau thời gian, bài có hỗ trợ, hay số hoạt động? Không dùng một tỷ lệ tổng trộn các loại bằng chứng.

L28. Khi có bài bị sửa đáp án, bạn muốn thông báo trong tài khoản hay ngay lúc mở bài ôn? Đề xuất tạm loại kết quả bị ảnh hưởng khỏi thống kê trình độ, giữ lịch sử cũ và chỉ cập nhật lịch sau khi người vận hành duyệt.

#### Kiểm chứng đợt phát hành

L29. Ai có thể thử bộ bài đầu tiên và họ đã biết chơi ở mức nào? Chỉ ghi người đã đồng ý thử; không cần thông tin cá nhân công khai.

L30. Bạn chấp nhận tiêu chí mở bản mới là một vòng học nhiều lượt hoàn chỉnh và 24 bài được duyệt, hay ưu tiên số lượng khác? Đề xuất không mở nếu còn sai luật, lộ lời giải sớm, mất nháp hoặc mất lịch ôn.

L31. Với lời giải, bạn muốn bàn cờ chuyển từng nước, so sánh hai hình trước sau, hay cả hai? Đề xuất mặc định bàn cờ từng bước, phần giải thích ngắn theo node, mở rộng khi cần.

L32. Có ví dụ một bài giảng hoặc một sản phẩm bạn thấy dạy tốt để mô tả điều thích và không thích không? Chỉ dùng làm tham khảo cấu trúc; nội dung/ảnh phải có quyền nếu định đưa vào Cờ Chill.

### Gợi ý thứ tự công việc cho Claude

1. Ghi baseline 12 fixture/4 minh họa và giữ test cũ. Sửa đếm/lọc phase để không tạo cảm giác có hai kho khác nhau.
2. Thiết kế schema v2 và migration; thêm validator cây biến, editor và preview trên 2–3 bài nháp kiểm chứng thật.
3. Xây player nhiều lượt, checkpoint, save/resume, reflection, timeout/chưa kết luận, retry và scheduling. Chưa tăng số lượng đại trà trước bước này.
4. Tạo taxonomy và màn Hành trình học từ dữ liệu, thay chuỗi liên kết cố định; bổ sung family-aware recommendation.
5. Biên soạn đợt 6 lesson/24 puzzle hoặc mục tiêu chủ sở hữu duyệt, qua pipeline kiểm chứng; báo tiến độ theo trạng thái nội dung.
6. Kiểm thử người dùng, kiểm tra trên hình chuyển giao tách khỏi bài đã học, điều chỉnh nhãn mức khó có log. Không tuyên bố hiệu quả học đã được xác thực từ pilot nhỏ.

Tài liệu này không có bài cờ mới đã được chứng minh, không thay thế kết quả engine trên máy thật và không chứng minh tác dụng sư phạm. Nó xác định phần còn thiếu và cách xây để các tuyên bố sau này có bằng chứng kiểm tra được.

---

<!-- nguồn: reports/v6_work/UI_AUDIT.md -->

## Đánh giá giao diện Cờ Chill cho bản bàn giao V6

> Tài liệu lịch sử ngày 25/10/2026, dựa trên source và ảnh của đợt bàn giao
> lúc đó; không dùng làm đánh giá giao diện hiện tại.

Ngày kiểm tra 25/10/2026. Phạm vi là đọc mã và đối chiếu hai ảnh người dùng cung cấp; không sửa mã ứng dụng, không xuất bản, không thay đổi tài khoản hoặc hosting. Các đề xuất dưới đây là công việc cho vòng triển khai tiếp theo, không phải tính năng đã hoàn thành.

### 1 Nguồn đối chiếu và phạm vi xác minh

Nguồn chính mới nhất trong đợt audit là gói source do chủ sản phẩm cung cấp ngày 24/10/2026 (1.217 entry). Đã đọc danh mục và so sánh từng byte, không giải nén hoặc chạy mã bất kỳ trong ZIP. Cả 16 file dưới đúng prefix `xiangqi-ai/online-preview/` (15 file runtime và README) giống hoàn toàn thư mục `online-preview/` tại thời điểm đó.

ZIP còn có các bản cũ dưới `xiangqi-ai/deliverables/Co_Chill_VSCode_2026_10_17/online-preview/` và `xiangqi-ai/var/co-chill-web-source-gon/online-preview/`. Các bản đó có `app.js`, `index.html`, `learning.js`, `experience.js` cũ hơn. Bản deliverables được nhắc là nội dung snapshot đã kiểm tra, không còn là thư mục trong repository sau khi gộp tài liệu lịch sử vào `V6_PREVIOUS.md`. Claude phải chọn đúng thư mục nguồn chính, không lấy file đầu tiên tìm thấy khi tìm đệ quy.

Gói `deliverables/Co_Chill_GIONG_CHATGPTSITE_2026_10_24.zip` cũng có đủ 15 file runtime và tất cả giống từng byte với nguồn chính. Đây là cơ sở kiểm tra mã bản đã bàn giao. Chưa lấy lại file trực tiếp từ máy chủ công khai trong đợt đánh giá này; ảnh người dùng là bằng chứng về lỗi hiển thị thực tế.

### 2 Lỗi chữ tiếng Việt trong ảnh tài khoản

#### Những gì đã xác nhận

- `online-preview/v5-ui.js:103` chứa đúng chuỗi `Chưa kết nối máy chủ tài khoản`.
- Đã đọc UTF-8 toàn bộ file HTML/CSS/JS của `online-preview/`: tất cả đều ở dạng Unicode NFC, không có ký tự thay thế U+FFFD, không có dấu kết hợp Unicode rời. Vì vậy chưa có bằng chứng rằng lỗi này do lưu sai encoding hoặc chuỗi NFD trong mã nguồn.
- `online-preview/index.html:4` đã có charset UTF-8.
- `online-preview/style.css:21` đặt h1 bằng Georgia, Times New Roman, serif; dòng 22 đặt h2 bằng cùng nhóm font. h1 có letter-spacing âm 0,7 px; h2 không đặt letter-spacing riêng.
- Đã đọc bảng cmap của Georgia và Georgia Bold trên máy kiểm tra bằng Python standard library. Cả hai thiếu các ký tự ư U+01B0, ả U+1EA3, ế U+1EBF, ố U+1ED1, ủ U+1EE7 có trong câu trên. Các file Times, Arial, Segoe UI ở cùng máy có đủ ký tự của câu.

#### Kết luận và giới hạn

Có vấn đề thực về độ phủ tiếng Việt của font Georgia tại môi trường local; hiện tượng chữ/dấu lệch trong ảnh phù hợp với khả năng trình duyệt phải thay font hoặc dựng tổ hợp dấu. Tuy nhiên chưa đọc được mục Rendered Fonts/computed style của đúng tab trong ảnh, nên chưa khẳng định duy nhất cơ chế browser gây lỗi. Không nên báo đã sửa chỉ bằng cách gọi normalize NFC: chuỗi hiện tại đã NFC.

#### Hướng xử lý cụ thể

1. Dùng font tiêu đề có đủ tiếng Việt. Quyết định bảo trì đơn giản nhất là dùng cùng Segoe UI/Arial/sans-serif cho các tiêu đề chức năng; có thể giữ chữ thương hiệu bằng ảnh logo đã có. Nếu muốn một font serif riêng, dùng bản font có đủ Vietnamese subset, giấy phép rõ, được lưu kèm dự án thay vì phụ thuộc font cài trên máy người xem.
2. Tập trung token `--font-ui` và `--font-heading`, áp dụng h1/h2/brand có chủ đích; không thay font chữ Hán của quân cờ một cách mù quáng.
3. Chạy trang mẫu chữ `Cờ tướng — kết nối — Nguyễn — luyện tập — đường đi — quyền quản trị — tướng, sĩ, tượng, xe, pháo, mã, tốt` ở normal/bold và cả ba theme. Kiểm tra bằng ảnh thật trên Chrome/Edge Windows và Safari/iOS hoặc thiết bị tương đương có người kiểm thử.
4. Mở DevTools kiểm tra font thực được dùng và chữ còn thiếu, kiểm tra không có CSS từ extension/bản cũ xen vào. Nếu chọn font mới, lưu file license và kiểm thử khi font tải thất bại.
5. Kiểm tra độ cao dòng tiêu đề, cắt dấu phía trên/dưới, phóng to 125/200 phần trăm, tránh đặt height cố định cho vùng chữ.

Nghiệm thu: không có dấu tách, ô vuông, chữ trộn font bất thường ở các chuỗi tiếng Việt mẫu; chữ không bị cắt ở cả 3 theme; không đổi luật chơi hay ngắt trạng thái phiên học.

### 3 Trang chủ bị bó chữ thành cột hẹp

#### Căn cứ trong mã

- `online-preview/style.css:67` giữ `.home-intro` căn giữa và max-width 740 px của bố cục cũ.
- `online-preview/v5.css:5` thêm padding-right 44 phần trăm vào cùng khối; dòng 6 đặt cover position absolute, width 40 phần trăm và height 260 px.
- Padding phần trăm được tính theo chiều rộng khối chứa. Kết hợp max-width cũ và padding lớn làm phần dành cho tiêu đề bị hẹp. Ảnh người dùng cho thấy đúng hậu quả: nhiều dòng ngắn và khoảng trống giữa chữ với cover.
- `style.css:269–271` thay đổi font và bỏ br ở desktop nhưng không giải quyết chỗ chứa chữ quá hẹp. `v5.css:19` chỉ chuyển về bố cục một cột khi viewport không quá 900 px, để lại nhiều độ rộng trung gian chưa tối ưu.
- Cover nguồn có tỷ lệ 1536 × 1024 nhưng đang ép object-fit cover trong ô có tỷ lệ biến đổi; nội dung ảnh có thể bị cắt khi card hẹp.

#### Hướng sửa

Chuyển hero thành CSS Grid có hai phần thật: `home-copy` và `home-visual`, bỏ padding giả lập cột và absolute positioning. Desktop dùng hai cột minmax(0, 1fr), gap khoảng 24–40 px theo chiều rộng container. Mobile xếp một cột; nội dung và nút tiếp tục phải xuất hiện sớm, ảnh không đẩy thao tác chính xuống nhiều màn hình. Không tiếp tục chồng thêm media query lên quy tắc lỗi cũ.

Đề xuất copy ngắn để người dùng duyệt: tiêu đề `Chơi cờ, hiểu từng nước.`; mô tả `Chơi một ván hoặc tiếp tục bài học của bạn.`. Giữ một CTA động theo quyết định V5 đã có: tiếp tục ván đang chơi, rồi ôn đến hạn, rồi bài đang dở, rồi bắt đầu. Bốn ô chính Chơi cờ, Bài học, Ván của tôi, Ôn tập vẫn giữ; không đặt thêm nhiều CTA cạnh tranh ngang hàng trên hero.

Visual chính ưu tiên bàn cờ nhỏ từ FEN hợp lệ hoặc cover thương hiệu có tỷ lệ cố định, không dùng một ảnh to chứa lại logo với nội dung gần giống header nếu nó không giúp hiểu hành động. Ảnh trang chủ trang trí không được làm lộ đáp án bài đang dở.

Nghiệm thu: tại 1024/1280/1440/1920 CSS px, tiêu đề không bị ép thành 5–6 dòng ngắn như ảnh; không có khoảng trống do absolute image; tại 360/390/768 px và zoom 200 phần trăm, không tràn ngang, nút chính và chữ không bị ảnh che. Tối đa 2–3 dòng tiêu đề trên desktop là mục tiêu thiết kế, không ép giữ nếu người dùng phóng chữ lớn.

### 4 Ba theme đã có nhưng khó tìm

#### Trạng thái thực tế

- `online-preview/experience.js:8–12`: bộ tùy chọn warm/cool/dark và kiểm tra giá trị hợp lệ.
- `online-preview/app.js:162`: Cài đặt có select Chủ đề với Sáng ấm, Trắng lạnh, Tối và nút Lưu tùy chọn.
- `online-preview/app.js:160`: áp dụng data-theme và lưu tùy chọn vào localStorage.
- `online-preview/style.css:3–11` có palette, sau đó `v5.css:15–16` lại ghi đè cool/dark. Có hai nơi định nghĩa cùng theme, dễ sửa thiếu hoặc lệch màu.
- `style.css:233–239` đã có CSS theme-picker/theme-swatch, nhưng form cài đặt hiện dùng select, không dựng ba ô xem trước tương ứng.
- `tools/test_v5_ui.cjs:74–121` có kiểm thử lưu theme và cô lập preference theo tài khoản; đây là kiểm thử logic, không thay thế thử hình ảnh/độ tương phản.

Không nên viết `chưa làm 3 theme`. Công việc đúng là tăng độ dễ tìm, đồng bộ token, sửa và nghiệm thu đủ thành phần.

#### Hướng sửa

Đặt nút Giao diện có biểu tượng tại header hoặc menu avatar, dẫn tới ba ô màu có tên rõ. Trong Cài đặt hiển thị cả ba thẻ preview, trạng thái chọn có dấu tick và aria-pressed hoặc radio chuẩn; người dùng nhìn thấy kết quả ngay khi chọn. Nếu lưu cloud thất bại vẫn giữ nháp local, hiện trạng thái thật; không lẫn preference của tài khoản khác.

Gộp palette vào một nguồn định nghĩa duy nhất. Kiểm tra button, disabled/focus, input/error, board, quân Đỏ/Đen, mũi tên, bảng, modal, account status. Không đổi nghĩa màu đỏ lỗi và nước bị chiếu qua theme. Hình minh họa nên dùng SVG theo token hoặc ảnh có nền trong suốt để không tạo mảng trắng chói trên nền tối.

Nghiệm thu: từ bất kỳ trang chính, tối đa hai thao tác để thấy ba lựa chọn; đổi theme và tải lại vẫn đúng; đổi tài khoản không lấy nhầm theme; chữ và điều khiển có tương phản đủ đọc; focus không chỉ dựa vào màu.

### 5 Ít chữ hơn nhưng thông tin học vẫn đầy đủ

Ba loại hình có mục đích riêng:

1. Icon điều hướng tự dựng SVG, có nhãn chữ ngắn. Chỉ icon không có tên dễ làm người mới đoán sai.
2. Sơ đồ bàn cờ dựng từ FEN hợp lệ cho bài học, bài tập, ván cũ. Cùng một renderer với bàn chơi giúp kiểm chứng quân và vị trí; không dùng hình tạo sinh làm nguồn sự thật luật cờ.
3. Minh họa thương hiệu từ logo/cover người dùng đã cung cấp hoặc tài sản có quyền rõ. Dùng tiết chế cho trạng thái trống, chào mừng, tổng kết; không che bàn cờ.

Chia thông tin theo nhịp: trước khi làm có tên bài, mục tiêu một câu và bàn cờ; sau phản ánh mới mở lời giải; trong lời giải mỗi bước có thế trước/sau, mũi tên hợp lệ và 1–2 câu. Phần căn cứ engine, độ sâu, nguồn bài nằm trong mục Chi tiết, vẫn truy cập được khi cần. Không giấu thông tin bắt buộc như chưa lưu/engine lỗi/đang dùng fallback.

Không dùng nhãn `đã hiểu` khi người chơi chỉ bấm xem hết; không biến minh họa thành coaching trong ván trực tiếp. Thumbnail bài chưa giải không vẽ sẵn mũi tên đáp án.

### 6 Đề xuất theo từng trang

#### Trang chủ

Hero grid mới, bốn card chủ chốt và một ô tiếp tục. Dùng mini-board hoặc biểu tượng theo hoạt động. Ẩn số 0 vô nghĩa với người mới, thay bằng gợi ý bắt đầu có thể thao tác. Người quay lại thấy ván/bài dở đúng trạng thái.

#### Chơi

Ba lựa chọn rõ: Với máy, Cùng bạn trên thiết bị, Trực tuyến. Chỉ mở Trực tuyến khi backend PvP có thật; trước đó ghi Sắp có ở mức roadmap, không tạo nút vào trận giả. Mức máy, thời gian và màu quân gọn trong panel; bàn cờ chiếm ưu tiên. Khi chơi không hiển thị eval/hint/lời giải. Điều khiển hòa, xin thua, mất kết nối cần xác nhận đúng hành vi và không che bàn.

#### Bài học và thư viện puzzle

Hiện `app.js:64` chỉ có ba tab giai đoạn và danh sách chữ; tab trung/tàn dùng lại cùng kho hình mẫu. Đổi sang card có thumbnail FEN, chủ đề, mục tiêu, độ khó tạm tính, độ dài dự kiến và trạng thái đã học. Bộ lọc nhiều chiều phải thật sự lọc dữ liệu; không chỉ đổi tiêu đề trang.

Chủ đề quân Xe/Pháo/Mã/Tốt/Sĩ/Tượng/Tướng là một chiều; chiến thuật, giai đoạn và mức khó là các chiều khác. Không ép một bài chỉ thuộc đúng một quân khi nó cần phối hợp Xe–Pháo. Đường học có bài giảng → ví dụ tương tác → bài tự làm → bài chuyển giao → ôn; số bài thực đã duyệt được hiển thị đúng.

#### Hành trình học

`app.js:164` hiện bốn node dẫn tới luật, bài học, chơi, ôn; không phải curriculum. Đổi thành các chương có quan hệ tiên quyết và node kỹ năng. Mỗi node có biểu tượng/mini-board, tên, mục tiêu ngắn, số bài, tiến độ, nút tiếp tục. Trang chi tiết chương mới chứa nội dung dài. Chưa chốt ngưỡng mastery thì cho học tự do và gợi thứ tự, không khóa giả theo EXP.

#### Màn học và lời giải

Giữ ba phần tự phản ánh và nước ứng viên đã chốt V5. Giảm cảm giác form dài bằng một câu hỏi chính mỗi bước hoặc nhóm câu gọn có chỉ báo 1/3, nhưng giữ được nháp và quay lại. Khi mở đáp án, có nút đi từng nước, đánh dấu thay đổi và đối chiếu suy nghĩ đầu với nguyên nhân cụ thể. Cần trả lời V6 về một màn/ba bước, không hỏi lại có phản ánh trước đáp án hay không.

#### Ván của tôi và xem lại

Card ván có thế cuối hoặc điểm đáng học làm thumbnail; thông tin đối thủ, kết quả, ngày, nguồn, trạng thái phân tích. Màn replay ưu tiên bàn + timeline. Danh sách điểm đáng học dùng thumbnail và lý do ngắn, không dồn mọi PV/CP vào một trang chữ. Phân tích chưa xong phải hiển thị tiến độ và cho hủy.

#### Ôn tập

Hiển thị bài đến hạn thành card ngắn, số bài còn lại, thời gian ước tính có nhãn ước tính. Bài bị hoãn sau ba lần thất bại vẫn là cần học tiếp; không mang biểu tượng đã hoàn thành. Trong bài ôn không có thumbnail gợi đáp án. Giữ mốc tính lịch từ hoàn thành theo V5.

#### Tiến độ và tổng kết

Dùng biểu đồ cột kỹ năng, lịch hoạt động, node đã hoàn tất; nhãn phân biệt tự giải/có hỗ trợ. Kèm số lượt làm mẫu số thật, dữ liệu còn ít thì nói rõ. Tránh radar/Elo suy diễn chính xác từ vài bài. Cuối phiên có ô tự đánh giá đã chốt, không bắt người dùng nhập đoạn dài để thoát.

#### Tài khoản

Ảnh đang hiển thị trạng thái API chưa kết nối, phù hợp bản static. Giữ trạng thái trung thực; đổi lời người dùng sang `Bạn đang dùng chế độ khách. Tiến độ được lưu trên trình duyệt này.` và CTA tiếp tục học. Chi tiết “API, máy chủ tĩnh, backend” chuyển vào hỗ trợ/chế độ kỹ thuật. Khi backend thật có sẵn, trang mới hiển thị đăng nhập/đăng ký và trạng thái lưu rõ. Không hiển thị hứa đồng bộ đa máy như đã hoạt động khi API không có.

#### Cài đặt

Ba thẻ theme preview, xem trước chữ Hán/Việt trên quân, cỡ chữ có ví dụ. Dữ liệu xuất/xóa ở nhóm riêng; nút xóa có xác nhận và mô tả phạm vi. Không làm mới cả app khiến người chơi mất vị trí sau khi chọn theme.

#### Luật và trợ giúp

Mỗi quân có sơ đồ nước đi, vị trí bị cản, ví dụ đúng/sai; bắt người học thử một thao tác nhỏ thay vì đọc hết bài dài. Luật chiếu/đuổi/lặp phải chờ nguồn và tình huống được duyệt, không dùng infographic đẹp để che sự chưa hoàn chỉnh. FAQ mở dần, hỗ trợ hiển thị đúng cách liên hệ đã được chủ sản phẩm xác nhận.

#### Quản trị và biên tập

Tách màn dành cho chủ website khỏi học viên. Hàng bảng quản trị cần lọc/tìm kiếm/phân trang; preview bài phải dùng cùng component với học viên và cảnh báo đáp án chỉ trong preview admin. Dữ liệu bản nháp/published/version không được giấu khi giao diện rút gọn.

### 7 Danh mục tài sản cần tạo

- Một bộ icon SVG thống nhất stroke cho bốn khu vực chính và các chủ đề quân.
- Thumbnail FEN tự sinh, tái dùng renderer; lazy-load theo trang để không dựng hàng trăm bàn cùng lúc.
- Trạng thái trống có minh họa nhỏ cho chưa có ván, chưa có bài đến hạn, chưa có kết quả lọc; kèm hành động cụ thể.
- Mini storyboard ba bước cho hướng dẫn học: tự nghĩ, xem lời giải có căn cứ, luyện lại. Hình không chứa biến cờ chưa xác minh.
- Biểu đồ tiến độ dùng dữ liệu thật. Không làm ảnh tĩnh giả biểu đồ hoạt động.
- Tài sản phải lưu tên, nguồn, giấy phép/quyền, tác giả và nơi dùng. Không sao chép ảnh của website cờ khác chỉ vì đã tham khảo phong cách.

### 8 Thứ tự triển khai UI đề nghị

1. Sửa font tiếng Việt và hero layout trước; chụp so sánh đúng hai màn người dùng báo.
2. Gộp theme tokens và làm theme picker dễ tìm; kiểm thử lưu preference/cô lập tài khoản không bị hồi quy.
3. Tạo component mini-board và card nội dung; xây thêm curriculum data rồi mới dựng trang chủ đề/level, tránh UI nhiều ô rỗng.
4. Giảm chữ trên tài khoản/học/ôn theo trạng thái thực; kiểm tra gate phản ánh và không coaching ván đang chơi.
5. Thêm biểu đồ/illustration đúng dữ liệu, kiểm thử tải mạng chậm và thiết bị cảm ứng.
6. Nghiệm thu cả luồng học, đăng nhập, theme, đồng bộ và điều hướng sau deploy. Không xem 1 ảnh đẹp là đủ nghiệm thu toàn website.

### 9 Ma trận nghiệm thu giao diện

Viewport đề nghị: 360 × 800, 390 × 844, 768 × 1024, 1024 × 768, 1440 × 900 và 1920 × 1080 CSS px; thực tế phải ghi rõ viewport và tỷ lệ zoom của ảnh bằng chứng. Theme warm/cool/dark; cỡ chữ normal/large; zoom 100/125/200 phần trăm; khách, đăng nhập, offline, loading, empty/error và nhiều nội dung.

Kiểm tra: không tràn ngang toàn trang; không che focus; bàn 9 × 10 không méo; chạm được quân/ô ở màn nhỏ; popup và bàn phím ảo không che câu đang nhập; câu hỏi không mất khi đổi tab/reload; ảnh có alt phù hợp; decorative image alt rỗng; nút icon có accessible name; animation tôn trọng reduced motion; màu không phải tín hiệu duy nhất cho đúng/sai.

Cần bổ sung kiểm thử browser screenshot với các trang home/account/settings/lesson/learn/play/path, nhưng không viết snapshot chứa dữ liệu riêng người dùng. Các bài test logic hiện có vẫn phải giữ. Kết quả Unicode/font/ZIP trong báo cáo này là kiểm tra tĩnh, không được gọi là đã chạy thành công tất cả ma trận thiết bị.

---

<!-- nguồn: docs/DEPLOY_GCP_V6.md -->

## GCP V6 — ghi chú chuẩn bị cũ

Tài liệu ngày 26/10/2026 là bản chuẩn bị trước khi Production được triển
khai. Các đường dẫn, port, lệnh Gunicorn và bước DNS của bản cũ không mô tả
Production hiện tại; không dùng tài liệu này để thay cấu hình VM.

Theo thông tin chủ dự án ngày 31/10/2026, `cochill.vn` đã chạy trên GCP VM
Ubuntu 24.04, source ở `/var/www/html`, Python 3.12 trong `.venv`, systemd
`cochill.service` với `serve --host 127.0.0.1 --port 8000`, Nginx HTTPS và
SQLite trên đĩa bền. Production dùng một process; trạng thái phòng và
semaphore Pikafish không được thiết kế cho nhiều worker/replica.

Để cập nhật code, xem log, sao lưu/khôi phục, gia hạn chứng chỉ, quản lý TOTP
và chuyển Gunicorn tùy chọn, dùng
[hướng dẫn Production hiện hành](../deploy/DEPLOY_GCP_VI.md). Thông tin này
dựa trên xác nhận của chủ dự án; chưa kiểm tra trực tiếp VM, chứng chỉ, backup
thực tế hoặc binary Pikafish/NNUE.

---

<!-- nguồn: docs/CLAUDE_HANDOFF_V6.md -->

## Bàn giao Claude — Cờ Chill V6, 26/10/2026

### Bắt đầu từ bản này

Đọc AGENTS.md → README.md → docs/V6_DECISIONS.md → KNOWN_LIMITATIONS.md.
Pack không có dữ liệu cá nhân, khóa, binary Pikafish,
NNUE hay lịch sử Git. Giữ repository cũ để đối chiếu; không force push.

Entry point: `python co_chill_server.py serve --port 8769`. Không dùng
`legacy/server.py` (local-only), không chỉ chạy `http.server` nếu cần
tài khoản/PvP.
Frontend không có npm build; toàn bộ script nạp theo thứ tự trong index.
Backend standard library, WSGI + SQLite; Gunicorn chỉ dùng khi deploy Linux.

### Ranh giới code

- Luật: `app/rules.py` và `online-preview/xiangqi.js`, test parity bằng tool.
- Bằng chứng phân tích: `app/pikafish.py` và `engine-client.js`. Kiểm tra mọi
  PV hợp lệ, góc nhìn điểm, mate/cp và bound; không để LLM tự chế nước/điểm.
- Phiên học cũ: `learning.js` + `experience.js`; nhiều lượt: `line-practice.js`.
  `curriculum.js` chứa nội dung và cây đáp án; frontend source vẫn đọc được
  đáp án, không coi reflection gate là cơ chế chống xem source.
- Persistence: luôn `save()`/cloud client; không tự tạo key localStorage chung
  cho mọi tài khoản. `state.lineSession`, `lineAttempts`, `lessonViews` đã có
  sanitize/replay. Xem bài không phải hoàn thành/đạt trình độ.
- UI bổ sung: v5-ui (account/admin), online-play (PvP), v6-learning-ui,
  v6-ui (presentation) theo thứ tự. Khi thay render, giữ các lớp bảo vệ;
  học phải tôn trọng activeGame và CCOnline live guard.
- PvP: server giữ room/game/revision/nonce/clock; không lấy whole client JSON
  làm ván chính thức. Review phải khớp `online-<gameId>` đã kết thúc trên server.
- Một instance/worker: engine semaphore và lifecycle phòng có scope process.
  Chưa được tăng nhiều worker/replica mà không thiết kế lại điều phối.

### Các phần cần ưu tiên

1. Xác minh GCP/Pikafish qua quyền riêng: version, path, NNUE, UCI handshake,
   search hai bên, timeouts, load. Không dùng URL Console như API.
2. Email recovery: verified email, token ngẫu nhiên một lần có hạn, chống
   dò tài khoản, rate limit, thu hồi phiên, provider gửi thư chỉ backend.
   Không log token, không dùng mật khẩu gửi qua mail. Cần owner duyệt dịch vụ.
3. Nhập tiến độ riêng có preview/dry-run, schema/version, validation và chọn
   merge; không nhập answer keys hoặc quyền admin. Bảo toàn cô lập tài khoản.
4. Phát triển nội dung trung/nâng cao thật: FEN + cây biến + tiêu chí chấm +
   nguồn/quyền + bằng chứng engine + người duyệt. Hai bài hiện cùng họ chiến
   thuật, không đủ tuyên bố coverage hoặc trình độ chương.
5. LLM explanation dùng schema từ evidence; thất bại chuyển template có nhãn.
   Không sinh nước, nhận định không có căn cứ hay chấm khả năng chỉ từ độ dài
   câu trả lời. Cần rubric, tập kiểm thử và đồng ý dữ liệu trước gửi provider.
6. 7 cấp bot, hàng đợi ưu tiên bot, deadline10s, chính sách10 ván: cần kiểm tra
   thực tế, không gán Elo. Nghiệm thu mất engine không trừ thời gian người chơi.
7. Tiếng Anh còn thiếu, auto-flip local, drawing answers, public profile,
   calendar/dashboard, luật lặp/chiếu đuổi, chat có quản trị và retention phòng.

### Hợp đồng phát hành

Chạy `python tools/run_checks.py`, browser E2E, đọc diff,
rồi tạo pack mới bằng `tools/build_v6_pack.py`. Không bỏ hoặc làm yếu test
đang fail. Kiểm tra pack sau giải nén ở thư mục mới; hash khớp không thay thế
test chạy. Không tự deploy/push/DNS/chi tiền/chuyển DB thật khi chưa được chủ
sản phẩm duyệt. Không xóa tài liệu gốc hoặc dữ liệu của người chơi.

### Demo 60 giây khi chưa có Pikafish

Vào khách → Hành trình học → một chương/bài → bài nhiều lượt. Tự trả lời ba
câu, thử nước, xem đối thủ đáp, hoàn tất chuỗi rồi mở giải thích. Hoàn thành
và thấy lịch ôn, reload để kiểm tra lưu. Một cửa sổ ẩn danh khác tạo khách
phòng PvP để thử kết nối cùng server. Đây là minh họa local, không xác nhận
khả năng chơi Internet hay sức cờ engine thật.

---

<!-- nguồn: reports/IMPLEMENTATION_REPORT_CODEX.md -->

## Báo cáo triển khai V6 — 26/10/2026

> Tài liệu lịch sử về các lượt ngày 26–27/10/2026; không mô tả trạng thái
> hiện tại của `codex-full`. Dùng README và KNOWN_LIMITATIONS.md cho thông tin
> hiện hành.

### Chỉnh giao diện bàn chơi và phản ánh — 27/10/2026

- Thêm style V6 có phạm vi cho trang chọn chế độ, khung bàn cờ/đồng hồ/biên
  bản ván và form ba câu suy nghĩ trong `online-preview/v6.css`. Giữ nguyên
  luồng chơi, luật, nội dung, reflection gate, account persistence và API.
- Kiểm tra giao diện trong browser qua server local dùng SQLite thử riêng:
  chơi với máy và màn phản ánh. Đã xem ở 1280x900 và 390x844; màn phản ánh
  không tràn ngang (document width 375px ở viewport 390px). Không dùng dữ liệu
  tài khoản thật. Đây là kiểm tra giao diện thủ công, không phải E2E toàn bộ.
- Hệ thống tài khoản đã có trong source: SQLite `users`/`sessions`/`states`,
  hash scrypt, session một user/phiên với thời hạn 7 ngày, state sync theo
  revision và cache account tách theo user ID ở browser. Không thay đổi
  backend vì chính sách multi-session, email recovery, backup/retention và
  hành vi xóa dữ liệu cần chủ sản phẩm chốt.
- Kiểm tra mới: 104 test Python đạt trong phần Python của runner; checker
  fixture đạt. Full runner không hoàn tất do môi trường chỉ có Node.js 6.14.0
  (không hỗ trợ cú pháp hiện dùng trong dự án); xem TEST_REPORT_CODEX.md.

### Bổ sung sau khi đối chiếu C/E — 26/10/2026

- Tại C, giữ kết nối SQLite `db=db` để xóa dữ liệu phòng và tài khoản trong cùng transaction; thêm helper `delete_identity_in_db` cho tác vụ dọn tài khoản cũ, kiểm tra kiểu dữ liệu preset/lời nhắn/đối tượng mời rời và không cho người chơi rời ghế khi ván đang tạm dừng.
- Thêm regression tests cho payload dạng array/object, rời phòng paused, lỗi HTTP không thành TypeError và rollback nếu xóa tài khoản lỗi sau khi đã dọn dữ liệu phòng.
- Giữ bộ 12 fixture của C vì checker hiện tại xác nhận 12 thế synthetic và toàn bộ nước hợp lệ; không nhập 12 fixture chỉ có ở E khi chưa có nguồn và kiểm chứng tương ứng.
- `python tools/run_checks.py` trên C: 104 bài Python, fixture/parity, cú pháp toàn bộ JavaScript và các bộ test JavaScript đều đạt. Môi trường kiểm tra: Python 3.14.2, Node.js 22.23.4. Lần chạy đầu gặp một lỗi timeout nhạy thời gian trong test Pikafish; test đó đạt khi chạy riêng và toàn bộ lượt chạy lại đạt.
- Không cập nhật mã ở E. Trạng thái Git ban đầu tại C được ghi lại trước khi tạo nhánh; các thay đổi đang dở vẫn còn nguyên và chưa được commit. Xem [TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md).

### Kết quả thực tế

Gói source tiếp tục từ repository V5 và ZIP chủ sản phẩm gửi ngày24/10.
Không rewrite toàn bộ, không deploy ChatGPT Site/cochill.vn, không push GitHub,
không thay DNS hoặc tạo hạ tầng trả phí. Gói để chủ sản phẩm cập nhật repository
và tiếp tục với Claude. Phần chưa đáp ứng V6 ghi ở KNOWN_LIMITATIONS.md và
docs/V6_DECISIONS.md; hoàn thiện pack không có nghĩa hoàn tất toàn bộ roadmap.

### Đã xây/cập nhật

- Giao diện: font không chân, cover rộng, chọn tài khoản/khách, thẻ3 theme,
  hỗ trợ English một phần giao diện. Giữ ảnh do chủ sản phẩm cung cấp.
- Nội dung: 3 khóa/7 chương,8 bài hướng dẫn và2 bài nhiều lượt bổ sung cho12 bài cơ
  bản. Bài có bàn cờ ví dụ/phát lại, provenance và giới hạn rõ.
- Nhiều lượt:3suy nghĩ ban đầu, nước ứng viên, phản ứng đối thủ từ cây kiểm
  tra luật, retry,3 lần sai hẹn lại, nhánh ngoài cây chưa chấm sai, explanation,
  hoàn thành một lần, bài liên quan, lịch ôn và self-report. Lưu/khôi phục nháp
  theo tài khoản, không coi xem bài là mastery.
- PvP: backend giữ trạng thái/luật/đồng hồ; guest hoặc account tạo/join/watch,
  phòng công khai/riêng và match theo preset,ready,hòa,đi lại,đầu hàng,tái đấu,
  khán giả/chat mẫu, history riêng. UI polling và nối đầy đủ API.
- Account V5 được giữ: scrypt,cookie,CSRF,role,TOTP,revision/conflict.
  Sửa transfer guest để không bỏ sót hoặc ghi đè tiến độ chỉ có bài nhiều lượt.
  Admin metrics bổ sung bài nhiều lượt, dedupe, không nâng proficiency giả.
- Sửa test TOTP phụ thuộc đồng hồ thật: giữ đúng mã phát lại và thêm ca mã
  mới ở bước thời gian kế tiếp; giữ nguyên bảo vệ xác thực production.
- Engine: thêm requireStrong để lỗi Pikafish không thành kết quả heuristic
  giả mạnh. Bot server/review tài khoản dùng chế độ này. Guest intermediate
  được hướng dẫn đăng nhập/dùng bài kiểm chứng thay phân tích nông.
- Công cụ: run_checks.py, builder V6 allowlist, verifier manifest/path/hash;
  hướng dẫn GitHub/Claude/GCP và báo cáo cập nhật.

### Kiến trúc

Frontend HTML/CSS/JavaScript không bundler; Python WSGI + SQLite cho API.
Luật hai phía có test parity. Browser phân lớp app cũ + UI mở rộng, shared
save/cloud boundary. Server chỉ phục vụ assets trong online-preview.
Pikafish qua subprocess UCI cùng máy; không nhận lệnh shell/path từ client.
Một worker nhiều thread cho pilot; không tự mở rộng đa process.

### File thay đổi chính

- online-preview/index.html,app.js,v5-ui.js,learning.js,experience.js,
  engine-client.js: nối modules, guard, lưu dữ liệu, export và engine.
- online-preview/v6-ui.js,v6.css: presentation/theme/language.
- online-preview/curriculum.js,line-practice.js,v6-learning-ui.js: chương,
  state machine bài nhiều lượt và màn học.
- online-preview/online-play.js: lobby/phòng/chơi/xem/history.
- co_chill_server.py,app/online_rooms.py,app/cloud_store.py: API/PvP/metrics.
- tests/test_online_rooms.py,test_online_http.py,test_cloud.py: regression.
- tools/test_v6_*.cjs,test_engine_client.cjs,test_v5_ui.cjs: test UI/learning.
- tools/run_checks.py,build_v6_pack.py,verify_source_pack.py: kiểm tra/đóng gói.
- README,AGENTS,CLAUDE,docs và các báo cáo: cấu trúc/run/handoff/quyết định.

Manifest trong ZIP là danh sách chính xác từng file/byte/hash. Không có DB,
log,secret,.git,node_modules,tài liệu trả lời cá nhân hoặc ZIP cũ lồng bên trong.
Tài liệu V3–V5 đã được tinh gọn trong `V6_PREVIOUS.md`; Final Pack gốc trong
`docs/spec/` và `docs/materials/` được giữ nguyên. Dữ liệu local trong `var/`
không bị đụng tới. Runtime legacy vẫn tách riêng và không phải entry point V6.

### Kiểm thử và lệnh

Chi tiết kết quả ở TEST_REPORT_CODEX.md. Các lệnh thực hiện gồm:
python -m unittest (bộ core và legacy), Python compile, node --check,
tools/check_online_preview.py,tools/check_browser_rules.py,các test JS,
tools/run_checks.py,browser Chrome với database thử riêng,build_v6_pack và
verify_source_pack. Browser E2E đi qua cả học4 quyết định và PvP2 cửa sổ.
Môi trường hạn chế socket phải cấp quyền local cho kiểm thử; không yếu test.

Không có eslint/tsc/npm build vì dự án chưa dùng các hệ đó. Syntax và hành
vi được kiểm tra bằng công cụ được đóng trong pack; không báo lint giả.

### Real / fallback / pending

| Phần | Trạng thái |
|---|---|
| Luật, API tài khoản, SQLite, PvP | Code chạy/test local thật; chưa nghiệm thu Internet |
| UCI adapter | Có; test protocol bằng tiến trình giả |
| Pikafish VM của chủ sản phẩm | Chưa kiểm tra binary/NNUE/kết nối thật |
| Máy cơ bản | Tìm kiếm heuristic có nhãn, không Elo/ML |
| Explanation | Template có căn cứ, chưa LLM |
| Bài/cây đáp án | Tự dựng, kiểm tra luật/mục tiêu hữu hạn; chưa chuyên gia duyệt |
| Thống kê và ôn | Quy tắc/client state, không bằng chứng hiệu quả giáo dục |

Nguồn dữ liệu: đặc tả/câu trả lời chủ sản phẩm, ảnh thương hiệu chủ sản phẩm,
các thế cờ synthetic của dự án. Không scrape, không dùng ván người chơi để
huấn luyện. Quyền ảnh/tài liệu và license code cần chủ sản phẩm xác nhận;
Pikafish/weights không được phân phối kèm.

### Chạy ngày mai và demo

Trong thư mục giải nén: `python co_chill_server.py serve --port 8769`.
Mở http://127.0.0.1:8769. Giữ terminal. Tests: `python tools/run_checks.py`
(cần Node). GitHub: docs/GITHUB_V6_CHO_NGUOI_MOI.md.

Demo60 giây: vào khách → Hành trình → bài nhiều lượt → trả lời3 câu và chọn
nước → đối thủ đáp → hoàn tất → explanation/phát lại → ghi nhận → lịch ôn.
Có thể chọn bài cơ bản nếu chưa giải được; không bật đáp án trước suy nghĩ.
PvP dùng hai cửa sổ/hồ sơ tách biệt trên cùng server để tạo/join/ready/chơi.
Chạy Internet cần triển khai và nghiệm thu GCP riêng.

### 5 khái niệm nên học

1. Frontend hiển thị/thao tác; backend kiểm quyền và giữ sự thật dùng chung.
2. Database khác source; Git giữ code, không nên giữ dữ liệu người chơi.
3. State machine giữ các bước suy nghĩ/practice/explain/finish không bị nhảy.
4. Engine/rules cung cấp bằng chứng; LLM nếu thêm chỉ giải thích bằng chứng.
5. Test + version control + deploy là ba việc riêng: test đạt không tự
   publish, push không tự tạo server và copy source không copy tài khoản.

---

<!-- nguồn: reports/TEST_REPORT_CODEX.md -->

## Kiểm thử V6 — 26/10/2026

> Báo cáo lịch sử; các kết quả dưới đây không phải kết quả kiểm tra hiện tại
> của `codex-full`. Xem KNOWN_LIMITATIONS.md và chạy lại
> `python tools/run_checks.py` để xác nhận source hiện tại.

### Kiểm tra giao diện sau chỉnh sửa — 27/10/2026

- `python tools/check_online_preview.py`: PASS; 12 fixture synthetic, provenance
  và danh sách nước hợp lệ khớp luật.
- Phần Python của `python tools/run_checks.py --node "C:\path\to\node.exe"`:
  104/104 test đạt với Python 3.14.0.
- Không thể xác nhận JavaScript suite bằng Node trong PATH: phiên bản thực tế
  là 6.14.0, không hỗ trợ optional chaining/nullish coalescing dùng trong source;
  syntax checks và một số test dừng với `SyntaxError`. Runner kết thúc lỗi, sau
  đó còn gặp lỗi encoding Windows khi in lỗi ra console. Đây là giới hạn runtime
  kiểm thử, không ghi nhận là JavaScript suite đạt; cần chạy lại bằng Node.js
  phù hợp với README trước khi phát hành.
- Browser thủ công trên `http://127.0.0.1:8769/` với SQLite thử riêng: trang
  chơi với máy và form reflection hiển thị; đã xem desktop 1280x900 và mobile
  390x844. Trên mobile, document width 375px, không tràn ngang viewport 390px.
  API `/api/session` trả 200 cho khách. Không kiểm tra PvP, engine thật, luồng
  đăng ký user hoặc production trong lần này.
- Server dùng cho kiểm tra đã tách khỏi database mặc định/production. Kết quả
  browser là kiểm tra giao diện thủ công; không thay E2E, usability test hay
  kiểm thử account đầy đủ.

### Lượt xác minh sau đối chiếu — 26/10/2026

- Đã chạy `python tools/run_checks.py` tại workspace C với Python 3.14.2 và Node.js 22.23.4.
- Đạt: 104 bài Python; kiểm tra 12 fixture synthetic với luật và nước hợp lệ; parity/kiểm tra luật trên trình duyệt; cú pháp toàn bộ JavaScript; toàn bộ 10 bộ test JavaScript của runner.
- Chạy riêng `tests.test_online_rooms` và `tests.test_online_http`: 36/36 đạt; `tests.test_cloud`: 21/21 đạt.
- Bổ sung regression coverage cho preset/visibility/message/userId sai kiểu, payload không phải object, rời phòng paused và rollback giao dịch xóa tài khoản. Kiểm tra diff whitespace đạt.
- Lần chạy toàn bộ đầu tiên có một timeout trong test `test_untrusted_or_incomplete_engine_output_falls_back` của Pikafish; không đổi test hay logic để né lỗi. Test đạt khi chạy riêng và cả lượt đầy đủ chạy lại đạt.
- Gói nguồn mới gồm 91 file; manifest, SHA-256 và CRC được xác minh. Chạy lại runner trên bản đã giải nén ở thư mục tạm độc lập: cả 27 bước kiểm tra đạt, gồm 104 bài Python, fixture/parity, syntax và các bộ test JavaScript.
- Đây là kiểm tra local của source hiện tại; không phải browser E2E đầy đủ cho toàn bộ hành trình học/tài khoản/PvP và không xác nhận Internet, GCP, Pikafish/NNUE thật, cochill.vn, tải hoặc kiểm toán bảo mật.

### Phạm vi

Tests chạy trên source hiện tại; không xác nhận binary Pikafish thật, VM
Google Cloud, production HTTPS/DNS, hai mạng Internet, tải lớn hoặc kiểm toán
bảo mật. Không bỏ/giảm test để qua. Bộ legacy vẫn giữ trong repo gốc.

### Python

Core pack gồm 103 test: 30 rules, 22 cloud, 17 Pikafish adapter, 21 online rooms,
13 online HTTP. Runner cuối đã chạy một lượt đủ 103/103 đạt (436,190 giây).
Legacy 34 learning và 8 HTTP đạt;
8 HTTP ban đầu gặp WinError10013 vì localhost bị chặn, sau cấp quyền chạy lại
đạt8/8. Tổng145 Python test qua các lượt, không gọi là một lượt discover145.

Một test content từng báo fail ở lượt trước nhưng không còn traceback lưu;
hai test content đã qua lượt kiểm tra gần nhất. Không kết luận nguyên nhân
khi chưa có bằng chứng và không bỏ test. Gói dùng core103, không mang legacy.

### JavaScript và parity

155/155 test JavaScript đạt: học cơ bản 26; experience 20; notation 14
(4.054 roundtrip); cloud client 21; engine client 11; V5 UI 11; V6 UI 10;
V6 learning 19; V6 online UI 13; V6 learning UI 10. Kiểm tra syntax toàn bộ
14 file JS và compile Python đạt. Không có eslint/TypeScript/build riêng.

Fixture checker: 12 bài khớp luật. Parity Python/JS: 205 vị trí, 5.468 vị trí
con, 25 FEN cases, perft2=1.920, 12 thế engine/153 biến, 10 input sai: PASS.
Lệnh tái lập: `python tools/run_checks.py`, có thể truyền `--node PATH`.

### Trình duyệt thực

Chrome headless, database thử riêng, không dùng tài khoản/người chơi thật:

- Hai context guest: tạo/join/ready, đi quân đồng bộ, reload giữ màu/history,
  khóa bài học trong ván, hòa có chấp nhận, history riêng mỗi người.
- Tái đấu đổi bên/gameID, đầu hàng ghi kết quả mới. Không pageerror.
- Học:3 câu suy nghĩ nháp giữ qua reload, không hiện giải thích trước gate,
  đi4 quyết định có đối thủ đáp, xem/phát lại explanation, finish một attempt,
  lịch ôn sau completion, reload giữ tiến độ, mở bài liên quan và lịch ôn.
- Chọn theme cool và EN, viewport390px không tràn ngang. Ảnh desktop/mobile
  đã mở kiểm tra; tiếng Anh một phần và nội dung học vẫn Việt như giới hạn.
- Bản đã giải nén chạy server riêng: đăng ký qua form thật, đồng bộ theme
  sang context trình duyệt thứ hai, đăng nhập mới thu hồi phiên cũ. Không
  pageerror; mật khẩu test sinh ngẫu nhiên trong bộ nhớ, không ghi file/log.

Bằng chứng local: var/v6/online-browser-result.json,
var/v6/learning-browser-result.json và ảnh cùng thư mục. Không đưa DB/log
kiểm thử vào gói public. Browser automation tự thao tác, chưa thay người chơi
thử tính dễ dùng hoặc hai mạng thật.

### Gói nguồn

Builder chỉ lấy allowlist; verifier đối chiếu manifest/hash/CRC, không merge
vào thư mục tồn tại, từ chối đường dẫn unsafe và file runtime/private thường
gặp. Cần chạy lại bộ checks trên thư mục vừa giải nén để xác minh đủ dependency.
Hash đảm bảo khớp nội dung, không tự chứng minh không có lỗ hổng hoặc secret.

#### Kết quả kiểm tra bản giải nén

Bản thử gồm 90 file, không thiếu asset được index tham chiếu; không có var,
.git, node_modules, database, log hoặc tài liệu trả lời cá nhân. Quét mẫu
private key/token phổ biến không thấy kết quả; đây không phải kiểm toán secret.

Chạy checks trên bản giải nén: 155 test JS, syntax, fixture/parity đều đạt.
Python đạt 102/103; test còn lại bị lỗi giả tại ranh giới TOTP30 giây: test
tạo mã mới nhưng coi là phát lại mã cũ. Đã sửa test để cố định đồng hồ, dùng
lại đúng mã, đồng thời bổ sung kiểm tra mã ở bước thời gian sau được chấp
nhận một lần và phát lại từ client khác bị từ chối. Không đổi logic bảo mật
production. Test đã sửa đạt khi chạy riêng; không loại bỏ/làm yếu assertion.

Gói cuối giữ nguyên toàn bộ runtime đã chạy ở bản giải nén, chỉ cập nhật
test xác thực và tài liệu. Verifier kiểm CRC/hash/manifest cho ZIP cuối;
test xác thực đã sửa được kiểm lại từ bản giải nén cuối. Như vậy core103 và
JS155 đều có kết quả đạt qua các lượt kiểm tra, không tuyên bố bản thử ban
đầu đạt tất cả trong một lượt.

---

<!-- nguồn: reports/PROJECT_MEMORY_VI.md -->

## Sổ tay hiện trạng Cờ Chill V6

Cập nhật 26/10/2026. Đây là ghi chú lịch sử, không mô tả trạng thái hiện tại
của `codex-full`, và không thay thế đặc tả gốc hoặc quyết định mới của chủ dự án.

### 1. Nguồn thông tin

- [README](README.md): quick start, kiến trúc, đóng gói và liên kết tài liệu.
- [AGENTS.md](AGENTS.md): quy tắc phát triển và các bất biến sản phẩm.
- [docs/CLAUDE_HANDOFF_V6.md](docs/CLAUDE_HANDOFF_V6.md) và
  [docs/V6_DECISIONS.md](docs/V6_DECISIONS.md): handoff, ranh giới kiến trúc,
  quyết định và ưu tiên tiếp theo.
- [docs/spec/](docs/spec/): Final Pack gốc; giữ nguyên nội dung. Khi có khác
  biệt, ưu tiên quyết định mới nhất của chủ dự án theo handoff.
- [IMPLEMENTATION_REPORT_CODEX.md](IMPLEMENTATION_REPORT_CODEX.md),
  [TEST_REPORT_CODEX.md](TEST_REPORT_CODEX.md) và
  [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md): trạng thái thực hiện, bằng
  chứng kiểm thử và giới hạn chưa giải quyết.
- [AI_USAGE.md](AI_USAGE.md), [PRIVACY.md](PRIVACY.md) và
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md): AI, dữ liệu và thông báo
  quyền sử dụng.

Tóm lược các ý tưởng trước V6 nằm trong [V6_PREVIOUS.md](V6_PREVIOUS.md).
Đó là ghi chú lịch sử, không phải bản kiểm kê hoặc hướng dẫn chạy hiện hành.
Dùng README và các tài liệu V6 ở trên để thực hiện công việc mới.

### 2. Chạy và kiểm tra

Từ thư mục gốc repository, dùng Python 3.12 trở lên:

```powershell
python co_chill_server.py serve --port 8769
```

Mở `http://127.0.0.1:8769/`; giữ terminal chạy và nhấn Ctrl+C để dừng.
Windows có thể dùng `py -3.12`; Linux/macOS có thể dùng `python3`. Ứng dụng
không cần Node.js, npm hoặc API key để chạy.

Để chạy bộ kiểm tra chuẩn, cài Node.js rồi chạy:

```powershell
python tools/run_checks.py
```

Runner bao gồm kiểm tra Python/JavaScript, nghiệp vụ, fixture và parity luật.
Chỉ ghi kết quả đã thực sự chạy; phạm vi và bằng chứng chi tiết nằm trong
`TEST_REPORT_CODEX.md`.

### 3. Kiến trúc hiện hành

```text
online-preview/  giao diện HTML/CSS/JavaScript
       │ HTTP cùng origin
       ▼
co_chill_server.py  server/API/CLI
       ├── app/rules.py, app/online_rooms.py
       ├── app/cloud_store.py, app/content_store.py
       └── app/pikafish.py
```

| Thành phần | Trách nhiệm |
|---|---|
| `co_chill_server.py` | Điểm khởi động local/WSGI, API và phục vụ giao diện |
| `app/rules.py` | Luật phía server; cùng frontend kiểm tra parity |
| `app/pikafish.py` | Adapter UCI; chỉ báo bằng chứng engine khi có kết quả hợp lệ |
| `app/cloud_store.py` | Tài khoản, phiên, tiến độ và SQLite |
| `app/content_store.py` | Nội dung có phiên bản |
| `app/online_rooms.py` | Trạng thái phòng, ván và đồng hồ PvP phía server |
| `online-preview/` | Bàn cờ, client API, trải nghiệm học và giao diện |
| `tests/`, `tools/` | Test, kiểm tra parity, runner và đóng gói source |

Script frontend được nạp theo thứ tự trong `online-preview/index.html`; không
di chuyển riêng một file mà chưa kiểm tra thứ tự và các guard tích hợp.

### 4. Luồng học và nguồn sự thật

Luồng mục tiêu: chơi/nhập ván → chọn điểm đáng học → reflection → giải thích
có căn cứ → retry → bài liên quan → spaced review → tiến độ.

- Luật và engine quyết định tính hợp lệ, nước đi và phân tích. Explanation
  provider không được tự tạo nước, biến hoặc đánh giá.
- Không hiện lời giải trước reflection; không hiện coaching trong live game.
- Ghi nhãn trung thực cho engine local, bài tập tổng hợp, heuristic và giải
  thích theo mẫu. Không tuyên bố ML được huấn luyện hay hiệu quả đã chứng minh.
- Dữ liệu người học không tự trở thành dữ liệu huấn luyện. Giữ chức năng xuất
  và xóa; không commit database, secret hoặc dữ liệu cá nhân.

### 5. Cấu hình và giới hạn vận hành

- SQLite local mặc định nằm trong `var/`; không đưa database hoặc backup vào
  Git/source pack.
- Engine Pikafish cần cấu hình binary/trọng số riêng; source pack không chứng
  minh engine trên Google Cloud hoạt động.
- Thiết kế hiện tại giả định một instance/process cho các tài nguyên có scope
  process. Không tăng workers/replicas nếu chưa thiết kế lại điều phối.
- Chưa public/deploy, đổi DNS, mua dịch vụ hoặc push mà không có chủ dự án
  duyệt. Tham khảo `docs/DEPLOY_GCP_V6.md` để chuẩn bị, không coi đó là bằng
  chứng đã triển khai.

### 6. Quy trình cập nhật ghi chú

Sau thay đổi đáng kể, cập nhật tài liệu trực tiếp liên quan và ghi đúng test
đã chạy. Trước khi bàn giao, xem:

```powershell
git status --short
git diff --check
python tools/run_checks.py
```

Chỉ chạy bộ kiểm tra nếu môi trường đã cài Node.js; với thay đổi tài liệu
thuần, kiểm tra nội dung/liên kết và diff là đủ. Không tự sinh lại inventory
cũ nếu chưa có yêu cầu và chưa xác định nó phục vụ workflow V6 nào.
