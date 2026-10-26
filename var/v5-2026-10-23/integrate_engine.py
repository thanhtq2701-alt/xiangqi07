from pathlib import Path
p=Path(__file__).resolve().parents[2]/'online-preview/app.js'
s=p.read_text(encoding='utf-8')
def fun(name,nextname,code):
    global s
    a=s.index('function '+name+'(')
    if s[a-6:a]=='async ':a-=6
    b=s.index('function '+nextname+'(',a)
    if s[b-6:b]=='async ':b-=6
    s=s[:a]+code.strip()+'\n'+s[b:]
s=s.replace("let internalNavigation=false,restoringNavigation=false;","let internalNavigation=false,restoringNavigation=false;\nlet analysisTask=null;")
fun('maybeBot','inferSkill',r'''
async function maybeBot(g){
 if(busy||!g||g.mode!=='bot'||g.status.over||XQ.Position.fromFen(g.fen).turn===g.player)return;
 busy=true; if(route()[0]==='game')render();
 const initialFen=g.fen, started=Date.now();
 try{
   if(tickGame(g)||g.status.over)return;
   const pos=XQ.Position.fromFen(g.fen);let move;
   if(g.engineChoice==='server'){
     const cloud=window.CCCloudUI?.snapshot();
     if(!cloud?.client.session.authenticated)throw new Error('Cần đăng nhập để dùng máy chủ. Chọn máy cơ bản để chơi không cần tài khoản.');
     if(cloud.client.pending&&!await cloud.client.flush())throw new Error('Chưa đồng bộ được ván.');
     const a=await cloud.client.request('/api/engine/analyze',{method:'POST',body:{purpose:'bot',gameId:g.id,fen:g.fen,mode:'quick'}});
     move=a.best_move;g.engineLabel=a.fallback?'Máy cơ bản dự phòng':a.engine_name||'Engine máy chủ';
   }else{
     await new Promise(r=>setTimeout(r,50));
     const a=XQ.analyze(pos,{depth:g.depth,maxMs:g.depth===2?550:180});move=a.bestMove;g.engineLabel='Máy cơ bản · '+a.depth+' nửa nước';
   }
   if(g.fen!==initialFen||g.status.over||!state.games.includes(g))return;
   if(!pos.legalMoves().includes(move))throw new Error('Máy chưa trả được nước hợp lệ.');
   busy=false;moveGame(g,move);
 }catch(error){
   // Server failures never become a human timeout. Keep the board and mark a technical pause.
   if(state.games.includes(g)&&!g.status.over){g.technicalPause=true;g.clock.last=Date.now();g.engineError=error.message;save();toast('Đã tạm dừng ván do máy chưa trả nước. Có thể thử lại hoặc kết thúc với nhãn sự cố kỹ thuật.');}
 }finally{busy=false;if(route()[0]==='game')render();}
}
''')
fun('analyzeGame','moments',r'''
async function analyzeGame(g,analysisMode='quick'){
 if(!g||!g.status.over||busy||activeGame())return;
 const task={controller:new AbortController(),route:location.hash};analysisTask=task;busy=true;analysisProgress='Đang chuẩn bị phân tích…';render();
 try{
   const cloud=window.CCCloudUI?.snapshot(),remote=!!cloud?.client.session.authenticated;
   if(remote&&cloud.client.pending&&!await cloud.client.flush())throw new Error('Chưa đồng bộ được ván. Mở Tài khoản để xử lý trước khi phân tích.');
   const turns=g.moves.map((m,i)=>({...m,ply:i})).filter(m=>g.mode==='local'||m.side===g.player).slice(-20),found=[];
   let fallback=false,engineName='Máy cơ bản trên thiết bị';
   for(let n=0;n<turns.length;n++){
     if(analysisTask!==task||task.controller.signal.aborted)return;
     analysisProgress=`Đang kiểm tra vị trí ${n+1} / ${turns.length}`;
     if($('analysis-progress'))$('analysis-progress').textContent=analysisProgress;
     const m=turns[n],pos=XQ.Position.fromFen(m.before);
     const raw=remote?await cloud.client.request('/api/engine/analyze',{method:'POST',signal:task.controller.signal,body:{purpose:'review-scan',gameId:g.id,fen:g.initialFen,moves:g.moves.slice(0,m.ply).map(x=>x.move),selectedMove:m.move,mode:analysisMode}}):CoChillEngine.local(pos,m.move,XQ.analyze);
     const a=CoChillEngine.validate(pos,raw);fallback=fallback||a.fallback;engineName=a.engine_name;
     const best=a.candidates[0],actual=a.selected,loss=CoChillEngine.difference(best,actual);
     if(!best||!actual||loss===null||loss<80||best.move===m.move)continue;
     const skill=inferSkill(pos,m.move),alternatives=a.candidates.filter(x=>CoChillEngine.difference(best,x)!==null&&CoChillEngine.difference(best,x)<=35).map(x=>x.move);
     let pvPos=pos;const line=best.pv.map(v=>{const description=XQ.describe(pvPos,v);pvPos=pvPos.play(v);return description;}).join('; sau đó ');
     found.push({id:g.id+'-p'+m.ply,title:'Vị trí ở nửa nước '+(m.ply+1),fen:pos.fen(),solution:best.move,alternatives,skill,source:a.fallback?'game-local':'game-engine',gameId:g.id,ply:m.ply,loss,
       what:`Trong ván bạn đi ${XQ.describe(pos,m.move)}. ${a.fallback?'Tìm kiếm cơ bản gợi ý':'Kết quả tìm kiếm đề xuất'} một phương án để đối chiếu; chưa phải phán quyết chắc chắn về tư duy.`,
       why:`Biến hợp lệ được tính: ${line}. Chênh lệch ${Math.round(loss)} điểm ${a.fallback?'quy ước tìm kiếm nông':'centipawn của engine'} từ cùng thế và cùng bên đi.`,
       how:HOW[skill],engine:{name:a.engine_name,fallback:a.fallback,depth:a.search?.depth,scoreType:best.score_type},pv:best.pv});
     await new Promise(r=>setTimeout(r,0));
   }
   if(analysisTask!==task||task.controller.signal.aborted)return;
   g.moments=found.sort((a,b)=>a.ply-b.ply);
   g.analysis={at:Date.now(),mode:analysisMode,positions:turns.length,fallback,engineName,limited:turns.length<g.moves.length};save();
 }catch(error){if(!task.controller.signal.aborted)toast(error.message||'Chưa phân tích được. Biên bản ván được giữ.');}
 finally{if(analysisTask===task){analysisTask=null;busy=false;render();}}
}
''')
fun('moments','replay',r'''
function moments(g){
 if(!g)return empty('Chưa có ván để xem lại','Chơi hoặc nhập một ván trước.','play','Mở trang chơi');
 if(!g.status.over)return empty('Ván đang diễn ra','Kết thúc ván rồi mở phần phân tích.','game/'+g.id,'Tiếp tục ván');
 return `${heading('Những điểm đáng nhìn lại','Chọn một hình để tự đánh giá trước khi xem phương án.','mistakes')}<p class="notice">${g.analysis?`${esc(g.analysis.engineName)} · đã kiểm tra ${g.analysis.positions} vị trí · ${g.analysis.mode==='deep'?'lượt phân tích kỹ hơn':'lượt phân tích nhanh'}. ${g.analysis.fallback?'Đang dùng máy cơ bản; gợi ý cần được đối chiếu.':''}`:'Kiểm tra tối đa 20 lượt gần nhất của bên bạn chọn. Số vị trí được đề xuất phụ thuộc bằng chứng; không ép mỗi ván phải có ba lỗi.'}</p>${busy?`<section class="panel empty"><span class="spinner"></span><p id="analysis-progress">${esc(analysisProgress)}</p>${btn('Hủy lượt phân tích','cancel-analysis','','secondary')}</section>`:g.moments?g.moments.length?'<div class="list">'+g.moments.map((p,i)=>`<div class="list-row"><div class="row-main"><span class="mini-icon">${i+1}</span><div><h3>${esc(p.title)}</h3><p>${state.records[p.id]?.pendingReview?'Cần học tiếp':state.records[p.id]?.completedAt?'Đã luyện · '+date(state.records[p.id].completedAt):'Tự quan sát trước khi xem phân tích'}</p></div></div>${btn('Suy nghĩ ở đây →','start',p.id,'secondary')}</div>`).join('')+'</div>':empty('Chưa có điểm cần sửa đủ rõ trong lượt tìm kiếm này','Bạn có thể viết ghi chú, chọn bài khác hoặc yêu cầu phân tích kỹ hơn. Kết quả này chưa chứng minh toàn ván hoàn hảo.'):`<section class="panel empty">${btn('Tìm điểm cần học →','analyze',g.id)}</section>`}<div class="button-row">${!busy&&g.moments?btn('Phân tích kỹ hơn','analyze-deep',g.id,'secondary'):''}<a class="secondary" href="#replay/${g.id}">Xem lại toàn ván</a><a class="quiet" href="#lessons">Chọn bài học khác</a></div>`;
}
''')
# Technical pause guards and recovery actions.
s=s.replace("if(!g.clock?.enabled)return '∞';", "if(g.technicalPause)return 'Tạm dừng';if(!g.clock?.enabled)return '∞';")
s=s.replace("if(!g||g.status.over||!g.clock?.enabled)return false;", "if(!g||g.status.over||g.technicalPause||!g.clock?.enabled)return false;")
s=s.replace("if(!g||g.status.over||busy)return;", "if(!g||g.status.over||g.technicalPause||busy)return;")
s=s.replace("${g.status.over?`<div class=\"game-result\">", "${g.technicalPause?`<p class=\"notice\">Máy gặp sự cố. Đồng hồ tạm dừng; ván chưa bị tính thua. ${esc(g.engineError||'')}</p><div class=\"button-row\">${btn('Thử máy lại','retry-bot',g.id,'secondary')}${btn('Kết thúc do kỹ thuật','technical-end',g.id,'quiet')}</div>`:''}${g.status.over?`<div class=\"game-result\">")
s=s.replace("case'rematch':", "case'retry-bot':{const g=state.games.find(x=>x.id===v);g.technicalPause=false;g.clock.last=Date.now();save();maybeBot(g);break;}case'technical-end':{const g=state.games.find(x=>x.id===v);g.technicalPause=false;g.status={over:true,winner:null,reason:'Kết thúc do sự cố kỹ thuật',technical:true};save();render();break;}case'rematch':")
s=s.replace("'Máy tìm kiếm tối đa '+g.depth+' nửa nước · chưa xếp hạng.'", "(g.engineLabel||'Máy cơ bản · chưa xếp hạng')")
# Two distinct actions for local draw consent.
start=s.index(" case'resign':case'draw':")
end=s.index(" case'retry-bot':",start)
s=s[:start]+r'''
 case'resign':{const g=state.games.find(x=>x.id===v);if(!g||g.status.over||!confirm('Xin thua và kết thúc ván này?'))break;g.status={over:true,winner:XQ.other(g.mode==='bot'?g.player:XQ.Position.fromFen(g.fen).turn),reason:'Xin thua'};save();render();break;}
 case'draw':{const g=state.games.find(x=>x.id===v);if(!g||g.status.over||g.mode!=='local')break;g.drawOffer={from:XQ.Position.fromFen(g.fen).turn,expiresAt:Date.now()+15000};save();render();break;}
 case'draw-accept':case'draw-decline':{const g=state.games.find(x=>x.id===v);if(!g?.drawOffer||g.status.over)break;if(a==='draw-accept'&&g.drawOffer.expiresAt>Date.now()&&!tickGame(g))g.status={over:true,winner:null,reason:'Hai bên đồng ý hòa'};delete g.drawOffer;save();render();break;}
'''+s[end:]
s=s.replace("<h3>Biên bản</h3>${notationTable(g)}", "${g.drawOffer&&!g.status.over&&g.drawOffer.expiresAt>Date.now()?`<div class=\"notice\"><p>${g.drawOffer.from==='w'?'Đỏ':'Đen'} đề nghị hòa. Bên còn lại xác nhận trong 15 giây; đồng hồ vẫn chạy.</p>${btn('Đồng ý hòa','draw-accept',g.id,'secondary')}${btn('Từ chối','draw-decline',g.id,'quiet')}</div>`:''}<h3>Biên bản</h3>${notationTable(g)}")
s=s.replace("if(g){if(tickGame(g))", "if(g){if(g.drawOffer&&g.drawOffer.expiresAt<=Date.now()){delete g.drawOffer;save();if(route()[0]==='game')render();}if(tickGame(g))")
s=s.replace("if(activeGame())return toast('Kết thúc ván đang chơi trước khi tạo ván khác.');", "if(activeGame())return toast('Kết thúc ván đang chơi trước khi tạo ván khác.');if(engineChoice==='server'&&!window.CCCloudUI?.sessionUser())return toast('Đăng nhập để dùng máy chủ, hoặc chọn máy cơ bản trên thiết bị.');")
# Accessible Ctrl+Enter; ordinary Enter stays a newline.
s=s.replace("document.addEventListener('keydown',e=>{const button=", "document.addEventListener('keydown',e=>{if(e.ctrlKey&&e.key==='Enter'&&e.target.closest('#reflection-form')){e.preventDefault();$('reflection-form').requestSubmit();return;}const button=")
p.write_text(s,encoding='utf-8')
