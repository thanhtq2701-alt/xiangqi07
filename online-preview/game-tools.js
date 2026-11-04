/* Vietnamese notation and conservative game adjudication for Cờ Chill.
 * Legal moves always come from XQ; notation cannot invent a legal move.
 * This is not a complete tournament arbiter. See docs/RULES_UIUX_2026_10_15.md.
 */
(function (root, factory) {
  'use strict';
  const rules = typeof module !== 'undefined' && module.exports ? require('./xiangqi.js') : root.XQ;
  const api = factory(rules);
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CC = Object.assign(root.CC || {}, api);
})(typeof globalThis !== 'undefined' ? globalThis : this, function (XQ) {
  'use strict';
  const CODES = Object.freeze({ k: 'Tg', a: 'S', e: 'V', r: 'X', h: 'M', c: 'P', p: 'B' });
  const position = value => typeof value === 'string' ? XQ.Position.fromFen(value) : value;
  const file = (index, side) => side === 'w' ? 9 - index % 9 : index % 9 + 1;

  function parts(pos, move) {
    const [src, dst] = XQ.parseMove(move), piece = pos.board[src], kind = piece.toLowerCase(), side = XQ.side(piece);
    const sy = Math.floor(src / 9), dy = Math.floor(dst / 9), from = file(src, side), to = file(dst, side);
    const direction = sy === dy ? '-' : ((side === 'w' ? dy < sy : dy > sy) ? '.' : '/');
    const end = direction === '-' || 'aeh'.includes(kind) ? to : Math.abs(dy - sy);
    const peers = [];
    pos.board.forEach((p, i) => { if (p === piece && i % 9 === src % 9) peers.push(i); });
    peers.sort((a, b) => side === 'w' ? a - b : b - a);
    const ordinal = peers.indexOf(src), code = CODES[kind];
    if (!code) throw new Error('Ô xuất phát không có quân cờ.');
    let head = code + from;
    if (peers.length > 1) {
      const duplicateFiles = new Set();
      pos.board.forEach((p, i) => {
        if (p === piece && pos.board.some((q, j) => j !== i && q === p && j % 9 === i % 9)) duplicateFiles.add(i % 9);
      });
      // Owner's convention (2026-11-04): counted from the moving side. Two on a file are t/s,
      // three are t/g/s, four or five are numbered from the front. A file number goes first
      // when two files both have stacks.
      if (peers.length >= 4) {
        // A lone pawn on file 2 would also read B2.1, so a colliding stack keeps its file: B92.1.
        const collides = pos.board.some((p, i) => p === piece && i % 9 !== src % 9 && file(i, side) <= peers.length);
        head = code + (collides ? from : '') + (ordinal + 1);
      } else {
        const label = peers.length === 2 ? 'ts'[ordinal] : 'tgs'[ordinal];
        head = code + (duplicateFiles.size > 1 ? from : '') + label;
      }
    }
    return { src, dst, code, from, direction, end, head, peers, ordinal };
  }

  function notateMove(value, move) {
    const pos = position(value);
    if (!pos.legalMoves().includes(move)) throw new Error(illegalMoveReason(pos, move));
    const p = parts(pos, move);
    return p.head + p.direction + p.end;
  }

  function parseNotation(value, text) {
    const pos = position(value), input = String(text || '').trim().toLowerCase();
    let unclear = false;
    for (const move of pos.legalMoves()) {
      const p = parts(pos, move);
      if ((p.head + p.direction + p.end).toLowerCase() === input) return move;
      if (p.peers.length > 1 && (p.code + p.from + p.direction + p.end).toLowerCase() === input) unclear = true;
    }
    if (unclear) throw new Error('Ký pháp chưa rõ quân nào: hai quân cùng cột phải ghi t (trước) hoặc s (sau), ví dụ Xt.1.');
    throw new Error('Không có nước hợp lệ khớp ký pháp này. Ví dụ P2-5, M8.7, Xt.1. Tượng ghi là V.');
  }

  // Reviews saved before 2026-11-04 store moves as "Xe a2 → a7 ăn Pháo". Replay them from the
  // saved position so stored text never shows machine coordinates.
  const SAVED_MOVE = /(Tướng|Sĩ|Tượng|Xe|Pháo|Mã|Tốt) ([a-i]\d) → ([a-i]\d)(?: ăn (?:Tướng|Sĩ|Tượng|Xe|Pháo|Mã|Tốt))?/g;
  function notateSavedText(fen, text) {
    if (typeof text !== 'string' || !text.includes('→')) return text;
    let pos = null;
    try { pos = position(fen); } catch { pos = null; }
    return text.replace(SAVED_MOVE, (whole, name, from, to) => {
      try {
        const notation = notateMove(pos, from + to);
        pos = pos.play(from + to);
        return notation;
      } catch { pos = null; return name; }
    });
  }

  function parseGameNotation(initialFen, text, maxPlies = 200) {
    if (typeof text !== 'string' || text.length > 20000) throw new Error('Biên bản quá dài hoặc không hợp lệ.');
    const bound = Math.max(1, Math.min(2000, Number.isInteger(maxPlies) ? maxPlies : 200));
    // Strip only numbered-list prefixes. A dot inside a move is an advance.
    let remaining = text.toLowerCase().replace(/(^|[\s,;|])\d+\s*[.)](?:\.\.)?/g, '$1').trim();
    let pos = position(initialFen), moves = [], positions = [pos.fen()];
    const token = /^(?:tg|[svxmpb])[1-9]{0,2}[tsg]?[.\/-][1-9](?=$|[\s,;|])/;
    while (remaining) {
      const match = remaining.match(token);
      if (!match) throw new Error('Không đọc được biên bản ở nửa nước ' + (moves.length + 1) + '. Chỉ nhận ký pháp chuẩn, ví dụ P2-5, M8.7, Xt.1; Tượng ghi là V. Chưa hỗ trợ chú thích xen trong ván.');
      if (moves.length >= bound) throw new Error('Bản thử giới hạn ' + bound + ' nửa nước khi nhập.');
      let move;
      try { move = parseNotation(pos, match[0]); } catch (error) { throw new Error('Nửa nước ' + (moves.length + 1) + ': ' + error.message); }
      pos = pos.play(move); moves.push(move); positions.push(pos.fen());
      remaining = remaining.slice(match[0].length).replace(/^[\s,;|]+/, '');
    }
    return { moves, positions };
  }

  function pairMoveHistory(initialFen, history) {
    let pos = position(initialFen), rows = [], number = 1;
    for (let index = 0; index < history.length; index++) {
      const move = typeof history[index] === 'string' ? history[index] : history[index].move;
      if (!rows.length || pos.turn === 'w') rows.push({ number, red: null, black: null });
      const entry = { move, notation: notateMove(pos, move), ply: index, before: pos.fen(), side: pos.turn };
      rows[rows.length - 1][pos.turn === 'w' ? 'red' : 'black'] = entry;
      if (pos.turn === 'b') number++;
      pos = pos.play(move);
    }
    return rows;
  }

  function between(pos, src, dst) {
    const sx = src % 9, sy = Math.floor(src / 9), dx = dst % 9, dy = Math.floor(dst / 9);
    if (sx !== dx && sy !== dy) return null;
    const step = sx === dx ? (dy > sy ? 9 : -9) : (dx > sx ? 1 : -1);
    let count = 0;
    for (let i = src + step; i !== dst; i += step) if (pos.board[i] !== '.') count++;
    return count;
  }

  function illegalMoveReason(value, move) {
    const pos = position(value);
    let src, dst;
    try { [src, dst] = XQ.parseMove(move); } catch { return 'Nước đi không hợp lệ.'; }
    const piece = pos.board[src], target = pos.board[dst];
    if (piece === '.') return 'Ô xuất phát không có quân.';
    if (XQ.side(piece) !== pos.turn) return 'Chưa đến lượt bên có quân này.';
    if (src === dst) return 'Quân cờ cần đi sang một ô khác.';
    if (target !== '.' && XQ.side(piece) === XQ.side(target)) return 'Ô đích đang có quân cùng bên.';
    const sx = src % 9, sy = Math.floor(src / 9), tx = dst % 9, ty = Math.floor(dst / 9);
    const ax = Math.abs(tx - sx), ay = Math.abs(ty - sy), red = pos.turn === 'w', kind = piece.toLowerCase();
    if (kind === 'k' || kind === 'a') {
      if (tx < 3 || tx > 5 || (red ? ty < 7 : ty > 2)) return XQ.NAMES[kind] + ' phải ở trong cung.';
      if (kind === 'k' && ax + ay !== 1) return 'Tướng đi một ô ngang hoặc dọc.';
      if (kind === 'a' && (ax !== 1 || ay !== 1)) return 'Sĩ đi chéo một ô trong cung.';
    } else if (kind === 'e') {
      if (red ? ty < 5 : ty > 4) return 'Tượng không được qua sông.';
      if (ax !== 2 || ay !== 2) return 'Tượng đi chéo hai ô.';
      if (pos.board[(sy + ty) / 2 * 9 + (sx + tx) / 2] !== '.') return 'Tượng bị cản mắt ở giữa đường chéo.';
    } else if (kind === 'h') {
      if (!((ax === 2 && ay === 1) || (ax === 1 && ay === 2))) return 'Mã đi một ô theo một hướng và hai ô theo hướng vuông góc.';
      const leg = (sy + (ay === 2 ? (ty - sy) / 2 : 0)) * 9 + sx + (ax === 2 ? (tx - sx) / 2 : 0);
      if (pos.board[leg] !== '.') return 'Mã bị cản chân bởi một quân đứng sát ở hướng đi dài.';
    } else if (kind === 'r' || kind === 'c') {
      if (ax && ay) return XQ.NAMES[kind] + ' chỉ đi ngang hoặc dọc.';
      const count = between(pos, src, dst);
      if (kind === 'r' && count) return 'Xe không được nhảy qua quân cản.';
      if (kind === 'c' && target === '.' && count) return 'Pháo không ăn quân thì không được nhảy qua quân cản.';
      if (kind === 'c' && target !== '.' && count !== 1) return 'Pháo ăn quân cần đúng một quân ngòi; đường này có ' + count + ' quân ngòi.';
    } else if (kind === 'p') {
      if (red ? ty > sy : ty < sy) return 'Tốt không được đi lùi.';
      if (ax + ay !== 1) return 'Tốt đi đúng một ô mỗi lượt.';
      if (ax && (red ? sy > 4 : sy < 5)) return 'Tốt chưa qua sông chưa được đi ngang.';
    }
    if (target.toLowerCase() === 'k') return 'Không đi nước bắt Tướng trực tiếp; ván kết thúc khi chiếu hết hoặc hết nước hợp lệ.';
    if (!pos.targets(src).includes(dst)) return 'Nước đi không đúng quy tắc di chuyển của quân này.';
    const after = pos.afterUnchecked(move), w = after.board.indexOf('K'), b = after.board.indexOf('k');
    if (w % 9 === b % 9 && between(after, w, b) === 0) return 'Nước này làm hai Tướng đối mặt trên một lộ trống.';
    if (after.inCheck(pos.turn)) return 'Nước này để Tướng của bạn vẫn bị chiếu hoặc tự đưa Tướng vào đường chiếu.';
    return '';
  }

  function gameTimeline(initialFen, history) {
    let pos = position(initialFen), quietPlies = 0;
    const positions = [pos], moves = [];
    for (const entry of history) {
      const move = typeof entry === 'string' ? entry : entry.move;
      const [, dst] = XQ.parseMove(move), capture = pos.board[dst] !== '.';
      const after = pos.play(move);
      quietPlies = capture ? 0 : quietPlies + 1;
      moves.push({ move, side: pos.turn, check: after.inCheck(after.turn), capture });
      positions.push(after); pos = after;
    }
    return { positions, moves, quietPlies };
  }

  function repetitionStatus(initialFen, history) {
    const timeline = gameTimeline(initialFen, history), { positions, moves, quietPlies } = timeline;
    const current = positions[positions.length - 1], key = current.fen();
    const matching = positions.flatMap((p, i) => p.fen() === key ? [i] : []);
    const base = { over: false, winner: null, reason: '', needsVerification: false, code: 'none', occurrences: matching.length, quietPlies };
    const status = current.status();
    if (status.over) return { ...base, ...status, code: 'terminal-position' };
    if (matching.length >= 4) {
      const start = matching[matching.length - 4], cycle = moves.slice(start), allCheck = side => {
        const own = cycle.filter(m => m.side === side);
        return own.length > 0 && own.every(m => m.check);
      };
      const red = allCheck('w'), black = allCheck('b');
      if (red !== black) return { ...base, over: true, winner: red ? 'b' : 'w', code: 'perpetual-check', reason: (red ? 'Đỏ' : 'Đen') + ' thua do chiếu liên tục một bên trong chu kỳ lặp bốn lần.' };
      if (red && black) return { ...base, needsVerification: true, code: 'mutual-check-review', reason: 'Hai bên cùng chiếu trong chu kỳ lặp bốn lần: cần kiểm chứng phán quyết, chưa tính thắng/thua.' };
      // Treat any possible capture threat by either player as uncertain chase.
      // This intentionally has false positives instead of wrongly declaring a draw.
      let possibleChase = false;
      for (const p of positions.slice(start)) {
        for (const side of ['w', 'b']) {
          const turn = new XQ.Position(p.board, side);
          if (turn.legalMoves().some(m => p.board[XQ.index(m.slice(2))] !== '.')) possibleChase = true;
        }
        if (possibleChase) break;
      }
      if (cycle.some(m => m.check) || possibleChase) return { ...base, needsVerification: true, code: 'repetition-review', reason: 'Thế cờ lặp bốn lần có tình huống chiếu hoặc bắt quân cần kiểm chứng; chưa tự xử hòa hoặc xử thua.' };
      return { ...base, over: true, code: 'quiet-repetition', reason: 'Hòa: thế cờ và lượt đi lặp bốn lần, không có chiếu hoặc nước bắt quân hợp lệ trong chu kỳ kiểm tra.' };
    }
    if (quietPlies >= 100) return { ...base, needsVerification: true, code: 'natural-movecount-review', reason: 'Đã có ít nhất 50 nước mỗi bên không bắt quân. Cần kiểm chứng cách đếm và điều kiện hòa; chưa tự tính kết quả.' };
    if (matching.length === 3) return { ...base, code: 'repetition-warning', reason: 'Thế cờ và lượt đi đã xuất hiện ba lần. Chưa tính kết quả; chu kỳ được kiểm tra lại nếu lặp lần thứ tư.' };
    return base;
  }

  return Object.freeze({ notateMove, parseNotation, notateSavedText, parseGameNotation, pairMoveHistory, illegalMoveReason, repetitionStatus });
});
