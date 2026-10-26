from pathlib import Path
r=Path(__file__).resolve().parents[2]
p=r/'online-preview/v5-ui.js';s=p.read_text(encoding='utf-8').replace('value="lesson"','value="content"').replace('value="ui"','value="interface"')
p.write_text(s,encoding='utf-8')
p=r/'online-preview/app.js';s=p.read_text(encoding='utf-8')
s=s.replace("let state=CC.fresh()", "let publishedPuzzles=[],publishedLoaded=false;\nconst puzzleBank=()=>FIXTURES.concat(publishedPuzzles);\nlet state=CC.fresh()")
# All read sites now include server-published lessons, without rewriting bundled fixtures.
prefix,body=s.split('let state=CC.fresh()',1)
s=prefix+'let state=CC.fresh()'+body.replace('FIXTURES','puzzleBank()')
s=s.replace("JSON.stringify(state));}catch", "JSON.stringify({...state,preferences:prefs}));}catch")
s=s.replace("12 hình cờ · 4 kỹ năng", "${puzzleBank().length} hình cờ · 4 kỹ năng")
s=s.replace("${p.source==='game-local'?'Từ ván của bạn · phân tích còn nông, cần kiểm chứng.':'Bài tự dựng · chưa được chuyên gia duyệt sư phạm.'}","${p.gameId?'Từ ván của bạn · đối chiếu với giới hạn của lượt tìm kiếm.':p.status==='published'?'Bài do chủ website biên tập và duyệt · '+esc(p.source):'Bài tự dựng · chưa được chuyên gia duyệt sư phạm.'}")
s=s.replace("const title=p.source==='game-local'?", "const title=p.gameId?")
s=s.replace("function learn(){\n const session=state.session,p=currentPuzzle();", "function learn(){\n const session=state.session,p=currentPuzzle();if(p?.id?.startsWith('custom-')&&publishedLoaded&&!publishedPuzzles.some(x=>x.id===p.id))return empty('Bài đang được kiểm tra lại','Nháp được giữ; bài tạm dừng chấm cho đến khi chủ website duyệt lại.','lessons','Chọn bài khác');")
s=s.replace("Lời giải theo mẫu và nước hợp lệ. Hệ thống tìm kiếm tối đa hai nửa nước; chưa có AI chấm lập luận. Không dùng điểm này làm xếp hạng.","Lời giải theo mẫu hoặc nội dung đã duyệt, dựa trên nước hợp lệ. ${p.engine?esc(p.engine.name)+' · độ sâu ghi nhận '+p.engine.depth+' nửa nước.':''} Chưa có AI chấm lập luận. Không dùng điểm này làm xếp hạng.")
s=s.replace("if(!force&&state.session&&state.session.stage!=='summary'", "if(!force&&state.session&&!['summary','parked'].includes(state.session.stage)")
s=s.replace("state.records[p.id]?.completedAt?'Đã hoàn thành · '+date(state.records[p.id].completedAt)","state.records[p.id]?.pendingReview?'Cần học tiếp':state.records[p.id]?.completedAt?(state.records[p.id].assisted?'Đã luyện có hỗ trợ · ':'Đã luyện · ')+date(state.records[p.id].completedAt)")
s=s.replace("const filtered=state.games.slice().reverse().filter(g=>libraryFilter==='all'", "const source=libraryFilter==='archive'?state.games.slice(0,-200):libraryFilter==='favorite'?state.games:state.games.slice(-200);const filtered=source.slice().reverse().filter(g=>libraryFilter==='archive'||libraryFilter==='all'")
s=s.replace("['favorite','Yêu thích']].map", "['favorite','Yêu thích'],['archive','Kho lưu trữ']].map")
s=s.replace("<p>Đối chiếu WXF Rules 2018.","<p>Mục tiêu sản phẩm là luật thi đấu Việt Nam. Hiện chưa có văn bản chính thức và bộ tình huống đã duyệt để xác nhận tuân thủ đầy đủ. Bộ xử lý hiện tại tham khảo WXF Rules 2018.")
# Keep a proper uncompleted state after assisted explanation; the wording makes the distinction clear.
s=s.replace("lượt luyện đã kết thúc", "lượt luyện đã ghi nhận")
p.write_text(s,encoding='utf-8')
