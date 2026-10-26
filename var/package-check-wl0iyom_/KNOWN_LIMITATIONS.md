# Giới hạn bản code V5 — 24/10/2026

Bản này có vòng học và nền tảng tài khoản chạy cùng một server. Đây vẫn là prototype/pilot; không phải mọi câu trả lời V5 đã được triển khai. Bảng đầy đủ: [42 nhóm yêu cầu](docs/V5_DECISIONS_2026_10_24.md).

1. **Engine mạnh chưa được cài và nghiệm thu.** Có adapter UCI, kiểm tra legal PV, điểm và timeout; bộ kiểm thử giao thức dùng chương trình UCI giả. Mặc định dùng engine local tối đa hai nửa nước. Tìm kiếm nông có thể bỏ lỡ hy sinh, chiến thuật dài và chiến lược; không dùng nó để chứng nhận một nước là tối ưu tuyệt đối.
2. **Luật thi đấu chưa hoàn chỉnh.** Luật di chuyển và an toàn Tướng có kiểm thử; các tình huống lặp/chiếu/đuổi và ngưỡng quốc gia Việt Nam còn cần nguồn chính thức và ca phân xử. FEN hợp cấu trúc không chứng minh thế có thể phát sinh trong một ván hợp lệ.
3. **Giảng dạy còn theo mẫu.** Chưa có LLM, chấm ngữ nghĩa, RAG sách hoặc ML. Nhập đủ ba câu và đi nước được chấp nhận không chứng minh người học hiểu; lượt có trợ giúp được tách khỏi lượt độc lập.
4. **Nội dung còn nhỏ.** 12 bài tự dựng, chưa là giáo trình hay bộ gold chuyên gia duyệt. Các ảnh Word chưa được biến thành bài đã xác minh. Gợi bài chưa gặp dựa trên lịch sử lưu và kho hiện có; chưa loại mọi tương đương đối xứng/đổi màu.
5. **Review bị giới hạn tài nguyên.** Quét tối đa 20 lượt của bên người học gần nhất; số điểm học không cố định ba. Không tìm thấy lỗi không đồng nghĩa ván hoàn hảo. Hủy ở trình duyệt bỏ kết quả trễ nhưng engine server có thể chạy đến timeout. Chưa có cây biến/note/thư mục riêng hoàn chỉnh hoặc OCR ảnh biên bản.
6. **Đồng bộ là trạng thái do thiết bị gửi.** CAS chống ghi đè nhầm và phiên một thiết bị giúp bảo toàn dữ liệu; đây không phải hệ chống gian lận. Cổng phản ánh phục vụ học tập: người có quyền xem code/dữ liệu trình duyệt vẫn có thể tìm đáp án. Thống kê không phải chứng cứ kỹ năng hay impact.
7. **Tài khoản cần hosting bền.** SQLite phải đặt trên ổ lưu bền vững của một instance. Chưa có Postgres, scale nhiều máy, queue engine phân tán, backup tự động hoặc SLA. Vercel static không chạy API tài khoản; Render filesystem tạm không phù hợp giữ tài khoản thật. Code chưa được deploy trong đợt này.
8. **Xác thực chưa đủ mọi nhu cầu production.** Có scrypt, HttpOnly, SameSite, CSRF, kiểm tra origin/quyền, TOTP owner và thu hồi phiên. Chưa có OAuth, email xác minh/phục hồi, passkey, mã dự phòng TOTP hoặc audit độc lập. Mất khóa owner cần vận hành xử lý; không tự khôi phục qua frontend.
9. **Quản trị và nội dung còn ở mức pilot.** Có thống kê, người dùng, khóa có lý do/thời hạn, hộp phản hồi, nháp/xuất bản/tạm gỡ và kiểm soát phiên bản. Lọc/phân trang giao diện cần cải thiện khi dữ liệu lớn. Chưa tự cách ly mọi bài bị báo hoặc thông báo lại tất cả người học; thay đổi danh mục cần tải lại/lấy lại danh mục.
10. **Lịch học chưa là mô hình lưu giữ được kiểm chứng.** Lịch bắt đầu khi hoàn thành; bài tạm dừng giữ riêng và nhắc ngày sau. Không có email/push, lịch nhắc chạy nền, đánh giá đầu vào chuẩn hóa, giáo trình thích nghi hoặc cổng bắt buộc hoàn thành backlog trước chơi.
11. **Chơi trực tuyến chưa có.** Hai người hiện dùng cùng thiết bị; chưa PvP qua mạng, matchmaking hoặc Elo. Chưa tự xử thua sau 30 giây mất mạng cho ván không đồng hồ. Không cho coaching trong ván đang diễn ra.
12. **Tính sẵn sàng sử dụng còn cần thử thực tế.** Có bố cục màn nhỏ, theme, thao tác bàn phím và nhãn tiếng Việt; chưa kiểm toán WCAG hoặc kiểm thử rộng iOS/Android/bàn phím ảo. Cần thử người thật và xử lý các điểm khó sử dụng trước khi mở rộng.
13. **Xuất dữ liệu không phải backup khôi phục.** JSON cá nhân bỏ khóa đáp án/biến sinh tự động; chưa có nhập phục hồi toàn bộ từ JSON. Backup SQLite là thao tác vận hành riêng. Xóa tài khoản xóa bản hoạt động, không tự xóa các bản tải xuống/backup bên ngoài. Dữ liệu không mã hóa ở mức file; người có quyền hệ điều hành/database có thể đọc.

Ưu tiên tiếp theo: nghiệm thu bản local → chọn hosting có dữ liệu bền → cài/đo engine thật → duyệt bộ bài và nguồn luật → thử pilot nhỏ. Không cần mua sách hay gọi LLM để chạy luồng hiện tại.

## Lịch sử giới hạn của các bản cũ

Những câu “chưa có tài khoản”, “chỉ demo hai bài” hoặc thông số khác bên dưới thuộc bản tại ngày ghi; không mô tả V5 phía trên.

# Cập nhật giới hạn ngày 16/10/2026

Site phiên bản 3 vẫn dùng engine browser tối đa 2 ply, giải thích mẫu, 12 bài tự dựng và dữ liệu localStorage. Chưa có LLM chấm lập luận, PvP trực tuyến, tài khoản/đồng bộ, OCR, engine mạnh hoặc bộ phân xử WXF đầy đủ. Lặp/đuổi hỗn hợp được gắn cần kiểm chứng. Thống kê hoạt động không chứng minh hiệu quả học tập. Xuất JSON để đọc, chưa nhập phục hồi tự động. Góc lật bàn chưa lưu qua reload; khi xin thua/thỏa thuận hòa, đồng hồ kết thúc còn hiện mốc nước gần nhất. Tùy chọn giọng chỉ đổi lời mở đầu. Xem [báo cáo mới](BAO_CAO_UIUX_V5_2026_10_16.md) để biết phạm vi chính xác; các mục dưới là lịch sử và bối cảnh backend local.

# Known limitations

1. Local search depth is at most 2 plies (one move and one response). Its material-oriented estimates can miss long tactics, sacrifices, strategic factors and horizon effects. Timeout may leave depth 0/1, explicitly reported. No Pikafish binary or NNUE is installed or distributed.
2. Movement legality is tested, but tournament adjudication is incomplete: no formal perpetual check/chase, no official move-limit draw or arbiter policy. Threefold repetition stops the demonstration game with a disclosed demo rule. FEN structural validity does not prove historical reachability.
3. Twelve synthetic exercises cover only four elementary themes. Their solutions are checked against the local engine, not an independent strong engine or human gold set. Engine tests sharing the same rules are not independent proof of full correctness.
4. Explanations are deterministic Vietnamese templates. They include legal candidate lines but do not deeply diagnose a learner's strategic intent. Free-text reflection is stored without automated semantic grading. No LLM, trained ML, RAG or personalized coaching model.
5. Review covers up to the latest 24 Red moves. Bot plays Black. No Black learner review, clocks, online PvP, undo negotiation, PGN/Vietnamese notation import, review tree or evaluation timeline UI.
6. No real placement test or progression across difficulty levels. Mastery values are bounded practice scores initialized at 50 upon first evidence, not proven competence or Elo. Unseen means an unexposed authored family, not guaranteed cognitive novelty; themes remain very simple.
7. Spaced repetition uses 1/2/7/14/30 day rules. No reminder delivery, retention model, scientific efficacy validation or calendar integration. Current bank exhaustion is labeled and repeats honestly.
8. SQLite guest persistence is local, unencrypted and tied to a browser cookie. No OAuth, multi-device sync, user recovery, production migrations, backup automation or production auth. Local database file access is outside guest API isolation.
9. Development HTTP server binds loopback only. No public hosting, production ASGI stack, distributed jobs, abuse quotas, production TLS, 100-concurrent-user validation or service-level guarantees. Review requests serialize SQLite writes and can take up to about 48 seconds for 24 uncached positions.
10. UI has responsive layouts, accessible names, Vietnamese piece labels and keyboard arrow navigation but has not undergone a full WCAG audit, screen-reader user testing or wide device/browser compatibility testing. Reflection drafts now autosave to the local server and restore on reload after saving; offline persistence, cross-tab conflict resolution and feedback/import draft saving remain absent. Force-closing before save can lose changes. No drag and drop. Hash links restore a game/exercise on reload, but do not implement full browser back/forward routing.
11. Feedback saves locally and is available in export, not delivered to the project owner. No pilot results, improvement claims or research conclusions exist.

Highest-value next step: owner-review a small diverse gold set with exact FEN, acceptable alternatives, deeper-engine checks, WHAT/WHY/HOW, learner level and source permission. Then replace the shallow engine through the existing adapter before expanding claims or public deployment.

12 October 2026: `Mo_Co_Chill.cmd` provides on-demand background startup independent of ChatGPT. It is not a Windows service or login task: run it again after reboot. It opens the default browser, whose guest cookie may differ from the in-app browser. Logs stay in ignored `var/`. Automatic recovery from a crashed server and log rotation are not implemented. Launcher reuse checks HTTP page markers, not a cryptographic app identity.

Public preview: online-preview/ is a separate static guided demo, not the full Python app. No free play/import/online engine/account/synchronized database. Reflection gating is UI-only and static answers are inspectable. Two original synthetic exercises, localStorage completion markers, next-day demo reminder date without notifications. See online-preview/README.md.


## Cập nhật ChatGPT Site V4 ngày 15 tháng 10 năm 2026

Bản public đã được nâng từ demo hai bài lên prototype trình duyệt có luật, chơi máy/hai người, review, 12 bài, resume, lịch ôn và tự đánh giá. Xem [báo cáo đầy đủ](BAO_CAO_CHATGPTSITE_V4_2026_10_15.md) để biết kiểm thử, phần thật/giới hạn và các mục V4 chưa làm. Ứng dụng Python local vẫn là triển khai riêng.
