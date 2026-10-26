from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'online-preview/app.js'
s=p.read_text(encoding='utf-8')
def swap(old,new):
    global s
    assert old in s,old[:100]
    s=s.replace(old,new)
def function(name,code,next_name):
    global s
    start=s.index('function '+name+'(')
    if s[start-6:start]=='async ': start-=6
    end=s.index('function '+next_name+'(',start)
    if s[end-6:end]=='async ': end-=6
    s=s[:start]+code.strip()+'\n'+s[end:]
swap("const $=id=>document.getElementById(id),KEY='co-chill-v4-browser',NAMES=", "let KEY='co-chill-v4-browser';\nconst $=id=>document.getElementById(id),NAMES=")
swap("minute:'2-digit'", "minute:'2-digit',timeZone:'Asia/Ho_Chi_Minh'")
swap("function save(){try{", "function save(){window.CCCloudUI?.save(state);try{")
swap("function dueRecords(){return Object.values(state.records).filter(r=>r.dueAt&&Date.parse(r.dueAt)<=Date.now());}","function dueRecords(){return Object.values(state.records).filter(r=>CC.reviewDueAt(r)&&Date.parse(CC.reviewDueAt(r))<=Date.now());}")
swap("state.games=state.games.slice(-200);", "/* Older games remain available in the archive; never silently truncate. */")
swap("Date.now()+10000", "Date.now()")
swap("case'about':content=about();break;", "case'about':content=about();break;case'account':content=window.CCCloudUI?.account()||empty('Đang kết nối tài khoản','Vui lòng đợi một chút.');break;case'admin':content=window.CCCloudUI?.admin()||'';break;case'editor':content=window.CCCloudUI?.editor()||'';break;case'help':content=window.CCCloudUI?.help()||'';break;case'privacy':content=window.CCCloudUI?.privacy()||'';break;")
swap("+' · Cờ Chill';applyPreferences();}", "+' · Cờ Chill';applyPreferences();window.CCCloudUI?.refreshChrome();}")
swap("state.session=CC.createSession(p,{source,related});", "state.session=CC.createSession(p,{source,related,firstExposure:!state.records[p.id]?.seenCount});")
# Mark exposure after deciding whether this was the first unseen position.
swap("state=CC.markSeen(state,p);state.session=CC.createSession(p,{source,related,firstExposure:!state.records[p.id]?.seenCount});", "const firstExposure=!state.records[p.id]?.seenCount;state=CC.markSeen(state,p);state.session=CC.createSession(p,{source,related,firstExposure});")
swap("case'start-review':beginPuzzle(findPuzzle(v),{source:'review'});break;", "case'start-review':if(state.records[v]?.pendingReview){if(activeGame())return toast('Kết thúc ván trước khi học.');state=CC.resumeParked(state,v);selected=null;save();go('learn');}else beginPuzzle(findPuzzle(v),{source:'review'});break;")
swap("if(check.reveal){state.session=CC.reveal(session);", "if(check.park){state=CC.parkPuzzle(state,session,p);selected=null;toast('Đã giữ bài chưa hoàn thành để thử lại ngày mai. Bạn có thể chuyển sang một hình dễ hơn.');}else if(check.reveal){state.session=CC.reveal(session);")
swap("const wait=Math.max(0,Math.ceil(((session.helpReadyAt||0)-Date.now())/1000));", "const wait=0;")
swap("if(session.stage==='related_pending'){", "if(session.stage==='parked'){right=`<p class=\"eyebrow\">CẦN HỌC TIẾP</p><h2>Mình quay lại hình này sau nhé.</h2><p>Ba lượt suy nghĩ đã được giữ. Đây chưa phải bài đã hoàn thành; ngày mai bạn có thể thử lại từ phần đang cần hiểu.</p><div class=\"button-row\"><a class=\"primary\" href=\"#lessons\">Chọn một bài khác</a><a class=\"secondary\" href=\"#review\">Xem lịch học tiếp</a></div>`;}else if(session.stage==='related_pending'){")
swap("if(s.related)go('summary');else nextRelated();", "if(state.session.stage==='parked'){render();return;}if(s.related)go('summary');else nextRelated();")
swap("<button class=\"primary\" type=\"submit\">Lưu & trở về trang chủ →</button>","<button class=\"primary\" type=\"submit\">Lưu & trở về trang chủ →</button><a class=\"quiet\" href=\"#home\">Bỏ qua tự đánh giá · kết quả học vẫn được giữ</a>")
swap("if(leaving&&!internalNavigation", "if(analysisTask&&location.hash!==analysisTask.route){analysisTask.controller.abort();analysisTask=null;busy=false;}if(leaving&&!internalNavigation")
swap("case'analyze':analyzeGame(state.games.find(g=>g.id===v));break;", "case'analyze':analyzeGame(state.games.find(g=>g.id===v));break;case'analyze-deep':analyzeGame(state.games.find(g=>g.id===v),'deep');break;case'cancel-analysis':analysisTask?.controller.abort();analysisTask=null;busy=false;render();toast('Đã hủy lượt phân tích; biên bản ván vẫn được giữ.');break;")
swap("<p class=\"subtle separation\">Hồ sơ trên trình duyệt, chưa có tài khoản đồng bộ. Đổi thiết bị không tự mang theo tiến độ.</p>","<p class=\"subtle separation\">Khách lưu trên máy. Đăng nhập để đồng bộ tiến độ giữa các thiết bị.</p><a class=\"primary\" href=\"#account\">Tài khoản & đồng bộ →</a>")
swap("<p>Phiên học được lưu trên trình duyệt này. Chưa có tài khoản, lưu máy chủ hoặc đồng bộ thiết bị.</p>","<p>Khách lưu trên trình duyệt. Khi đăng nhập, tiến độ được đồng bộ vào tài khoản; xem trạng thái lưu ở đầu trang.</p><a class=\"secondary\" href=\"#account\">Tài khoản, xuất và xóa dữ liệu</a>")
swap("<p class=\"notice\">Trình độ tự chọn:","<p class=\"notice\">EXP hoạt động: ${stats.independent*10+stats.assisted*3} · điểm động viên theo lượt luyện, không phải Elo hoặc trình độ. Trình độ tự chọn:")
swap("<small id=\"draft-status\">Đã lưu trên trình duyệt này</small>","<small id=\"draft-status\">Nháp được giữ trên máy; trạng thái đồng bộ ở đầu trang.</small><details class=\"separation\"><summary>Báo vấn đề về hình này</summary>${window.CCCloudUI?.feedbackForm('#learn/'+p.id)||''}</details>")
swap("if(imported&&state.games.some(g=>g.initialFen===fen&&JSON.stringify(g.moves.map(m=>m.move))===JSON.stringify(moves)))return toast('Ván hoặc thế cờ này đã có trong Ván của tôi.');", "if(imported){const duplicate=state.games.find(g=>g.initialFen===fen&&JSON.stringify(g.moves.map(m=>m.move))===JSON.stringify(moves));if(duplicate){go('moments/'+duplicate.id);return toast('Đã mở biên bản có sẵn; không tạo bản trùng.');}}")
swap("newGame({color:data.get('color'),seconds,increment,depth:Number(data.get('depth')||1)});", "newGame({color:data.get('color'),seconds,increment,depth:Number(data.get('depth')||1),engineChoice:String(data.get('engine')||'local')});")
swap("increment=0,depth=1}={})", "increment=0,depth=1,engineChoice='local'}={})")
swap("player:color,depth,initialFen", "player:color,depth,engineChoice,initialFen")
swap("<span>Mức tìm kiếm của máy</span>","<span>Mức tìm kiếm cơ bản</span>")
swap("<option value=\"2\">Kỹ hơn · tối đa 2 nửa nước</option></select></label>","<option value=\"2\">Kỹ hơn · tối đa 2 nửa nước</option></select></label><label class=\"field\"><span>Bộ tính nước</span><select name=\"engine\"><option value=\"local\">Cơ bản · chạy trên thiết bị</option><option value=\"server\">Máy chủ · cần tài khoản, tùy engine đã cài</option></select></label>")
swap("<span>FEN ban đầu · có thể để trống</span>","<span>FEN đầu ván · để trống để dùng thế xuất phát</span>")
swap("newGame({fen,moves:parsed.moves,imported:true,color:String(data.get('reviewSide'))});", "if(XQ.Position.fromFen(fen).fen()!==XQ.Position.fromFen(XQ.START_FEN).fen()||!parsed.moves.length)throw new Error('Nhập ván cần biên bản từ thế xuất phát. FEN đơn lẻ chưa được coi là một ván đầy đủ.');if(!data.has('completeRecord'))throw new Error('Xác nhận bạn đã nhập đủ biên bản từ đầu đến cuối.');newGame({fen,moves:parsed.moves,imported:true,color:String(data.get('reviewSide'))});")
swap("<button class=\"secondary\" type=\"submit\">Kiểm tra & mở ván</button>","<label class=\"check-line\"><input type=\"checkbox\" name=\"completeRecord\" required><span>Tôi đã nhập toàn bộ biên bản từ đầu đến cuối (kết quả có thể do đầu hàng/thỏa thuận).</span></label><button class=\"secondary\" type=\"submit\">Kiểm tra & mở ván</button>")
# New Home priority, keeping the owner's four destinations and current layout.
swap("function home(){const due=dueRecords().length,s=state.session,ongoing=s&&s.stage!=='summary';", "function home(){const due=dueRecords().length,s=state.session,g=activeGame(),ongoing=s&&!['summary','parked'].includes(s.stage);")
swap("<section class=\"home-intro\"><span", "<section class=\"home-intro\"><img class=\"home-cover\" src=\"cover-co-chill.png\" alt=\"Cờ Chill · câu lạc bộ cờ tướng\" width=\"1536\" height=\"1024\"><span")
swap("${ongoing?'Bài học của bạn vẫn ở đây':due?`${due} hình cờ đã đến lúc ôn`:'Bắt đầu bằng một thế cờ nhỏ'}", "${g?'Ván của bạn đang tiếp tục':due?`${due} hình cờ đã đến lúc ôn`:ongoing?'Bài học của bạn vẫn ở đây':'Bắt đầu bằng một thế cờ nhỏ'}")
swap("${ongoing?'Câu trả lời và bước đang làm đã được giữ lại.':due?'Ôn một chút, rồi tiếp tục hành trình.':'Khoảng 3–5 phút · Không cần tài khoản'}", "${g?'Quay lại ván; đồng hồ vẫn chạy nếu bạn đã chọn tính giờ.':due?'Ôn một chút, rồi tiếp tục hành trình.':ongoing?'Câu trả lời và bước đang làm đã được giữ lại.':'Khoảng 3–5 phút · Không cần tài khoản'}")
swap("${ongoing?btn('Tiếp tục →','resume'):due?'<a class=\"primary\" href=\"#review\">Ôn hôm nay →</a>':'<a class=\"primary\" href=\"#howto\">Bắt đầu chơi →</a>'}","${g?`<a class=\"primary\" href=\"#game/${g.id}\">Tiếp tục ván →</a>`:due?'<a class=\"primary\" href=\"#review\">Ôn hôm nay →</a>':ongoing?btn('Tiếp tục →','resume'):'<a class=\"primary\" href=\"#howto\">Bắt đầu chơi →</a>'}")
function('reviews',r'''
function reviews(){
 const rows=Object.values(state.records).filter(r=>CC.reviewDueAt(r)).sort((a,b)=>Date.parse(CC.reviewDueAt(a))-Date.parse(CC.reviewDueAt(b))),s=state.session;
 return `${heading('Ôn tập','Học tiếp phần chưa hiểu, rồi ôn những hình đã hoàn thành. Giờ Việt Nam · UTC+7.')}${s&&!['summary','parked'].includes(s.stage)?`<div class="next-up"><div><strong>Bài đang dở vẫn được giữ</strong><p>Tiếp tục đúng bước và câu trả lời.</p></div>${btn('Tiếp tục →','resume')}</div>`:''}${['game','lesson'].map(group=>{const entries=rows.filter(r=>{const p=findPuzzle(r.puzzleId);return p&&(group==='game'?!!p.gameId:!p.gameId);});return `<section class="panel separation"><h2>${group==='game'?'Từ ván của bạn':'Từ bài học'}</h2>${entries.length?entries.map(r=>{const p=findPuzzle(r.puzzleId),due=CC.reviewDueAt(r),late=Date.parse(due)<=Date.now();return `<div class="list-row"><div><h3>${esc(p.title)}</h3><p class="${late?'due-now':''}">${r.pendingReview?'Cần học tiếp · chưa hoàn thành':'Ôn hình đã học'} · ${late?'Đến hạn':'Hẹn '+date(due)}</p></div>${btn(r.pendingReview?'Học tiếp':'Ôn lại','start-review',p.id,'secondary')}</div>`;}).join(''):'<p>Chưa có hình trong hàng đợi này.</p>'}</section>`;}).join('')}<p class="notice separation">Lịch hoàn thành: 1 / 2 / 7 / 14 / 30 ngày theo kết quả. Hình chưa giải được được hẹn học tiếp ngày sau, không tính là hoàn thành. Tự đánh giá không thay đổi lịch.</p>`;
}
''','summary')
function('about',r'''
function about(){return `${heading('Về Cờ Chill','Bản V5 · chơi, suy nghĩ, vận dụng và trở lại.')}<article class="article"><h2>Vòng học đang hoạt động</h2><p>Chơi với máy hoặc hai người một thiết bị, nhập biên bản từ đầu ván, chọn điểm cần xem lại, tự nêu nhận định và một nước, đối chiếu lời giải, thử lại, luyện một hình liên quan và ôn theo lịch. Ba lượt chưa tìm ra được giữ là cần học tiếp.</p><h2>Tài khoản và quản trị</h2><p>Khi chạy cùng máy chủ Cờ Chill, bạn có thể đăng ký, đăng nhập, đồng bộ giữa thiết bị, xuất và xóa dữ liệu. Chủ website có thống kê, phản hồi và công cụ biên tập. Bản chỉ có giao diện tĩnh vẫn dùng chế độ khách.</p><h2>Phân tích có căn cứ</h2><p>Luật kiểm tra nước đi. Bộ kết nối Pikafish chỉ hoạt động khi người vận hành cài engine và trọng số phù hợp; chưa có sẵn trong mã nguồn. Khi dùng tìm kiếm cơ bản, giao diện ghi rõ giới hạn. Mọi chuỗi được phát lại qua luật; điểm vật chất tìm kiếm nông không chứng minh một sai lầm chiến lược.</p><h2>Giới hạn hiện tại</h2><p>Lời giải theo mẫu, chưa có LLM chấm lập luận, AI tự huấn luyện, Elo được kiểm định, PvP online hoặc giáo trình lớn đã duyệt. 12 hình mẫu tự dựng dùng để thử vòng học. Bộ luật giải đấu Việt Nam và các chuỗi chiếu/đuổi phức tạp chưa được xác minh đầy đủ.</p><div class="button-row"><a class="primary" href="#help">Trợ giúp & phản hồi</a><a class="secondary" href="#privacy">Cách sử dụng dữ liệu</a></div></article>`;}
''','applyPreferences')
p.write_text(s,encoding='utf-8')
ui=root/'online-preview/v5-ui.js'
t=ui.read_text(encoding='utf-8').replace("user.role==='owner'", "user.role==='admin'").replace("sessionUser()?.role!=='owner'", "sessionUser()?.role!=='admin'")
ui.write_text(t,encoding='utf-8')
i=root/'online-preview/index.html'
t=i.read_text(encoding='utf-8').replace('<link rel="stylesheet" href="style.css">','<link rel="stylesheet" href="style.css">\n  <link rel="stylesheet" href="v5.css">')
t=t.replace('<script src="app.js" defer></script>','<script src="cloud-client.js" defer></script>\n  <script src="engine-client.js" defer></script>\n  <script src="app.js" defer></script>\n  <script src="v5-ui.js" defer></script>')
t=t.replace('<div class="workspace">','<div class="workspace">\n    <div class="account-strip"><a id="account-link" href="#account">Đăng nhập / đăng ký</a><span id="sync-status" role="status">Khách · lưu trên máy</span><a id="admin-link" href="#admin" hidden>Quản trị</a><a href="#help">Trợ giúp</a></div>')
t=t.replace('<span>Lưu trên trình duyệt này</span>','<span id="storage-location">Lưu trên trình duyệt này</span>')
i.write_text(t,encoding='utf-8')
