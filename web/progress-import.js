/* Cờ Chill progress import with a preview. Reads only the app's own exports
 * (co-chill-personal-export v1 and co-chill-account-export-v1), rebuilds the
 * learning history through the same sanitizers used for sync, and replays every
 * game move with the rules. It never imports answer keys, account or role
 * fields, feedback, server-owned online games or unfinished drafts; the result
 * lands only in the state of whoever is using the app now.
 * Browser: CCImport. Node: require('./progress-import.js'). */
(function (root, factory) {
  'use strict';
  const node = typeof module !== 'undefined' && module.exports;
  const api = factory(node ? require('./xiangqi.js') : root.XQ, node ? require('./learning.js') : root.CC,
    node ? require('./curriculum.js') : root.CCCurriculum);
  if (node) module.exports = api;
  root.CCImport = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (XQ, Learning, Curriculum) {
  'use strict';
  const MAX_CHARS = 5 * 1024 * 1024;
  const MAX_GAME_MOVES = 2000;
  const PERSONAL = 'co-chill-personal-export', ACCOUNT = 'co-chill-account-export-v1';
  const MODES = ['merge', 'replace'];
  const plain = value => !!value && typeof value === 'object' && !Array.isArray(value);
  const list = value => Array.isArray(value) ? value : [];
  const str = (value, limit) => typeof value === 'string' ? value.slice(0, limit) : '';
  const validId = value => typeof value === 'string' && /^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,199}$/.test(value) &&
    !['constructor', 'prototype', '__proto__'].includes(value);
  const COORD = /^[a-i][0-9][a-i][0-9]$/;
  const fail = message => { const error = new Error(message); error.importError = true; throw error; };

  function hash(value) {
    let output = 2166136261;
    for (let i = 0; i < value.length; i += 1) output = Math.imul(output ^ value.charCodeAt(i), 16777619);
    return (output >>> 0).toString(36);
  }

  // Basic exercises: one record per position, attempts in time order.
  function records(raw) {
    const entries = Array.isArray(raw) ? raw.filter(plain).map(r => [r.puzzleId, r]) : plain(raw) ? Object.entries(raw) : [];
    const result = {};
    for (const [id, record] of entries.slice(0, 2000)) {
      if (!validId(id) || !plain(record) || result[id]) continue;
      result[id] = { id, skill: str(record.skill, 40), attempts: list(record.attempts).filter(plain).slice(-200).map(a => ({
        ...pick(a, ['startedAt', 'completedAt', 'source', 'candidate', 'firstCandidate', 'success', 'assisted', 'unknown', 'firstExposure', 'related']),
        answers: list(a.answers).slice(0, 3), firstAnswers: Array.isArray(a.firstAnswers) ? a.firstAnswers.slice(0, 3) : null,
        // The personal export has no attempt ids; derive a stable one so a second import is a no-op.
        id: validId(a.id) ? a.id : 'imp_' + hash(id + '|' + a.startedAt + '|' + a.completedAt)
      })) };
    }
    return result;
  }

  function pick(source, keys) {
    const result = {};
    for (const key of keys) if (source[key] !== undefined) result[key] = source[key];
    return result;
  }

  // Multi-step exercises: walk the current tree from the root so stored node ids are never trusted.
  function lineAttempt(raw) {
    if (!plain(raw)) return null;
    const exercise = Curriculum.findExercise(raw.puzzleId);
    if (!exercise || raw.version !== exercise.version) return null;
    let nodeId = exercise.root;
    const history = [];
    for (const entry of list(raw.history).slice(0, 21)) {
      const node = exercise.nodes[nodeId], edge = plain(entry) && node && node.choices.find(choice => choice.move === entry.move);
      if (!edge) return null;
      history.push({ nodeId, move: edge.move, reply: edge.reply, at: entry.at });
      if (edge.next) nodeId = edge.next;
    }
    return { ...pick(raw, ['puzzleId', 'version', 'startedAt', 'completedAt', 'candidate', 'success', 'assisted', 'firstExposure']),
      answers: list(raw.answers).slice(0, 3), finalNodeId: nodeId, history,
      id: validId(raw.id) ? raw.id : 'line:' + exercise.id + ':imp_' + hash(raw.startedAt + '|' + raw.completedAt) };
  }

  // Finished local games only. Every move is replayed; a result the rules can see wins over the file.
  function game(raw, now) {
    if (!plain(raw) || !validId(raw.id) || raw.id.startsWith('online-')) return { reject: 'invalid' };
    if (!plain(raw.status) || raw.status.over !== true) return { reject: 'unfinished' };
    let pos;
    try { pos = XQ.Position.fromFen(raw.initialFen); } catch { return { reject: 'invalid' }; }
    const initialFen = pos.fen(), moves = [], source = list(raw.moves);
    if (source.length > MAX_GAME_MOVES) return { reject: 'invalid' };
    for (const item of source) {
      const move = typeof item === 'string' ? item : plain(item) ? item.move : null;
      if (!COORD.test(move || '') || !pos.legalMoves().includes(move)) return { reject: 'invalid' };
      const next = pos.play(move);
      moves.push({ move, before: pos.fen(), after: next.fen(), side: pos.turn });
      pos = next;
    }
    const ruled = pos.status();
    const status = ruled.over ? { over: true, winner: ruled.winner, reason: ruled.reason } : {
      over: true, winner: ['w', 'b'].includes(raw.status.winner) ? raw.status.winner : null,
      reason: str(raw.status.reason, 200) || 'Đã kết thúc theo file nhập', needsVerification: raw.status.needsVerification === true };
    const created = Number(raw.createdAt);
    return { game: { id: raw.id, title: str(raw.title, 120) || 'Ván đã nhập', createdAt: Number.isFinite(created) && created > 0 && created <= now ? created : now,
      mode: ['bot', 'deep', 'local', 'import'].includes(raw.mode) ? raw.mode : 'import', player: raw.player === 'b' ? 'b' : 'w',
      initialFen, fen: pos.fen(), moves, status, clock: { enabled: false }, importedAt: new Date(now).toISOString() } };
  }

  /** Text of a chosen file -> what it holds. Throws an Error with a Vietnamese message. */
  function parse(text, options = {}) {
    if (typeof text !== 'string' || !text.trim()) fail('File trống.');
    if (text.length > MAX_CHARS) fail('File lớn hơn 5 MB.');
    let data;
    try { data = JSON.parse(text.replace(/^﻿/, '')); } catch { fail('File không phải JSON hợp lệ.'); }
    if (!plain(data)) fail('Không nhận ra file. Chỉ nhập file do Cờ Chill xuất.');
    const now = Number.isFinite(options.now) ? options.now : Date.now();
    let source, kind, account = null;
    const ignored = [];
    // A finished exercise is already in the history; only work still in progress is a draft.
    const open = (draft, done) => plain(draft) && !done.includes(draft.stage);
    if (data.format === PERSONAL) {
      if (data.version !== 1) fail('Phiên bản file xuất chưa được hỗ trợ.');
      kind = 'personal'; source = data;
      if (open(data.draft, ['complete', 'summary']) || open(data.lineDraft, ['finished'])) ignored.push('drafts');
    } else if (data.format === ACCOUNT) {
      if (!plain(data.state)) fail('File tài khoản thiếu phần tiến độ.');
      kind = 'account'; source = data.state;
      account = plain(data.account) ? str(data.account.username, 80) || null : null;
      if (open(source.session, ['complete', 'summary']) || open(source.lineSession, ['finished'])) ignored.push('drafts');
      if (list(data.onlineGames).length) ignored.push('onlineGames');
      if (list(data.feedback).length) ignored.push('feedback');
    } else fail('Không nhận ra file. Chỉ nhập file do Cờ Chill xuất (dữ liệu cá nhân hoặc tài khoản).');
    if (str(source.profile && source.profile.name, 80)) ignored.push('profile');
    const games = [], rejected = { games: 0, unfinished: 0, lineAttempts: 0 };
    for (const raw of list(source.games).slice(0, 5000)) {
      const result = game(raw, now);
      if (result.game) games.push(result.game);
      else if (result.reject === 'unfinished') rejected.unfinished += 1;
      else rejected.games += 1;
    }
    const lineAttempts = [];
    for (const raw of list(source.lineAttempts).slice(-2000)) {
      const item = lineAttempt(raw);
      if (item) lineAttempts.push(item); else rejected.lineAttempts += 1;
    }
    return { kind, account, ignored, rejected, raw: { records: records(source.records), lineAttempts, games,
      lessonViews: list(source.lessonViews).filter(plain).map(v => ({ id: v.id, at: v.at, kind: 'viewed' })),
      summaries: list(source.summaries).filter(plain) } };
  }

  const attemptKey = a => a.startedAt + '|' + a.completedAt;
  function union(base, extra, key, limit) {
    const seen = new Set(base.map(key)), result = base.slice();
    for (const item of extra) if (!seen.has(key(item))) { seen.add(key(item)); result.push(item); }
    return result.slice(-limit);
  }
  const byTime = (a, b) => (Date.parse(a.completedAt) || 0) - (Date.parse(b.completedAt) || 0);

  function combine(state, imported, mode) {
    const base = mode === 'replace' ? { ...Learning.fresh(), session: state.session, lineSession: state.lineSession, profile: state.profile } : state;
    const result = { ...base, version: 2, records: { ...(base.records || {}) } };
    for (const [id, record] of Object.entries(imported.records)) {
      const current = result.records[id];
      if (!current) { result.records[id] = { ...record, seenCount: record.attempts.length }; continue; }
      // Same attempt exported and re-imported: match by time as well as id.
      const attempts = union(list(current.attempts), record.attempts, attemptKey, 400)
        .filter((a, i, all) => all.findIndex(b => b.id === a.id) === i).sort(byTime);
      result.records[id] = { ...current, attempts };
    }
    result.lineAttempts = union(list(base.lineAttempts), imported.lineAttempts, a => a.puzzleId + '|' + attemptKey(a), 2000)
      .filter((a, i, all) => all.findIndex(b => b.id === a.id) === i).sort(byTime);
    result.lessonViews = union(list(base.lessonViews), imported.lessonViews, v => v.id, 1000);
    result.summaries = union(list(base.summaries), imported.summaries, s => s.id, 200);
    result.games = union(list(base.games), imported.games, g => g.id, 5000);
    return result;
  }

  function counts(state) {
    const recs = Object.values(state.records || {});
    return { games: list(state.games).filter(g => g && g.status && g.status.over).length,
      positions: recs.filter(r => list(r.attempts).length).length,
      attempts: recs.reduce((sum, r) => sum + list(r.attempts).length, 0),
      lineAttempts: list(state.lineAttempts).length, lessonViews: list(state.lessonViews).length,
      summaries: list(state.summaries).length };
  }

  /** New learner state after importing; nothing is saved here. */
  function apply(state, imported, mode, options = {}) {
    if (!MODES.includes(mode)) throw new Error('Chọn cách nhập: gộp hoặc thay thế.');
    const now = Number.isFinite(options.now) ? options.now : Date.now();
    return Learning.sanitize(combine(state, imported.raw, mode), { now });
  }

  /** Counts before / in the file / after, for the preview table. */
  function preview(state, imported, mode, options = {}) {
    const now = Number.isFinite(options.now) ? options.now : Date.now();
    const valid = Learning.sanitize({ ...Learning.fresh(), ...imported.raw }, { now });
    const rawAttempts = Object.values(imported.raw.records).reduce((sum, r) => sum + r.attempts.length, 0);
    const file = counts(valid);
    return { mode, kind: imported.kind, account: imported.account, ignored: imported.ignored.slice(),
      before: counts(state), file, after: counts(apply(state, imported, mode, { now })),
      rejected: { ...imported.rejected, attempts: rawAttempts - file.attempts,
        lineAttempts: imported.rejected.lineAttempts + imported.raw.lineAttempts.length - file.lineAttempts } };
  }

  return Object.freeze({ MODES: MODES.slice(), parse, preview, apply });
});
