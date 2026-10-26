(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.CC = Object.assign(root.CC || {}, api);
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // Transparent demo scheduling, not a trained or clinically validated model.
  const DAY = 86400000;
  const INTERVALS = [1, 2, 7, 14, 30];
  const STAGES = ['reflect', 'explain', 'retry', 'complete', 'summary', 'related_pending', 'parked'];
  const FORBIDDEN = new Set(['__proto__', 'prototype', 'constructor']);
  const MIN_TIME = Date.UTC(2000, 0, 1);
  const MAX_TIME = Date.UTC(2100, 0, 1);
  const MAX_HISTORY = 200;

  function plain(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  function text(value, limit) {
    return typeof value === 'string' ? value.slice(0, limit) : '';
  }

  function validId(value) {
    return typeof value === 'string' && /^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,199}$/.test(value) && !FORBIDDEN.has(value);
  }

  function move(value) {
    return typeof value === 'string' && /^[a-i][0-9][a-i][0-9]$/.test(value) ? value : null;
  }

  function time(value) {
    let number = NaN;
    if (typeof value === 'number') number = value;
    else if (value instanceof Date) number = value.getTime();
    else if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(value)) number = Date.parse(value);
    return Number.isFinite(number) && number >= MIN_TIME && number <= MAX_TIME ? number : null;
  }

  function nowValue(value) {
    const result = time(value === undefined ? Date.now() : value);
    if (result === null) throw new TypeError('A valid completion time is required.');
    return result;
  }

  function iso(value) { return new Date(value).toISOString(); }

  function safeJson(value, depth) {
    if (depth > 8) return null;
    if (value === null || typeof value === 'boolean') return value;
    if (typeof value === 'number') return Number.isFinite(value) ? value : null;
    if (typeof value === 'string') return value.slice(0, 10000);
    if (Array.isArray(value)) return value.slice(0, 500).map(item => safeJson(item, depth + 1));
    if (!plain(value)) return null;
    const result = {};
    Object.keys(value).slice(0, 100).forEach(key => {
      if (!FORBIDDEN.has(key)) result[key] = safeJson(value[key], depth + 1);
    });
    return result;
  }

  function fresh() {
    return { version: 2, records: {}, session: null, lineSession: null, lineAttempts: [], lessonViews: [], games: [], summaries: [], profile: { name: '' } };
  }

  function copyState(state) {
    return Object.assign({}, state, {
      version: 2,
      records: Object.assign({}, state.records || {}),
      games: (state.games || []).slice(),
      summaries: (state.summaries || []).slice(),
      profile: Object.assign({ name: '' }, state.profile || {})
    });
  }

  function hash(value) {
    let output = 2166136261;
    for (let i = 0; i < value.length; i += 1) output = Math.imul(output ^ value.charCodeAt(i), 16777619);
    return (output >>> 0).toString(36);
  }

  function puzzleSnapshot(puzzle) {
    if (!plain(puzzle) || !validId(puzzle.id)) return null;
    const result = { id: puzzle.id };
    if (Number.isInteger(puzzle.version) && puzzle.version > 0) result.version = puzzle.version;
    ['fen', 'skill', 'title', 'what', 'why', 'how', 'source', 'gameId'].forEach(key => {
      if (typeof puzzle[key] === 'string') result[key] = text(puzzle[key], key === 'why' || key === 'how' ? 10000 : 3000);
    });
    if (move(puzzle.solution)) result.solution = puzzle.solution;
    if (Array.isArray(puzzle.alternatives)) result.alternatives = puzzle.alternatives.map(move).filter(Boolean).slice(0, 90);
    if (Number.isInteger(puzzle.ply) && puzzle.ply >= 0 && puzzle.ply <= 10000) result.ply = puzzle.ply;
    return result;
  }

  function createSession(puzzle, options) {
    options = options || {};
    if (!plain(puzzle) || !validId(puzzle.id)) throw new TypeError('Puzzle ID is invalid.');
    const timestamp = nowValue(options.now);
    const source = text(options.source, 100) || 'practice';
    return {
      id: 's_' + hash(puzzle.id + '|' + source + '|' + String(options.related === true)) + '_' + timestamp,
      puzzleId: puzzle.id,
      puzzle: puzzleSnapshot(puzzle),
      source,
      related: options.related === true,
      firstExposure: options.firstExposure === true,
      stage: 'reflect',
      answers: ['', '', ''],
      candidate: null,
      unknown: false,
      assisted: false,
      seenExplanation: false,
      attempts: [],
      startedAt: iso(timestamp),
      completedAt: null,
      selected: null,
      submissionCount: 0,
      retryCount: 0,
      helpLevel: 0,
      helpReadyAt: 0,
      firstCandidate: null,
      firstAnswers: null,
      coachFeedback: '',
      summaryNote: '',
      summaryChecks: []
    };
  }

  function canReveal(session) {
    if (!plain(session)) return false;
    if (session.stage === 'parked') return false;
    // Legal move validation belongs to the Xiangqi rules module before submission.
    return session.unknown === true || (
      Array.isArray(session.answers) && session.answers.length === 3 &&
      session.answers.every(answer => typeof answer === 'string' && answer.trim().length > 0) &&
      move(session.candidate) !== null
    );
  }

  function reveal(session) {
    if (!canReveal(session)) throw new Error('Reflect before revealing the explanation.');
    return Object.assign({}, session, {
      answers: [0, 1, 2].map(index => text(Array.isArray(session.answers) ? session.answers[index] : '', 10000)),
      attempts: (session.attempts || []).slice(),
      stage: 'explain',
      seenExplanation: true,
      assisted: session.assisted === true || session.unknown === true
    });
  }

  function emptyRecord(puzzle) {
    return {
      puzzleId: puzzle.id,
      skill: text(puzzle.skill, 100),
      seenCount: 0,
      lastSeenAt: null,
      attempts: [],
      completionCount: 0,
      successStreak: 0,
      completedAt: null,
      dueAt: null,
      intervalDays: null
    };
  }

  function markSeen(state, puzzle, options) {
    if (!plain(puzzle) || !validId(puzzle.id)) throw new TypeError('Puzzle ID is invalid.');
    const timestamp = nowValue(options && options.now);
    const result = copyState(state);
    const previous = result.records[puzzle.id] || emptyRecord(puzzle);
    result.records[puzzle.id] = Object.assign({}, previous, {
      seenCount: Math.min(100000, (previous.seenCount || 0) + 1),
      lastSeenAt: iso(timestamp)
    });
    return result;
  }

  function schedule(previous, success, assisted) {
    const streak = success && !assisted ? Math.min(5, (previous.successStreak || 0) + 1) : 0;
    return {
      successStreak: streak,
      intervalDays: !success ? 1 : assisted ? 2 : INTERVALS[Math.max(0, streak - 1)]
    };
  }

  // Vietnam has a fixed UTC+7 offset. Tomorrow at the same local clock time
  // is exactly 24 hours later, independent of the browser's time zone.
  function nextVietnamDay(value) { return iso(nowValue(value) + DAY); }

  function reviewDueAt(record) {
    if (!plain(record)) return null;
    const dates = [time(record.dueAt), time(record.pendingReview && record.pendingReview.dueAt)].filter(value => value !== null);
    return dates.length ? iso(Math.min(...dates)) : null;
  }

  function parkPuzzle(state, session, puzzle, options) {
    options = options || {};
    if (!plain(puzzle) || !validId(puzzle.id) || !plain(session) || session.puzzleId !== puzzle.id || !validId(session.id)) {
      throw new TypeError('Pending review must match the active puzzle.');
    }
    const timestamp = nowValue(options.now);
    const previous = (state.records || {})[puzzle.id] || emptyRecord(puzzle);
    if (previous.pendingReview && previous.pendingReview.sessionId === session.id) return state;
    if (session.stage !== 'reflect' || Number(session.submissionCount) < 3 || !canReveal(session)) {
      throw new Error('Three complete unsuccessful submissions are required before parking.');
    }
    if (session.candidate === puzzle.solution || (puzzle.alternatives || []).includes(session.candidate)) {
      throw new Error('An accepted candidate must not be parked as unsuccessful.');
    }
    const started = time(session.startedAt);
    if (started === null || timestamp < started) throw new RangeError('Pending review cannot precede the session start.');
    const parked = sanitizeSession(Object.assign({}, session, {
      stage: 'parked', assisted: true, seenExplanation: false, completedAt: null
    }), timestamp);
    const result = copyState(state);
    result.records[puzzle.id] = Object.assign({}, previous, {
      seenCount: Math.max(1, previous.seenCount || 0),
      lastSeenAt: previous.lastSeenAt || session.startedAt,
      pendingReview: { status: 'incomplete', sessionId: session.id, parkedAt: iso(timestamp), dueAt: nextVietnamDay(timestamp), session: parked }
    });
    result.session = parked;
    // This is a continuation reminder, never a completed SRS attempt.
    return result;
  }

  function resumeParked(state, puzzleId, options) {
    const previous = validId(puzzleId) && (state.records || {})[puzzleId];
    const pending = previous && previous.pendingReview;
    const timestamp = nowValue(options && options.now);
    if (!pending || !pending.session || !pending.session.puzzle) throw new Error('There is no saved incomplete position to resume.');
    if (time(pending.parkedAt) === null || timestamp < time(pending.parkedAt)) throw new RangeError('Resume cannot precede the pending review.');
    const old = sanitizeSession(pending.session, timestamp);
    if (!old || old.puzzleId !== puzzleId) throw new Error('The saved incomplete position is invalid.');
    const session = createSession(old.puzzle, { now: timestamp, source: old.source, related: old.related, firstExposure: false });
    Object.assign(session, {
      answers: old.answers.slice(), candidate: old.candidate, assisted: true,
      firstAnswers: old.firstAnswers ? old.firstAnswers.slice() : old.answers.slice(),
      firstCandidate: old.firstCandidate || old.candidate,
      helpLevel: Math.max(1, old.helpLevel || 0),
      coachFeedback: 'Tiếp tục hình đang học. Bản trả lời trước vẫn được giữ; lượt này có hỗ trợ.'
    });
    const result = copyState(state);
    result.session = session;
    result.records[puzzleId] = Object.assign({}, previous, { pendingReview: Object.assign({}, pending, { status: 'in_progress' }) });
    return result;
  }

  function finishPuzzle(state, session, puzzle, options) {
    options = options || {};
    if (!plain(puzzle) || !validId(puzzle.id) || !plain(session) || session.puzzleId !== puzzle.id || !validId(session.id)) {
      throw new TypeError('Completion must match the active puzzle.');
    }
    const previous = (state.records || {})[puzzle.id] || emptyRecord(puzzle);
    // Repeated clicks or reloads must never move the original completion anchor.
    if ((previous.attempts || []).some(attempt => attempt.id === session.id)) return state;
    if (!['explain', 'retry', 'complete'].includes(session.stage) || !canReveal(session)) {
      throw new Error('Complete reflection and explanation before finishing.');
    }
    if (typeof options.success !== 'boolean') throw new TypeError('An observed move result is required.');
    const completed = nowValue(options.now);
    const started = time(session.startedAt);
    if (started === null || completed < started) throw new RangeError('Completion cannot precede the session start.');
    if (time(previous.completedAt) !== null && completed < time(previous.completedAt)) throw new RangeError('Completion cannot precede the previous review.');
    const assisted = session.assisted === true || session.unknown === true || options.assisted === true;
    const nextSchedule = schedule(previous, options.success, assisted);
    const attempt = {
      id: session.id,
      startedAt: iso(started),
      completedAt: iso(completed),
      source: text(session.source, 100),
      related: session.related === true,
      answers: session.answers.slice(0, 3).map(answer => text(answer, 10000)),
      candidate: move(session.candidate),
      firstCandidate: move(session.firstCandidate),
      firstAnswers: Array.isArray(session.firstAnswers) ? [0, 1, 2].map(index => text(session.firstAnswers[index], 1500)) : null,
      unknown: session.unknown === true,
      firstExposure: session.firstExposure === true && !assisted &&
        !(previous.attempts || []).length && (previous.seenCount || 0) <= 1 && (session.submissionCount || 0) <= 1,
      success: options.success,
      assisted,
      intervalDays: nextSchedule.intervalDays
    };
    const result = copyState(state);
    result.records[puzzle.id] = Object.assign({}, previous, nextSchedule, {
      puzzleId: puzzle.id,
      skill: text(puzzle.skill, 100),
      attempts: (previous.attempts || []).concat(attempt).slice(-MAX_HISTORY),
      completionCount: Math.min(MAX_HISTORY, (previous.attempts || []).length + 1),
      seenCount: Math.max(1, previous.seenCount || 0),
      lastSeenAt: previous.lastSeenAt || session.startedAt,
      completedAt: iso(completed),
      dueAt: iso(completed + nextSchedule.intervalDays * DAY),
      lastSuccess: options.success,
      assisted,
      learningStatus: assisted ? 'assisted' : options.success ? 'independent_move' : 'needs_practice',
      pendingReview: null
    });
    result.session = Object.assign({}, session, {
      answers: session.answers.slice(),
      attempts: (session.attempts || []).slice(),
      stage: 'complete',
      completedAt: iso(completed)
    });
    return result;
  }

  function recommend(puzzles, records, skill, excludeId) {
    records = records || {};
    const candidates = (Array.isArray(puzzles) ? puzzles : []).filter(puzzle =>
      plain(puzzle) && validId(puzzle.id) && puzzle.skill === skill && puzzle.id !== excludeId);
    if (!candidates.length) return null;
    const exposed = puzzle => Object.prototype.hasOwnProperty.call(records, puzzle.id) &&
      plain(records[puzzle.id]) && ((records[puzzle.id].seenCount || 0) > 0 || !!records[puzzle.id].lastSeenAt || !!records[puzzle.id].completedAt);
    candidates.sort((a, b) => {
      const seenDifference = Number(exposed(a)) - Number(exposed(b));
      if (seenDifference) return seenDifference;
      const aTime = time((records[a.id] || {}).lastSeenAt) || time((records[a.id] || {}).completedAt) || 0;
      const bTime = time((records[b.id] || {}).lastSeenAt) || time((records[b.id] || {}).completedAt) || 0;
      return aTime - bTime || a.id.localeCompare(b.id);
    });
    const puzzle = candidates[0];
    const unseen = !exposed(puzzle);
    return { puzzle, unseen, reason: unseen ? 'unseen_same_skill' : 'oldest_seen_same_skill' };
  }

  function summarizeSession(state, assessment, options) {
    const result = copyState(state);
    const timestamp = nowValue(options && options.now);
    const sessionId = state.session && validId(state.session.id) ? state.session.id : null;
    assessment = plain(assessment) ? assessment : {};
    const summary = {
      id: 'summary_' + (sessionId || timestamp),
      kind: 'self_report',
      sessionId,
      at: iso(timestamp),
      checks: Array.isArray(assessment.checks) ? assessment.checks.filter(value => typeof value === 'string').slice(0, 20).map(value => text(value, 200)) : [],
      note: text(assessment.note, 3000)
    };
    result.summaries = result.summaries.filter(item => item.id !== summary.id).concat(summary).slice(-200);
    // Self-report is deliberately separate from observed performance and schedules.
    return result;
  }

  function sanitizeSession(raw, now) {
    if (!plain(raw) || !validId(raw.id) || !validId(raw.puzzleId)) return null;
    const started = time(raw.startedAt);
    if (started === null || started > now + 300000) return null;
    const result = {
      id: raw.id,
      puzzleId: raw.puzzleId,
      puzzle: puzzleSnapshot(raw.puzzle),
      source: text(raw.source, 100) || 'practice',
      related: raw.related === true,
      firstExposure: raw.firstExposure === true,
      stage: STAGES.includes(raw.stage) ? raw.stage : 'reflect',
      answers: [0, 1, 2].map(index => text(Array.isArray(raw.answers) ? raw.answers[index] : '', 10000)),
      candidate: move(raw.candidate),
      unknown: raw.unknown === true,
      assisted: raw.assisted === true,
      seenExplanation: raw.seenExplanation === true,
      attempts: Array.isArray(raw.attempts) ? raw.attempts.slice(-100).map(item => safeJson(item, 0)) : [],
      startedAt: iso(started),
      completedAt: null,
      selected: typeof raw.selected === 'string' && /^[a-i][0-9]$/.test(raw.selected) ? raw.selected : null
    };
    result.submissionCount = Math.min(3, Math.max(0, Math.floor(Number(raw.submissionCount) || 0)));
    result.retryCount = Math.min(3, Math.max(0, Math.floor(Number(raw.retryCount) || 0)));
    result.helpLevel = Math.min(3, Math.max(0, Math.floor(Number(raw.helpLevel) || 0)));
    // Guidance opens immediately; migrate the old artificial countdown away.
    result.helpReadyAt = 0;
    result.firstCandidate = move(raw.firstCandidate);
    result.firstAnswers = Array.isArray(raw.firstAnswers) ? [0, 1, 2].map(index => text(raw.firstAnswers[index], 1500)) : null;
    result.coachFeedback = text(raw.coachFeedback, 1000);
    result.summaryNote = text(raw.summaryNote, 1500);
    result.summaryChecks = Array.isArray(raw.summaryChecks) ? raw.summaryChecks.filter(x => /^[0-3]$/.test(x)).slice(0, 4) : [];
    const completed = time(raw.completedAt);
    if (completed !== null && completed >= started && completed <= now + 300000) result.completedAt = iso(completed);
    if (['explain', 'retry', 'complete', 'summary'].includes(result.stage) && !canReveal(result)) result.stage = 'reflect';
    if (result.stage === 'complete' && !result.completedAt) result.stage = 'explain';
    if (raw.resumeSide === 'red' || raw.resumeSide === 'black' || raw.resumeSide === 'r' || raw.resumeSide === 'b') result.resumeSide = raw.resumeSide;
    ['relatedFrom', 'pendingPuzzleId', 'originPuzzleId'].forEach(key => { if (validId(raw[key])) result[key] = raw[key]; });
    return result;
  }

  function sanitizeRecord(id, raw, now) {
    if (!validId(id) || !plain(raw)) return null;
    const result = emptyRecord({ id, skill: raw.skill });
    const lastSeen = time(raw.lastSeenAt);
    if (lastSeen !== null && lastSeen <= now + 300000) result.lastSeenAt = iso(lastSeen);
    result.seenCount = Number.isInteger(raw.seenCount) && raw.seenCount >= 0 ? Math.min(100000, raw.seenCount) : 0;
    const seenIds = new Set();
    (Array.isArray(raw.attempts) ? raw.attempts : []).slice(-MAX_HISTORY).forEach(rawAttempt => {
      if (!plain(rawAttempt) || !validId(rawAttempt.id) || seenIds.has(rawAttempt.id) || typeof rawAttempt.success !== 'boolean') return;
      const started = time(rawAttempt.startedAt);
      const completed = time(rawAttempt.completedAt);
      if (started === null || completed === null || completed < started || completed > now + 300000) return;
      if (time(result.completedAt) !== null && completed < time(result.completedAt)) return;
      seenIds.add(rawAttempt.id);
      const assisted = rawAttempt.assisted === true || rawAttempt.unknown === true;
      const scheduleResult = schedule(result, rawAttempt.success, assisted);
      const attempt = {
        id: rawAttempt.id,
        startedAt: iso(started),
        completedAt: iso(completed),
        source: text(rawAttempt.source, 100),
        related: rawAttempt.related === true,
        answers: [0, 1, 2].map(index => text(Array.isArray(rawAttempt.answers) ? rawAttempt.answers[index] : '', 10000)),
        candidate: move(rawAttempt.candidate),
        firstCandidate: move(rawAttempt.firstCandidate),
        firstAnswers: Array.isArray(rawAttempt.firstAnswers) ? [0, 1, 2].map(index => text(rawAttempt.firstAnswers[index], 1500)) : null,
        unknown: rawAttempt.unknown === true,
        firstExposure: rawAttempt.firstExposure === true && result.attempts.length === 0 && !assisted,
        success: rawAttempt.success,
        assisted,
        intervalDays: scheduleResult.intervalDays
      };
      result.attempts.push(attempt);
      Object.assign(result, scheduleResult, {
        completedAt: iso(completed),
        dueAt: iso(completed + scheduleResult.intervalDays * DAY),
        lastSuccess: attempt.success,
        assisted,
        learningStatus: assisted ? 'assisted' : attempt.success ? 'independent_move' : 'needs_practice'
      });
    });
    result.completionCount = result.attempts.length;
    if (result.completionCount) {
      result.seenCount = Math.max(1, result.seenCount);
      result.lastSeenAt = result.lastSeenAt || result.completedAt;
    }
    if (plain(raw.pendingReview)) {
      const pending = raw.pendingReview;
      const parkedAt = time(pending.parkedAt);
      const session = sanitizeSession(pending.session, now);
      if (parkedAt !== null && parkedAt <= now + 300000 && session && session.puzzleId === id &&
          pending.sessionId === session.id && session.stage === 'parked' && session.submissionCount >= 3 &&
          session.puzzle && session.candidate !== session.puzzle.solution &&
          !(session.puzzle.alternatives || []).includes(session.candidate) &&
          (time(result.completedAt) === null || parkedAt >= time(result.completedAt))) {
        result.pendingReview = { status: pending.status === 'in_progress' ? 'in_progress' : 'incomplete',
          sessionId: session.id, parkedAt: iso(parkedAt), dueAt: nextVietnamDay(parkedAt), session };
      }
    }
    return result;
  }

  function sanitize(raw, options) {
    const result = fresh();
    if (!plain(raw) || raw.version !== 2) return result;
    const timestamp = nowValue(options && options.now);
    if (plain(raw.records)) Object.keys(raw.records).slice(0, 2000).forEach(id => {
      const record = sanitizeRecord(id, raw.records[id], timestamp);
      if (record) result.records[id] = record;
    });
    result.session = sanitizeSession(raw.session, timestamp);
    // V6 data stays inside the same per-account snapshot as legacy learning.
    // Replay accepted moves instead of trusting a saved checkpoint/completion.
    const lineApi = typeof globalThis !== 'undefined' && globalThis.CCLine ||
      (typeof module !== 'undefined' && module.exports ? require('./line-practice.js') : null);
    const curriculum = typeof globalThis !== 'undefined' && globalThis.CCCurriculum ||
      (typeof module !== 'undefined' && module.exports ? require('./curriculum.js') : null);
    if (lineApi && curriculum) {
      const exercise = raw.lineSession && curriculum.findExercise(raw.lineSession.exerciseId);
      if (exercise) result.lineSession = lineApi.restore(exercise, raw.lineSession, { now: timestamp });
      const seenAttempts = new Set();
      for (const attempt of (Array.isArray(raw.lineAttempts) ? raw.lineAttempts : []).slice(-2000)) {
        const item = attempt && curriculum.findExercise(attempt.puzzleId);
        const clean = item && lineApi.sanitizeAttempt(item, attempt, { now: timestamp });
        if (clean && !seenAttempts.has(clean.id)) { seenAttempts.add(clean.id); result.lineAttempts.push(clean); }
      }
      const seenLessons = new Set();
      result.lessonViews = (Array.isArray(raw.lessonViews) ? raw.lessonViews : []).filter(view => {
        if (!plain(view) || !curriculum.findLesson(view.id) || seenLessons.has(view.id) || time(view.at) === null || time(view.at) > timestamp + 300000) return false;
        seenLessons.add(view.id); return true;
      }).map(view => ({ id: view.id, at: iso(time(view.at)), kind: 'viewed' }));
    }
    // 200 is a display/archive boundary, not permission to erase older games.
    result.games = Array.isArray(raw.games) ? raw.games.filter(plain).map(game => safeJson(game, 0)) : [];
    result.profile.name = plain(raw.profile) ? text(raw.profile.name, 80) : '';
    if (Array.isArray(raw.summaries)) result.summaries = raw.summaries.slice(-200).filter(summary =>
      plain(summary) && validId(summary.id) && time(summary.at) !== null && time(summary.at) <= timestamp + 300000
    ).map(summary => ({
      id: summary.id,
      kind: 'self_report',
      sessionId: validId(summary.sessionId) ? summary.sessionId : null,
      at: iso(time(summary.at)),
      checks: Array.isArray(summary.checks) ? summary.checks.filter(item => typeof item === 'string').slice(0, 20).map(item => text(item, 200)) : [],
      note: text(summary.note, 3000)
    }));
    return result;
  }

  return { DAY, INTERVALS: INTERVALS.slice(), fresh, sanitize, createSession, canReveal, reveal, markSeen, finishPuzzle, recommend, summarizeSession, nextVietnamDay, reviewDueAt, parkPuzzle, resumeParked };
});
