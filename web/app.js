'use strict';

const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const PIECES = {K:'帥',A:'仕',E:'相',H:'傌',R:'俥',C:'炮',P:'兵',k:'將',a:'士',e:'象',h:'馬',r:'車',c:'砲',p:'卒'};
const NAMES = {k:'Tướng',a:'Sĩ',e:'Tượng',h:'Mã',r:'Xe',c:'Pháo',p:'Tốt'};
const state = {page:'home', game:null, exercise:null, moments:[], selected:null, flipped:false, boot:null, hint:null, retry:false};
const sq = i => String.fromCharCode(97 + i % 9) + (9 - Math.floor(i / 9));
const date = value => value ? new Date(value).toLocaleDateString('vi-VN', {day:'numeric',month:'numeric',year:'numeric'}) : '—';
let toastTimer;
const drafts = new Map();
let draftTimer, draftQueue = Promise.resolve();
let pieceLabels = 'han';
try { pieceLabels = localStorage.getItem('chill-piece-labels') === 'vi' ? 'vi' : 'han'; } catch (_) { /* Preferences are optional. */ }

function draftStatus(id, message) {
  if (state.exercise?.id === id && $('#draft-status')) $('#draft-status').textContent = message;
}

function captureDraft(form) {
  const id = state.exercise.id;
  const entry = drafts.get(id) || {version:0};
  entry.data = Object.fromEntries(new FormData(form));
  entry.version++; entry.pending = true;
  drafts.set(id, entry);
  draftStatus(id, 'Đang giữ bản nháp trên trang…');
  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => saveDraft(id), 600);
}

function saveDraft(id = state.exercise?.id) {
  clearTimeout(draftTimer);
  const entry = drafts.get(id);
  if (!entry?.pending) return draftQueue;
  const version = entry.version, data = {...entry.data};
  // Serialize autosaves so an older response cannot overwrite a newer draft.
  draftQueue = draftQueue.then(async () => {
    draftStatus(id, 'Đang lưu bản nháp…');
    try {
      await api('/api/draft', {id, ...data});
      if (drafts.get(id)?.version === version) {
        entry.pending = false;
        draftStatus(id, 'Đã lưu bản nháp trên máy chủ cục bộ · Chưa gửi câu trả lời');
      }
    } catch (error) {
      draftStatus(id, `Chưa lưu được: ${error.message} Giữ trang mở và bấm Lưu nháp; đừng tải lại lúc này.`);
    }
  });
  return draftQueue;
}

function restoreDraft() {
  const form = $('#reflect-form'), e = state.exercise;
  if (!form || !e) return;
  const draft = drafts.get(e.id)?.data || e.draft;
  if (draft) for (const key of ['evaluation','threat','plan','confidence']) {
    if (typeof draft[key] === 'string') form.elements[key].value = draft[key];
  }
  draftStatus(e.id, drafts.get(e.id)?.pending ? 'Bản nháp chưa lưu xong · Giữ trang mở' : draft ? 'Đã khôi phục bản nháp · Đáp án vẫn được giữ kín' : 'Bản nháp sẽ tự lưu sau khi bạn nhập.');
}

async function saveAllDrafts() {
  for (const [id, entry] of drafts) if (entry.pending) await saveDraft(id);
}

async function boot() {
  try {
    state.boot = await api('/api/bootstrap');
    const [page, id] = location.hash.slice(1).split('/');
    if (page==='exercise' && /^[a-f0-9]{32}$/.test(id || '')) {
      openExercise(await api('/api/exercise?id='+id)); return;
    }
    if (page==='play' && /^[a-f0-9]{32}$/.test(id || '')) state.game=await api('/api/game?id='+id);
    state.page = ['home','play','practice','dashboard','lessons','settings'].includes(page) ? page : 'home';
    render();
  } catch (error) {
    if (state.boot) { state.page='home'; render(); toast('Không mở được bài/ván đã chọn. Bạn có thể tiếp tục từ danh sách trên trang chủ.', true); }
    else $('#main').innerHTML=`<section class="card connection-error"><h1>Chưa kết nối được Cờ Chill</h1><p>${esc(error.message)}</p><p>Trong thư mục dự án, chạy <code>python server.py --port 8765</code> và giữ cửa sổ đó mở.</p><button class="primary" data-action="reconnect">Kết nối lại</button></section>`;
  }
}

function continuePanel() {
  const pending = state.boot.dashboard.pending || [];
  if (!pending.length) return '';
  const labels = {reflection:'Tiếp tục suy nghĩ', attempt:'Tiếp tục thử nước', retry:'Tiếp tục thử lại'};
  return `<section class="card continue-card" aria-label="Bài đang học"><div><span class="eyebrow">TIẾP TỤC TỪ CHỖ ĐÃ DỪNG</span><h2>${esc(pending[0].title)}</h2><p>${esc(pending[0].skill_name)} · ${pending[0].has_draft?'Có bản nháp đã lưu':'Tiến trình đã được lưu'}</p></div><button class="primary" data-exercise="${pending[0].id}">${labels[pending[0].stage]} →</button>${pending.length>1?`<details><summary>Còn ${pending.length-1} bài đang dở</summary>${pending.slice(1).map(e=>`<button class="text-link" data-exercise="${e.id}">${esc(e.title)} · ${esc(e.skill_name)}</button>`).join('')}</details>`:''}</section>`;
}

function toast(message, error=false) {
  $('#toast').textContent = message;
  $('#toast').classList.toggle('toast-error', error);
  $('#toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 5500);
}

async function api(path, data) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 75000);
  try {
    const response = await fetch(path, {signal:controller.signal, ...(data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})});
    let result;
    try { result = await response.json(); } catch (_) { throw new Error('Máy chủ trả dữ liệu không hợp lệ. Hãy kiểm tra cửa sổ server.'); }
    if (!response.ok) throw new Error(result.error || 'Không thể xử lý yêu cầu.');
    return result;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Chờ quá lâu. Dữ liệu có thể đã được lưu; hãy mở lại ván hoặc bài từ trang chủ trước khi thử lại.');
    if (error instanceof TypeError) throw new Error('Không kết nối được server cục bộ. Kiểm tra python server.py --port 8765 đang chạy; nội dung đang nhập vẫn ở trên trang.');
    throw error;
  } finally { clearTimeout(timer); }
}

async function task(fn, label='Đang xử lý…') {
  if (!$('#busy').hidden) return;
  $('#busy-label').textContent = label;
  $('#busy').hidden = false;
  $('#main').inert = true; $('.sidebar').inert = true;
  const started = Date.now();
  const ticker = setInterval(() => { $('#busy-time').textContent = `${Math.floor((Date.now()-started)/1000)} giây · Vui lòng giữ trang mở. Không gửi lại yêu cầu.`; }, 1000);
  try { await fn(); }
  catch (error) { toast(error.message, true); }
  finally { clearInterval(ticker); $('#busy-time').textContent=''; $('#busy').hidden = true; $('#main').inert=false; $('.sidebar').inert=false; }
}

function intro(title, subtitle, eyebrow='MỖI NGÀY, HIỂU THÊM MỘT CHÚT') {
  return `<div class="page-intro"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p>${subtitle}</p></div><span class="day-pill">◷ &nbsp; Học theo nhịp của bạn</span></div>`;
}

function boardLines(flipped=false) {
  let lines = '';
  for (let y=0; y<10; y++) lines += `<path d="M 50 ${50+y*100} H 850"/>`;
  for (let x=0; x<9; x++) {
    lines += x===0 || x===8 ? `<path d="M ${50+x*100} 50 V 950"/>` : `<path d="M ${50+x*100} 50 V 450 M ${50+x*100} 550 V 950"/>`;
  }
  return `<svg class="board-svg" viewBox="0 0 900 1000" aria-hidden="true"><g stroke="#9d7e4d" stroke-width="2" fill="none">${lines}<path d="M350 50L550 250M550 50L350 250M350 750L550 950M550 750L350 950"/><rect x="39" y="39" width="822" height="922" stroke-width="3"/></g><g fill="#a18456" font-family="serif" font-size="44"><text x="170" y="517">楚 河</text><text x="585" y="517">漢 界</text></g><g fill="#917448" font-size="18" font-family="sans-serif">${Array.from({length:9},(_,x)=>`<text x="${43+x*100}" y="986">${String.fromCharCode(97+(flipped?8-x:x))}</text>`).join('')}${Array.from({length:10},(_,y)=>`<text x="8" y="${56+y*100}">${flipped?y:9-y}</text>`).join('')}</g></svg>`;
}

function heroBoard() {
  const samples = [[0,0,'r'],[4,0,'k'],[8,0,'r'],[2,2,'c'],[4,4,'p'],[6,5,'P'],[2,6,'H'],[0,7,'R'],[4,9,'K'],[7,8,'C']];
  return `<div class="mini-board"><svg viewBox="0 0 900 1000" aria-hidden="true">${boardLines().replace(/^<svg[^>]*>/,'').replace(/<\/svg>$/,'')}<g>${samples.map(([x,y,p])=>`<circle cx="${50+x*100}" cy="${50+y*100}" r="43" fill="#f8e6c4" stroke="#b28f57" stroke-width="3"/><text x="${50+x*100}" y="${68+y*100}" text-anchor="middle" font-family="serif" font-size="58" fill="${p===p.toUpperCase()?'#a74331':'#37433b'}">${PIECES[p]}</text>`).join('')}</g></svg></div>`;
}

function home() {
  const d = state.boot.dashboard;
  return `${intro('Chào bạn, cùng học cờ nhé.','Biến một nước đi chưa tốt thành một điều bạn thực sự hiểu.')}
    ${continuePanel()}<section class="hero"><div class="hero-copy"><div class="eyebrow">CỜ CHILL · HỌC TỪ VÁN CỜ CỦA MÌNH</div><h2>Đừng chỉ biết nước hay.<br>Hãy hiểu vì sao.</h2><p>Chơi một ván. Nhìn lại cách bạn suy nghĩ.<br>Thử lại, rồi mang điều vừa học sang một thế cờ mới.</p><div class="actions"><button class="primary" data-action="demo">Thử hành trình 60 giây <span>↗</span></button><button class="secondary" data-nav="play">Chơi ván mới</button></div></div><div class="hero-art">${heroBoard()}<span class="art-caption">MỖI NƯỚC ĐI LÀ MỘT CƠ HỘI HỌC</span></div></section>
    <div class="home-columns"><section><div class="section-line"><h2>Một vòng học, một bước tiến</h2><span class="small-note">Bắt đầu thật đơn giản</span></div><div class="card journey">${[['▦','Chơi & nhìn lại','Tìm điểm đáng suy nghĩ trong ván cờ.'],['✧','Tự suy nghĩ','Nói ý tưởng của bạn trước khi xem lời giải.'],['↻','Thử & áp dụng','Đi lại rồi giải một thế cờ liên quan.'],['◷','Nhớ lâu hơn','Ôn đúng lúc và theo dõi tiến bộ.']].map(([icon,title,body])=>`<div class="journey-step"><span class="step-icon">${icon}</span><h3>${title}</h3><p>${body}</p></div>`).join('')}</div><div class="card next-card"><span class="next-icon">◷</span><div><h3>${d.due.length ? `${d.due.length} kỹ năng đến lịch ôn` : 'Một chút hôm nay, vững hơn ngày mai'}</h3><p>${d.total_attempts ? 'Lịch ôn đã sẵn sàng trong trang tiến bộ của bạn.' : 'Sau bài đầu tiên, lịch ôn sẽ xuất hiện ở đây.'}</p></div><button class="text-link" data-nav="dashboard">Xem lịch ôn →</button></div></section>
    <section><div class="section-line"><h2>Dấu chân học tập</h2><span class="badge">Của riêng bạn</span></div><div class="card insight-card"><div class="empty-graphic"><i></i><i></i><i></i><i></i></div><h3>${d.total_attempts ? `${d.total_attempts} lần thử đã được ghi nhận` : 'Tiến bộ bắt đầu từ sự tò mò'}</h3><p>${d.total_attempts ? `Bạn đã thử ${d.transfer_total} bài mới không có trợ giúp. Hãy quan sát cả cách nghĩ, không chỉ đáp án.` : 'Chưa có dữ liệu học tập. Hoàn thành hành trình đầu tiên để tìm điểm cần luyện và tạo lịch ôn riêng.'}</p><button class="text-link" data-nav="dashboard">Khám phá tiến bộ của tôi →</button><div class="small-note">Không xếp hạng. Không áp lực chuỗi ngày.</div></div></section></div>`;
}

function board(view, interactive=true) {
  const order = Array.from({length:90}, (_,i) => state.flipped ? 89-i : i);
  const targets = state.selected ? view.legal.filter(m=>m.startsWith(state.selected)).map(m=>m.slice(2)) : [];
  const last = state.game && state.page==='play' ? state.game.history.at(-1)?.move : null;
  return `<div class="board-card"><div class="player-row"><span class="player-mark ${state.flipped?'red':''}">${state.flipped?'帥':'將'}</span><span>${state.flipped?'Bên Đỏ':'Bên Đen'}</span><span class="turn-label">${view.turn==='b'?'Đen đi':'Đỏ đi'}</span></div><div class="board-wrap">${boardLines(state.flipped)}<div class="board-grid" role="group" aria-label="Bàn cờ tướng 9 cột 10 hàng">${order.map(i=>{const p=view.board[i],s=sq(i);return `<button class="square ${state.selected===s?'selected':''} ${targets.includes(s)?'target':''} ${last?.includes(s)?'last':''}" data-square="${s}" tabindex="${i===order[0]?0:-1}" ${interactive?'':'disabled'} aria-label="${s}${p!=='.'?` ${p===p.toUpperCase()?'Đỏ':'Đen'} ${NAMES[p.toLowerCase()]}`:' trống'}" aria-pressed="${state.selected===s}" title="${s}">${p!=='.'?`<span class="piece ${p===p.toUpperCase()?'red':''}">${pieceLabels==='vi'?`<span class="piece-name">${NAMES[p.toLowerCase()]}</span>`:PIECES[p]}</span>`:''}</button>`;}).join('')}</div></div><div class="player-row bottom"><span class="player-mark ${state.flipped?'':'red'}">${state.flipped?'將':'帥'}</span><span>${state.flipped?'Bên Đen':'Bên Đỏ'}</span><span class="turn-label">${state.selected ? `Đã chọn ${state.selected}` : interactive?'Chọn quân → chọn điểm đến':'Quan sát trước khi đi'}</span></div><div class="board-tools"><button class="subtle" data-action="flip">⇅ Lật bàn cờ</button><label class="piece-label-control">Chữ quân<select id="piece-labels"><option value="han" ${pieceLabels==='han'?'selected':''}>Chữ Hán</option><option value="vi" ${pieceLabels==='vi'?'selected':''}>Tiếng Việt</option></select></label><span class="small-note">${interactive?'Chấm xanh = nước hợp lệ':'Đáp án được giữ kín trước suy nghĩ'}</span></div><div class="board-caption">Tọa độ a0–i9 tính từ phía Đỏ. Ví dụ a0a1 = từ a0 đến a1. Bàn phím: phím mũi tên để di chuyển, Enter chọn, Esc hủy.</div></div>`;
}

function play() {
  const g=state.game;
  if (!g) return `${intro('Bắt đầu từ một ván cờ.','Chọn một cách chơi, rồi dành thời gian hiểu những nước mình đã đi.','CHƠI & NHÌN LẠI')}<div class="lesson-grid"><div class="card"><div class="lesson-number">01</div><h3>Chơi với máy cục bộ</h3><p>Bạn cầm Đỏ. Máy dùng tìm kiếm nông, thích hợp để thử tính năng; chưa phải đối thủ mạnh.</p><button class="primary" data-action="new-bot">Bắt đầu ván cờ →</button></div><div class="card"><div class="lesson-number">02</div><h3>Hai người cùng thiết bị</h3><p>Luân phiên Đỏ và Đen trên một bàn cờ. Phần học tập xem lại các nước của bên Đỏ.</p><button class="secondary" data-action="new-local">Chơi cùng nhau</button></div><div class="card"><div class="lesson-number">03</div><h3>Thử ván minh họa</h3><p>Một đoạn ván tổng hợp với cơ hội ăn quân bị bỏ lỡ. Trải nghiệm trọn vòng học trong khoảng một phút.</p><button class="secondary" data-action="demo">Tải ván minh họa</button></div><div class="card"><div class="lesson-number">04</div><h3>Nhập FEN & biên bản</h3><p>Dùng ký hiệu tọa độ a0a1, cách nhau bằng dấu cách. Mọi nước đều được kiểm tra luật.</p>${importForm()}</div></div>`;
  return `${intro(g.mode==='demo'?'Ván minh họa đã sẵn sàng.':'Mỗi nước đi đều có một ý tưởng.',g.status.over?'Ván đã dừng. Bây giờ, cùng tìm điều đáng học.':'Chỉ chơi cờ lúc này. Sau ván, chúng ta sẽ cùng nhìn lại.','CHƠI & NHÌN LẠI')}<div class="play-layout">${board(g,!g.status.over && (g.mode!=='bot'||g.turn==='w'))}<div class="panel-stack"><div class="card"><span class="badge">${g.mode==='demo'?'VÁN TỔNG HỢP MINH HỌA':g.mode==='bot'?'MÁY CỤC BỘ · BẠN CẦM ĐỎ':'BÀN CỜ CỤC BỘ'}</span><h2>${esc(g.status.reason)}</h2><p>${g.status.over?'Tìm một thời điểm quan trọng, ghi lại suy nghĩ của bạn rồi so sánh với kết quả tìm kiếm.':'Chọn quân và chọn điểm đến. Tướng không được để bị chiếu; dấu xanh chỉ những nước hợp lệ.'}</p><div class="actions" style="margin-top:18px"><button class="primary wide" data-action="review" ${g.history.length?'':'disabled'}>${g.status.over?'Bắt đầu xem lại →':'Kết thúc & học từ ván này →'}</button>${!g.status.over&&g.mode==='bot'&&g.turn==='b'?'<button class="secondary wide" data-action="bot">Máy đi</button>':''}<button class="subtle" data-action="choose-game">Chọn ván khác</button></div><div class="callout">Phân tích dùng công cụ cục bộ, tối đa 2 nửa nước. Chưa phải engine mạnh hay lời khuyên thi đấu.</div></div><div class="card"><div class="section-line"><h3>Biên bản ván cờ</h3><span class="small-note">${g.history.length} nửa nước</span></div><div class="moves">${g.history.map((h,i)=>`<div class="move-item"><b>${i+1}.</b>${esc(h.label)}</div>`).join('') || '<p class="small-note">Đỏ đi trước. Nước đầu tiên đang chờ bạn.</p>'}</div><details style="margin-top:15px"><summary class="small-note">FEN để lưu hoặc nhập lại</summary><pre>${esc(g.initial_fen)}</pre><pre>${g.history.map(h=>h.move).join(' ')}</pre></details></div></div></div>`;
}

function importForm() {
  return `<form id="import-form" class="inline-form"><label>FEN (bỏ trống để dùng thế xuất phát)<textarea name="fen" class="fen" placeholder="rheakaehr/9/… w"></textarea></label><label>Các nước đi<input type="text" name="moves" placeholder="b0c2 b9c7" maxlength="3000"></label><button class="secondary" type="submit">Nhập và xem lại</button></form>`;
}

function reflectionForm(e) {
  return `<span class="badge">01 · SUY NGHĨ TRƯỚC</span><h2>Bạn nhìn thấy điều gì?</h2><p>Chưa cần tìm ngay đáp án. Hãy nói cách bạn đánh giá thế cờ. “Chưa biết” cũng là một điểm bắt đầu.</p><div class="reflection-count"><span></span><span></span><span></span></div><p id="draft-status" class="draft-status" role="status" aria-live="polite"></p><button type="button" class="subtle" data-action="save-draft">Lưu nháp ngay</button><form id="reflect-form"><div class="form-field"><label for="evaluation">1. Bên nào có lợi thế? Vì sao?</label><textarea id="evaluation" name="evaluation" required maxlength="1500" placeholder="Hãy nhìn số quân, vị trí và an toàn của Tướng…"></textarea></div><div class="form-field"><label for="threat">2. Đối phương đang đe dọa điều gì?</label><textarea id="threat" name="threat" required maxlength="1500" placeholder="Một quân đang bị tấn công, đường chiếu, hoặc điều bạn chưa chắc…"></textarea></div><div class="form-field"><label for="plan">3. Bạn muốn đi nước nào? Dự kiến họ đáp ra sao?</label><textarea id="plan" name="plan" required maxlength="1500" placeholder="Nêu nước ứng viên và lý do chọn…"></textarea></div><div class="form-field"><label for="confidence">Bạn tự tin đến đâu?</label><select id="confidence" name="confidence"><option value="unsure">Tôi còn phân vân</option><option value="some">Tôi có một hướng suy nghĩ</option><option value="sure">Tôi khá tự tin</option></select></div><button class="primary wide" type="submit">${e.kind==='review'?'Lưu suy nghĩ & xem phân tích →':'Lưu suy nghĩ & thử nước đi →'}</button></form><p class="small-note" style="margin-top:12px">Chỉ lưu cục bộ. Không chấm điểm văn phong hay tự suy diễn tính cách.</p>`;
}

function explanation(e) {
  const x=e.explanation;
  return `<span class="badge">DỰA TRÊN LUẬT & TÌM KIẾM CỤC BỘ</span><h2>Điều đáng học ở đây</h2>${[['WHAT · Điều đã xảy ra',x.what],['WHY · Vì sao cần xem lại',x.why],['HOW · Cách nghĩ cho lần sau',x.how]].map(([h,p])=>`<div class="explain-block"><h3>${h}</h3><p>${esc(p)}</p></div>`).join('')}<div class="pv">Dòng hợp lệ: ${esc(x.pv.join(' → '))}</div><div class="small-note">${esc(x.caution)}</div><details style="margin-top:12px"><summary class="small-note">Nguồn và giới hạn phân tích</summary><p class="small-note">${esc(e.analysis.engine)} · Độ sâu ${e.analysis.depth} nửa nước · ${e.analysis.nodes} nút · template-v1. ${e.analysis.truncated?'Tìm kiếm chạm giới hạn thời gian.':''} Không dùng LLM; dữ liệu ${e.source==='synthetic-codex-v1'?'tổng hợp để minh họa, chưa được chủ dự án duyệt':'do bạn chơi hoặc nhập'}.</p></details>`;
}

function exercise() {
  const e=state.exercise;
  if (!e) return practicePage();
  const interactive = !!e.reflection && (e.kind==='practice'||state.retry) && !e.complete;
  let content;
  if (!e.reflection) content=reflectionForm(e);
  else if (e.complete) content=`<span class="badge success">ĐÃ HOÀN THÀNH</span><h2>Mang cách nghĩ này đi xa hơn.</h2><p>${esc(e.result.message)}</p><div class="callout success">Đã lưu lần thử · Ôn kỹ năng vào ${date(e.result.next_review_at)}.<br>Lịch ôn ưu tiên thế cờ chưa gặp cùng chủ đề.</div><div class="actions"><button class="primary wide" data-action="related">Luyện một thế cờ liên quan →</button><button class="secondary wide" data-nav="dashboard">Xem tiến bộ của tôi</button></div><details style="margin-top:20px"><summary class="small-note">Xem lại lời giải</summary>${explanation(e)}</details>`;
  else if (e.revealed) content=`${e.result?`<div class="callout error">${esc(e.result.message)}</div>`:''}${explanation(e)}<div class="actions" style="margin-top:19px">${state.retry?'<div class="callout wide">Chọn quân trên bàn cờ để thử lại. Mọi lần sửa sau lời giải đều là có trợ giúp.</div>':'<button class="primary wide" data-action="retry">Tôi đã hiểu · thử lại trên bàn cờ ↻</button>'}</div>`;
  else content=`<span class="badge">02 · ÁP DỤNG CÁCH NGHĨ</span><h2>Đến lượt bạn tìm nước đi.</h2><p>Đã lưu suy nghĩ. Hãy chọn quân trên bàn cờ rồi chọn điểm đến. Đáp án vẫn đang được giữ kín.</p><div class="callout">${e.unseen?'Thế cờ thuộc nhóm bạn chưa gặp. Lần thử đầu không gợi ý sẽ được ghi nhận riêng.':'Bạn đã gặp các nhóm thế cờ trong chủ đề này. Đây là lượt ôn, không tính là chuyển giao mới.'}</div><button class="subtle" data-action="hint">${e.hints?'Xem lời giải (có trợ giúp)':'Gợi ý cách nghĩ'}</button>${state.hint?`<div class="callout">${esc(state.hint)}</div>`:''}`;
  return `${intro(e.title,`${e.kind==='review'?'Nhìn lại ván cờ':'Luyện chuyển giao'} · ${e.skill_name}`,'HIỂU TRƯỚC · NHỚ LÂU HƠN')}<div class="learning-path">${['Tự suy nghĩ','Hiểu & thử lại','Thế cờ liên quan','Ghi nhớ & tiến bộ'].map((s,i)=>`<span class="${i===(e.complete?3:!e.reflection?0:e.kind==='practice'?2:1)?'active':''}">${i+1}. ${s}</span>`).join('')}</div>${state.moments.length>1&&e.kind==='review'?`<div class="moment-tabs">${state.moments.map(m=>`<button data-exercise="${m.id}" class="${m.id===e.id?'active':''}">${esc(m.title)}</button>`).join('')}</div>`:''}<div class="play-layout">${board(e,interactive)}<div class="panel-stack"><section class="card">${e.played?`<div class="small-note" style="margin-bottom:13px">Nước đã chơi: <code>${esc(e.played)}</code> · ${e.severity==='explore'?'Điểm để suy nghĩ, chưa phát hiện sai lầm rõ':'Điểm cần xem lại'}</div>`:''}${content}${e.reflection?`<details class="feedback"><summary>Suy nghĩ ban đầu của tôi</summary><p>${esc(e.reflection.evaluation)}</p><p>${esc(e.reflection.threat)}</p><p>${esc(e.reflection.plan)}</p></details><details class="feedback"><summary>Góp ý về thế cờ hoặc lời giải</summary><form id="feedback-form"><textarea name="message" required maxlength="2000" placeholder="Bạn thấy điều gì cần sửa?"></textarea><button class="subtle" type="submit">Lưu góp ý trên máy</button></form></details>`:''}</section></div></div>`;
}

function practicePage() {
  return `${intro('Luyện cách nghĩ, không học thuộc.','Chọn một kỹ năng. Hệ thống ưu tiên thế cờ bạn chưa gặp trong chủ đề đó.','LUYỆN TƯ DUY')}<div class="callout">12 thế cờ tổng hợp cho demo · Lời giải được kiểm tra luật và công cụ cục bộ, chưa phải bộ bài do chuyên gia thẩm định.</div><div class="lesson-grid">${Object.entries(state.boot.skills).map(([id,name],i)=>`<article class="card"><span class="lesson-number">0${i+1}</span><h3>${esc(name)}</h3><p>${esc(state.boot.lessons[id])}</p><button class="secondary" data-skill="${id}">Luyện chủ đề này →</button><div class="small-note" style="margin-top:10px">3 thế cờ · Cơ bản · Suy nghĩ trước lời giải</div></article>`).join('')}</div>`;
}

function dashboard() {
  const d=state.boot.dashboard;
  return `${continuePanel()}${intro('Nhìn lại để đi xa hơn.','Dữ liệu từ những lần bạn thực sự luyện tập. Chưa có dữ liệu thì chưa kết luận.','TIẾN BỘ CỦA TÔI')}<div class="metric-grid"><div class="card metric"><small>Lần thử đầu đã ghi nhận</small><b>${d.total_attempts}</b><small>Không cộng lại khi thử sửa đáp án</small></div><div class="card metric"><small>Bài mới đúng, không trợ giúp</small><b>${d.transfer_total?`${d.transfer_success}/${d.transfer_total}`:'—'}</b><small>${d.transfer_total?'Tín hiệu chuyển giao sơ bộ':'Cần một bài mới để bắt đầu đo'}</small></div><div class="card metric"><small>Kỹ năng đến lịch ôn</small><b>${d.due.length}</b><small>Tối đa 8 chủ đề trong hàng đợi</small></div></div><div class="dashboard-grid"><section class="card"><h2>Kỹ năng đang xây dựng</h2><p class="small-note" style="margin-top:10px">Điểm luyện tập theo quy tắc, không phải Elo hoặc chứng nhận thành thạo. Chất lượng lập luận chưa được tự động đánh giá.</p>${d.skills.length?d.skills.map(s=>`<div class="skill-item"><div class="skill-top"><strong>${esc(s.name)}</strong><span>${s.mastery_score}/100</span></div><div class="progress"><span style="width:${Number(s.mastery_score)}%"></span></div><div class="small-note">${s.evidence_count} bằng chứng · ${s.transfer_success_count} bài mới đúng · ${s.lapse_count} lần cần ôn sớm<br>Lịch tiếp theo: ${date(s.next_review_at)} (${s.stability} ngày)</div><button class="text-link" data-skill="${s.skill}">${d.due.some(x=>x.skill===s.skill)?'Đến lịch · ôn ngay':'Luyện thêm tự chọn'} →</button></div>`).join(''):'<div class="empty">Chưa đủ bằng chứng để nhận xét kỹ năng.<br>Hãy hoàn thành một lượt xem lại hoặc bài luyện.</div><button class="primary" data-action="demo">Bắt đầu hành trình đầu tiên →</button>'}</section><section class="card"><h2>Những lần bạn đã suy nghĩ</h2>${d.attempts.length?d.attempts.map(a=>`<div class="activity"><span class="badge ${a.correct?'success':''}">${a.correct?'Đúng':'Cần ôn'}</span><strong>${esc(state.boot.skills[a.skill])}</strong><small>${date(a.created_at)} · ${a.assisted?'Có trợ giúp':'Tự giải'} · ${a.kind==='review'?'Thử lại từ ván cờ':'Bài luyện'}</small><small>Nước ${esc(a.move)} · Ôn vào ${date(a.next_review_at)}</small></div>`).join(''):'<div class="empty">Nhật ký sẽ xuất hiện sau lần thử đầu tiên. Không có số liệu minh họa thay cho tiến bộ thật.</div>'}</section><section class="card"><h2>Điểm cần xem lại gần đây</h2>${d.reviews.length?d.reviews.map(r=>`<div class="activity"><button class="text-link" data-exercise="${r.id}">${esc(r.title)} →</button><small>${esc(state.boot.skills[r.skill])} · ${r.complete?'Đã thử lại đúng':'Đang học'}</small></div>`).join(''):'<p class="empty">Chưa xem lại ván nào.</p>'}</section><section class="card"><h2>Ván cờ đã lưu</h2>${d.games.length?d.games.slice().reverse().map(g=>`<div class="activity"><button class="text-link" data-game="${g.id}">${g.mode==='demo'?'Ván minh họa':g.mode==='bot'?'Ván với máy':g.mode==='import'?'Ván đã nhập':'Ván cùng thiết bị'} · ${g.moves} nửa nước →</button><small>${date(g.created_at)}</small></div>`).join(''):'<p class="empty">Ván mới sẽ tự lưu sau mỗi nước đi.</p>'}</section></div>`;
}

function lessons() {
  return `${intro('Sổ tay nhỏ, nền tảng chắc.','Kiểm tra luật, quan sát hai phía, rồi mới chọn nước đi.','SỔ TAY CỜ TƯỚNG')}<div class="lesson-grid">${Object.entries(state.boot.lessons).map(([id,body],i)=>`<article class="card"><span class="lesson-number">0${i+1}</span><h3>${esc(state.boot.skills[id])}</h3><p>${esc(body)}</p><button class="text-link" data-skill="${id}">Thử áp dụng →</button></article>`).join('')}<article class="card"><h3>Cách dùng bàn cờ</h3><p>Đỏ đi trước. Bấm quân rồi bấm điểm đến có dấu xanh. Các cột a–i từ trái sang phải phía Đỏ, các hàng 0–9 từ phía Đỏ lên phía Đen. a0a1 là nước từ a0 đến a1.</p><p>Sĩ đi chéo một bước trong cung. Tượng đi chéo hai bước, không qua sông, không nhảy qua quân cản mắt. Tốt đi thẳng một bước, qua sông mới được đi ngang, không đi lùi.</p></article><article class="card"><h3>Đọc kết quả một cách thận trọng</h3><p>Điểm cục bộ quy ước: Xe 900, Pháo 450, Mã 400, Sĩ/Tượng 200, Tốt 100; Tốt qua sông thêm 40. Không phải xác suất thắng. Hai nửa nước chỉ là một lượt đi và một lượt đáp.</p><p>Luật lặp thế trong demo chỉ dừng ở 3 lần; chưa áp dụng phán quyết chiếu dai/đuổi dai của giải đấu.</p></article></div>`;
}

function settings() {
  return `${intro('Dữ liệu thuộc về bạn.','Không tài khoản, không mật khẩu, không gửi suy nghĩ đến dịch vụ AI.','PHIÊN KHÁCH & MINH BẠCH')}<div class="settings"><section class="card"><h3>Phiên khách trên thiết bị này</h3><p>Cookie nhận diện trình duyệt, SQLite lưu ván cờ, câu trả lời, lần thử, lịch ôn và góp ý trên máy đang chạy server. Xóa cookie sẽ mất liên kết với phiên cũ. Đây chưa phải hệ thống tài khoản hoặc đồng bộ đa thiết bị.</p><button class="secondary" data-action="export">Tải bản sao dữ liệu JSON ↓</button></section><section class="card"><h3>Thành phần nào đang chạy?</h3><p>Luật cờ: mã kiểm tra tất định trên server.<br>Engine: chill-local-1.0, tìm kiếm tối đa 2 nửa nước, chưa tích hợp Pikafish.<br>Lời giải: mẫu tiếng Việt từ dữ kiện hợp lệ, không dùng LLM.<br>Gợi ý bài & lịch ôn: thuật toán theo quy tắc, không phải mô hình ML.<br>12 thế luyện: dữ liệu tổng hợp, chưa được chủ dự án duyệt.</p><p>Không thu email, tuổi hoặc thông tin liên lạc. Không tự động dùng dữ liệu của bạn để huấn luyện hoặc chia sẻ. Góp ý chỉ lưu trên máy và có trong bản xuất; chưa gửi cho ai.</p></section><section class="card danger-zone"><h3>Xóa dữ liệu của phiên này</h3><p>Xóa ván cờ, câu trả lời, lịch ôn, tiến bộ và góp ý. Không thể hoàn tác; hãy xuất bản sao trước nếu cần.</p><button class="danger" data-action="delete">Xóa toàn bộ dữ liệu của tôi</button></section></div>`;
}

function render() {
  const labels={home:'Góc học tập',play:'Chơi cờ',practice:'Luyện tư duy',exercise:'Hành trình học',dashboard:'Tiến bộ của tôi',lessons:'Sổ tay cờ tướng',settings:'Dữ liệu & quyền riêng tư'};
  $('#breadcrumb').textContent=labels[state.page];
  document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('active',b.dataset.nav===state.page));
  $('#main').innerHTML=({home,play,practice:practicePage,exercise,dashboard,lessons,settings}[state.page])();
  restoreDraft();
  const id = state.page==='exercise'?state.exercise?.id:state.page==='play'?state.game?.id:null;
  history.replaceState(null, '', '#'+state.page+(id?'/'+id:''));
}

async function navigate(page) {
  await saveAllDrafts();
  state.selected=null;
  if (page==='dashboard'||page==='home') state.boot.dashboard=await api('/api/dashboard');
  state.page=page;
  render();
  window.scrollTo({top:0,behavior:'instant'});
}

function openExercise(e) {
  void saveAllDrafts();
  state.exercise=e; state.page='exercise'; state.selected=null; state.hint=null; state.retry=false; render();
}

document.addEventListener('input', event => {
  if (event.target.closest('#reflect-form')) captureDraft($('#reflect-form'));
});
document.addEventListener('change', event => {
  if (event.target.id !== 'piece-labels') return;
  pieceLabels = event.target.value === 'vi' ? 'vi' : 'han';
  try { localStorage.setItem('chill-piece-labels', pieceLabels); } catch (_) { /* Still usable for this page. */ }
  render();
  $('#piece-labels')?.focus();
});
document.addEventListener('visibilitychange', () => { if (document.hidden) void saveAllDrafts(); });
window.addEventListener('beforeunload', event => {
  if ([...drafts.values()].some(d=>d.pending)) { event.preventDefault(); event.returnValue=''; }
});
document.addEventListener('keydown', event => {
  const cell = event.target.closest('[data-square]');
  if (!cell || cell.disabled || !$('#busy').hidden) return;
  const cells = [...document.querySelectorAll('[data-square]')];
  const current = cells.indexOf(cell), row=Math.floor(current/9), column=current%9;
  let next=current;
  if (event.key==='ArrowLeft') next=row*9+Math.max(0,column-1);
  else if (event.key==='ArrowRight') next=row*9+Math.min(8,column+1);
  else if (event.key==='ArrowUp') next=Math.max(0,row-1)*9+column;
  else if (event.key==='ArrowDown') next=Math.min(9,row+1)*9+column;
  else if (event.key==='Home') next=row*9;
  else if (event.key==='End') next=row*9+8;
  else if (event.key==='Escape') {
    state.selected=null;
    const focused=cell.dataset.square;
    const view=state.page==='play'?state.game:state.exercise;
    $('.board-card').outerHTML=board(view,true);
    const target=document.querySelector(`[data-square="${focused}"]`);
    document.querySelectorAll('[data-square]').forEach(c=>c.tabIndex=-1);
    target.tabIndex=0;target.focus();event.preventDefault();return;
  } else return;
  event.preventDefault();cell.tabIndex=-1;cells[next].tabIndex=0;cells[next].focus();
});

async function chooseSquare(square) {
  const view=state.page==='play'?state.game:state.exercise;
  const chosen = state.selected;
  if (chosen && view.legal.includes(chosen+square)) {
    await task(async()=>{
      if (state.page==='play') {
        state.game=await api('/api/move',{id:view.id,move:chosen+square});state.selected=null;render();
        if (state.game.mode==='bot' && !state.game.status.over && state.game.turn==='b') {
          $('#busy-label').textContent='Máy đang tìm nước hợp lệ…';
          state.game=await api('/api/bot',{id:view.id});render();
        }
      } else {
        state.exercise=await api('/api/attempt',{id:view.id,move:chosen+square});state.selected=null;state.retry=true;render();
      }
    },'Đang kiểm tra nước đi…');
    return;
  }
  if (view.legal.some(m=>m.startsWith(square))) state.selected = chosen===square?null:square;
  else {state.selected=null;if(chosen)toast('Điểm đến chưa hợp lệ. Chọn lại quân và một chấm xanh.');}
  // Replace only the board to preserve partially written reflection/feedback.
  const boardNode=$('.board-card');
  if (boardNode) {
    boardNode.outerHTML=board(view,true);
    document.querySelectorAll('[data-square]').forEach(c=>c.tabIndex=c.dataset.square===square?0:-1);
    document.querySelector(`[data-square="${square}"]`)?.focus();
  }
}

document.addEventListener('click',async event=>{
  const button=event.target.closest('button,a.brand');
  if (!button || button.disabled) return;
  if (button.dataset.action==='reconnect') return task(boot, 'Đang kết nối lại…');
  if (!state.boot || !$('#busy').hidden) return;
  if (button.matches('a.brand')) {event.preventDefault();return task(()=>navigate('home'));}
  if (button.dataset.square) return chooseSquare(button.dataset.square);
  if (button.dataset.nav) return task(()=>navigate(button.dataset.nav));
  if (button.dataset.skill) return task(async()=>openExercise(await api('/api/practice',{skill:button.dataset.skill})), 'Đang chuẩn bị thế cờ…');
  if (button.dataset.exercise) return task(async()=>openExercise(await api('/api/exercise?id='+button.dataset.exercise)));
  if (button.dataset.game) return task(async()=>{state.game=await api('/api/game?id='+button.dataset.game);await navigate('play');});
  const action=button.dataset.action;
  if (action==='save-draft') { await saveDraft(); return; }
  if (action==='flip') {state.flipped=!state.flipped; const view=state.page==='play'?state.game:state.exercise; const interactive=state.page==='play'?!view.status.over&&(view.mode!=='bot'||view.turn==='w'):!!view.reflection&&(view.kind==='practice'||state.retry)&&!view.complete;$('.board-card').outerHTML=board(view,interactive);return;}
  if (action==='retry') {state.retry=true;render();toast('Chọn quân và đi lại trên bàn cờ.');return;}
  if (action==='choose-game') {state.game=null;render();return;}
  await task(async()=>{
    if (action==='demo' || action==='new-bot' || action==='new-local') {
      state.game=await api('/api/game',{mode:action==='demo'?'demo':action==='new-bot'?'bot':'local'});
      state.moments=[];await navigate('play');
    } else if (action==='review') {
      const review=await api('/api/review',{id:state.game.id});state.game=await api('/api/game?id='+state.game.id);state.moments=review.moments;openExercise(review.moments[0]);
      toast(`Đã xem ${review.coverage} nước Đỏ gần nhất. Đáp án chỉ hiện sau suy nghĩ của bạn.`);
    } else if (action==='bot') {state.game=await api('/api/bot',{id:state.game.id});render();}
    else if (action==='hint') {const result=await api('/api/hint',{id:state.exercise.id});state.exercise=result;state.hint=result.hint;state.retry=true;render();}
    else if (action==='related') openExercise(await api('/api/practice',{from_id:state.exercise.id}));
    else if (action==='export') {
      const data=await api('/api/export');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='co-chill-du-lieu.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    } else if (action==='delete' && confirm('Xóa toàn bộ dữ liệu của phiên này? Hành động này không thể hoàn tác.')) {
      await api('/api/delete',{confirmation:'DELETE'});drafts.clear();clearTimeout(draftTimer);state.game=null;state.exercise=null;state.moments=[];await navigate('home');toast('Đã xóa dữ liệu của phiên này.');
    }
  }, action==='review'?'Đang tìm điểm đáng học… (tối đa 24 nước Đỏ gần nhất)':action==='related'?'Đang chọn thế cờ liên quan…':'Đang chuẩn bị…');
});

document.addEventListener('submit', event=>{
  event.preventDefault();
  const form=event.target, data=Object.fromEntries(new FormData(form));
  task(async()=>{
    if (form.id==='reflect-form') {clearTimeout(draftTimer);state.exercise=await api('/api/reflect',{id:state.exercise.id,...data});drafts.delete(state.exercise.id);render();}
    else if (form.id==='feedback-form') {await api('/api/feedback',{id:state.exercise.id,...data});form.reset();toast('Đã lưu góp ý cục bộ. Có thể tải cùng bản xuất dữ liệu.');}
    else if (form.id==='import-form') {
      if(!data.fen.trim())delete data.fen;
      state.game=await api('/api/game',{mode:'import',...data});await navigate('play');
    }
  });
});

task(boot,'Đang mở góc học tập…');

