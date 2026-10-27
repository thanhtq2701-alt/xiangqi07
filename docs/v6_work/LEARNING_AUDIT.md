# Kiểm tra kho bài và thiết kế học tập cho V6

Ngày kiểm tra 25 tháng 10 năm 2026. Phạm vi chỉ đọc mã nguồn và tài liệu; không thay đổi chức năng, không sinh thêm bài chưa kiểm chứng. Các số lượng đề xuất bên dưới là mục tiêu xây dựng, không phải nội dung đã tồn tại.

## Đối chiếu đúng gói ZIP người dùng vừa cung cấp

Baseline bổ sung đã được kiểm tra trực tiếp là `C:\Users\thanh\Downloads\xiangqi-ai-20261024T180855Z-1-001.zip`, dung lượng 117516268 byte, gồm 1217 entry. Chỉ đọc danh mục và các file mã liên quan; không thực thi mã trong ZIP, không mở hoặc xuất dữ liệu tài khoản riêng.

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

## Kết luận hiện trạng đã kiểm chứng

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

## Những quyết định cũ cần giữ

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

## Phân biệt bài giảng và bài luyện

Một lesson nên dạy đúng một mục tiêu bằng bàn cờ và câu hỏi ngắn: mở đầu nêu tình huống, một minh họa có thể bước tới/lùi, một ví dụ dễ nhầm có thể bật tắt quân chắn, rồi bài thực hành khác vị trí. Không biến mọi lesson thành đoạn văn dài. Một puzzle kiểm tra một hoặc nhiều quyết định của người học, có mục tiêu, phản ứng đối thủ và điều kiện kết thúc rõ.

Ví dụ mục tiêu bài Pháo là nhận ra khi nào quân ngòi di chuyển khiến đòn ăn quân không còn tồn tại. Hình minh họa có thể đánh dấu ngòi trong phần giảng; hình kiểm tra sau đó không được tự đánh dấu ngòi hay mũi tên đáp án trước khi người học suy nghĩ. Đồ họa phải biểu diễn đúng một trạng thái luật sinh ra từ FEN, không dùng ảnh trang trí vẽ tùy ý để khẳng định vị trí chiến thuật.

## Mô hình bài nhiều lượt cần triển khai

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

## Lộ trình chủ đề có thể mở rộng

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

## Độ khó và quy mô đề xuất

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

## Quy trình kiểm chứng nội dung

1. Nhập nháp có nguồn và quyền dùng. Lưu file gốc riêng, không tự chuyển ván cá nhân vào kho chung.
2. Kiểm tra FEN/bên đi, số quân, Tướng, mọi cạnh hợp lệ, trạng thái sau mỗi nước và điều kiện kết thúc. Loại cây hỏng, node mồ côi, vòng lặp không kiểm soát.
3. Phân tích bằng engine đúng phiên bản đang phục vụ, so các nước ứng viên và phản ứng phòng thủ cần thiết. Giới hạn thời gian/nodes, xác minh không timeout hoặc score bound bị hiểu thành kết luận chắc chắn. Ghi lại bằng chứng; không gọi hợp lệ là tối ưu.
4. Người biên tập duyệt mục tiêu, chấp nhận các phương án tương đương có căn cứ, xem lời giải có bám vào bằng chứng không; kiểm tra câu hỏi không vô tình tiết lộ đáp án.
5. Xem trước toàn vòng: reflection, chuỗi nước, lời giải, retry, bài liên quan, lịch ôn. Cần thao tác trên cả màn hình nhỏ.
6. Xuất bản version bất biến có log. Có nút báo vấn đề; bài sai bị rút khỏi chấm ngay, giữ lịch sử phục vụ sửa lỗi.

## Lịch ôn và đánh giá vận dụng

Giữ nguyên mốc 1/2/7/14/30 ngày đang được kiểm thử như lịch heuristic. `learning.js:181` quyết định lịch theo thành công và hỗ trợ; bài chưa hoàn thành có lịch học tiếp riêng. Không gọi đây là mô hình ML hay chứng minh hiệu quả nhớ lâu.

Với bài nhiều lượt, chỉ ghi hoàn thành sau khi đạt điều kiện cuối cây và kết thúc hình; nhấp hoàn thành lặp lại không được đẩy lịch thêm. Hình chuyển giao có completionAt riêng, không phụ thuộc bài gốc hoặc màn tự đánh giá. Pause giữ node/câu trả lời/lượt gửi. V6 phải chốt ba lần chưa đạt áp dụng cả hình hay từng checkpoint; không tự đổi quy tắc cũ mà không hỏi.

Nên bổ sung `familyId` và phân loại firstExposure: hình chưa gặp, biến thể cùng family, đã xem đáp án, luyện lại, ôn, chuyển giao. Các biến thể lật gương/đổi màu không được dùng để thổi phồng tỷ lệ vận dụng. Related recommendation ưu tiên cùng kỹ năng, đúng mức phù hợp và family mới; hết bài phải nói rõ thay vì gọi bài cũ là mới.

Dashboard nên tách hoạt động, thành công nước đi độc lập, có hỗ trợ, khả năng nhớ lại sau thời gian và kết quả trên hình khác. Ngưỡng 6 mẫu trong code là điều kiện hiển thị tạm, không phải độ tin cậy thống kê được xác thực. Không cộng ván chơi, lesson đã xem và puzzle đã giải thành một tỷ lệ thành thạo. Chỉ tự khai trình độ phải ghi tự khai; thay đổi level bằng bài thực tế cần chính sách minh bạch.

## Danh sách nghiệm thu cần giao Claude

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

## Câu hỏi V6 bổ sung để chủ sở hữu trả lời

Đây là câu hỏi mới hoặc phần V5 còn chưa đủ cụ thể. Số câu mỗi nhóm theo nhu cầu, không cố định tám câu. Có thể trả lời Đồng ý đề xuất để đội phát triển tự xử lý chi tiết kỹ thuật.

### Nhánh học và thứ tự ưu tiên

L01. Trong đợt kế tiếp, ba nhánh cần làm sâu nhất là Xe, Pháo, Mã hay muốn thay một nhánh bằng chống mất quân/bảo vệ Tướng/phối hợp? Xếp thứ tự và nêu nhóm người học chính của từng nhánh.

L02. Trong nhánh Xe đầu tiên, chọn ba mục tiêu muốn người học tự làm được sau học: tìm đường mở, bảo vệ quân, tính ăn rồi bị ăn lại, phối hợp hai Xe, hay mục tiêu khác. Với Pháo và Mã có thể ghi tương tự, không cần tự tạo FEN.

L03. Hành trình nên là bản đồ mở cho chọn mọi bài, hay có khóa chương? Nếu khóa, có chấp nhận dùng bài vận dụng độc lập làm điều kiện, còn EXP chỉ để động viên? Đề xuất cho làm bài vượt cấp thay vì bắt người biết chơi học lại luật.

L04. Người học đi theo một nhánh Xe tới hết rồi sang Pháo, hay xen kẽ theo điểm yếu và lịch ôn? Đề xuất nhánh chính do người học chọn, hệ thống chen bài ôn đến hạn và đề nghị chuyển nhánh khi cần.

L05. Một phiên học mong muốn kéo dài khoảng bao lâu và tối đa bao nhiêu hình nhiều lượt? Có ưu tiên thời gian 5 phút, 10–15 phút hay không giới hạn?

L06. Những chương nào cần xuất hiện ngay nhưng mang nhãn Đang chuẩn bị, và chương nào nên ẩn cho tới khi có bài thật? Đề xuất chỉ hiện số bài đã duyệt và không tạo nút học rỗng.

### Độ khó

L07. Bạn muốn người dùng nhìn thấy mấy mức và tên gì? Có đồng ý khung Nhập môn, Cơ bản, Trung cấp, Nâng cao kèm nhãn dự kiến trước khi có dữ liệu thật?

L08. Cung cấp một hình bạn coi là trung cấp và một hình nâng cao, hoặc cho phép người biên tập đề xuất để bạn duyệt. Nêu vì sao khó; có thể ghi chưa biết đáp án để engine kiểm chứng, không cần đoán.

L09. Tỷ lệ bài giữ ở mức một quyết định cho người mới nên khoảng bao nhiêu? Đề xuất vẫn giữ nền tảng nhưng phần người đã biết luật ưu tiên tính phản ứng và phối hợp nhiều lượt.

L10. Khi một người liên tiếp chưa đạt một mức, hệ thống tự hạ bài, hỏi trước khi hạ, hay giữ mức nhưng thêm gợi ý? V5 đã có tự giảm mức chơi máy; câu này chỉ hỏi mức bài học để không nhập hai khái niệm làm một.

L11. Bạn muốn hiển thị mức khó trên từng bài hay chỉ theo chương? Có cho người học tự chọn bài khó hơn khuyến nghị với nhãn thử thách không?

### Bài nhiều lượt và nhánh

L12. Ở quyết định thứ hai và các bước sau, người học chỉ chọn nước, trả lời một câu ngắn, hay lặp lại cả bộ reflection? Đề xuất một câu ở các điểm thay đổi kế hoạch, tránh bắt viết lại ba đoạn giống nhau.

L13. Ba lần thử chưa đạt áp dụng cho cả hình hay mỗi checkpoint? Sau khi dùng hết, giữ đúng nhánh đang dở hay quay lại gốc hôm sau? Đề xuất giữ nhánh để không mất phần đã làm, nhưng không tính hoàn thành hình.

L14. Đối thủ trong bài nên luôn đáp nước phòng thủ mạnh nhất, đi nhánh đã biên soạn để dạy mục tiêu, hay cho người học chọn nhánh sau lời giải? Đề xuất lúc chấm dùng nhánh đã duyệt, lúc học thêm có thể khám phá.

L15. Với một nước hợp lệ ngoài cây mà engine chưa kết luận kịp, bạn muốn chờ phân tích, tạm lưu để người duyệt xem, hay thử lại phương án khác? Đề xuất không chấm sai chắc chắn khi chưa có căn cứ.

L16. Điểm kết thúc bài muốn là đạt vật chất/mục tiêu, chiếu hết, hay đánh tới hết ván? Nêu riêng cho bài chiến thuật, kế hoạch vị trí và tàn cuộc.

L17. Khi sai ở bước cuối nhưng đã làm đúng các bước đầu, có ghi nhận từng phần trên dashboard không? Đề xuất lưu từng quyết định nhưng chỉ gắn Hoàn thành hình khi đạt điều kiện cuối.

L18. Retry sau lời giải nên bắt giải lại toàn hình hay chỉ checkpoint chưa hiểu? Đề xuất có cả hai nhưng đều mang nhãn luyện lại có hỗ trợ; không thay kết quả lần đầu.

### Nguồn bài và duyệt

L19. Đợt nội dung đầu tiên bạn muốn chốt ở 6 lesson/24 puzzle tập trung Xe Pháo Mã, hay số khác? Đây là mục tiêu biên soạn mới, có thể giảm để duyệt kỹ hơn.

L20. Bạn có thể cung cấp bao nhiêu ván/hình có quyền dùng trong tuần đầu? Với mỗi nguồn chỉ cần mô tả loại file, số lượng, chủ đề, người cho phép và hạn gửi; đáp án chưa biết được để trống.

L21. Ai sẽ duyệt nhận định chiến thuật và lời giải trước khi xuất bản? Nếu chỉ mình bạn, nhịp khoảng 10 thế mỗi tuần trong V5 còn phù hợp không?

L22. Có chấp nhận bài tự dựng được ghi rõ nguồn và chờ duyệt để lấp các nhóm còn thiếu không? Điều kiện tối thiểu đề xuất là qua luật, engine có log và người biên tập duyệt.

L23. Bài do người chơi đóng góp cần được xin phép chia sẻ riêng ở thời điểm nào: khi gửi ván, khi đề nghị lấy một thế, hay trước lúc xuất bản? Đề xuất kho riêng mặc định, xin phép trước khi đưa lên kho chung.

L24. Bạn muốn tự biên tập bằng đặt quân trên bàn, dán FEN/biên bản, hay cả hai? Chọn thao tác ưu tiên cho bản đầu: nhập nguồn, đặt câu hỏi, sửa nhánh, preview, gỡ bài.

### Ôn và thống kê

L25. Với một bài nhiều lượt, bài ôn yêu cầu giải lại cả cây, một nhánh được chọn hay chỉ điểm từng vướng? Đề xuất một nhánh có ý nghĩa, xoay nhánh giữa các lần ôn và ghi rõ mức đã kiểm tra.

L26. Khi hết bài cùng chủ đề chưa gặp, ưu tiên đề nghị chủ đề khác, tạo hình từ ván của người học sau xác minh, hay luyện lại? V5 đã muốn nói rõ hết bài; câu này cần xếp thứ tự để recommendation thực hiện nhất quán.

L27. Trong dashboard, ba thông tin nào bạn muốn nhìn đầu tiên: bài đến hạn, nhánh đang học, tự giải hình mới, nhớ lại sau thời gian, bài có hỗ trợ, hay số hoạt động? Không dùng một tỷ lệ tổng trộn các loại bằng chứng.

L28. Khi có bài bị sửa đáp án, bạn muốn thông báo trong tài khoản hay ngay lúc mở bài ôn? Đề xuất tạm loại kết quả bị ảnh hưởng khỏi thống kê trình độ, giữ lịch sử cũ và chỉ cập nhật lịch sau khi người vận hành duyệt.

### Kiểm chứng đợt phát hành

L29. Ai có thể thử bộ bài đầu tiên và họ đã biết chơi ở mức nào? Chỉ ghi người đã đồng ý thử; không cần thông tin cá nhân công khai.

L30. Bạn chấp nhận tiêu chí mở bản mới là một vòng học nhiều lượt hoàn chỉnh và 24 bài được duyệt, hay ưu tiên số lượng khác? Đề xuất không mở nếu còn sai luật, lộ lời giải sớm, mất nháp hoặc mất lịch ôn.

L31. Với lời giải, bạn muốn bàn cờ chuyển từng nước, so sánh hai hình trước sau, hay cả hai? Đề xuất mặc định bàn cờ từng bước, phần giải thích ngắn theo node, mở rộng khi cần.

L32. Có ví dụ một bài giảng hoặc một sản phẩm bạn thấy dạy tốt để mô tả điều thích và không thích không? Chỉ dùng làm tham khảo cấu trúc; nội dung/ảnh phải có quyền nếu định đưa vào Cờ Chill.

## Gợi ý thứ tự công việc cho Claude

1. Ghi baseline 12 fixture/4 minh họa và giữ test cũ. Sửa đếm/lọc phase để không tạo cảm giác có hai kho khác nhau.
2. Thiết kế schema v2 và migration; thêm validator cây biến, editor và preview trên 2–3 bài nháp kiểm chứng thật.
3. Xây player nhiều lượt, checkpoint, save/resume, reflection, timeout/chưa kết luận, retry và scheduling. Chưa tăng số lượng đại trà trước bước này.
4. Tạo taxonomy và màn Hành trình học từ dữ liệu, thay chuỗi liên kết cố định; bổ sung family-aware recommendation.
5. Biên soạn đợt 6 lesson/24 puzzle hoặc mục tiêu chủ sở hữu duyệt, qua pipeline kiểm chứng; báo tiến độ theo trạng thái nội dung.
6. Kiểm thử người dùng, kiểm tra trên hình chuyển giao tách khỏi bài đã học, điều chỉnh nhãn mức khó có log. Không tuyên bố hiệu quả học đã được xác thực từ pilot nhỏ.

Tài liệu này không có bài cờ mới đã được chứng minh, không thay thế kết quả engine trên máy thật và không chứng minh tác dụng sư phạm. Nó xác định phần còn thiếu và cách xây để các tuyên bố sau này có bằng chứng kiểm tra được.
