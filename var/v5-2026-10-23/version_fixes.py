from pathlib import Path
p=Path(__file__).resolve().parents[2]/'online-preview/app.js';s=p.read_text(encoding='utf-8')
s=s.replace("render();toast('Đã lưu giao diện trên trình duyệt này.');", "save();render();toast('Đã lưu giao diện; đăng nhập sẽ đồng bộ tùy chọn.');")
s=s.replace("if(!p)return toast('Không tìm thấy bài.');", "if(!p)return toast('Không tìm thấy bài.');if(p.id.startsWith('custom-')&&state.session?.puzzleId===p.id&&state.session.puzzle?.version!==p.version){if(!confirm('Bài đã có phiên bản mới. Xuất bản nháp hiện tại ra file rồi bắt đầu lại với nội dung mới?'))return;download('co-chill-nhap-truoc-cap-nhat.json',JSON.stringify(CC.safeExport(state),null,2));}")
s=s.replace("if(p?.id?.startsWith('custom-')&&publishedLoaded", "if(p?.id?.startsWith('custom-')&&session?.puzzle?.version!==p.version)return empty('Bài có nội dung mới','Bản nháp cũ được giữ và tạm dừng chấm. Chọn lại bài trong thư viện để xuất nháp rồi bắt đầu phiên bản mới.','lessons','Mở thư viện');if(p?.id?.startsWith('custom-')&&publishedLoaded")
p.write_text(s,encoding='utf-8')
