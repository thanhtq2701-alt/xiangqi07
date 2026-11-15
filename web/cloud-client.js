/* Account transport and revisioned persistence. No passwords or session tokens are stored here. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.CoChillCloud = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  class ApiError extends Error {
    constructor(message, status, data) { super(message); this.status = status; this.data = data; this.code = data?.code; }
  }
  class Client {
    constructor({fetcher = (...args) => fetch(...args), notify = () => {}} = {}) {
      this.fetcher = fetcher; this.notify = notify;
      this.session = {authenticated:false}; this.available = false;
      this.revision = 0; this.pending = null; this.sending = false; this.conflict = null;
      this.epoch = 0; this.lastSaved = null;
      this.stateReady = false; this.draftVersion = 0; this.readVersion = 0; this.writeVersion = 0;
      this.sendingEpoch = null; this.controllers = new Set(); this.authenticating = false; this.loggingOut = false;
    }
    async request(path, {method = 'GET', body, signal} = {}) {
      if (signal?.aborted) throw new DOMException('Yêu cầu đã hủy.', 'AbortError');
      const controller = new AbortController();
      this.controllers.add(controller);
      const abort = () => controller.abort();
      signal?.addEventListener('abort', abort, {once:true});
      const timer = setTimeout(abort, path.includes('/engine/') ? 25000 : 15000);
      try {
        const headers = {'Accept':'application/json'};
        if (body !== undefined) headers['Content-Type'] = 'application/json';
        if (this.session.csrf) headers['X-CSRF-Token'] = this.session.csrf;
        const response = await this.fetcher(path, {method, credentials:'same-origin', cache:'no-store', headers, signal:controller.signal,
          ...(body !== undefined ? {body:JSON.stringify(body)} : {})});
        const type = response.headers?.get('content-type') || '';
        if (!type.includes('application/json')) throw new ApiError('Máy chủ tài khoản chưa được bật ở địa chỉ này.', response.status);
        const data = await response.json();
        if (!response.ok) throw new ApiError(typeof data.error === 'string' ? data.error : data.message || data.error?.message || 'Yêu cầu chưa thực hiện được.', response.status, data);
        return data;
      } finally { clearTimeout(timer); signal?.removeEventListener('abort', abort); this.controllers.delete(controller); }
    }
    adoptSession(session, {preserveDraft = false} = {}) {
      // A response from an old account must never update a new account's CAS
      // revision or queue, even if a mock/network ignores AbortController.
      this.epoch++; this.readVersion++;
      for (const controller of this.controllers) controller.abort();
      this.session = session; this.stateReady = false; this.revision = 0; this.lastSaved = null;
      this.sending = false; this.sendingEpoch = null;
      if (!preserveDraft) { this.pending = null; this.conflict = null; this.draftVersion++; }
    }
    expire() {
      this.adoptSession({authenticated:false}, {preserveDraft:true});
      this.notify('expired');
    }
    sameSession(epoch, userId) {
      return this.epoch === epoch && this.session.authenticated && this.session.user?.id === userId;
    }
    async probe() {
      const epoch = this.epoch;
      try {
        const session = await this.request('/api/session');
        if (epoch !== this.epoch) return this.session;
        if (session.authenticated !== this.session.authenticated || session.user?.id !== this.session.user?.id) {
          this.adoptSession(session, {preserveDraft:!session.authenticated});
        } else this.session = session;
        this.available = true;
      } catch { if (epoch === this.epoch) this.available = false; }
      return this.session;
    }
    async authenticate(kind, credentials) {
      if (!['login','register'].includes(kind)) throw new ApiError('Thao tác tài khoản không hợp lệ.', 400);
      if (this.authenticating || this.loggingOut) throw new ApiError('Đang xử lý tài khoản. Hãy chờ hoàn tất.', 409, {code:'auth_busy'});
      this.authenticating = true;
      try {
        const session = await this.request('/api/auth/' + kind, {method:'POST',body:credentials});
        this.adoptSession(session); this.available = true;
        return session;
      } finally { this.authenticating = false; }
    }
    async readState() {
      if (!this.session.authenticated) throw new ApiError('Hãy đăng nhập trước khi tải tiến độ.', 401);
      // A GET during a PUT may see either side of the commit. Do not let it
      // replace the revision that the in-flight save is about to acknowledge.
      if (this.sending && this.sendingEpoch === this.epoch) throw new ApiError('Đang lưu tiến độ. Hãy chờ lưu xong rồi tải lại.', 409, {code:'save_in_progress'});
      const epoch = this.epoch, userId = this.session.user?.id, readVersion = ++this.readVersion, writeVersion = this.writeVersion;
      let data;
      try { data = await this.request('/api/state'); }
      catch (error) {
        if (this.sameSession(epoch, userId) && (error.status === 401 || error.status === 403)) this.expire();
        throw error;
      }
      if (!this.sameSession(epoch, userId)) throw new ApiError('Đã đổi phiên; bỏ kết quả của tài khoản cũ.', 409, {code:'stale_session'});
      if (readVersion !== this.readVersion || writeVersion !== this.writeVersion) throw new ApiError('Đã có lần tải hoặc lưu mới hơn; bỏ kết quả cũ.', 409, {code:'stale_read'});
      if (!Number.isSafeInteger(data.revision) || data.revision < 0 || !data.state || typeof data.state !== 'object' || Array.isArray(data.state)) {
        throw new ApiError('Dữ liệu tiến độ máy chủ không hợp lệ.', 502, {code:'invalid_state'});
      }
      this.revision = data.revision; this.lastSaved = JSON.stringify(data.state);
      this.stateReady = true;
      return data;
    }
    queue(state) {
      if (!this.session.authenticated || this.loggingOut) return;
      this.pending = JSON.stringify(state); this.draftVersion++;
      this.notify(this.conflict ? 'conflict' : 'pending');
    }
    async flush() {
      if ((this.sending && this.sendingEpoch === this.epoch) || !this.pending || this.conflict || !this.session.authenticated || !this.stateReady || this.loggingOut) return false;
      this.sending = true; const epoch = this.epoch; this.sendingEpoch = epoch;
      try {
        while (this.pending && epoch === this.epoch && this.session.authenticated && !this.loggingOut) {
          const payload = this.pending;
          this.notify('saving');
          this.writeVersion++;
          const data = await this.request('/api/state', {method:'PUT',body:{revision:this.revision,state:JSON.parse(payload)}});
          if (epoch !== this.epoch) return false;
          if (!Number.isSafeInteger(data.revision) || data.revision !== this.revision + 1) {
            throw new ApiError('Máy chủ trả phiên bản không hợp lệ. Hãy kiểm tra lại hai bản tiến độ.', 409, {code:'invalid_revision'});
          }
          this.revision = data.revision; this.lastSaved = payload;
          if (this.pending === payload) this.pending = null;
          this.notify(this.pending ? 'pending' : 'saved');
        }
        return true;
      } catch (error) {
        if (epoch !== this.epoch) return false;
        if (error.status === 409) { this.conflict = {message:error.message}; this.notify('conflict'); }
        else if (error.status === 401 || error.status === 403) this.expire();
        else this.notify('offline');
        return false;
      } finally { if (this.sendingEpoch === epoch) {this.sending = false; this.sendingEpoch = null;} }
    }
    async useServer() {
      const draftVersion = this.draftVersion;
      const data = await this.readState();
      if (draftVersion !== this.draftVersion) return this.draftChanged();
      this.pending = null; this.conflict = null; this.notify('saved'); return data.state;
    }
    async useDraft(state) {
      // Only called after the user explicitly chooses this draft over the current server revision.
      const draftVersion = this.draftVersion;
      await this.readState();
      if (draftVersion !== this.draftVersion) return this.draftChanged();
      this.conflict = null; this.queue(state); return this.flush();
    }
    draftChanged() {
      const message = 'Bản nháp vừa có thay đổi trong lúc tải. Đã giữ bản mới; hãy chọn lại bản cần dùng.';
      this.conflict = {message}; this.notify('conflict');
      throw new ApiError(message, 409, {code:'draft_changed'});
    }
    async logout() {
      if (this.authenticating || this.loggingOut) throw new ApiError('Đang xử lý tài khoản. Hãy chờ hoàn tất.', 409, {code:'auth_busy'});
      this.loggingOut = true;
      try {
        await this.request('/api/auth/logout', {method:'POST',body:{}});
        this.adoptSession({authenticated:false});
      } finally { this.loggingOut = false; }
    }
  }
  return {Client,ApiError};
});
