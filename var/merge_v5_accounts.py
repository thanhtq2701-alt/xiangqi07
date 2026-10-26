from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
p=root/'docs/CO_CHILL_V5_QUESTIONS.md'
s=p.read_text(encoding='utf-8')
s=re.sub(r'\n\*\*Bổ sung quyết định ngày 16/10/2026:.*?\n\n','\n',s,count=1)
s=s.replace('## Câu hỏi để hoàn thiện trải nghiệm học và chuẩn bị thử nghiệm','## Câu hỏi hoàn thiện sản phẩm và hệ thống tài khoản')
s=s.replace('Ngày hoàn thiện 16 tháng 10 năm 2026. Người trả lời Trần Quốc Thanh.', 'Bản cập nhật tài khoản ngày 16 tháng 10 năm 2026. Người trả lời Trần Quốc Thanh.')
s=s.replace('Có 41 câu trong 8 nhóm, số câu khác nhau theo nhu cầu.', 'Có 46 câu trong 9 nhóm, số câu khác nhau theo nhu cầu. Đây là bản Word duy nhất bạn cần điền; file bàn giao TXT chỉ để đọc, không phải biểu mẫu thứ hai. Bản này giữ mã 01–41, cập nhật các câu 25, 28, 32, 37, 39 và 40; thêm câu 42–46 về tài khoản và quản trị. Nếu đã điền bản cũ, giữ câu trả lời cũ và chỉ rà lại những câu được cập nhật.')
s=s.replace('hay việc để PvP và tài khoản đồng bộ sang giai đoạn sau.', 'hoặc việc có đưa tài khoản vào V5 hay không: bạn đã chốt có tài khoản, đồng bộ và quản trị trong V5. PvP trực tuyến vẫn để sau.')
s=s.replace('- Trước mắt ưu tiên vòng học công khai chạy được trên máy tính và điện thoại. UX35 để PvP trực tuyến, tài khoản đồng bộ nhiều thiết bị và AI huấn luyện riêng sang sau.', '- Đợt V5 bổ sung tài khoản thật, lưu dữ liệu tập trung, dùng nhiều thiết bị và trang quản trị để chủ sản phẩm xem tài khoản mới cùng thống kê toàn hệ thống. Đây là quyết định mới thay việc để tài khoản sang sau trong UX35; chưa phải chức năng đã phát hành.\n- Giữ vòng học hoạt động trên máy tính và điện thoại. PvP trực tuyến và AI huấn luyện riêng vẫn để sau.')
s=s.replace('Bạn muốn chỉ thống kê từ lần thử sáu cho từng chỉ số.', 'Bạn muốn chỉ hiện một số chỉ số học từ lần thử sáu. Ngưỡng này không áp dụng cho số tài khoản, ván hoặc lượt học thực tế: những số đếm đó được hiển thị ngay khi ghi nhận hợp lệ.')
def question(n,title,body):
 global s
 pattern=rf'### V5 {n:02d} .*?(?=\n### V5 |\n## |\Z)'
 s,count=re.subn(pattern,f'### V5 {n:02d} {title}\n\n{body.strip()}\n',s,count=1,flags=re.S)
 assert count==1,n
question(28,'Dashboard cá nhân và quản trị cần giúp bạn biết điều gì','''Ưu tiên 1. Cập nhật theo quyết định đưa tài khoản và quản trị vào V5; đối chiếu UX21.

Trang cá nhân cho người chơi xem tiến độ của họ; trang quản trị cho bạn xem toàn hệ thống. Trong dashboard quản trị, ngoài tài khoản mới và tài khoản hoạt động, ba thông tin nào cần ở đầu trang: số ván, lượt học hoàn tất, lượt ôn, bước bỏ dở hay tỷ lệ làm bài có hỗ trợ? Bạn xem theo ngày, tuần hay tháng và có cần xuất bảng thống kê không?

Đề xuất: mặc định 7 ngày gần nhất, có chọn khoảng thời gian và dấu thời điểm cập nhật. Một tài khoản dùng nhiều máy vẫn đếm một tài khoản; số tài khoản không tự bằng số người thật. Tách test nội bộ và phiên có trợ giúp. Số đếm hiển thị từ dữ liệu đầu tiên; chỉ tỷ lệ hoặc kết luận học tập cần đủ mẫu như câu 25. Không hiển thị số giả hoặc gọi hoạt động là hiệu quả học đã kiểm định.

Trả lời: Ba thông tin đầu trang… / Khoảng thời gian… / Cần xuất bảng không… / Muốn bấm vào chỉ số để xem chi tiết nào…''')
question(32,'Người chơi đăng nhập như thế nào và có chế độ khách không','''Ưu tiên 1. Cập nhật: tài khoản và đồng bộ nhiều thiết bị đã được chốt cho V5.

Bạn muốn người chơi đăng nhập bằng email, Google hoặc phương thức quen thuộc nào? Có cho chơi thử không cần tài khoản và chỉ yêu cầu đăng nhập khi lưu đồng bộ không? Tên hiển thị có được khác tên tài khoản đăng nhập không? Chỉ nêu trải nghiệm mong muốn, không gửi mật khẩu hoặc mã xác thực.

Đề xuất: bản đầu dùng một phương thức xác thực có quản lý, cho tên hiển thị riêng; nếu có chế độ khách thì nói rõ dữ liệu chỉ nằm trên máy cho đến khi người chơi chọn chuyển vào tài khoản. Có đăng xuất và khôi phục quyền truy cập. Codex đề xuất dịch vụ phù hợp ngân sách trước triển khai; không tự tạo cơ chế lưu mật khẩu dạng rõ.

Trả lời: Phương thức ưu tiên… / Có chế độ khách không… / Bắt buộc đăng nhập ở bước nào… / Quy tắc tên hiển thị…''')
question(37,'Phân bổ ngân sách cho tài khoản và các nâng cấp khác','''Ưu tiên 1. Cập nhật theo phạm vi tài khoản trong V5; đối chiếu UX27, UX28, UX30 và UX35.

Tài khoản, lưu tập trung và quản trị đã là yêu cầu của V5. Với trần 200.000 đồng mỗi tháng cho tất cả dịch vụ, bạn ưu tiên phần ngân sách còn lại cho engine mạnh hơn hay lời giải linh hoạt hơn? Khi dịch vụ gần chạm hạn mức, cần báo cho bạn ở đâu và những chức năng trả phí nào được tạm dừng?

Đề xuất: giữ độ đúng luật và vòng học hiện có, ưu tiên nền tảng tài khoản/lưu dữ liệu; engine nông và lời giải mẫu vẫn là phương án không trả phí. Không tự nâng gói, không đánh mất dữ liệu đã lưu để xử lý hạn mức. Nếu hạn mức chặn ghi mới, hiển thị rõ tình trạng và hỗ trợ xuất dữ liệu. Báo phương án chi phí trước khi bật dịch vụ.

Trả lời: Thứ tự ưu tiên thêm… / Phần ngân sách dành cho từng nhóm nếu muốn… / Kênh báo hạn mức… / Chức năng được tạm dừng…''')
question(39,'Thứ tự triển khai trong đợt V5','''Ưu tiên 2. Cập nhật theo phạm vi V5 mới và UX34.

V5 đã phải có tài khoản, đồng bộ và quản trị, đồng thời giữ vòng học hoạt động. Ngoài phần bắt buộc đó, hãy chọn tối đa ba cải thiện quan trọng nhất: câu hỏi/lời giải, nội dung được duyệt, engine, mobile hoặc công cụ biên tập. Bạn muốn thử từng bản nhỏ hay chờ một bản tích hợp cuối cùng?

Đề xuất: nghiệm thu tài khoản và quyền truy cập trước, tiếp đến đồng bộ và thống kê, rồi ghép các cải thiện trải nghiệm đã chốt. Mỗi đợt có kết quả quan sát được; không mở rộng sang PvP hoặc trained ML chỉ vì đã có tài khoản.

Trả lời: Ba cải thiện ưu tiên… / Thử từng bản hay bản tích hợp… / Tiêu chí quan trọng nhất khi duyệt…''')
question(40,'Dịch vụ và quyền triển khai bản V5 lên web','''Ưu tiên 1. Cập nhật: bản V5 cần backend, tài khoản, dữ liệu tập trung và quản trị.

Bạn đã có tài khoản hosting, dịch vụ đăng nhập hoặc database nào? Chỉ ghi tên dịch vụ và người quản lý, không đưa thông tin đăng nhập. Với mong muốn chuyển sang Vercel đã trao đổi, bạn muốn chuyển khi V5 đủ tính năng hay thử trước ở địa chỉ thử nghiệm? Có cần tên miền riêng trong cùng đợt không?

Đề xuất: chọn cách deploy sau khi chốt dữ liệu và ngân sách. Hosting frontend, xác thực và database là các phần có thể tách riêng; chỉ chuyển địa chỉ web sẽ không tự tạo hệ thống tài khoản. Chuẩn bị môi trường thử và cách quay lại bản ổn định; xin duyệt hành động cần quyền trước khi kết nối hoặc phát hành.

Trả lời: Dịch vụ đã có… / Người quản lý dịch vụ… / Thời điểm chuyển sang Vercel… / Tên miền riêng nếu cần…''')
extra='''## I Chi tiết tài khoản quản trị và đồng bộ

Tài khoản đăng ký thành công trên thiết bị A phải xuất hiện trong quản trị của bạn trên thiết bị B; người chơi đăng nhập trên thiết bị C thấy dữ liệu đã đồng bộ. Đây là tiêu chí đã chốt. Các câu sau chỉ làm rõ cách dùng và xử lý trường hợp phát sinh.

### V5 42 Ai quản trị và được xem những dữ liệu nào

Ưu tiên 1. Câu mới cho hệ thống quản trị V5.

Trước mắt chỉ bạn quản trị hay có thêm người hỗ trợ? Với mỗi vai trò, họ được xem thống kê tổng hợp, danh sách tài khoản, biên bản ván hay câu trả lời tự do đến mức nào? Có cần người chỉ đọc báo cáo nhưng không khóa/xóa tài khoản không? Không ghi password hoặc thông tin riêng của người thử vào đây.

Đề xuất: bắt đầu với một chủ sở hữu; quyền quản trị được gán qua bước xác minh, không có lựa chọn tự đăng ký làm admin. Dashboard mặc định dùng thống kê và mã tài khoản; chỉ cho xem nội dung riêng khi có mục đích và phạm vi đã thông báo. Backend kiểm tra quyền cho mọi yêu cầu; lưu nhật ký thao tác quan trọng.

Trả lời: Các vai trò cần có… / Mỗi vai trò được xem gì… / Ai được khóa hoặc xóa… / Cách muốn thông báo quyền xem cho người chơi…

### V5 43 Bạn muốn biết có tài khoản mới theo cách nào

Ưu tiên 1. Câu mới làm rõ yêu cầu biết đăng ký từ bất kỳ thiết bị nào.

Chỉ cần mở dashboard thấy tài khoản mới, hay bạn muốn nhận thêm email hoặc thông báo ngoài web? Muốn báo từng lần, gộp theo ngày hay chỉ báo khi có vấn đề? Nếu có xác minh email, cần phân biệt người mới đăng ký và người đã xác minh như thế nào?

Đề xuất: server ghi nhận tài khoản ngay khi tạo thành công; dashboard cho thấy trạng thái xác minh và thời điểm làm mới. Bản đầu dùng danh sách cập nhật khi mở/làm mới, có thể tự cập nhật khi trang đang mở. Email/push là tùy chọn phải bật riêng; tránh gửi dữ liệu người học không cần thiết và tránh tạo thông báo trùng.

Trả lời: Chỉ dashboard hay thêm kênh khác… / Từng lần hay bản tổng hợp… / Mức chậm chấp nhận… / Phân biệt trạng thái đăng ký và xác minh…

### V5 44 Chuyển tiến độ local cũ vào tài khoản ra sao

Ưu tiên 1. Câu mới về dữ liệu của bản đang dùng.

Khi người chơi đăng nhập lần đầu, cần chuyển những gì từ trình duyệt cũ: ván, nháp, câu trả lời, kết quả, lịch ôn hay tùy chọn giao diện? Nếu tài khoản đã có dữ liệu và máy đang mở cũng có dữ liệu local, bạn muốn xem trước rồi hợp nhất hay lựa chọn từng nhóm? Máy dùng chung cần bước xác nhận nào để tránh gán dữ liệu nhầm người?

Đề xuất: hỏi người dùng có muốn nhập phần local vào tài khoản, cho xem số lượng và nội dung liên quan trước khi xác nhận. Không tự coi toàn bộ dữ liệu trên máy là của người vừa đăng nhập; nhập lại không nhân đôi kết quả. Giữ khả năng xuất bản sao và báo rõ mục nào chưa chuyển được.

Trả lời: Các nhóm cần chuyển… / Cách chọn và hợp nhất… / Xác nhận trên máy dùng chung… / Điều bắt buộc không được mất…

### V5 45 Khi dùng hai máy hoặc mất mạng thì giữ tiến độ thế nào

Ưu tiên 1. Câu mới về đồng bộ nhiều thiết bị.

Giả sử cùng tài khoản đang làm một bài trên điện thoại và laptop, rồi hai máy gửi câu trả lời khác nhau: bạn muốn chỉ một phiên được sửa, chọn bản nào, hay để người chơi quyết định? Khi mất mạng giữa bài, người chơi được tiếp tục viết nháp hay phải dừng? Bạn muốn nhìn thấy trạng thái đang lưu, đã đồng bộ và chưa đồng bộ ở đâu?

Đề xuất: lưu nháp trên thiết bị khi cần và hiển thị rõ phần chưa gửi; chỉ nói đã đồng bộ sau khi máy chủ xác nhận. Nếu có xung đột, giữ cả bản nháp và yêu cầu chọn, không âm thầm ghi đè. Một lần hoàn thành chỉ ghi nhận một kết quả và một mốc ôn dù gửi lại nhiều lần.

Trả lời: Quy tắc khi mở hai máy… / Hành vi lúc mất mạng… / Vị trí báo trạng thái… / Mức chờ đồng bộ chấp nhận…

### V5 46 Khóa tài khoản và xử lý yêu cầu của người chơi

Ưu tiên 1. Câu mới về thao tác quản trị; chính sách lưu giữ và xóa vẫn trả lời tại câu 29–30.

Khi bạn khóa tài khoản, người chơi có được xem hoặc xuất dữ liệu cũ không, hay phải liên hệ bạn? Cần khóa có thời hạn hay đến khi mở lại? Người chơi gửi yêu cầu mở lại, sửa thông tin hoặc xóa tài khoản ở đâu? Bạn muốn màn hình xác nhận thao tác quản trị hiển thị những gì để tránh chọn nhầm người?

Đề xuất: phân biệt khóa sử dụng với xóa dữ liệu; ghi lý do, thời điểm và người thực hiện. Quyền khóa/mở có hiệu lực phía server; xóa cần xác nhận riêng theo chính sách đã chốt. Người dùng vẫn có một đường gửi yêu cầu về dữ liệu hoặc truy cập. Không cho admin xem mật khẩu, đăng nhập giả làm người dùng hoặc sửa kết quả học tùy ý.

Trả lời: Quyền còn lại khi bị khóa… / Thời hạn khóa… / Kênh yêu cầu hỗ trợ… / Nội dung xác nhận trước thao tác…

'''
assert '### V5 42 ' not in s
s=s.replace('## Cách gửi lại V5',extra+'## Cách gửi lại V5')
s=s.replace('Ưu tiên trả lời nhóm A, B và các câu ưu tiên 1 trước; những câu về tài khoản, công cụ biên tập và Vercel có thể bổ sung sau khi thử.', 'Ưu tiên các câu mức 1, gồm phần tài khoản: câu 28, 32, 37, 40 và 42–46. Nếu đã điền bản cũ, chỉ rà lại các câu 25, 28, 32, 37, 39, 40 và điền thêm 42–46; các câu còn lại giữ câu trả lời trước. Bạn không phải điền file TXT bàn giao hoặc một bộ bổ sung riêng.')
assert len(re.findall(r'^### V5 \d+',s,re.M))==46
p.write_text(s,encoding='utf-8')
