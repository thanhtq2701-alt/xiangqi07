# Định dạng nhập thế cờ `cochill-positions-v1`

Dùng để đưa một bộ thế cờ (ví dụ thế trung cuộc) vào kho bài nhiều lượt. Công cụ
`tools/import_positions.py` **chỉ kiểm luật**: FEN, bên đi, từng nước của từng
đường, thế trùng và các trường bắt buộc. Công cụ không đánh giá nước nào là tốt
nhất; mọi bản nháp đều mang nhãn "cần engine/người duyệt" và không tự vào `web/`.

## Cách chạy

```powershell
python tools/import_positions.py duong-dan\the-co.json
python tools/import_positions.py duong-dan\the-co.json --write var\import
```

- Lệnh đầu là chạy thử (dry-run): chỉ in báo cáo, không ghi file.
- `--write THƯ_MỤC` ghi `exercises.json` (khung bài `line-v1`),
  `content-en.json` (khung mục tiếng Anh `exercises#<id>.<trường>`) và
  `report.json`, chỉ khi không còn lỗi. Công cụ từ chối ghi vào `web/`.
- Mã thoát: 0 không lỗi, 1 có lỗi, 2 không đọc được file.
- Báo cáo ghi `LỖI` (phải sửa) và `LƯU Ý` (nên xem), kèm vị trí
  `positions[i] "id" (dòng N)` và số nửa nước. Nước trong báo cáo hiển thị
  bằng ký pháp Việt.
- Đọc ký pháp Việt cần Node.js (cùng mã `web/game-tools.js` của ứng dụng);
  không có Node thì chỉ nhận tọa độ máy kiểu `h2e2`.

## Cấu trúc file

File JSON UTF-8:

```json
{
  "format": "cochill-positions-v1",
  "positions": [
    {
      "id": "mid-rook-001",
      "title": {"vi": "Tên bài, không lộ lời giải", "en": "Title, no spoiler"},
      "fen": "3aka3/5R3/5R3/9/9/9/9/9/9/3K5 w",
      "sideToMove": "w",
      "phase": "middle",
      "chapterId": "coordination",
      "skill": "safety",
      "familyId": "two-rooks-palace",
      "difficulty": "intermediate",
      "objective": "mate",
      "goal": {"vi": "Mục tiêu, không lộ nước đi", "en": "Objective, no moves"},
      "lines": [
        "Xt.1 Tg5.1 Xt/1 Tg5/1 Xs-5 S4.5 X5.1",
        "Xt.1 Tg5.1 Xs.1 Tg5.1 Xt-5 S4.5 X5/1"
      ],
      "explanation": {
        "what": {"vi": "Chuyện gì xảy ra", "en": "What happens"},
        "why": {"vi": "Vì sao", "en": "Why"},
        "how": {"vi": "Cách nhận ra", "en": "How to spot it"}
      },
      "source": {"name": "Người soạn hoặc nguồn", "nameEn": "Author or source"},
      "rights": "own-work",
      "rightsNote": ""
    }
  ]
}
```

Ví dụ trên dùng lại thế của bài `v6-rooks-palace-a` nên khi chạy sẽ báo trùng;
đó là hành vi đúng.

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | Có | 3–64 ký tự `a-z`, `0-9`, `-`; không trùng kho hiện có |
| `title`, `goal` | Có | Chuỗi tiếng Việt hoặc `{"vi","en"}`; thiếu `en` là lưu ý, phải bổ sung trước khi vào `web/` |
| `fen` | Có | FEN cờ tướng, 2 hoặc 6 trường; lượt đi là `w` (Đỏ) hoặc `b` (Đen) |
| `sideToMove` | Có | Phải khớp lượt trong FEN; đây là bên người học |
| `phase` | Không | `opening`, `middle` (mặc định), `end` |
| `chapterId` | Có | Chương có sẵn trong `web/curriculum.js` |
| `skill` | Có | Một từ; nên dùng `material`, `cannon`, `horse`, `safety` để có bài cơ bản cùng kỹ năng |
| `familyId` | Không | Họ chiến thuật; mặc định bằng `id` |
| `difficulty` | Có | `intermediate` (3–4 quyết định) hoặc `advanced` (6–7); lệch số quyết định là lưu ý |
| `objective` | Có | `mate`: đường nào cũng kết thúc bằng chiếu hết. `advantage`: kết thúc không chiếu hết, chỉ thành bản nháp (xem giới hạn) |
| `lines` | Có | Đường chính đứng đầu, sau đó các biến. Mỗi đường đi từ thế đầu, người học đi trước, kết thúc bằng nước người học. Ghi bằng ký pháp Việt (`P2-5`, `M8.7`, `Xt.1`, Tượng là `V`) hoặc tọa độ máy; cách nhau bằng dấu cách, hoặc là một mảng |
| `explanation` | Không | Lời giải thích của người soạn; thiếu là lưu ý |
| `source.name` | Có | Ai soạn hoặc lấy từ đâu; `nameEn` là bản tiếng Anh |
| `rights` | Có | `own-work` (tự soạn), `permission` (được cho phép), `licensed` (có giấy phép). Chưa rõ quyền thì không nhập |
| `rightsNote` | Khi `permission`/`licensed` | Ai cho phép, giấy phép nào |

## Biến (nhiều đường)

Các đường được gộp theo phần đầu giống nhau thành cây `line-v1`:

- Hai đường khác nhau ở **nước người học** thành hai phương án cùng được chấp
  nhận tại vị trí đó.
- `line-v1` chỉ có **một nước đáp của đối thủ** cho mỗi nước được chấp nhận.
  Hai đường cùng nước người học nhưng khác nước đáp là lỗi.
- Một đường không được dừng ở chỗ đường khác còn đi tiếp, và ngược lại.

## Những gì công cụ đánh dấu cần duyệt

Mỗi bản nháp có `importReview.pending`:

1. Nước được chấp nhận có phải nước tốt nhất, nước đáp có phải phản ứng mạnh
   nhất: cần engine hoặc người duyệt.
2. `rejectedMoves` để trống: mọi nước hợp lệ ngoài cây sẽ ở trạng thái chờ
   kiểm chứng, không bị chấm sai.
3. Với `objective: "advantage"`: `format` là `line-v1-draft`, ứng dụng chưa
   chạy được (xem dưới).

`proof.method` là `author-lines`, `expertReviewed` và `pikafishVerified` là
`false`.

## Giới hạn

- Bài nhiều lượt hiện tại (`web/line-practice.js`) chỉ nhận điểm kết thúc là
  chiếu hết. Thế trung cuộc kết thúc bằng lợi thế cần mở rộng định dạng và tiêu
  chí chấm có bằng chứng engine trước khi đưa vào ứng dụng.
- Chưa có chú thích theo từng nước, chưa nhập danh sách nước sai do người soạn
  chỉ định.
- Công cụ kiểm thế trùng chính xác (lỗi), đối xứng trái–phải và đổi màu/lật bàn
  (lưu ý); không phát hiện thế "gần giống" khác vài quân.
- Đưa bản nháp vào `web/curriculum.js` và `web/content-en.js` là bước thủ công
  có người duyệt.
