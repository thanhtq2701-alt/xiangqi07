/* Cờ Chill V6 multi-decision practice. Rules validate every transition.
 * This is a deterministic learning workflow, not an engine or text grader.
 * Browser: CCLine. Node: require('./line-practice.js'). All state functions
 * return new values; callers persist the session in the current account.
 */
(function (root, factory) {
  'use strict';
  const api = factory(typeof module !== 'undefined' && module.exports ? require('./xiangqi.js') : root.XQ);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CCLine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (XQ) {
  'use strict';
  const DAY = 86400000;
  const copy = value => JSON.parse(JSON.stringify(value));
  const plain = value => !!value && typeof value === 'object' && !Array.isArray(value);
  const id = value => typeof value === 'string' && /^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,159}$/.test(value) && !['constructor', 'prototype', '__proto__'].includes(value);
  function time(value) {
    const result = value === undefined ? Date.now() : typeof value === 'string' ? Date.parse(value) : value;
    if (!Number.isFinite(result) || result < Date.UTC(2000, 0, 1) || result > Date.UTC(2100, 0, 1)) throw new Error('Thời điểm lưu không hợp lệ.');
    return result;
  }
  const iso = value => new Date(time(value)).toISOString();
  const answers = value => [0, 1, 2].map(i => typeof value?.[i] === 'string' ? value[i].slice(0, 1500) : '');
  const reflected = value => answers(value).every(a => a.trim().length > 0);
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  function validate(exercise) {
    assert(plain(exercise) && exercise.format === 'line-v1' && id(exercise.id) && Number.isInteger(exercise.version) && exercise.version > 0, 'Định dạng bài nhiều lượt chưa hợp lệ.');
    assert(plain(exercise.nodes) && id(exercise.root) && Object.prototype.hasOwnProperty.call(exercise.nodes, exercise.root), 'Thiếu vị trí bắt đầu.');
    const nodeIds = Object.keys(exercise.nodes);
    assert(nodeIds.length > 0 && nodeIds.length <= 256 && nodeIds.every(id), 'Số vị trí hoặc mã vị trí không hợp lệ.');
    const rootPos = XQ.Position.fromFen(exercise.fen);
    assert(['w', 'b'].includes(exercise.learner) && rootPos.turn === exercise.learner, 'Sai bên đi của người học.');
    const visited = new Set(), visiting = new Set();
    function walk(nodeId, expectedFen, depth) {
      assert(depth <= 20 && !visiting.has(nodeId), 'Bài có vòng lặp hoặc vượt giới hạn bước.');
      const node = exercise.nodes[nodeId];
      assert(plain(node) && node.id === nodeId, 'Thiếu vị trí trong bài.');
      const pos = XQ.Position.fromFen(node.fen);
      assert(pos.fen() === expectedFen && pos.turn === exercise.learner, 'Nhánh không khớp thế cờ.');
      if (visited.has(nodeId)) return;
      visiting.add(nodeId);
      assert(Array.isArray(node.choices) && node.choices.length > 0 && node.choices.length <= 90, 'Vị trí cần ít nhất một phương án đã duyệt.');
      const legal = pos.legalMoves(), seenMoves = new Set();
      assert(Array.isArray(node.rejectedMoves || []), 'Danh sách nước chưa đạt không hợp lệ.');
      for (const edge of node.choices) {
        assert(plain(edge) && legal.includes(edge.move) && !seenMoves.has(edge.move), 'Phương án trùng hoặc sai luật.');
        seenMoves.add(edge.move);
        let next = pos.play(edge.move);
        if (exercise.proof?.method === 'exhaustive-checking-mate') assert(next.inCheck(), 'Bài chiếu liên tục có nước không chiếu.');
        if (edge.next === null) {
          assert(edge.reply === null && next.status().over && next.status().winner === exercise.learner && next.inCheck(), 'Điểm kết thúc chưa phải chiếu hết.');
        } else {
          assert(id(edge.next) && next.legalMoves().includes(edge.reply), 'Nước đáp hoặc nhánh tiếp theo không hợp lệ.');
          next = next.play(edge.reply);
          walk(edge.next, next.fen(), depth + 1);
        }
      }
      for (const rejected of node.rejectedMoves || []) assert(legal.includes(rejected) && !seenMoves.has(rejected), 'Nước chưa đạt phải hợp lệ và không trùng đáp án.');
      visiting.delete(nodeId); visited.add(nodeId);
    }
    walk(exercise.root, rootPos.fen(), 0);
    assert(visited.size === nodeIds.length, 'Bài có vị trí rời không sử dụng.');
    return true;
  }
  function create(exercise, options = {}) {
    validate(exercise);
    const now = time(options.now);
    return { kind: 'line-v1', id: 'line:' + exercise.id + ':' + now, exerciseId: exercise.id, version: exercise.version,
      stage: 'reflect', nodeId: exercise.root, answers: ['', '', ''], firstAnswers: null, firstCandidate: null,
      candidate: null, history: [], attempts: [], failureCount: 0, assisted: false, solved: false,
      seenExplanation: false, startedAt: iso(now), updatedAt: iso(now), completedAt: null, dueAt: null,
      pendingReviewAt: null, pendingVerification: null, related: options.related === true,
      firstExposure: options.firstExposure === true, source: 'authored-line-practice' };
  }
  function checkSession(exercise, session) {
    assert(plain(session) && session.kind === 'line-v1' && session.exerciseId === exercise.id && session.version === exercise.version, 'Bài đã đổi phiên bản hoặc nháp không khớp.');
    assert(plain(exercise.nodes[session.nodeId]) && Array.isArray(session.history), 'Vị trí đang học không hợp lệ.');
  }
  function currentPosition(exercise, session) {
    checkSession(exercise, session);
    if (session.solved && session.history.length) {
      let pos = XQ.Position.fromFen(exercise.fen);
      for (const entry of session.history) { pos = pos.play(entry.move); if (entry.reply) pos = pos.play(entry.reply); }
      return pos;
    }
    return XQ.Position.fromFen(exercise.nodes[session.nodeId].fen);
  }
  function submit(exercise, session, options = {}) {
    checkSession(exercise, session);
    assert(['reflect', 'practice', 'awaiting_verification'].includes(session.stage), 'Hãy tiếp tục bài trước khi gửi nước.');
    const now = time(options.now);
    assert(now >= time(session.updatedAt), 'Không thể gửi nước trước thời điểm lưu gần nhất.');
    const next = copy(session), node = exercise.nodes[next.nodeId], move = options.move || next.candidate;
    if (!next.history.length && !next.firstAnswers && options.answers) next.answers = answers(options.answers);
    if (!reflected(next.firstAnswers || next.answers) || typeof move !== 'string') return { session: next, outcome: 'incomplete' };
    const pos = XQ.Position.fromFen(node.fen);
    if (!pos.legalMoves().includes(move)) return { session: next, outcome: 'illegal' };
    if (!next.firstAnswers) { next.firstAnswers = answers(next.answers); next.firstCandidate = move; }
    next.candidate = move; next.updatedAt = iso(now); next.pendingVerification = null;
    const edge = node.choices.find(choice => choice.move === move);
    if (!edge && !(node.rejectedMoves || []).includes(move)) {
      next.stage = 'awaiting_verification';
      next.pendingVerification = { nodeId: node.id, move, at: iso(now) };
      return { session: next, outcome: 'pending_verification' };
    }
    next.attempts.push({ nodeId: node.id, move, at: iso(now), accepted: !!edge });
    next.attempts = next.attempts.slice(-200);
    if (!edge) {
      next.failureCount += 1; next.assisted = true;
      if (next.failureCount >= 3) {
        next.stage = 'parked'; next.lastAttemptHistory = next.history.slice();
        next.history = []; next.nodeId = exercise.root; next.candidate = null;
        next.pendingReviewAt = iso(now + DAY); next.solved = false;
        return { session: next, outcome: 'parked' };
      }
      next.stage = next.history.length ? 'practice' : 'reflect';
      return { session: next, outcome: 'retry' };
    }
    next.history.push({ nodeId: node.id, move, reply: edge.reply, at: iso(now) });
    next.candidate = null;
    if (edge.next === null) {
      next.solved = true; next.stage = 'explain'; next.seenExplanation = true;
    } else { next.nodeId = edge.next; next.stage = 'practice'; }
    return { session: next, outcome: next.solved ? 'solved' : 'advanced', playerMove: move, opponentMove: edge.reply };
  }
  function restore(exercise, raw, options = {}) {
    try {
      validate(exercise); checkSession(exercise, raw);
      assert(id(raw.id) && ['reflect', 'practice', 'awaiting_verification', 'explain', 'parked', 'finished'].includes(raw.stage), 'Trạng thái nháp không hợp lệ.');
      const now = time(options.now), started = time(raw.startedAt), updated = time(raw.updatedAt);
      assert(started <= updated && updated <= now + 300000, 'Thời điểm nháp không hợp lệ.');
      const result = create(exercise, { now: started, related: raw.related, firstExposure: raw.firstExposure });
      result.id = raw.id; result.answers = answers(raw.answers);
      result.firstAnswers = reflected(raw.firstAnswers) ? answers(raw.firstAnswers) : null;
      result.firstCandidate = typeof raw.firstCandidate === 'string' && XQ.Position.fromFen(exercise.fen).legalMoves().includes(raw.firstCandidate) ? raw.firstCandidate : null;
      result.assisted = raw.assisted === true;
      result.failureCount = Math.min(3, Math.max(0, Number.isInteger(raw.failureCount) ? raw.failureCount : 0));
      let nid = exercise.root, previousTime = started, terminal = false;
      assert(raw.history.length <= 20, 'Nháp quá dài.');
      for (const entry of raw.history) {
        assert(!terminal && plain(entry) && entry.nodeId === nid && reflected(result.firstAnswers), 'Lịch sử nhánh không hợp lệ.');
        const node = exercise.nodes[nid], edge = node.choices.find(x => x.move === entry.move);
        const at = time(entry.at);
        assert(edge && edge.reply === entry.reply && at >= previousTime && at <= updated, 'Nước hoặc thời điểm lưu không hợp lệ.');
        result.history.push({ nodeId: nid, move: edge.move, reply: edge.reply, at: iso(at) });
        previousTime = at; terminal = edge.next === null;
        if (!terminal) nid = edge.next;
      }
      assert(raw.nodeId === nid, 'Checkpoint không khớp lịch sử.');
      result.nodeId = nid; result.solved = terminal; result.updatedAt = iso(updated);
      result.stage = terminal ? 'explain' : result.history.length ? 'practice' : 'reflect';
      result.seenExplanation = raw.seenExplanation === true || terminal;
      if (result.seenExplanation && !terminal) result.assisted = true;
      result.candidate = XQ.Position.fromFen(exercise.nodes[nid].fen).legalMoves().includes(raw.candidate) ? raw.candidate : null;
      result.attempts = (Array.isArray(raw.attempts) ? raw.attempts : []).slice(-200).filter(a => plain(a) && exercise.nodes[a.nodeId] && typeof a.move === 'string' && typeof a.accepted === 'boolean').map(a => ({ nodeId: a.nodeId, move: a.move, accepted: a.accepted, at: iso(time(a.at)) }));
      if (result.failureCount || result.attempts.some(a => !a.accepted)) result.assisted = true;
      if (raw.stage === 'parked') {
        assert(!terminal && !result.history.length && nid === exercise.root && result.failureCount === 3, 'Nháp học tiếp không hợp lệ.');
        result.stage = 'parked'; result.pendingReviewAt = iso(time(raw.pendingReviewAt));
        assert(time(result.pendingReviewAt) >= updated, 'Lịch học tiếp không hợp lệ.');
      } else if (raw.stage === 'awaiting_verification') {
        assert(!terminal && raw.pendingVerification?.nodeId === nid && result.candidate && raw.pendingVerification.move === result.candidate, 'Yêu cầu kiểm chứng không hợp lệ.');
        result.stage = 'awaiting_verification'; result.pendingVerification = { nodeId: nid, move: result.candidate, at: iso(updated) };
      } else if (raw.stage === 'explain' && result.seenExplanation) result.stage = 'explain';
      if (raw.stage === 'finished') {
        assert(terminal && reflected(result.firstAnswers) && time(raw.completedAt) >= previousTime && time(raw.completedAt) <= now + 300000, 'Lượt hoàn thành không hợp lệ.');
        result.completedAt = iso(raw.completedAt); result.dueAt = iso(time(result.completedAt) + (result.assisted ? 2 : 1) * DAY); result.stage = 'finished';
      }
      return result;
    } catch { return null; }
  }
  function reveal(exercise, session, options = {}) {
    checkSession(exercise, session);
    assert(session.stage !== 'parked' && session.stage !== 'finished', 'Hãy mở lại lượt học trước.');
    assert(reflected(session.firstAnswers || session.answers) || options.assisted === true, 'Hãy tự quan sát trước lời giải.');
    const next = copy(session); next.stage = 'explain'; next.seenExplanation = true;
    if (!next.solved) next.assisted = true;
    return next;
  }
  function retry(exercise, session, options = {}) {
    checkSession(exercise, session);
    assert(['explain', 'finished'].includes(session.stage), 'Thử lại mở sau lời giải.');
    const next = create(exercise, { now: options.now, related: session.related });
    next.answers = answers(session.firstAnswers || session.answers); next.firstAnswers = reflected(next.answers) ? next.answers.slice() : null;
    next.firstCandidate = session.firstCandidate; next.assisted = true; next.seenExplanation = true;
    next.stage = next.firstAnswers ? 'practice' : 'reflect';
    return next;
  }
  function resumeParked(exercise, session, options = {}) {
    checkSession(exercise, session); assert(session.stage === 'parked', 'Không có hình chờ học tiếp.');
    const next = create(exercise, { now: options.now, related: session.related });
    next.answers = answers(session.firstAnswers || session.answers); next.firstAnswers = reflected(next.answers) ? next.answers.slice() : null;
    next.firstCandidate = session.firstCandidate; next.assisted = true;
    return next;
  }
  function finish(exercise, session, options = {}) {
    checkSession(exercise, session);
    if (session.stage === 'finished') return { session, attempt: null };
    assert(session.stage === 'explain' && session.solved && reflected(session.firstAnswers), 'Cần hoàn thành chuỗi nước và xem giải thích trước.');
    const now = time(options.now); assert(now >= time(session.updatedAt), 'Thời điểm hoàn thành quá sớm.');
    const next = copy(session); next.stage = 'finished'; next.completedAt = iso(now); next.updatedAt = iso(now);
    next.dueAt = iso(now + (next.assisted ? 2 : 1) * DAY);
    return { session: next, attempt: { id: next.id, puzzleId: exercise.id, version: exercise.version, skill: exercise.skill,
      familyId: exercise.familyId, startedAt: next.startedAt, completedAt: next.completedAt, dueAt: next.dueAt,
      answers: answers(next.firstAnswers), candidate: next.firstCandidate, success: true, assisted: next.assisted,
      firstExposure: next.firstExposure && !next.assisted, learnerDecisions: next.history.length, source: next.source,
      finalNodeId: next.nodeId, history: copy(next.history),
      verification: exercise.proof?.method || 'authored-line', reasoningGraded: false } };
  }
  function sanitizeAttempt(exercise, raw, options = {}) {
    if (!plain(raw) || raw.puzzleId !== exercise.id || raw.version !== exercise.version || raw.success !== true || !Array.isArray(raw.history)) return null;
    const restored = restore(exercise, {kind:'line-v1',id:raw.id,exerciseId:raw.puzzleId,version:raw.version,stage:'finished',nodeId:raw.finalNodeId,
      history:raw.history,answers:raw.answers,firstAnswers:raw.answers,firstCandidate:raw.candidate,assisted:raw.assisted,firstExposure:raw.firstExposure,
      startedAt:raw.startedAt,updatedAt:raw.completedAt,completedAt:raw.completedAt,seenExplanation:true,failureCount:raw.assisted?1:0,attempts:[]},options);
    if (!restored) return null;
    const pending = {...restored,stage:'explain',completedAt:null,dueAt:null};
    return finish(exercise,pending,{now:restored.completedAt}).attempt;
  }
  return Object.freeze({ DAY, validate, create, currentPosition, submit, restore, reveal, retry, resumeParked, finish, sanitizeAttempt });
});
