/* Public profile (#u/<publicId>) and the account controls for it.
 * Owner decisions 19/11/2026: a random public id (never the username), only
 * server-recorded online games, opponents shown according to their own setting,
 * new accounts public by default, older accounts asked once until they choose.
 * Loaded last so it can add to pages rendered by the other layers.
 * Browser: CCPublic. Node: require('./public-profile.js') for the pure helpers. */
(function (root, factory) {
  'use strict';
  const api = factory(root);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) {
    root.CCPublic = api;
    if (root.document && typeof render === 'function') api.install();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';
  const ID = /^[0-9a-f]{12}$/;
  const REASONS = { resigned: 'Xin thua', timeout: 'Hết giờ', disconnected: 'Mất kết nối', draw_agreed: 'Hòa thỏa thuận', room_closed: 'Phòng đã đóng' };
  const OUTCOMES = { win: 'Thắng', loss: 'Thua', draw: 'Hòa' };
  const html = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const reasonText = reason => REASONS[reason] || reason || '';
  // Vietnam time, fixed UTC+7.
  const dayText = iso => { const t = Date.parse(iso); if (!Number.isFinite(t)) return ''; const d = new Date(t + 7 * 3600000); return String(d.getUTCDate()).padStart(2, '0') + '/' + String(d.getUTCMonth() + 1).padStart(2, '0') + '/' + d.getUTCFullYear(); };
  const monthText = joined => /^\d{4}-\d{2}$/.test(joined || '') ? joined.slice(5) + '/' + joined.slice(0, 4) : '';
  const isPublicId = value => typeof value === 'string' && ID.test(value);

  /** Rows for the move list of one public game, in traditional notation. */
  function notationRows(game, tools) {
    try { return tools.pairMoveHistory(game.initialFen, game.moves || []); } catch { return null; }
  }

  function gameHTML(game, open, tools) {
    const opponent = game.opponent || {};
    const name = opponent.kind === 'public' && isPublicId(opponent.publicId)
      ? `<a href="#u/${opponent.publicId}">${html(opponent.name)}</a>` : html(opponent.name);
    const rows = open ? notationRows(game, tools) : null;
    const record = open ? (rows && rows.length
      ? `<table class="notation-table"><thead><tr><th>Nước</th><th>Đỏ</th><th>Đen</th></tr></thead><tbody>${rows.map(r => `<tr><td>${r.number}</td><td>${html(r.red ? r.red.notation : '…')}</td><td>${html(r.black ? r.black.notation : '')}</td></tr>`).join('')}</tbody></table>`
      : '<p class="subtle">Ván kết thúc trước nước đầu tiên.</p>') : '';
    return `<li class="public-game outcome-${html(game.outcome)}"><div class="public-game-row"><span class="public-outcome">${OUTCOMES[game.outcome] || ''}</span><div><p><span>${game.side === 'b' ? 'Cầm Đen' : 'Cầm Đỏ'}</span> · <span>gặp</span> ${name}</p><p class="subtle"><span>${dayText(game.endedAt)}</span> · <span>${html(reasonText(game.reason))}</span> · <b>${(game.moves || []).length}</b> <span>nửa nước</span></p></div><button type="button" class="quiet" data-public-action="toggle-game" data-value="${html(game.gameId)}" aria-expanded="${open}">${open ? 'Ẩn biên bản' : 'Xem biên bản'}</button></div>${record}</li>`;
  }

  /** The whole public page from an API answer (pure, for tests). */
  function profileHTML(profile, options = {}) {
    const t = profile.totals || {};
    const games = profile.games || [];
    return `<section class="public-profile"><p class="eyebrow">Hồ sơ công khai</p><h1>${html(profile.displayName)}</h1><p class="subtle"><span>Tham gia từ</span> ${monthText(profile.joined)}</p>`
      + `<div class="stat-grid public-stats"><div class="stat"><b>${t.games || 0}</b><span>ván online</span></div><div class="stat"><b>${t.wins || 0}</b><span>thắng</span></div><div class="stat"><b>${t.losses || 0}</b><span>thua</span></div><div class="stat"><b>${t.draws || 0}</b><span>ván hòa</span></div></div>`
      + `<section class="panel"><h2>Ván gần đây</h2>${games.length ? `<ol class="public-games">${games.map(g => gameHTML(g, g.gameId === options.open, options.tools)).join('')}</ol>` : '<p>Chưa có ván online nào kết thúc.</p>'}`
      + `<p class="subtle separation">Chỉ gồm ván online giao hữu đã kết thúc do máy chủ ghi. Không xếp hạng, không phải Elo; phần học và suy nghĩ của người chơi không hiển thị ở đây.</p></section></section>`;
  }

  function accountPanelHTML(user, origin) {
    if (!user || !isPublicId(user.publicId)) return '';
    if (user.role !== 'user') return `<section class="panel separation public-account"><h2>Hồ sơ công khai</h2><p>Tài khoản quản trị không có hồ sơ công khai.</p></section>`;
    const visible = user.profileVisibility === 'public';
    const link = origin + '/#u/' + user.publicId;
    return `<section class="panel separation public-account" id="public-profile-settings"><h2>Hồ sơ công khai</h2>`
      + `<p>${visible ? 'Đang công khai: ai có link đều xem được tên hiển thị và các ván online đã kết thúc của bạn.' : 'Đang riêng tư: không ai xem được hồ sơ của bạn; trong lịch sử của người khác, bạn hiện là "Người chơi ẩn".'}</p>`
      + (visible ? `<p class="public-link"><code>${html(link)}</code></p><div class="button-row"><a class="secondary" href="#u/${user.publicId}">Xem hồ sơ của tôi</a><button type="button" class="secondary" data-public-action="copy" data-value="${html(link)}">Sao chép link</button><button type="button" class="quiet" data-public-action="visibility" data-value="private">Chuyển sang riêng tư</button></div>`
        : `<div class="button-row"><button type="button" class="secondary" data-public-action="visibility" data-value="public">Công khai hồ sơ</button></div>`)
      + `<p class="subtle">Không hiện tên đăng nhập, tiến độ học hay câu trả lời của bạn. Link dùng mã ngẫu nhiên.</p></section>`;
  }

  function promptHTML(user) {
    if (!user || user.role !== 'user' || user.profileVisibility !== 'unset') return '';
    return `<section class="panel public-prompt" role="region" aria-labelledby="public-prompt-title"><h2 id="public-prompt-title">Bạn muốn công khai hồ sơ không?</h2>`
      + `<p>Cờ Chill có thêm hồ sơ công khai: tên hiển thị và các ván online đã kết thúc, xem được qua một link ngẫu nhiên. Tài khoản của bạn đang riêng tư cho tới khi bạn chọn.</p>`
      + `<div class="button-row"><button type="button" class="primary" data-public-action="visibility" data-value="public">Công khai</button><button type="button" class="secondary" data-public-action="visibility" data-value="private">Giữ riêng tư</button></div><p class="subtle">Đổi lại bất cứ lúc nào trong Tài khoản.</p></section>`;
  }

  const SIGNUP_NOTE = '<p class="subtle">Hồ sơ công khai bật sẵn: chỉ tên hiển thị và các ván online đã kết thúc. Tắt bất cứ lúc nào trong Tài khoản.</p>';

  let installed = false, current = { id: null, data: null, error: '', loading: false }, open = null;

  function install() {
    if (installed) return;
    installed = true;
    const previous = render;
    const cloud = () => root.CCCloudUI;
    const user = () => cloud() && cloud().sessionUser ? cloud().sessionUser() : null;
    const client = () => cloud() && cloud().snapshot ? cloud().snapshot().client : null;
    async function load(id) {
      current = { id, data: null, error: '', loading: true };
      try {
        const c = client();
        if (!c || !c.available) throw new Error('Cần máy chủ Cờ Chill để xem hồ sơ công khai.');
        const data = await c.request('/api/public/' + id);
        if (current.id === id) current = { id, data, error: '', loading: false };
      } catch (error) {
        if (current.id === id) current = { id, data: null, error: error.message || 'Không tải được hồ sơ.', loading: false };
      }
      if (route()[0] === 'u') render();
    }
    render = function publicRender() {
      previous();
      if (booting) return;
      const [page, id] = route(), main = $('main');
      if (page === 'u') {
        if (!isPublicId(id)) main.innerHTML = empty('Không tìm thấy hồ sơ công khai', 'Link hồ sơ có thể đã sai hoặc người chơi đã chuyển sang riêng tư.', 'home', 'Về trang chủ');
        else {
          if (current.id !== id && !current.loading) load(id);
          main.innerHTML = current.id === id && current.data ? profileHTML(current.data, { open, tools: root.CC })
            : current.id === id && current.error ? empty('Không tìm thấy hồ sơ công khai', current.error, 'home', 'Về trang chủ')
            : '<section class="panel empty"><p>Đang tải hồ sơ công khai…</p></section>';
          document.title = 'Hồ sơ công khai · Cờ Chill';
        }
      } else {
        const u = user();
        if (page === 'account' && u) main.insertAdjacentHTML('beforeend', accountPanelHTML(u, root.location.origin));
        if (page === 'account' && !u) { const form = main.querySelector('[data-cloud-form="register"] button[type="submit"]'); if (form) form.insertAdjacentHTML('beforebegin', SIGNUP_NOTE); }
        if (['home', 'account', 'profile'].includes(page || 'home') && promptHTML(u)) main.insertAdjacentHTML('afterbegin', promptHTML(u));
      }
      if (root.CCV6UI) root.CCV6UI.refresh(false);
    };
    document.addEventListener('click', async event => {
      const target = event.target.closest && event.target.closest('[data-public-action]');
      if (!target) return;
      event.preventDefault();
      const action = target.dataset.publicAction, value = target.dataset.value;
      if (action === 'toggle-game') { open = open === value ? null : value; render(); return; }
      if (action === 'copy') {
        try { await root.navigator.clipboard.writeText(value); toast('Đã sao chép link hồ sơ'); } catch { toast('Không thể sao chép tự động. Hãy tự chép link: ' + value); }
        return;
      }
      if (action === 'visibility' && ['public', 'private'].includes(value)) {
        target.disabled = true;
        try {
          const c = client(), result = await c.request('/api/account/visibility', { method: 'POST', body: { visibility: value } });
          c.session.user = result.user;
          current = { id: null, data: null, error: '', loading: false };
          render();
          toast(value === 'public' ? 'Hồ sơ đã công khai.' : 'Hồ sơ đã chuyển sang riêng tư.');
        } catch (error) { toast(error.message || 'Chưa đổi được. Hãy thử lại.'); } finally { target.disabled = false; }
      }
    });
    render();
  }

  return Object.freeze({ install, profileHTML, accountPanelHTML, promptHTML, reasonText, dayText, monthText, isPublicId, SIGNUP_NOTE });
});
