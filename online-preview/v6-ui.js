/* V6 presentation layer. Rules, reflection gates and authentication stay in their owners. */
(function (root, factory) {
  'use strict';
  const api = factory(root);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CCV6UI = api;
  if (typeof document !== 'undefined' && typeof render === 'function') api.install();
})(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';
  const ENTRY_KEY = 'co-chill-entry-v6';
  const LANGUAGE_PREFIX = 'co-chill-interface-language-v6:';
  const dictionary = {
    'Trang chủ':'Home', 'Chơi':'Play', 'Chơi cờ':'Play chess', 'Bài học':'Lessons',
    'Ván của tôi':'My games', 'Ôn tập':'Review', 'Hành trình học':'Learning journey',
    'Tiến độ':'Progress', 'Cách học & luật':'How to learn & rules', 'Cài đặt':'Settings',
    'Về Cờ Chill':'About Cờ Chill', 'Của tôi':'My space', 'Góc của bạn':'Your space',
    'Tiến độ & hồ sơ':'Progress & profile', 'CHƠI · HIỂU · TIẾN BỘ':'PLAY · UNDERSTAND · IMPROVE',
    'Mỗi lần hiểu thêm một chút.':'Learn a little more each time.',
    'Đăng nhập / đăng ký':'Sign in / register', 'Quản trị':'Administration', 'Trợ giúp':'Help',
    'Cài đặt & dữ liệu':'Settings & data', 'Về bản thử':'About this preview',
    '♪ Âm thanh bật':'♪ Sound on', '♪ Âm thanh tắt':'♪ Sound off',
    '← Quay lại':'← Back', 'Bản thử nghiệm':'Preview', 'Đăng nhập':'Sign in',
    'Tạo tài khoản':'Create an account', 'Tài khoản Cờ Chill':'Cờ Chill account',
    'Giữ ván cờ và tiến độ khi đổi máy.':'Keep your games and progress across devices.',
    'Chào bạn trở lại':'Welcome back', 'Bắt đầu một hành trình':'Start your journey',
    'Tên đăng nhập':'Username', 'Mật khẩu':'Password', 'Tên hiển thị':'Display name',
    'Tên hiển thị (không cần tên thật)':'Display name (your real name is not required)',
    'Mã xác thực quản trị (nếu có)':'Administrator verification code (if applicable)',
    'Quên mật khẩu?':'Forgot your password?', 'Đăng nhập →':'Sign in →',
    'Chưa kết nối máy chủ tài khoản':'Account service is unavailable',
    'Thử kết nối lại':'Try again', 'Đăng xuất':'Sign out', 'Đồng bộ ngay':'Sync now',
    'Xuất dữ liệu tài khoản':'Export account data', 'Xuất dữ liệu cá nhân':'Export my data',
    'Xem / chuyển dữ liệu khách':'Review / transfer guest data',
    'Xóa tài khoản và dữ liệu':'Delete account and data', 'Xóa tài khoản của tôi':'Delete my account',
    'Nhập mật khẩu để xác nhận':'Enter your password to confirm',
    'Chọn cách hiển thị thoải mái cho bạn.':'Make this space comfortable for you.',
    'Giao diện và bàn cờ':'Appearance & board', 'Chủ đề':'Theme', 'Sáng ấm':'Warm light',
    'Trắng lạnh':'Cool light', 'Tối':'Dark', 'Tên quân':'Piece labels', 'Chữ Hán':'Chinese characters',
    'Tiếng Việt':'Vietnamese', 'Cỡ chữ':'Text size', 'Dễ đọc':'Standard', 'Lớn hơn':'Larger',
    'Mức tự chọn':'Preferred level', 'Chưa biết chơi':'New to Xiangqi', 'Mới biết luật':'Learning the rules',
    'Đã biết chơi':'Familiar with the game', 'Giọng hướng dẫn':'Coaching tone',
    'Trung tính':'Neutral', 'Bạn học cùng':'Study companion', 'Bật âm thanh nhẹ':'Enable gentle sounds',
    'Lưu tùy chọn':'Save preferences', 'Dữ liệu và quyền riêng tư':'Data & privacy',
    'Tài khoản, xuất và xóa dữ liệu':'Account, export & delete data',
    'Xóa lịch sử học và lịch ôn':'Delete learning history & review schedule',
    'Xóa toàn bộ dữ liệu':'Delete all data', 'Quay về hồ sơ →':'Back to profile →',
    'Giao diện và dữ liệu →':'Appearance & data →', 'Tài khoản & đồng bộ →':'Account & sync →',
    'Góc cá nhân':'Personal space', 'Lưu tên':'Save name', 'Tiến độ của bạn':'Your progress',
    'Ngôn ngữ giao diện':'Interface language', 'Nội dung bài học hiện bằng tiếng Việt.':'Lesson content is currently in Vietnamese.',
    'Màu ấm, nền kem và nét xanh lá.':'Cream tones with a fresh green accent.',
    'Sắc xanh trầm trên nền xám lạnh.':'Muted blue on a cool slate background.',
    'Nền tối dịu, quân cờ dễ phân biệt.':'A calm dark surface with distinct pieces.',
    'Chọn màu để xem ngay. Tùy chọn được lưu cùng hồ sơ hiện tại.':'Preview a theme instantly. Preferences are saved for the current profile.',
    'Chọn cách bắt đầu':'Choose how to begin', 'Chơi một ván, học từ nước đi của mình.':'Play a game. Learn from your own moves.',
    'Một không gian để chơi, suy nghĩ và tiến bộ.':'A space to play, reflect and improve.',
    'Tiếp tục với tài khoản':'Continue with an account', 'Đăng nhập hoặc tạo tài khoản':'Sign in or create an account',
    'Lưu tiến độ và tiếp tục trên thiết bị khác.':'Save your progress and continue on another device.',
    'Tiếp tục với tư cách khách':'Continue as a guest', 'Bắt đầu ngay trên thiết bị này.':'Start here on this device.',
    'Tiến độ khách được lưu trong trình duyệt này.':'Guest progress is saved in this browser.',
    'Bản xem trước chưa có dịch vụ tài khoản. Bạn có thể chơi và học với chế độ khách.':'Account services are not available in this preview. You can play and learn as a guest.',
    'Cách lưu dữ liệu':'How data is saved', 'Chơi · Suy nghĩ · Tiến bộ':'Play · Reflect · Improve',
    'Ván của bạn đang tiếp tục':'Your game is in progress', 'Bài học của bạn vẫn ở đây':'Your lesson is waiting',
    'Bắt đầu bằng một thế cờ nhỏ':'Start with a position', 'Tiếp tục ván →':'Continue game →',
    'Ôn hôm nay →':'Review today →', 'Tiếp tục →':'Continue →', 'Bắt đầu chơi →':'Start playing →',
    'Ôn một chút, rồi tiếp tục hành trình.':'Review a position, then continue your journey.',
    'Câu trả lời và bước đang làm đã được giữ lại.':'Your answers and current step have been saved.',
    'Khoảng 3–5 phút · Không cần tài khoản':'About 3–5 minutes · No account required',
    'Một ván với máy, hoặc cùng một người bạn trên thiết bị này.':'Play the computer or a friend on this device.',
    'Từ ý tưởng khai cuộc đến cách nhìn một thế cờ.':'From opening ideas to understanding a position.',
    'Trở lại những khoảnh khắc đáng học từ ván của bạn.':'Return to learning moments from your own games.',
    'Tiếp tục bài đang dở và luyện lại khi đến hẹn.':'Resume unfinished work and revisit it when due.',
    'Máy nhẹ · Hai người':'Basic bot · Two players', 'Theo nhịp của bạn':'At your own pace',
    'hình đã luyện':'positions practised', 'ván đã lưu':'games saved', 'lần tự nhìn lại':'session reflections',
    'Không có lời giải trước khi bạn suy nghĩ.':'Reflect before seeing the answer.',
    'Tìm hiểu cách học ↗':'Explore the learning flow ↗',
    'Học một ý tưởng, rồi đặt nó vào một thế cờ cụ thể.':'Learn an idea, then use it on the board.',
    'Khai cuộc':'Opening', 'Trung cuộc':'Middlegame', 'Tàn cuộc':'Endgame', 'Luyện':'Practise',
    'Xem hướng dẫn →':'View lesson →', 'Chọn bài':'Choose a lesson', 'Xem luật':'View rules',
    'Mở lịch ôn':'Open reviews', 'Cần học tiếp':'Continue learning', 'Đến hạn ôn':'Due for review',
    'Cơ bản':'Basic', 'Trung cấp':'Intermediate', 'Nâng cao':'Advanced',
    'Độ khó':'Difficulty', 'Chiến thuật':'Tactic', 'Tất cả':'All',
    'Gửi suy nghĩ & nước đi':'Submit reflection & move', 'Gửi câu trả lời':'Submit answers',
    'Tạm dừng':'Pause', 'Thử lại':'Retry', 'Xem lời giải':'View explanation',
    'Nước trước':'Previous move', 'Nước tiếp':'Next move', 'Lật bàn':'Flip board',
    'Đầu hàng':'Resign', 'Xin thua':'Resign', 'Cầu hòa':'Offer a draw', 'Xin hòa':'Offer a draw',
    'Đồng ý hòa':'Accept draw', 'Từ chối':'Decline', 'Tái đấu':'Rematch',
    'Chơi với máy':'Play the computer', 'Hai người một máy':'Two players on one device',
    'Trực tuyến':'Online', 'Tạo phòng':'Create room', 'Vào phòng':'Join room',
    'Mã phòng':'Room code', 'Phòng cộng đồng':'Community lobby', 'Ký phổ':'Moves',
    'Bắt đầu ván':'Start game', 'Thời gian':'Time control', 'Màu quân':'Your side',
    'Đỏ':'Red', 'Đen':'Black', 'Ngẫu nhiên':'Random', 'Không giới hạn':'Unlimited',
    'Gửi phản hồi':'Send feedback', 'Vấn đề bạn gặp':'What happened?',
    'Câu hỏi / lời giải':'Question / explanation', 'Luật hoặc nước đi':'Rules or moves',
    'Giao diện / thao tác':'Interface / interaction', 'Tài khoản / đồng bộ':'Account / sync',
    'Khác':'Other', 'Mô tả · điều xảy ra và điều bạn mong đợi':'Describe what happened and what you expected',
    'Đang kiểm tra kết nối':'Checking connection', 'Khách · lưu trên máy này':'Guest · saved on this device',
    'Chế độ khách · chưa có máy chủ tài khoản':'Guest mode · account service unavailable',
    'Đang tải tiến độ':'Loading progress', 'Đã đồng bộ':'Synced',
    'Có thay đổi chưa đồng bộ':'Changes waiting to sync', 'Đang đồng bộ…':'Syncing…',
    'Mất kết nối · nháp vẫn ở máy này':'Offline · draft kept on this device',
    'Có hai bản tiến độ · cần chọn bản giữ':'Progress conflict · choose which version to keep',
    'Phiên đăng nhập đã kết thúc':'Your sign-in session has ended',
    'Khách · lưu trên thiết bị':'Guest · saved on this device',
    'Đang mở Cờ Chill và kiểm tra phiên đăng nhập…':'Opening Cờ Chill and checking your session…',
    'Đến nội dung chính':'Skip to content', 'Bật / tắt âm thanh':'Toggle sound',
    'Hồ sơ và tiến độ cá nhân':'Profile and progress', 'Điều hướng chính':'Main navigation',
    'Điều hướng điện thoại':'Mobile navigation', 'Bốn khu vực chính':'Four main areas'
  };
  const icons = {
    play:'<path d="M7 3h10v4h-2v3l4 8v3H5v-3l4-8V7H7zM5 18h14M9 7h6"/>',
    lessons:'<path d="M12 5C8 2 4 3 3 4v16c3-1 6-1 9 1 3-2 6-2 9-1V4c-1-1-5-2-9 1zm0 0v16M6 8h3M15 8h3"/>',
    history:'<path d="M3 11a9 9 0 1 1 2 7M3 5v6h6M12 7v5l3 2"/>',
    review:'<path d="M8 3h8v3H8zM8 5H5v16h14V5h-3M8 12l2 2 5-5M8 18h8"/>',
    user:'<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
    guest:'<circle cx="12" cy="9" r="4"/><path d="M5 21v-2a7 7 0 0 1 14 0v2M4 3l2 2M20 3l-2 2"/>',
    pencil:'<path d="m4 16 11-11 4 4L8 20H4zM13 7l4 4M16 4l1-1a2 2 0 0 1 3 3l-1 1"/>',
    question:'<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5M12 17h.01"/>',
    language:'<path d="M3 5h11M8 3v2M5 5c0 5 3 8 7 10M12 5c0 5-3 8-7 10M13 21l4-11 4 11M15 17h4"/>',
    palette:'<circle cx="12" cy="12" r="9"/><circle cx="8" cy="8" r="1"/><circle cx="14" cy="6" r="1"/><circle cx="18" cy="11" r="1"/><path d="M6 14h4v5"/>'
  };
  let installed = false, language = 'vi', scope = 'guest', guestSelected = false;
  const memoryLanguages = new Map(), originalText = new WeakMap(), originalAttributes = new WeakMap();
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const languageKey = user => LANGUAGE_PREFIX + (user?.id ? 'account:'+encodeURIComponent(String(user.id)) : 'guest');
  const shouldShowEntry = ({booting=false,user=null,guest=false,page='home'}={}) => !booting && !user && !guest && !['account','privacy','help'].includes(page);
  function icon(name) { return `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">${icons[name] || icons.question}</svg>`; }
  function translate(text, lang = language) {
    if (lang !== 'en') return text;
    const raw = String(text), trimmed = raw.trim();
    let result = dictionary[trimmed];
    if (!result) {
      let m;
      if ((m=trimmed.match(/^(\d+) hình cờ đã đến lúc ôn$/))) result=`${m[1]} positions are ready for review`;
      else if ((m=trimmed.match(/^(\d+) hình đến hạn$/))) result=`${m[1]} positions due`;
      else if ((m=trimmed.match(/^(\d+) hình cờ · (\d+) kỹ năng$/))) result=`${m[1]} positions · ${m[2]} skills`;
      else if (trimmed.startsWith('Tài khoản · ')) result='Account · '+translate(trimmed.slice(12),lang);
    }
    return result ? raw.replace(trimmed,result) : raw;
  }
  function storageRead(key) { try { return root.localStorage?.getItem(key); } catch { return null; } }
  function storageWrite(key,value) { try { root.localStorage?.setItem(key,value); return true; } catch { return false; } }
  function currentUser() { return root.CCCloudUI?.sessionUser?.() || null; }
  function readLanguage() {
    const nextScope = languageKey(currentUser());
    const stored = memoryLanguages.get(nextScope) || storageRead(nextScope);
    scope = nextScope; language = stored === 'en' ? 'en' : 'vi';
    if (document.documentElement) document.documentElement.lang=language;
    return language;
  }
  function setLanguage(value) {
    if (!['vi','en'].includes(value)) return false;
    scope=languageKey(currentUser()); language=value; memoryLanguages.set(scope,value); storageWrite(scope,value);
    refresh(false); return true;
  }
  function textNodes(node) {
    if (!node || node.nodeType===1 && /^(INPUT|TEXTAREA|SCRIPT|STYLE|CODE|PRE)$/.test(node.tagName)) return;
    if (node.nodeType===3) {
      const previous=originalText.get(node), raw=node.nodeValue;
      const source=previous && raw===previous.displayed ? previous.source : raw;
      const displayed=translate(source);
      if (displayed!==raw) node.nodeValue=displayed;
      originalText.set(node,{source,displayed}); return;
    }
    for (const child of Array.from(node.childNodes || [])) textNodes(child);
  }
  function translateElement(node) {
    textNodes(node);
    if (!node?.getAttribute) return;
    const memory=originalAttributes.get(node)||{};
    for (const attribute of ['aria-label','title','placeholder']) {
      const raw=node.getAttribute(attribute); if (!raw) continue;
      const previous=memory[attribute], source=previous && raw===previous.displayed?previous.source:raw, displayed=translate(source);
      if(raw!==displayed)node.setAttribute(attribute,displayed);
      memory[attribute]={source,displayed};
    }
    originalAttributes.set(node,memory);
  }
  function languageControls() {
    return `<span class="v6-language-control" role="group" aria-label="Ngôn ngữ giao diện">${icon('language')}<button type="button" data-v6-action="language" data-value="vi" lang="vi" aria-pressed="${language==='vi'}" aria-label="Tiếng Việt">VI</button><button type="button" data-v6-action="language" data-value="en" lang="en" aria-pressed="${language==='en'}" aria-label="English">EN</button></span>`;
  }
  function cover() {
    return '<div class="v6-cover"><img src="cover-co-chill.png" width="1536" height="1024" alt="Cờ Chill · câu lạc bộ cờ tướng" fetchpriority="high"></div>';
  }
  function entryHTML(available) {
    return `<section class="v6-entry">${cover()}<div class="v6-entry-body"><div class="v6-entry-title"><p class="eyebrow">CỜ CHILL</p><h1>Chọn cách bắt đầu</h1><p>Một không gian để chơi, suy nghĩ và tiến bộ.</p></div><div class="v6-entry-options"><section class="v6-entry-option"><span class="v6-illustration">${icon('user')}</span><h2>Tiếp tục với tài khoản</h2><p>Lưu tiến độ và tiếp tục trên thiết bị khác.</p>${available?'<a href="#account" class="primary">Đăng nhập hoặc tạo tài khoản</a>':'<button class="primary" type="button" disabled>Đăng nhập hoặc tạo tài khoản</button>'}</section><section class="v6-entry-option"><span class="v6-illustration">${icon('guest')}</span><h2>Tiếp tục với tư cách khách</h2><p>Bắt đầu ngay trên thiết bị này.</p><button type="button" class="${available?'secondary':'primary'}" data-v6-action="guest">Tiếp tục với tư cách khách</button><small>Tiến độ khách được lưu trong trình duyệt này.</small></section></div>${!available?'<p class="v6-entry-notice" role="status">Bản xem trước chưa có dịch vụ tài khoản. Bạn có thể chơi và học với chế độ khách.</p>':''}<div class="v6-entry-footer"><a href="#privacy">Cách lưu dữ liệu</a><a href="#help">Trợ giúp</a><span class="v6-language-note" ${language==='en'?'':'hidden'}>Nội dung bài học hiện bằng tiếng Việt.</span></div></div></section>`;
  }
  function themePicker(selected) {
    const descriptions={warm:'Màu ấm, nền kem và nét xanh lá.',cool:'Sắc xanh trầm trên nền xám lạnh.',dark:'Nền tối dịu, quân cờ dễ phân biệt.'};
    const labels={warm:'Sáng ấm',cool:'Trắng lạnh',dark:'Tối'};
    return `<fieldset class="v6-theme-fieldset"><legend>Chủ đề</legend><div class="v6-theme-picker">${['warm','cool','dark'].map(theme=>`<label class="v6-theme-option"><input type="radio" name="theme" value="${theme}" ${selected===theme?'checked':''}><span class="v6-theme-preview ${theme}" aria-hidden="true"><span class="v6-preview-sidebar"></span><span class="v6-preview-card"></span><span class="v6-preview-button"></span></span><strong>${labels[theme]}</strong><small>${descriptions[theme]}</small></label>`).join('')}</div><p class="subtle">Chọn màu để xem ngay. Tùy chọn được lưu cùng hồ sơ hiện tại.</p></fieldset>`;
  }
  function decorateMain() {
    const main=document.getElementById('main');
    if (!main) return;
    const page=typeof route==='function'?route()[0]:'home';
    const gated=shouldShowEntry({booting:typeof booting!=='undefined'&&booting,user:currentUser(),guest:guestSelected,page});
    document.body?.classList?.toggle('v6-entry-active',gated);
    if (gated) {
      const available=!!root.CCCloudUI?.snapshot?.().client?.available;
      main.innerHTML=entryHTML(available);
      document.title=translate('Chọn cách bắt đầu')+' · Cờ Chill';
    }
    const selectors=[
      '.site-header','.sidebar','.mobile-nav','.account-strip','footer','.skip-link',
      '.v6-entry','.v6-home-copy','.home-card','.next-up','.home-bottom','.v6-language-panel','.v6-theme-fieldset',
      '#main .crumb','#main .page-top','#main button','#main .field > span','#main option',
      '#main .filters','#main .button-row a','#main .panel > h2','#main .panel > h3',
      '#main .v6-section-heading','#main .v6-interface-label'
    ];
    for(const element of document.querySelectorAll(selectors.join(',')))translateElement(element);
    for(const element of document.querySelectorAll('[data-v6-action="language"]'))element.setAttribute('aria-pressed',String(element.dataset.value===language));
    for(const note of document.querySelectorAll('.v6-language-note'))note.hidden=language!=='en';
    if (!gated) {
      const heading=document.querySelector('#main h1');
      if(heading)document.title=heading.textContent+' · Cờ Chill';
    }
  }
  function refresh(reload=true) {
    if (reload) readLanguage();
    else if (document.documentElement) document.documentElement.lang=language;
    decorateMain();
  }
  function install() {
    if (installed) return; installed=true;
    guestSelected=storageRead(ENTRY_KEY)==='guest'; readLanguage();
    const baseHome=home, baseSettings=settings, baseRender=render;
    home=function v6Home() {
      const old=baseHome();
      const rest=old.replace(/<section class="home-intro">[\s\S]*?<\/section>/,'');
      let cardIndex=0;
      const decorated=rest.replace(/<span class="tile-symbol">[\s\S]*?<\/span>/g,()=>`<span class="tile-symbol v6-card-icon">${icon(['play','lessons','history','review'][cardIndex++])}</span>`);
      return `<div class="v6-home">${cover()}<div class="v6-home-content"><section class="v6-home-copy"><p class="eyebrow">Chơi · Suy nghĩ · Tiến bộ</p><h1>Chơi một ván, học từ nước đi của mình.</h1></section>${decorated}</div></div>`;
    };
    settings=function v6Settings() {
      const old=baseSettings();
      const theme=typeof prefs!=='undefined'?prefs.theme:'warm';
      const updated=old.replace(/<label class="field"><span>Chủ đề<\/span><select name="theme"[\s\S]*?<\/select><\/label>/,themePicker(theme));
      return updated.replace('<div class="settings-grid grid-2">',`<section class="v6-language-panel panel"><div><h2>Ngôn ngữ giao diện</h2><p class="subtle">Nội dung bài học hiện bằng tiếng Việt.</p></div>${languageControls()}</section><div class="settings-grid grid-2">`);
    };
    render=function v6Render(){baseRender();refresh();};
    const header=document.querySelector('.header-actions');
    if(header&&!document.getElementById('v6-header-language')){
      const control=document.createElement('div');control.id='v6-header-language';control.innerHTML=languageControls();header.prepend(control);
    }
    document.addEventListener('click',event=>{
      const button=event.target.closest?.('[data-v6-action]'); if(!button)return;
      const action=button.dataset.v6Action;
      if(action==='language'){event.preventDefault();setLanguage(button.dataset.value);}
      if(action==='guest'){
        event.preventDefault(); if(typeof booting!=='undefined'&&booting)return;
        guestSelected=true;storageWrite(ENTRY_KEY,'guest');go('home');
      }
    });
    document.addEventListener('change',event=>{
      if(event.target.name!=='theme'||!event.target.closest?.('#settings-form'))return;
      const form=event.target.closest('form'),data=new FormData(form);
      prefs=CC.preferences({...Object.fromEntries(data.entries()),sound:data.has('sound'),sidebar:prefs.sidebar});
      save();render();
    });
    root.addEventListener?.('storage',event=>{
      if(event.key===languageKey(currentUser()))refresh();
      if(event.key===ENTRY_KEY){guestSelected=event.newValue==='guest';render();}
    });
    // Sync messages can change outside render. Observe only chrome, never inputs or lesson content.
    if(typeof MutationObserver!=='undefined'){
      const observer=new MutationObserver(()=>{
        for(const id of ['sync-status','storage-location','account-link']){
          const node=document.getElementById(id);if(node)translateElement(node);
        }
      });
      for(const id of ['sync-status','storage-location','account-link']){
        const node=document.getElementById(id);if(node)observer.observe(node,{childList:true,characterData:true,subtree:true});
      }
    }
    render();
  }
  return {install,refresh,setLanguage,language:()=>language,t:translate,icon,languageKey,shouldShowEntry,entryHTML,themePicker,ENTRY_KEY};
});
