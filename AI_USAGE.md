# Sử dụng AI trong đợt V5 — 24/10/2026

Codex hỗ trợ đọc câu trả lời V5, triển khai, rà soát, viết kiểm thử và tài liệu. Nguồn thực tế đọc là `E:\ThanhTQ\App cờ tướng\10-23\V5.docx` (940 đoạn, 96 khối câu hỏi/trả lời), cùng vật liệu dự án trước đó. Đây là hoạt động phát triển phần mềm có AI hỗ trợ, **không có nghĩa website đã có LLM hoặc một mô hình được huấn luyện**.

Trong bản chạy hiện tại:

- Luật cờ và engine xác định nước hợp lệ/biến/đánh giá trong phạm vi tìm kiếm. Adapter UCI trong `app/pikafish.py` kiểm tra kết quả trước khi dùng. Chưa cài hoặc nghiệm thu binary Pikafish và NNUE thật.
- Khi thiếu engine ngoài, tìm kiếm local có giới hạn được gắn nhãn dự phòng. Lời giải tiếng Việt theo mẫu; chưa chấm được ý nghĩa mọi câu trả lời tự do, chưa có RAG đọc sách hoặc huấn luyện từ tài liệu.
- Lịch ôn, gợi bài, mức hoạt động và thống kê là quy tắc/heuristic. Chưa có thử nghiệm chứng minh tác động học tập hoặc Elo.
- 12 bài tổng hợp có sẵn được giữ, không quảng bá là dữ liệu chuyên gia đã duyệt. Bốn ảnh thế cờ nhúng trong Word được xem để hiểu yêu cầu nhưng không phát hành thành bài: còn thiếu nguồn/quyền và thông tin xác minh đáp án.
- Logo và cover do chủ sản phẩm cung cấp được dùng cho giao diện. Không lấy code, hình hoặc kho bài của website khác.
- Tài khoản và lần học tạo trong kiểm thử là dữ liệu thử, không phải người dùng thật hay kết quả pilot. Không gửi dữ liệu học đến LLM, không tự dùng dữ liệu tài khoản làm tập huấn luyện.

Đợt này chuẩn bị code và cấu hình local; không tự push GitHub, phát hành site, mua dịch vụ hoặc công khai repository. Danh sách thực hiện và bằng chứng ở [báo cáo triển khai](IMPLEMENTATION_REPORT_CODEX.md), [test report](TEST_REPORT_CODEX.md); phần chưa làm ở [đối chiếu V5](docs/V5_DECISIONS_2026_10_24.md).

## Lịch sử các đợt trước

Các ghi chú dưới đây mô tả đúng đợt được ghi, không thay thế trạng thái V5 phía trên.

# Cập nhật sử dụng AI ngày 16/10/2026

Codex đọc UI UX + Luật/UX35, hỗ trợ viết UI, ký phổ Việt, logic trải nghiệm và kiểm thử, soạn 41 câu hỏi V5; bản Site được phát hành bằng plugin Sites. Logo từ tài liệu chủ sản phẩm, các ảnh ứng dụng tham khảo không được sao chép lên Site. Đã đọc nguồn luật WXF chính thức và ghi phạm vi hạn chế trong `docs/RULES_UIUX_2026_10_15.md`. Sản phẩm không gọi API LLM, không huấn luyện ML và không gửi dữ liệu học đi huấn luyện. Lời giải đang là mẫu dựa trên luật; giọng thân thiện không phải AI hội thoại. Chi tiết và kết quả thực: [báo cáo phát hành](BAO_CAO_UIUX_V5_2026_10_16.md).

# AI usage and integrity

9 October 2026: Codex researched public official pages from Xiangqi services and directly inspected three interfaces to inform usability improvements. The sources, access limits and implemented changes are in RESEARCH_AND_IMPROVEMENTS_2026_10_09.md. No competitor code, imagery, puzzles or game corpus was imported; no new owner V4 answers were assumed. Added local draft/resume and accessibility improvements, without changing runtime engine or introducing LLM/ML. New browser QA attempts are test records only.

The owner supplied product intent in Answer V3.docx, the Final Pack specifications and Codex execution instructions. Codex read both complete Word texts and all archive members, inventoried the entire parent folder and inspected the older discovery question bank. No application code existed in the supplied folder.

Codex generated the Python application, rules, shallow search, template teaching logic, synthetic positions, frontend, automated tests and documentation. All are AI-assisted implementation, not human-authored gold annotations. Human work already supplied: product thesis, learning philosophy, desired workflow and domain intent. Human validation still required: chess accuracy beyond tested movement, lesson pedagogy, puzzle diversity and level suitability, reasoning rubrics, pilot interpretation.

Runtime AI status: no paid API calls, no LLM model, no neural model and no training. `LocalEngine` uses deterministic search with a deadline and cache. `TemplateProvider` explains structured legal lines. Scheduling and recommendation are heuristics. An `ExplanationProvider` interface exists, but arbitrary new provider text is rejected in favor of the canonical template until reliable semantic grounding is added.

Data: twelve original synthetic fixtures and a two-ply synthetic demonstration fragment. They are not owner games, real player records, a licensed external dataset or an expert-reviewed gold set. Automated legality/depth-2 verification is distinct from expert pedagogical validation.

12 October 2026: Codex added and tested a local Windows launcher and startup documentation. This adds no LLM calls, training, external hosting or data transmission.

UI tests created local demonstration attempts solely to verify behavior. Those records are test evidence, not evidence of user learning, adoption or impact. No claims of trained ML, measured improvement, users or concurrent capacity are made. Future training reuse must require separate consent and reviewed data provenance.

12 October 2026: Codex polished repository documentation and prepared a public-readiness report with historical pattern scanning and fresh automated checks. No new model integration, external dataset, public deployment or learner-data transmission was added.

12 October 2026: Codex created a separate public static preview via the Sites plugin. Two original fixtures and legal-move sets were exported from the existing rules; no LLM-generated analysis or third-party chess assets. Browser-local completion timestamps are not learning-impact evidence. The owner's plan and private repository documents are excluded from deployed assets.


## Cập nhật ChatGPT Site V4 ngày 15 tháng 10 năm 2026

Bản public đã được nâng từ demo hai bài lên prototype trình duyệt có luật, chơi máy/hai người, review, 12 bài, resume, lịch ôn và tự đánh giá. Xem [báo cáo đầy đủ](BAO_CAO_CHATGPTSITE_V4_2026_10_15.md) để biết kiểm thử, phần thật/giới hạn và các mục V4 chưa làm. Ứng dụng Python local vẫn là triển khai riêng.
