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

# Nhập bài từ file Excel của chủ dự án (`tools/import_curriculum_xlsx.py`)

Dùng cho file `var/import/CoChill_70_bai_final.xlsx` (70 bài, nhập ngày
20/11/2026). Thư mục `var/` được Git bỏ qua: file Excel được đọc tại chỗ, không
sao chép, không sửa, không commit. Công cụ chỉ dùng thư viện chuẩn của Python
(file .xlsx là file zip chứa XML) và kiểm luật bằng `app/rules.py`.

```powershell
python tools/import_curriculum_xlsx.py                  # chạy thử: chỉ báo cáo
python tools/import_curriculum_xlsx.py --write          # ghi web/curriculum-pack.js
python tools/import_curriculum_xlsx.py --translation-template var\import\can-dich.json
python tools/stamp_static_versions.py                   # sau khi ghi
```

- Mã thoát: 0 không lỗi, 1 có lỗi (không ghi gì), 2 không đọc được file.
- Chạy lại trên cùng file cho ra đúng từng byte cũ ("đã khớp, không cần ghi
  lại"), nên không bao giờ nhân đôi bài. `version` của một bài chỉ tăng khi
  cây nước đi đổi (nháp đang làm của bài đó sẽ không khôi phục); đổi chữ thì
  giữ nguyên.

## Sheet và cột được đọc

| Sheet | Cột | Vào trường |
|---|---|---|
| `Du_lieu_ky_thuat` (chuẩn cho logic) | `id`, `loai_bai`, `chu_de`, `muc_do`, `so_quyet_dinh`, `ben_di`, `fen`, `loi_giai_uci`, `nguon` | `id`, `objective` (`mate`/`material`), `chapterId` + `phase`, `difficulty`, `decisions`, `learner`, `fen`, `exampleLine`, `source` |
| `Bai_hoc` | `danh_gia_hinh_co`, `muc_tieu`, `ghi_chu_kiem_chung` | `assessment` (nhận định thế cờ), `idea` (ý tưởng chính), `urgency` (vì sao phải hành động ngay); các cột còn lại chỉ để đối chiếu |
| `Cay_nuoc_di` | `node_id`, `next_node_id`, `uci_nguoi_hoc`, `uci_doi_thu`, `uci_nuoc_khac_chap_nhan`, `ly_do_nuoc_di`, `phan_ung_can_luu_y`, `nuoc_khac_chap_nhan` | `nodes`, `choices[].move/.reply/.next`, nước khác được nhận, `choices[].reason`, `nodes[].watchOut`, `choices[].note`; ký pháp Việt chỉ để đối chiếu |

Không nhập: cột `hinh_co` (ảnh; bàn cờ vẽ từ FEN) và sheet `Engine_doi_chieu`
(tham khảo, không phải đáp án). Tiêu đề, mục tiêu trước khi giải, nhãn độ khó và
nhãn kiểm chứng sinh từ mẫu, có sẵn tiếng Anh. Chương: Khai cuộc →
`opening-foundation`, Xe → `rook`, Pháo → `cannon`, Mã → `horse`, Tốt → `pawn`,
An toàn Tướng → `kingSafety`, Phối hợp quân → `coordination`, Tàn cuộc →
`end-basic`.

## Công cụ dừng khi (LỖI)

- Thiếu sheet hoặc cột; file không phải .xlsx; phần XML quá lớn hoặc có
  `DOCTYPE`/`ENTITY`.
- `id` sai mẫu, trùng trong file, hoặc đã có trong ứng dụng; thế cờ trùng.
- FEN không đọc được; `ben_di` khác bên đi trong FEN; thế đầu đã hết ván.
- Nước UCI không hợp lệ; `so_quyet_dinh` khác số lượt trong `loi_giai_uci`.
- `Cay_nuoc_di` lệch `loi_giai_uci` (nước người học, nước đáp, `node_id`,
  `next_node_id`, số dòng); thiếu `ly_do_nuoc_di`.
- Bài Chiếu hết mà nước cuối chưa chiếu bí; bài Ăn quân mà cuối biến đã hết ván
  hoặc quân lực không hơn lúc đầu (thang điểm quân thô, giống
  `web/line-practice.js`).
- Nước khác được nhận không hợp lệ, không đạt mục tiêu, hoặc (ở lượt giữa) không
  dẫn tới cùng thế sau nước đáp.
- `Bai_hoc` lệch `Du_lieu_ky_thuat`; thiếu nhận định, mục tiêu hoặc ghi chú.
- Thiếu bản dịch tiếng Anh trong `tools/curriculum_pack_en.json`, hoặc bản dịch
  còn chữ Việt, có từ bị bảng thuật ngữ cấm, có tọa độ máy.

## Lưu ý (không dừng)

- Ở nước cuối bài chiếu hết, mọi nước chiếu bí ngay mà cây không ghi đều được
  thêm vào đáp án (`auto: "mate"`), vì bộ luật chứng minh được.
- Có nước chiếu bí ngay ở lượt giữa: chỉ báo, trong ứng dụng vẫn chờ kiểm chứng.
- Ký pháp Việt của tác giả khác cách ghi của ứng dụng (cần Node.js); giao diện
  luôn dùng cách ghi của ứng dụng.
- Bài Đen đi trước mà `muc_tieu` không mở đầu bằng "Đen đi trước.".
- Số quyết định nằm ngoài khoảng của mức độ (trung cấp 3–4, khó 5–7).

## Bản dịch tiếng Anh

`tools/curriculum_pack_en.json` ghi `{"tiếng Việt": "English"}` cho mọi đoạn chữ
của tác giả. Đổi chữ trong Excel thì bản dịch cũ không còn khớp và công cụ báo
thiếu: chạy `--translation-template` để có danh sách cần dịch (đã điền sẵn bản
dịch còn dùng được), dịch theo `docs/I18N_GLOSSARY.md`, rồi chạy lại. Ký pháp
trong bản tiếng Anh dùng WXF (X5.5 → R5+5).
