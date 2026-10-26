# Engine mạnh cho Cờ Chill V5

> Cập nhật V6 ngày26/10/2026: UI bot máy chủ/review tài khoản gửi
> `requireStrong: true`. Nếu adapter phải fallback, API trả503 và không gửi
> điểm/biến thay thế. Phần fallback bên dưới chỉ mô tả chế độ cơ bản được
> gọi rõ ràng. Chưa nghiệm thu Pikafish thật trên VM của chủ sản phẩm.

## Đã có và chưa có

`app/pikafish.py` là bộ kết nối UCI có thể gọi một engine đã được chủ sở hữu cài trên máy chủ. Mã kiểm tra bắt tay, giới hạn thời gian, kiểm tra nước/biến bằng luật cờ, đánh giá riêng nước người học chọn và đóng tiến trình sau mỗi yêu cầu.

**Repository không kèm Pikafish hoặc trọng số NNUE; chưa kiểm thử sức mạnh với một binary Pikafish thực.** Bài kiểm thử dùng tiến trình UCI giả do dự án tự viết để kiểm tra giao thức và lỗi. Chưa có cấu hình thì dùng `chill-local-1.0`, tìm kiếm tối đa hai nửa nước với giới hạn thời gian. Kết quả ghi `fallback=true`, `confidence=limited`, không tự khẳng định nước tối ưu hay người học đã hiểu bài.

Tính năng này không huấn luyện AI mới và không gọi LLM. Không có tải về, mua giấy phép hoặc thực thi engine nhận từ trình duyệt.

## Cấu hình sau khi bạn có engine được phép sử dụng

1. Chọn binary đúng hệ điều hành/CPU từ nguồn chính thức. Kiểm tra nguồn, phiên bản, mã băm và điều kiện của đúng binary cùng trọng số. Không tải một file lạ rồi đổi tên thành Pikafish.
2. Giữ binary/trọng số ở máy chủ, ngoài thư mục static. Không đặt các file này hoặc mật khẩu trong Git.
3. Đặt biến môi trường trước khi khởi động server:

```powershell
$env:PIKAFISH_PATH = 'E:\Engines\pikafish\pikafish.exe'
$env:PIKAFISH_NNUE_PATH = 'E:\Engines\pikafish\pikafish.nnue'
```

Trên máy chủ Linux, dùng đường dẫn tuyệt đối Linux, ví dụ `/opt/pikafish/pikafish`. `PIKAFISH_NNUE_PATH` có thể bỏ nếu bản engine đã tự tìm được đúng trọng số; khi đặt thì file phải tồn tại. Đường dẫn không được nhập từ API/frontend. Các đường dẫn ví dụ trên **không phải file đã cài sẵn**.

Thông số tùy chọn được giới hạn tại server:

| Biến | Mặc định | Giới hạn |
|---|---:|---:|
| `PIKAFISH_QUICK_MS` | 600 ms mỗi lượt tìm | 50–3000 ms |
| `PIKAFISH_DEEP_MS` | 2000 ms mỗi lượt tìm | 100–5000 ms |
| `PIKAFISH_THREADS` | 1 | 1–2 |
| `PIKAFISH_HASH_MB` | 32 MB | 16–128 MB |

Một yêu cầu có nước cần chấm chạy hai lượt: tìm các ứng viên rồi tìm riêng nước được chọn từ cùng thế. Tổng thời gian còn gồm khởi động/kiểm tra/đóng engine; adapter có hạn chót tổng và chỉ cho một tiến trình UCI hoạt động cùng lúc trong một Python process. API cũng cần giới hạn tần suất và số worker. Threads/Hash là giới hạn yêu cầu engine tuân thủ, **không phải sandbox hệ điều hành cho một chương trình độc hại**; chỉ chạy binary tin cậy. Cần quota/container khi đưa lên hạ tầng thật.

## Hợp đồng với API và giao diện

```python
from app.pikafish import AnalysisEngine, EngineUnavailable

engine = AnalysisEngine()
status = engine.status()
result = engine.analyze(fen, moves=[], selected_move=None, mode='quick')
```

- `fen` là thế ban đầu; `moves` là lịch sử hợp lệ nối tiếp từ thế đó, tối đa 600 nửa nước. Nếu chỉ có FEN hiện tại thì bỏ `moves`. Không gửi FEN cuối kèm lại lịch sử đã áp dụng.
- Chuỗi nước dùng tọa độ `a0a1`, cùng quy ước của `app.rules` và frontend. `from`/`to` là chỉ số 0–89 tính từ hàng trên xuống.
- Kết quả gồm `candidates`, `best_move`, `selected`, `score`, `score_type`, `search`, `provenance` và cảnh báo. `lines` là alias danh sách ứng viên để dễ đọc, **không tương thích yêu cầu xếp hạng toàn bộ nước của legacy `validate_analysis`**.
- `cp` là điểm do engine UCI trả về; `mate` là số nước chiếu hết theo giao thức, giữ riêng. `heuristic_cp` là thang tự viết của fallback, không được so trực tiếp với điểm Pikafish hoặc gán Elo. Điểm dương luôn có lợi cho **bên đến lượt ở thế cuối đầu vào**, kể cả khi bên đó là Đen. Không tự đảo dấu khi so nước cùng thế.
- `selected` được tìm riêng bằng `searchmoves`; thiếu một nước trong MultiPV không có nghĩa nước ấy sai. Hai lượt tìm có thể đạt độ sâu khác nhau; giữ metadata và không dùng chênh lệch làm phán quyết tuyệt đối. `bound` phân biệt ước lượng cận với kết quả không có cận ở độ sâu hữu hạn.
- Hiển thị tối đa 20 nửa nước của biến. Không gọi đây là 20 cặp nước. Các biến được phát lại qua luật trước khi trả về.
- `status()` chỉ kiểm tra cấu hình/file. `configured_unverified` không chứng minh engine chạy được; xem kết quả thực và bộ thế đã duyệt. Phiên bản engine được giữ ở chi tiết để kiểm tra khi có báo lỗi; không cần đưa tên kỹ thuật lên màn chính.
- Không bịa phần giải thích khi engine lỗi. Timeout/malformed/biến sai/mất executable trả fallback có nhãn. `EngineUnavailable('busy')` nên thành phản hồi 429/503 và giữ bài/nháp; `ValueError` là dữ liệu đầu vào sai.
- API phải kiểm soát reflection và không cung cấp coaching trong ván đang chơi. Adapter không có ngữ cảnh tài khoản/phiên học để tự áp dụng cổng đó. Hủy ở trình duyệt phải bỏ kết quả trễ; engine vẫn có thể chạy đến hết hạn thời gian nếu server chưa có tín hiệu hủy.
- FEN đơn không chứa lịch sử chiếu/đuổi. Adapter gửi lịch sử khi có, nhưng luật phân xử lặp/đuổi ở ứng dụng vẫn cần kiểm chứng riêng. Không tuyên bố đầy đủ chuẩn giải đấu.

## Kiểm tra

```powershell
python -m unittest tests.test_pikafish -v
```

Kiểm thử: no binary/đường dẫn sai, handshake/readiness/search timeout, giới hạn output, tiến trình thoát, thiếu phân tích, bestmove/PV bất hợp lệ, cp/mate/dấu bên Đen, lịch sử, selected move từ cùng root, không trộn độ sâu, giới hạn tài nguyên, biến môi trường, queue bận và ván hết nước.

Trước khi gọi là phân tích mạnh đã nghiệm thu: chủ sở hữu cung cấp engine/trọng số đúng quyền; chạy thật trên máy chủ dự kiến; đối chiếu bộ thế đã duyệt; đo thời gian/tài nguyên; thử mất dịch vụ; xác minh frontend không dùng fallback để chấm sai chắc chắn.

## Nguồn chính thức đã đối chiếu ngày 23/10/2026

- [Pikafish và giấy phép mã nguồn](https://github.com/official-pikafish/Pikafish): kiểm tra GPL-3.0 và nghĩa vụ đi kèm đúng bản phân phối.
- [Giao thức UCI của Pikafish](https://github.com/official-pikafish/Pikafish/wiki/UCI-%26-Commands): dùng handshake, tùy chọn, FEN/lịch sử, tìm theo thời gian, MultiPV và searchmoves.
- [Kho trọng số](https://github.com/official-pikafish/Networks): điều kiện trọng số cần kiểm tra riêng, không suy luận quyền của trọng số từ giấy phép mã nguồn. Dùng đúng quyền hoặc chọn phương án được phép; không dùng lén tài liệu hay engine.

Đây là hướng dẫn tích hợp; không tự quyết định tính hợp pháp của một gói cụ thể chưa được cung cấp.
