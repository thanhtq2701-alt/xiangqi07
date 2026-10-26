/* V6 friendly online rooms. The server owns identity, moves, clock and results.
 * No engine/coaching payload is requested while a room is live. */
(function (root, factory) {
  'use strict';
  const api=factory(root);
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  if(root){root.CCOnline=api;if(root.document&&typeof render==='function')api.install();}
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const LIVE=new Set(['playing','paused']);
  const PROTECTED=new Set(['learn','line','practice','lesson','lessons','opening','moments','replay','review','path','rules','howto','editor','course','chapter','chapter-lesson']);
  const PRESETS={rapid:'10 phút + 5 giây',blitz:'5 phút + 3 giây',bullet:'1 phút',untimed:'Không giới hạn'};
  const LABELS={waiting:'Chờ hai người sẵn sàng',playing:'Ván đang diễn ra',paused:'Ván tạm dừng · cả hai cần sẵn sàng lại',finished:'Ván đã kết thúc'};
  let session=null,room=null,listing=null,problem='',working=false,loading=false,chosen=null,epoch=0,authKey='',lastSession=0,lastHistory='',flipped=false,installed=false;
  function code(value){const s=String(value||'').trim().toUpperCase();return /^[0-9A-F]{10}$/.test(s)?s:null;}
  function isLive(){return !!room&&LIVE.has(room.status);}
  function blocks(page){return isLive()&&PROTECTED.has(page);}
  function millis(value){return Math.max(0,Math.ceil(Number(value||0)/1000));}
  function clockLabel(value){const s=millis(value);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0');}
  function historyGame(record,XQ){
    if(!record||record.serverVerified!==true||record.mode!=='online'||record.id!=='online-'+record.gameId||!record.status?.over||!['w','b'].includes(record.player)||!Array.isArray(record.moves)||record.moves.length>600)throw new Error('Biên bản máy chủ không hợp lệ.');
    let p=XQ.Position.fromFen(record.initialFen);const moves=[];
    for(const entry of record.moves){if(entry.side!==p.turn)throw new Error('Biên bản sai lượt.');const before=p.fen(),side=p.turn;p=p.play(entry.move);moves.push({move:entry.move,before,after:p.fen(),side});}
    const date=Number(record.endedAt)*1000;if(!Number.isFinite(date)||date<946684800000)throw new Error('Biên bản thiếu thời gian.');
    return {id:record.id,title:'Giao hữu với '+String(record.opponent||'người chơi').slice(0,60),createdAt:new Date(date).toISOString(),mode:'online',player:record.player,depth:1,initialFen:record.initialFen,fen:p.fen(),moves,status:{...record.status},clock:{w:0,b:0,last:date,enabled:false,increment:0},invalidMoves:[],serverVerified:true,roomCode:record.roomCode};
  }
  function currentAuth(){const c=root.CCCloudUI?.snapshot?.();return String(c?.client?.epoch||0)+':'+String(root.CCCloudUI?.sessionUser?.()?.id||'guest');}
  function syncAuth(){const key=currentAuth();if(key!==authKey){authKey=key;epoch++;session=null;room=null;listing=null;chosen=null;lastSession=0;lastHistory='';problem='';}return epoch;}
  function remember(value){try{if(session?.user)sessionStorage.setItem('co-chill-room:'+session.user.id,value||'');}catch{}}
  function remembered(){try{return code(sessionStorage.getItem('co-chill-room:'+session.user.id));}catch{return null;}}
  async function request(path,method='GET',body){
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
    try{
      const headers={Accept:'application/json'};if(body!==undefined)headers['Content-Type']='application/json';if(method!=='GET'&&session?.csrf)headers['X-CSRF-Token']=session.csrf;
      const response=await fetch('/api/rooms'+path,{method,credentials:'same-origin',cache:'no-store',headers,body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal});
      if(!(response.headers.get('content-type')||'').includes('application/json'))throw new Error('Nơi này chưa chạy máy chủ phòng cờ. Mở bản Python cùng API để chơi trực tuyến.');
      const data=await response.json();if(!response.ok){const e=new Error(data.error||'Không kết nối được phòng cờ.');e.status=response.status;throw e;}return data;
    }catch(e){if(e.name==='AbortError')throw new Error('Máy chủ phản hồi chậm. Hãy đợi trạng thái mới; không tự gửi lặp nước.');throw e;}finally{clearTimeout(timer);}
  }
  async function identity(){const token=syncAuth(),value=await request('/session');if(token!==epoch)return false;if(session?.user?.id!==value.user?.id){room=null;listing=null;chosen=null;lastHistory='';}session=value;lastSession=Date.now();return true;}
  function accept(value){if(!code(value?.code)||!value.gameId||!LABELS[value.status])throw new Error('Trạng thái phòng không hợp lệ.');if(room?.gameId!==value.gameId||room?.fen!==value.fen)chosen=null;if(room?.gameId!==value.gameId)flipped=value.side==='b';room=value;remember(room.code);}
  async function importHistory(){
    if(!session?.user)return;const token=epoch,uid=session.user.id,records=await request('/history');if(token!==epoch||session?.user?.id!==uid)return;
    // Auth changes are checked again before writing to the active learner's store.
    if(currentAuth()!==authKey)return;
    let added=0;for(const raw of records.games||[]){if(state.games.some(g=>g.id===raw.id))continue;try{state.games.push(historyGame(raw,XQ));added++;}catch{problem='Một biên bản không vượt qua kiểm tra luật; bản gốc vẫn ở máy chủ.';}}
    if(added)save();
  }
  async function refresh({quiet=false}={}){
    if(loading||working||typeof booting!=='undefined'&&booting)return;
    syncAuth();const [page,raw]=route();if(page!=='online'&&!room&&session)return;
    if(quiet&&!room&&session)return;
    const wasLive=isLive();loading=true;try{
      if(!session||Date.now()-lastSession>10000){if(!await identity())return;}
      const token=epoch;if(!session.user)return;
      const target=page==='online'&&raw?code(raw):room?.code||remembered();
      if(page==='online'&&raw&&!target)throw new Error('Mã phòng gồm 10 ký tự 0–9 hoặc A–F.');
      if(target){
        try{const value=await request('/'+target);if(token!==epoch)return;accept(value);}
        catch(e){if(e.status===403||e.status===404){room=null;remember('');if(page==='online'&&raw)problem='Bạn chưa vào phòng này hoặc đã rời phòng. Chọn Vào chơi hoặc Xem ván bên dưới.';}else throw e;}
      }
      if((page==='online'&&!raw&&!quiet)||(!room&&page!=='online')){const value=await request('');if(token!==epoch)return;listing=value;
        if(!room&&value.mine?.[0]){const valueRoom=await request('/'+value.mine[0].code);if(token!==epoch)return;accept(valueRoom);}}
      if(room?.status==='finished'&&lastHistory!==room.gameId){await importHistory();if(token!==epoch)return;lastHistory=room.gameId;}
    }catch(e){problem=e.message;if(e.status===401){session=null;room=null;lastSession=0;}}
    finally{loading=false;const [currentPage,currentCode]=route();if(!quiet||(currentPage==='online'&&currentCode)||wasLive!==isLive())render();}
  }
  function button(label,action,value='',style='secondary',disabled=false){return `<button type="button" class="${style}" data-online-action="${action}" data-value="${esc(value)}" ${disabled||working?'disabled':''}>${esc(label)}</button>`;}
  function presetSelect(){return `<select name="preset">${Object.entries(PRESETS).map(([id,name])=>`<option value="${id}">${name}</option>`).join('')}</select>`;}
  function notices(){return `${problem?`<p class="notice" role="alert">${esc(problem)}</p>`:''}${working?'<p role="status">Đang gửi tới máy chủ…</p>':''}`;}
  function guestHTML(){return `<section class="panel"><h2>Chọn tên để vào phòng</h2><p>Khách chơi giao hữu bằng phiên máy chủ 24 giờ. Tiến độ học khách vẫn ở trình duyệt; đăng nhập để giữ tiến độ khi đổi máy.</p><form data-online-form="guest"><label class="field"><span>Tên hiển thị</span><input name="displayName" minlength="2" maxlength="60" required autocomplete="nickname"></label><button class="primary" ${working?'disabled':''}>Vào bằng tên khách</button> <a href="#account">Đăng nhập tài khoản</a></form></section>`;}
  function joinHTML(value=''){return `<form data-online-form="join"><label class="field"><span>Mã phòng</span><input name="code" value="${esc(value)}" required pattern="[0-9a-fA-F]{10}" maxlength="10" placeholder="10 ký tự" autocomplete="off"></label><div class="button-row"><button class="primary" name="role" value="join">Vào chơi</button><button class="secondary" name="role" value="watch">Xem ván</button></div></form>`;}
  function lobbyHTML(){return `${heading('Chơi trực tuyến','Giao hữu · máy chủ xác nhận nước và đồng hồ','play')}${notices()}${!session?`<section class="panel"><p>${loading?'Đang kiểm tra máy chủ…':'Cần máy chủ Cờ Chill để mở phòng.'}</p>${button('Thử kết nối lại','refresh')}</section>`:!session.user?guestHTML():`<p class="subtle">${esc(session.user.displayName)} · ${session.guest?'Phiên khách 24 giờ':'Tài khoản'} · Chưa xếp hạng sức cờ</p>${room?`<p class="notice"><a href="#online/${room.code}">Quay lại phòng ${room.code} →</a> · ${esc(LABELS[room.status])}</p>`:''}<div class="grid-2"><section class="panel"><h2>Mời một người bạn</h2><form data-online-form="create"><label class="field"><span>Thời gian</span>${presetSelect()}</label><label class="field"><span>Hiển thị phòng</span><select name="visibility"><option value="private">Riêng · vào bằng mã</option><option value="public">Cộng đồng</option></select></label><details><summary>Tự chọn đồng hồ</summary><label class="field"><span>Số phút mỗi bên · để trống dùng mức trên; 0 là không giờ</span><input name="minutes" type="number" min="0" max="60" step="1"></label><label class="field"><span>Giây cộng mỗi nước</span><input name="increment" type="number" min="0" max="30" value="0"></label></details><button class="primary" ${working?'disabled':''}>Tạo phòng</button></form></section><section class="panel"><h2>Vào phòng có sẵn</h2>${joinHTML()}<hr><form data-online-form="match"><label class="field"><span>Ghép theo thời gian · chưa ghép theo sức cờ</span>${presetSelect()}</label><button class="secondary" ${working?'disabled':''}>Tìm người chơi</button></form></section></div><section class="panel separation"><h2>Phòng cộng đồng</h2>${button('Làm mới','refresh')}${(listing?.rooms||[]).map(r=>`<div class="button-row"><b>${esc(r.code)}</b><span>${esc(LABELS[r.status])} · ${esc(PRESETS[r.options.preset]||'Tự chọn')}</span>${r.openSeat?button('Vào chơi','join',r.code):''}${button('Xem ván','watch',r.code,'quiet')}</div>`).join('')||'<p>Chưa có phòng công cộng. Bạn có thể tạo phòng hoặc tìm người chơi.</p>'}<div class="button-row">${button('Tải ván đã hoàn tất của tôi','history','', 'quiet')}${session.guest?button('Xóa phiên khách trên máy chủ','delete-guest','','quiet'):''}</div></section>`}`;}
  function offerHTML(kind,offer){if(!offer)return '';const mine=offer.by===session.user.id,label=kind==='draw'?'hòa':'đi lại';return `<div class="notice"><p>${mine?'Bạn':'Đối thủ'} đề nghị ${label}${kind==='draw'?' · hiệu lực 15 giây':''}.</p>${!mine&&room.side?button('Đồng ý',kind+'-accept')+button('Từ chối',kind+'-decline','','quiet'):''}</div>`;}
  function roomHTML(){
    const raw=route()[1];if(!session?.user)return lobbyHTML();if(!room||room.code!==code(raw))return heading('Vào phòng','Chọn vai trò trước khi tham gia.','online')+notices()+`<section class="panel">${joinHTML(code(raw)||'')}</section>`;
    const p=XQ.Position.fromFen(room.fen),mine=room.side,canMove=room.status==='playing'&&mine===p.turn&&!working;
    const old=boardFlipped;boardFlipped=flipped;let board;try{board=boardHTML(p,{interactive:canMove,chosen,last:room.moves.at(-1)});}finally{boardFlipped=old;}
    board=board.replace(/data-action="flip-board"/g,'data-online-action="flip"');
    const player=s=>`<span><b>${s==='w'?'Đỏ':'Đen'} · ${esc(room.players[s]?.displayName||'Chờ người chơi')}</b>${room.players[s]?.id===session.user.id?' · Bạn':''}</span><strong>${room.options.seconds?clockLabel(room.clock[s]):'∞'}</strong>`;
    const result=room.result?.winner?(room.result.winner==='w'?'Đỏ':'Đen')+' thắng':'Ván đã kết thúc';
    return `${heading('Phòng '+room.code,'Chia sẻ mã hoặc địa chỉ trang này để mời bạn.','online')}${notices()}<div class="learn-grid"><div class="board-panel"><div class="board-meta">${player(flipped?'w':'b')}</div>${board}<div class="board-meta">${player(flipped?'b':'w')}</div><p class="subtle">Đồng hồ cập nhật từ máy chủ. Giữ trang mở và mạng ổn định; mất kết nối 30 giây có thể bị xử thua.</p></div><section class="panel game-panel"><h2>${esc(LABELS[room.status])}</h2><p>${mine?'Bạn cầm '+(mine==='w'?'Đỏ':'Đen'):'Bạn đang xem ván'}${room.status==='playing'?' · '+(p.turn==='w'?'Đỏ':'Đen')+' đến lượt':''}</p>${room.status==='finished'?`<p class="notice">${result} · ${esc(room.result.reason)}</p>${mine?`<a class="primary" href="#moments/online-${esc(room.gameId)}">Xem lại ván của tôi →</a><p>${room.rematch.includes(session.user.id)?'Đã mời tái đấu; chờ đối thủ.':button('Mời tái đấu · đổi màu','rematch')}</p>`:''}`:''}${mine&&['waiting','paused'].includes(room.status)?button(room.ready.includes(session.user.id)?'Đã sẵn sàng · chờ đối thủ':'Sẵn sàng','ready','','primary',room.ready.includes(session.user.id)||!room.players.w||!room.players.b):''}${room.status==='paused'?'<p>Máy chủ đã tạm dừng. Cả hai xác nhận để tiếp tục, không tự ghi thắng/thua khi cùng mất kết nối.</p>':''}${offerHTML('draw',room.drawOffer)}${offerHTML('takeback',room.takebackOffer)}${mine&&room.status==='playing'?`<div class="button-row">${button('Đề nghị hòa','draw')}${button('Xin đi lại','takeback','','quiet',!room.moves.length)}</div>`:''}${mine&&isLive()?button('Đầu hàng','resign','','quiet'):button('Rời phòng','leave','','quiet')}<h3>Biên bản</h3>${notationTable({initialFen:room.initialFen,moves:room.moves.map(move=>({move}))})}<p class="subtle">Không mở hướng dẫn hoặc phân tích khi đang chơi/xem ván sống. ${esc(room.rulesNotice||'')}</p></section></div><section class="panel separation"><h2>Lời nhắn trong phòng</h2><div class="button-row">${Object.entries(room.chatOptions||{}).map(([id,text])=>button(text,'chat',id,'quiet')).join('')}</div><p class="subtle">Chỉ lời nhắn trung tính; chưa có chat tự do.</p>${(room.messages||[]).slice(-8).map(m=>`<p><b>${esc(m.displayName)}:</b> ${esc(m.message)}</p>`).join('')}<details><summary>Người xem · ${(room.spectators||[]).length}</summary>${(room.spectators||[]).map(s=>`<p>${esc(s.displayName)} ${room.ownerId===session.user.id?button('Mời rời phòng','kick',s.id,'quiet'):''}</p>`).join('')}</details></section>`;
  }
  function guardHTML(){return empty('Ván trực tuyến đang diễn ra','Hoàn tất ván hoặc rời phần xem trước khi mở nội dung học.','online/'+room.code,'Quay lại phòng');}
  async function mutate(task){if(working)return;syncAuth();const token=epoch;working=true;problem='';render();try{await task(token);}catch(e){if(token===epoch)problem=e.message;}finally{working=false;render();}}
  async function action(name,data={}){if(!room)return;const target=room.code;await mutate(async token=>{const value=await request('/'+target+'/'+name,'POST',data);if(token!==epoch)return;accept(value);chosen=null;if(name==='leave'){room=null;remember('');go('online');}if(value.status==='finished'){await importHistory();if(token===epoch)lastHistory=value.gameId;}});}
  async function join(target,watch=false){if(activeGame())throw new Error('Kết thúc ván trên thiết bị trước khi vào phòng trực tuyến.');target=code(target);if(!target)throw new Error('Mã phòng gồm 10 ký tự 0–9 hoặc A–F.');const token=epoch,value=await request('/'+target+'/'+(watch?'watch':'join'),'POST',{});if(token!==epoch)return;accept(value);go('online/'+room.code);}
  function install(){if(installed)return;installed=true;const previous=render;
    render=function onlineRender(){syncAuth();previous();if(booting)return;const [page,id]=route();if(blocks(page))$('main').innerHTML=guardHTML();else if(page==='online'){$('main').innerHTML=id?roomHTML():lobbyHTML();document.title='Chơi trực tuyến · Cờ Chill';}else if(page==='play'){const card=document.querySelector('[data-action="mode"][data-value="online"]');if(card){card.disabled=false;card.dataset.onlineAction='lobby';card.removeAttribute('data-action');const text=card.querySelector('span:last-child');if(text)text.textContent='Phòng mời bạn · ghép cộng đồng';}}};
    document.addEventListener('click',async event=>{
      const target=event.target.closest?.('[data-online-action]'),square=event.target.closest?.('[data-square]');
      if(square&&route()[0]==='online'){
        event.preventDefault();event.stopImmediatePropagation();if(!room||working||room.status!=='playing')return;const p=XQ.Position.fromFen(room.fen);if(p.turn!==room.side)return;
        const sq=square.dataset.square,piece=p.board[XQ.index(sq)];if(piece!=='.'&&XQ.side(piece)===room.side){chosen=chosen===sq?null:sq;render();return;}if(!chosen)return;
        const move=chosen+sq;if(!p.legalMoves().includes(move)){toast('Nước đi chưa hợp lệ. Chọn lại quân hoặc ô đích.');return;}
        const nonce='move_'+(root.crypto?.randomUUID?.()||Date.now().toString(36)+'_'+Math.random().toString(36).slice(2));await action('move',{move,expectedRevision:room.revision,nonce});return;
      }
      if(!target)return;event.preventDefault();event.stopImmediatePropagation();const name=target.dataset.onlineAction,value=target.dataset.value;
      if(name==='lobby'){go('online');refresh();return;}if(name==='refresh'){problem='';await refresh();return;}if(name==='flip'){flipped=!flipped;render();return;}
      if(name==='resign'&&!confirm('Đầu hàng ván trực tuyến này? Kết quả sẽ được ghi là thua.'))return;
      if(name==='delete-guest'&&!confirm('Xóa phiên khách và dữ liệu phòng có tên khách này trên máy chủ? Biên bản liên quan của đối thủ cũng bị xóa.'))return;
      if(['join','watch','history','delete-guest'].includes(name)){await mutate(async token=>{if(name==='history')await importHistory();else if(name==='delete-guest'){await request('/guest','DELETE');if(token===epoch){remember('');session=null;room=null;listing=null;lastSession=0;}}else await join(value,name==='watch');});return;}
      await action(name,name==='resign'?{confirm:true}:name==='chat'?{message:value}:name==='kick'?{userId:value}:{});
    },true);
    document.addEventListener('submit',async event=>{
      const form=event.target.closest?.('[data-online-form]');if(!form)return;event.preventDefault();event.stopImmediatePropagation();const data=new FormData(form),type=form.dataset.onlineForm,watch=event.submitter?.value==='watch';
      await mutate(async token=>{
        if(type==='guest'){const value=await request('/guest','POST',{displayName:data.get('displayName')});if(token!==epoch)return;session=value;lastSession=Date.now();return;}
        if(type==='join'){await join(data.get('code'),watch);return;}
        if(activeGame())throw new Error('Kết thúc ván trên thiết bị trước khi vào một ván trực tuyến.');
        const input={preset:data.get('preset')};if(type==='create'){input.visibility=data.get('visibility');if(String(data.get('minutes')||'').trim()!==''){input.seconds=Number(data.get('minutes'))*60;input.increment=Number(data.get('increment'));}}
        const value=await request(type==='match'?'/match':'','POST',input);if(token!==epoch)return;accept(value);go('online/'+room.code);
      });
      if(type==='guest')refresh();
    },true);
    root.addEventListener('hashchange',()=>{if(route()[0]==='online')refresh();});
    root.addEventListener('online',refresh);setInterval(()=>refresh({quiet:true}),2000);render();refresh();
  }
  return {install,isLive,blocks,guardHTML,refresh,code,clockLabel,historyGame,PRESETS,snapshot:()=>({session,room,listing,problem,working})};
});
