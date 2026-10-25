/* V5 account/admin screens. The learning state remains in app.js; this adapter owns synchronization. */
'use strict';
window.CCCloudUI = (() => {
  const guestKey = 'co-chill-v4-browser';
  let status = 'checking', ready = false, timer, refreshTimer, loading = false;
  let adminData = null, adminError = '', contentData = null, editingContent=null, accountReturn = '#home';
  const client = new CoChillCloud.Client({notify: updateStatus});
  const labels = {checking:'Đang kiểm tra kết nối',guest:'Khách · lưu trên máy này',static:'Chế độ khách · chưa có máy chủ tài khoản',loading:'Đang tải tiến độ',saved:'Đã đồng bộ',pending:'Có thay đổi chưa đồng bộ',saving:'Đang đồng bộ…',offline:'Mất kết nối · nháp vẫn ở máy này',conflict:'Có hai bản tiến độ · cần chọn bản giữ',expired:'Phiên đăng nhập đã kết thúc'};
  function updateStatus(value) {
    status = value;
    const bar = $('sync-status');
    if (bar) { bar.textContent = labels[value] || value; bar.dataset.status = value; }
    if (client.session.authenticated && ready) {
      try { localStorage.setItem(KEY+'-sync', JSON.stringify({revision:client.revision,dirty:!!client.pending||!!client.conflict})); } catch {}
    }
    if (value === 'expired') {
      ready = false; booting=false; adminData=null; contentData=null; editingContent=null; adminError='';
      client.session = {authenticated:false};
      KEY = guestKey; state = CC.fresh(); selected = null;
      toast('Phiên đã kết thúc, có thể do đăng nhập trên máy khác. Đăng nhập lại để lấy tiến độ; nháp của bạn được giữ riêng trên máy này.');
      go('account');
    }
  }
  function saveState(value) {
    if (!ready || !client.session.authenticated) return;
    client.queue({...value,preferences:prefs});
    clearTimeout(timer); timer = setTimeout(() => client.flush(), 700);
  }
  function sessionUser() { return client.session.authenticated ? client.session.user : null; }
  function snapshot() { return {client,status,ready}; }
  function refreshChrome() {
    // Rendering must never repeat lifecycle transitions such as expiring a session.
    const bar=$('sync-status');if(bar){bar.textContent=labels[status]||status;bar.dataset.status=status;}
    const link = $('account-link'), admin = $('admin-link'), user = sessionUser();
    if (link) link.textContent = user ? 'Tài khoản · '+user.username : 'Đăng nhập / đăng ký';
    if (admin) admin.hidden = !user || !['owner','admin','reporter','report'].includes(user.role);
    const footer = $('storage-location'); if (footer) footer.textContent = user ? 'Tài khoản · '+(labels[status]||status) : 'Khách · lưu trên thiết bị';
  }
  async function activate() {
    ready = false; loading = true; booting=true; updateStatus('loading');render();
    const user = sessionUser(); if (!user) return;
    const epoch=client.epoch, uid=user.id, storageKey='co-chill-account-'+user.id;
    const stillCurrent=()=>client.epoch===epoch&&sessionUser()?.id===uid;
    let cached = null, metadata = null;
    try { cached = JSON.parse(localStorage.getItem(storageKey)||'null'); metadata = JSON.parse(localStorage.getItem(storageKey+'-sync')||'null'); } catch {}
    try {
      const remote = await client.readState();
      if(!stillCurrent())return;
      KEY=storageKey;
      if (cached && metadata?.dirty) {
        state = CC.sanitize(cached);
        prefs=CC.preferences(cached.preferences);
        if (metadata.revision === remote.revision) client.queue({...state,preferences:prefs});
        else { client.conflict = {message:'Bản nháp trên máy và bản máy chủ khác nhau.'}; client.pending = JSON.stringify({...state,preferences:prefs}); }
      } else {
        state = CC.sanitize(remote.state);
        prefs = CC.preferences(remote.state?.preferences);
      }
      state.profile.name = user.displayName || state.profile.name;
      ready = true; updateStatus(client.conflict?'conflict':client.pending?'pending':'saved');
      localStorage.setItem(storageKey,JSON.stringify({...state,preferences:prefs}));
      if (client.pending && !client.conflict) await client.flush();
    } catch (error) {
      if(!stillCurrent()||['stale_session','stale_read'].includes(error.data?.code))return;
      if(error.status===401||error.status===403){updateStatus('expired');return;}
      // Authenticated account only; a guest never receives another account's cached state.
      KEY=storageKey;state = cached ? CC.sanitize(cached) : CC.fresh();
      prefs=CC.preferences(cached?.preferences);
      ready = true; updateStatus('offline');
      toast('Chưa tải được tiến độ máy chủ. Đang giữ bản nháp trên máy; mở Tài khoản để thử lại.');
    } finally { if(stillCurrent()){loading = false; booting=false; selected = null; render();} }
  }
  async function init() {
    await client.probe();
    if (client.session.authenticated) await activate();
    else updateStatus(client.available?'guest':'static');
    if(client.available) await loadPublished();
    booting=false;
    render();
    const currentGame=activeGame();if(currentGame){tickGame(currentGame);maybeBot(currentGame);}
    refreshTimer = setInterval(async () => {
      if (!client.session.authenticated || document.hidden) return;
      try {
        const old = client.session.user.id, epoch=client.epoch, session = await client.request('/api/session');
        if(epoch!==client.epoch)return;
        if (!session.authenticated || session.user.id !== old) return client.expire();
        client.session = session;
        if (client.pending && !client.conflict) await client.flush();
        if(route()[0]==='admin'&&['admin','report'].includes(session.user.role))await loadAdmin();
      } catch { updateStatus('offline'); }
    }, 15000);
  }
  async function loadPublished(){
    try{
      const data=await client.request('/api/content');
      publishedPuzzles=(data.puzzles||[]).filter(p=>{try{const pos=XQ.Position.fromFen(p.fen),legal=pos.legalMoves();return typeof p.id==='string'&&legal.includes(p.solution)&&(p.alternatives||[]).every(m=>legal.includes(m));}catch{return false;}});
      publishedLoaded=true;
    }catch{/* Bundled synthetic lessons remain available without the optional backend. */}
  }
  function authFields() { return '<label class="field"><span>Tên đăng nhập</span><input name="username" autocomplete="username" required minlength="3" maxlength="30" pattern="[A-Za-z0-9_.-]+" placeholder="Ví dụ: co_thu_07"></label><label class="field"><span>Mật khẩu · ít nhất 10 ký tự</span><input name="password" type="password" autocomplete="current-password" required minlength="10" maxlength="128"></label>'; }
  function account() {
    const user = sessionUser();
    if (!user) return `${heading('Tài khoản Cờ Chill','Giữ ván cờ và tiến độ khi đổi máy.')}<p class="notice">${esc(labels[status]||'')} · Bạn vẫn có thể <a href="#home">học với chế độ khách</a>.</p>${!client.available?'<section class="panel"><h2>Chưa kết nối máy chủ tài khoản</h2><p>Bản web tĩnh vẫn chơi và học trên máy này. Tài khoản cần chạy cùng API Cờ Chill. Nếu bạn đã mở đúng máy chủ, hãy thử kết nối lại.</p>'+btn('Thử kết nối lại','cloud-reconnect','','secondary')+'</section>':`<div class="grid-2"><section class="panel"><h2>Chào bạn trở lại</h2><form data-cloud-form="login">${authFields()}<label class="field"><span>Mã xác thực quản trị (nếu có)</span><input name="totpCode" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" placeholder="6 chữ số"></label><button class="primary" type="submit">Đăng nhập →</button><p class="form-error" role="alert"></p></form><details><summary>Quên mật khẩu?</summary><p>Bản này chưa có email khôi phục. Liên hệ chủ website để xác minh quyền sở hữu; không tạo tài khoản mới với kỳ vọng tự nhận lại dữ liệu cũ.</p></details></section><section class="panel"><h2>Bắt đầu một hành trình</h2><form data-cloud-form="register">${authFields().replace('current-password','new-password')}<label class="field"><span>Tên hiển thị (không cần tên thật)</span><input name="displayName" autocomplete="nickname" maxlength="40" required></label><label class="check-line"><input type="checkbox" required><span>Tôi đã đọc <a href="#privacy">cách lưu và xóa dữ liệu</a>. Một tài khoản chỉ có một phiên đăng nhập đang hoạt động.</span></label><button class="primary" type="submit">Tạo tài khoản</button><p class="form-error" role="alert"></p></form><p class="subtle">Chưa dùng email hoặc tài khoản mạng xã hội. Không yêu cầu ngày sinh hay số điện thoại.</p></section></div>`}`;
    return `${heading('Tài khoản của bạn','Một tài khoản, tiến độ tiếp tục trên máy bạn đang dùng.')}<div class="next-up"><div><strong>${esc(user.displayName||user.username)}</strong><p>@${esc(user.username)} · ${esc(labels[status])}</p></div>${btn('Đồng bộ ngay','cloud-sync','','secondary')}</div>${client.conflict?`<section class="panel"><h2>Chọn bản tiến độ để tiếp tục</h2><p>Bản nháp trên máy và máy chủ đều được giữ cho đến khi bạn chọn. Hãy xuất nháp trước nếu cần đối chiếu.</p><div class="button-row">${btn('Xuất bản nháp','cloud-export-draft','','secondary')}${btn('Dùng bản máy chủ','cloud-use-server','','secondary')}${btn('Giữ bản nháp máy này','cloud-use-draft','','secondary')}</div></section>`:''}<div class="grid-2 separation"><section class="panel"><h2>Thông tin và mật khẩu</h2><form data-cloud-form="account"><label class="field"><span>Tên hiển thị</span><input name="displayName" maxlength="40" value="${esc(user.displayName)}" required></label><label class="field"><span>Tên đăng nhập</span><input name="username" value="${esc(user.username)}" minlength="3" maxlength="30" required pattern="[A-Za-z0-9_.-]+"></label><label class="field"><span>Mật khẩu hiện tại (khi đổi thông tin đăng nhập)</span><input name="currentPassword" type="password" autocomplete="current-password"></label><label class="field"><span>Mật khẩu mới (để trống nếu giữ)</span><input name="newPassword" type="password" autocomplete="new-password" minlength="10" maxlength="128"></label><button class="primary">Lưu thay đổi</button><p class="form-error" role="alert"></p></form></section><section class="panel"><h2>Dữ liệu thuộc về bạn</h2><p>Tài khoản không tự nhận dữ liệu của khách trên máy dùng chung.</p><div class="button-row">${btn('Xem / chuyển dữ liệu khách','cloud-import-guest','','secondary')}${btn('Xuất dữ liệu tài khoản','cloud-export','','secondary')}${btn('Đăng xuất','cloud-logout','','secondary')}</div><p class="subtle">Đăng xuất xóa bản nháp tài khoản khỏi trình duyệt này. Hãy đồng bộ hoặc xuất trước khi đăng xuất.</p><details class="separation"><summary>Xóa tài khoản và dữ liệu</summary><p>Xóa thật tiến độ trên máy chủ và bản nháp tài khoản trên máy này. Không giữ bản ẩn để huấn luyện. Không thể hoàn tác.</p><form data-cloud-form="delete"><label class="field"><span>Nhập mật khẩu để xác nhận</span><input name="password" type="password" autocomplete="current-password" required></label><button class="danger">Xóa tài khoản của tôi</button><p class="form-error" role="alert"></p></form></details><a class="quiet" href="#privacy">Đọc chính sách dữ liệu</a></section></div>`;
  }
  function help() { return `${heading('Trợ giúp','Bạn có thể quay lại bài đang làm bất cứ lúc nào.')}<div class="grid-2"><section class="panel"><h2>Cần bắt đầu từ đâu?</h2><div class="button-row"><a class="secondary" href="#howto">Cách học</a><a class="secondary" href="#rules">Luật đi quân</a><a class="secondary" href="#account">Tài khoản & đồng bộ</a><a class="secondary" href="#about">Khả năng và giới hạn</a></div>${state.session?btn('Tiếp tục bài đang làm','resume','','primary'):''}</section><section class="panel"><h2>Gửi phản hồi</h2>${feedbackForm()}</section></div>`; }
  function feedbackForm(context) { return `<form data-cloud-form="feedback"><label class="field"><span>Vấn đề bạn gặp</span><select name="category"><option value="content">Câu hỏi / lời giải</option><option value="rules">Luật hoặc nước đi</option><option value="interface">Giao diện / thao tác</option><option value="account">Tài khoản / đồng bộ</option><option value="other">Khác</option></select></label><label class="field"><span>Mô tả · điều xảy ra và điều bạn mong đợi</span><textarea name="message" rows="3" maxlength="3000" required></textarea></label><input type="hidden" name="context" value="${esc(context||location.hash)}"><p class="subtle">Chỉ gửi mô tả và mã trang/bài; không tự đính kèm câu trả lời riêng, mật khẩu hay toàn bộ ván.</p><button class="secondary" ${!sessionUser()?'disabled':''}>Gửi phản hồi</button>${!sessionUser()?'<p><a href="#account">Đăng nhập để gửi phản hồi cho quản trị.</a></p>':''}<p class="form-error" role="alert"></p></form>`; }
  function privacy() { return `${heading('Dữ liệu và quyền riêng tư','Chính sách của bản thử V5 · 23/10/2026')}<article class="article"><h2>Khi chơi với chế độ khách</h2><p>Ván, suy nghĩ, tiến độ và tùy chọn được lưu trong trình duyệt. Không có bản khách bí mật trên máy chủ. Xóa dữ liệu trình duyệt có thể làm mất phần này.</p><h2>Khi tạo tài khoản</h2><p>Máy chủ lưu tên đăng nhập, tên hiển thị, mật khẩu đã băm, phiên đăng nhập, tiến độ bạn đồng bộ và phản hồi bạn chủ động gửi. Không yêu cầu tên thật, số điện thoại hay ngày sinh. Mỗi lần đăng nhập mới kết thúc phiên cũ.</p><h2>Ai được xem?</h2><p>Chủ website và vai trò đọc báo cáo xem danh sách tài khoản, thống kê hoạt động và biên bản ván phục vụ vận hành. Màn quản trị không cung cấp nội dung câu trả lời riêng hay mật khẩu. Số liệu là hoạt động được thiết bị gửi lên, chưa phải Elo hoặc hiệu quả học tập đã kiểm định.</p><h2>Quyền lựa chọn</h2><p>Bạn có thể xuất dữ liệu, xóa lịch sử hoặc xóa tài khoản. Xóa tài khoản xóa dữ liệu hoạt động trên máy chủ; nhật ký bảo mật tối thiểu và bản sao lưu do người vận hành quản lý được mô tả trong tài liệu triển khai. Dữ liệu không được dùng để huấn luyện AI hoặc gửi đến nhà cung cấp LLM. Chưa tự động xóa tài khoản không hoạt động sau một năm.</p><h2>Độ bền dữ liệu</h2><p>Chỉ báo “Đã đồng bộ” sau xác nhận của máy chủ. Nếu mất mạng, bản nháp ở lại máy này. Chủ website cần dùng lưu trữ bền vững và sao lưu khi mở công khai. Website chưa có email, quảng cáo, thanh toán hoặc thông báo đẩy.</p><a class="primary" href="#account">Mở tài khoản và dữ liệu →</a></article>`; }
  async function loadAdmin() {
    const epoch=client.epoch,uid=sessionUser()?.id;
    adminError = ''; adminData = null; render();
    try {
      const [stats,users,feedback] = await Promise.all([client.request('/api/admin/stats'),client.request('/api/admin/users'),sessionUser()?.role==='admin'?client.request('/api/admin/feedback'):Promise.resolve({feedback:[]})]);
      if(epoch!==client.epoch||uid!==sessionUser()?.id)return;
      adminData = {stats,users:users.users,feedback:feedback.feedback||feedback.items||[]};
    } catch(e) { if(epoch===client.epoch&&uid===sessionUser()?.id)adminError = e.message; }
    if (epoch===client.epoch&&uid===sessionUser()?.id&&route()[0]==='admin') render();
  }
  function admin() {
    const user = sessionUser();
    if (!user || !['owner','admin','reporter','report'].includes(user.role)) return heading('Quản trị')+empty('Bạn chưa có quyền quản trị','Quyền được cấp bởi chủ website ở máy chủ.','account','Mở tài khoản');
    if (!adminData) return heading('Quản trị Cờ Chill','Số liệu lấy từ máy chủ · giờ Việt Nam')+`<section class="panel"><p>${esc(adminError||'Bấm làm mới để lấy số liệu hiện tại.')}</p>${btn('Làm mới dữ liệu','admin-refresh','','secondary')}</section>`;
    const {stats,users,feedback} = adminData, totals=stats.totals||{};
    return `${heading('Quản trị Cờ Chill','Thống kê ghi nhận từ tài khoản đã đồng bộ · UTC+7')}<div class="button-row">${btn('Làm mới dữ liệu','admin-refresh','','secondary')}<a class="secondary" href="#editor">Biên tập bài học</a></div><div class="stat-grid">${[[stats.accounts,'tài khoản'],[stats.newAccounts,'tài khoản mới trong kỳ'],[stats.activeAccounts,'tài khoản hoạt động'],[totals.games||0,'ván đã đồng bộ'],[totals.learningAttempts||0,'lượt học'],[totals.reviews||0,'lượt ôn']].map(([n,t])=>`<div class="stat"><b>${Number(n)||0}</b><span>${t}</span></div>`).join('')}</div><p class="notice">${esc(stats.notice||'Số liệu do thiết bị đồng bộ, chưa được xác minh độc lập.')} Không dùng tài khoản thử để tuyên bố tác động sản phẩm.</p><section class="panel"><h2>Tài khoản</h2><div class="table-scroll"><table><thead><tr><th>Tài khoản</th><th>Đăng ký</th><th>Hoạt động</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>${users.map(u=>`<tr><td><b>${esc(u.displayName||u.username)}</b><br><small>@${esc(u.username)} · ${esc(u.role)}</small></td><td>${date(u.createdAt)}</td><td>${Number(u.metrics?.games)||0} ván · ${Number(u.metrics?.learningAttempts)||0} lượt học</td><td>${u.locked?'Tạm khóa':'Hoạt động'}${u.testAccount?' · test':''}</td><td>${btn('Chi tiết','admin-user',String(u.id),'quiet')}${user.role==='admin'&&u.id!==user.id?btn(u.locked?'Mở khóa':'Khóa có hạn','admin-lock',String(u.id),'quiet'):''}</td></tr>`).join('')}</tbody></table></div><div id="admin-user-detail"></div></section><section class="panel separation"><h2>Phản hồi</h2>${feedback.length?feedback.map(f=>`<article class="explanation-section"><p><b>${esc(f.category)} · ${esc(f.status)}</b> · ${date(f.createdAt)}</p><p>${esc(f.message)}</p><small>${esc(typeof f.context==='string'?f.context:JSON.stringify(f.context||{}))}</small>${user.role==='admin'?`<div class="button-row">${btn('Đang xem xét','feedback-review',String(f.id),'quiet')}${btn('Đã xử lý','feedback-resolve',String(f.id),'quiet')}</div>`:''}</article>`).join(''):'<p>Chưa có phản hồi.</p>'}</section>`;
  }
  function editor() {
    if (sessionUser()?.role!=='admin') return heading('Biên tập')+empty('Chỉ chủ website được biên tập','Đăng nhập tài khoản quản trị.','account');
    return `${heading('Biên tập bài học','Kiểm tra luật trước; duyệt nội dung và nguồn trước khi xuất bản.','admin')}<p class="notice">Nước hợp lệ chưa đủ chứng minh lời giải tối ưu. Lưu nháp, kiểm tra với engine và tự duyệt trước khi xuất bản.</p><div class="grid-2"><section class="panel"><h2>${editingContent?'Sửa bản nháp':'Thế cờ mới'}</h2><form data-cloud-form="content"><label class="field"><span>Tiêu đề</span><input name="title" required maxlength="120"></label><label class="field"><span>FEN · đầy đủ hai Tướng và bên đi</span><textarea name="fen" required rows="3"></textarea></label><label class="field"><span>Nước mẫu (tọa độ a0a1)</span><input name="solution" required pattern="[a-i][0-9][a-i][0-9]"></label><label class="field"><span>Các nước khác chấp nhận (cách nhau bằng dấu phẩy)</span><input name="alternatives"></label><label class="field"><span>Kỹ năng</span><select name="skill">${Object.entries(SKILLS).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></label>${[['what','Nhận định thế cờ'],['why','Lý do và căn cứ'],['how','Cách suy nghĩ lần sau'],['source','Nguồn và quyền sử dụng']].map(([k,l])=>`<label class="field"><span>${l}</span><textarea name="${k}" required rows="2" maxlength="3000"></textarea></label>`).join('')}<button class="primary">Lưu bản nháp đã kiểm tra luật</button><p class="form-error" role="alert"></p></form></section><section class="panel"><h2>Nội dung đang quản lý</h2>${btn('Tải danh sách','content-list','','secondary')}<div id="content-list">${contentData?contentData.map(p=>`<article class="explanation-section"><b>${esc(p.title)}</b><p>${esc(p.status)} · phiên bản ${p.version}</p><div class="button-row">${btn('Xem / sửa','content-edit',p.id,'secondary')}${btn('Duyệt & xuất bản','content-publish',p.id,'secondary')}${btn('Tạm gỡ để kiểm tra','content-withdraw',p.id,'quiet')}</div></article>`).join(''):'<p>Chưa tải nội dung.</p>'}</div></section></div>`;
  }
  async function signOut(deleted = false) {
    const oldKey = KEY;
    if (!deleted) await client.logout();
    else {client.epoch++;client.session={authenticated:false};client.pending=null;client.conflict=null;}
    clearTimeout(timer); ready=false; adminData=null; contentData=null; adminError='';
    localStorage.removeItem(oldKey); localStorage.removeItem(oldKey+'-sync');
    KEY=guestKey; state=CC.sanitize(JSON.parse(localStorage.getItem(guestKey)||'null')); selected=null;
    updateStatus('guest'); go('account');
  }
  document.addEventListener('submit', async event => {
    const form=event.target, kind=form.dataset.cloudForm; if(!kind)return;
    event.preventDefault();const error=form.querySelector('.form-error'), submit=form.querySelector('[type=submit],button');
    const data=Object.fromEntries(new FormData(form));error.textContent='';if(submit)submit.disabled=true;
    try {
      if (kind==='login'||kind==='register') { ready=false;adminData=null;contentData=null;await client.authenticate(kind,data);await activate();if(client.session.authenticated){go(accountReturn.replace(/^#/,''));toast('Đã đăng nhập. Tiến độ được lưu riêng theo tài khoản.');} }
      if (kind==='account') { if(!data.newPassword)delete data.newPassword;if(!data.currentPassword)delete data.currentPassword;const result=await client.request('/api/account',{method:'PATCH',body:data});if(result.csrf)client.session=result;else client.session.user=result.user;state.profile.name=result.user.displayName;save();render();toast('Đã cập nhật tài khoản.'); }
      if (kind==='delete') {if(!confirm('Xóa vĩnh viễn tài khoản và tiến độ trên máy chủ?'))return;await client.request('/api/account',{method:'DELETE',body:{password:data.password}});await signOut(true);toast('Đã xóa tài khoản và dữ liệu.');}
      if (kind==='feedback') { await client.request('/api/feedback',{method:'POST',body:{category:data.category,message:data.message,context:{route:data.context,puzzleId:state.session?.puzzleId||null}}});form.reset();toast('Đã gửi phản hồi cho quản trị. Câu trả lời học tập không bị đính kèm.'); }
      if (kind==='content') {data.alternatives=data.alternatives.split(/[\s,]+/).filter(Boolean);data.status='draft';if(editingContent)data.version=editingContent.version;await client.request('/api/admin/content'+(editingContent?'/'+encodeURIComponent(editingContent.id):''),{method:editingContent?'PATCH':'POST',body:data});editingContent=null;const result=await client.request('/api/admin/content');contentData=result.content||[];await loadPublished();render();toast('Đã lưu nháp. Chưa xuất bản cho người học.');}
    } catch(e) {error.textContent=e.message||'Chưa thực hiện được. Hãy thử lại.';} finally {if(submit)submit.disabled=false;}
  });
  document.addEventListener('click', async event => {
    const target=event.target.closest('[data-action]');if(!target)return;
    const action=target.dataset.action, value=target.dataset.value;
    if(!/^(cloud-|admin-|feedback-|content-)/.test(action))return;
    target.disabled=true;
    try {
      if(action==='cloud-reconnect'){await client.probe();if(client.session.authenticated)await activate();else updateStatus(client.available?'guest':'static');render();}
      if(action==='cloud-sync'){if(client.conflict)go('account');else if(!client.stateReady){await activate();}else {await client.flush();render();}}
      if(action==='cloud-export-draft')download('co-chill-nhap-ca-nhan.json',JSON.stringify(CC.safeExport(state),null,2));
      if(action==='cloud-use-server'){
        if(!confirm('Thay bản nháp trên máy bằng bản máy chủ? Hãy xuất nháp trước nếu cần.'))return;
        const epoch=client.epoch,storageKey=KEY,remote=await client.useServer();
        if(epoch!==client.epoch||storageKey!==KEY)return;
        state=CC.sanitize(remote);prefs=CC.preferences(remote?.preferences);
        localStorage.setItem(storageKey,JSON.stringify({...state,preferences:prefs}));render();
      }
      if(action==='cloud-use-draft'){if(!confirm('Ghi bản nháp máy này lên máy chủ, thay phiên bản hiện tại?'))return;await client.useDraft({...state,preferences:prefs});render();}
      if(action==='cloud-logout'){if(client.pending&&!await client.flush()&&!confirm('Chưa đồng bộ được. Đăng xuất sẽ xóa nháp tài khoản trên máy này. Bạn đã xuất bản sao và vẫn muốn tiếp tục?'))return;await signOut();}
      if(action==='cloud-export'){const data=await client.request('/api/export');download('co-chill-tai-khoan.json',JSON.stringify(data,null,2));}
      if(action==='cloud-import-guest'){
        const guest=CC.sanitize(JSON.parse(localStorage.getItem(guestKey)||'null'));
        if(!guest.games.length&&!Object.keys(guest.records).length&&!guest.session)return toast('Không có dữ liệu khách để chuyển.');
        if(state.games.length||Object.keys(state.records).length||state.session)return toast('Tài khoản đã có tiến độ. Hãy xuất hai bản để đối chiếu; chưa tự hợp nhất vì có thể trùng hoặc khác chủ.');
        if(!confirm(`Dữ liệu khách trên máy này có ${guest.games.length} ván và ${Object.keys(guest.records).length} hình. Xác nhận đây là dữ liệu của bạn và chuyển vào tài khoản?`))return;
        state=guest;state.profile.name=sessionUser().displayName;save();await client.flush();render();
      }
      if(action==='admin-refresh')await loadAdmin();
      if(action==='admin-user'){const d=await client.request('/api/admin/users/'+encodeURIComponent(value));$('admin-user-detail').innerHTML=`<h3>${esc(d.user.username)}</h3><pre>${esc(JSON.stringify(d.metrics,null,2))}</pre><p>Không hiển thị câu trả lời tự do riêng tư.</p>${(d.games||[]).slice(0,20).map(g=>`<details><summary>${esc(g.title||g.id)}</summary><pre>${esc(JSON.stringify(g,null,2))}</pre></details>`).join('')}`;}
      if(action==='admin-lock'){const user=adminData.users.find(u=>String(u.id)===value);const reason=user.locked?'Mở khóa theo duyệt của chủ website':prompt('Lý do tạm khóa 24 giờ (người chơi sẽ được thông báo):');if(!reason)return;if(!confirm(`${user.locked?'Mở khóa':'Tạm khóa 24 giờ'} @${user.username}?`))return;await client.request('/api/admin/users/'+encodeURIComponent(value)+'/lock',{method:'POST',body:{locked:!user.locked,reason,until:new Date(Date.now()+86400000).toISOString()}});await loadAdmin();}
      if(action==='feedback-review'||action==='feedback-resolve'){await client.request('/api/admin/feedback/'+encodeURIComponent(value),{method:'PATCH',body:{status:action==='feedback-review'?'reviewing':'resolved'}});await loadAdmin();}
      if(action==='content-edit'){editingContent=contentData?.find(p=>p.id===value)||null;render();const form=document.querySelector('[data-cloud-form=content]');if(editingContent&&form){for(const key of ['title','fen','solution','skill','what','why','how','source'])form.elements[key].value=editingContent[key]||'';form.elements.alternatives.value=(editingContent.alternatives||[]).join(', ');form.scrollIntoView({block:'start'});}}
      if(action==='content-list'){const epoch=client.epoch,d=await client.request('/api/admin/content');if(epoch!==client.epoch)return;contentData=d.content||[];render();}
      if(action==='content-publish'||action==='content-withdraw'){if(!confirm(action==='content-publish'?'Bạn đã duyệt nhận định, nước mẫu và quyền dùng nguồn? Xuất bản cho người học?':'Tạm gỡ bài này khỏi danh sách luyện?'))return;const current=contentData?.find(p=>p.id===value);if(!current)throw new Error('Tải lại nội dung trước khi thay đổi.');const epoch=client.epoch;await client.request('/api/admin/content/'+encodeURIComponent(value),{method:'PATCH',body:{status:action==='content-publish'?'published':'withdrawn',version:current.version}});const d=await client.request('/api/admin/content');if(epoch!==client.epoch)return;contentData=d.content||[];await loadPublished();render();}
    } catch(e) {toast(e.message);} finally {target.disabled=false;}
  });
  document.addEventListener('click',e=>{const a=e.target.closest('a[href="#account"]');if(a&&route()[0]!=='account')accountReturn=location.hash||'#home';});
  window.addEventListener('online',()=>{if(client.session.authenticated)client.flush();});
  window.addEventListener('hashchange',()=>{if(route()[0]==='admin'&&['admin','report'].includes(sessionUser()?.role))loadAdmin();});
  return {init,save:saveState,refreshChrome,snapshot,sessionUser,account,admin,editor,help,privacy,feedbackForm,loadAdmin};
})();
CCCloudUI.init();
