/* Cờ Chill browser rules and bounded local search.
 * Port of app/rules.py and app/engine.py; parity-tested against those sources.
 * Coordinates a0..i9, board top-down. No tournament repetition/chase adjudication.
 * Local material search only: not Pikafish, an LLM, or a trained model.
 */
(function (root) {
  'use strict';

  const START_FEN = 'rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w';
  const NAMES = Object.freeze({ k: 'Tướng', a: 'Sĩ', e: 'Tượng', r: 'Xe', h: 'Mã', c: 'Pháo', p: 'Tốt' });
  const VALUES = Object.freeze({ k: 0, r: 900, c: 450, h: 400, e: 200, a: 200, p: 100 });
  const ENGINE_VERSION = 'chill-browser-local-1.0';
  const ELEPHANT_POINTS = {
    w: new Set(['2,9', '6,9', '0,7', '4,7', '8,7', '2,5', '6,5']),
    b: new Set(['2,0', '6,0', '0,2', '4,2', '8,2', '2,4', '6,4'])
  };

  function side(piece) { return piece !== piece.toLowerCase() ? 'w' : 'b'; }
  function other(turn) { return turn === 'w' ? 'b' : 'w'; }
  function square(i) { return String.fromCharCode(97 + i % 9) + (9 - Math.floor(i / 9)); }
  function index(sq) {
    if (typeof sq !== 'string' || !/^[a-i][0-9]$/.test(sq)) throw new Error('Ô cờ phải có dạng a0 đến i9.');
    return (9 - Number(sq[1])) * 9 + sq.charCodeAt(0) - 97;
  }
  function parseMove(move) {
    if (typeof move !== 'string' || move.length !== 4) throw new Error('Nước đi phải có dạng a0a1.');
    return [index(move.slice(0, 2)), index(move.slice(2))];
  }

  class Position {
    constructor(board, turn = 'w') {
      if (!Array.isArray(board) || board.length !== 90 || !['w', 'b'].includes(turn)) throw new Error('Bàn cờ không hợp lệ.');
      this.board = Object.freeze(board.slice());
      this.turn = turn;
    }

    static fromFen(fen) {
      if (typeof fen !== 'string' || fen.length > 200) throw new Error('FEN không hợp lệ.');
      const fields = fen.trim().split(/\s+/);
      if (![2, 6].includes(fields.length) || !['w', 'b'].includes(fields[1])) throw new Error('FEN cần bàn cờ và lượt w hoặc b.');
      const ranks = fields[0].split('/');
      if (ranks.length !== 10) throw new Error('FEN cần đúng 10 hàng.');
      const board = [], aliases = { n: 'h', N: 'H', b: 'e', B: 'E' };
      for (const rank of ranks) {
        const row = [];
        for (let piece of rank) {
          piece = aliases[piece] || piece;
          if (/^[1-9]$/.test(piece)) row.push(...Array(Number(piece)).fill('.'));
          else if ('rheakcpRHEAKCP'.includes(piece)) row.push(piece);
          else throw new Error('Ký hiệu FEN không hợp lệ.');
        }
        if (row.length !== 9) throw new Error('Mỗi hàng FEN cần đúng 9 ô.');
        board.push(...row);
      }
      const pos = new Position(board, fields[1]);
      for (const color of ['w', 'b']) {
        for (const [kind, maximum] of Object.entries({ k: 1, r: 2, h: 2, c: 2, a: 2, e: 2, p: 5 })) {
          const piece = color === 'w' ? kind.toUpperCase() : kind;
          const count = board.filter(p => p === piece).length;
          if (count > maximum || (kind === 'k' && count !== 1)) throw new Error('Số quân không hợp lệ; mỗi bên cần một Tướng.');
        }
      }
      board.forEach((piece, i) => {
        if (piece === '.') return;
        const x = i % 9, y = Math.floor(i / 9), color = side(piece), red = color === 'w', kind = piece.toLowerCase();
        if (['k', 'a'].includes(kind) && !(x >= 3 && x <= 5 && (red ? y >= 7 && y <= 9 : y >= 0 && y <= 2))) {
          throw new Error('Tướng và Sĩ phải ở trong cung.');
        }
        if (kind === 'a' && (x + y) % 2 !== (red ? 0 : 1)) throw new Error('Sĩ không ở điểm hợp lệ trong cung.');
        if (kind === 'e' && !ELEPHANT_POINTS[color].has(x + ',' + y)) throw new Error('Tượng không ở điểm hợp lệ bên mình.');
        if (kind === 'p' && ((red && y > 6) || (!red && y < 3) || ((red ? y >= 5 : y <= 4) && x % 2))) {
          throw new Error('Tốt chưa qua sông phải nằm trên lộ xuất phát.');
        }
      });
      if (pos.inCheck(other(pos.turn))) throw new Error('FEN không hợp lệ: bên vừa đi vẫn bị chiếu hoặc hai Tướng đối mặt.');
      return pos;
    }

    fen() {
      const ranks = [];
      for (let y = 0; y < 10; y++) {
        let row = '', empty = 0;
        for (const piece of this.board.slice(y * 9, y * 9 + 9)) {
          if (piece === '.') empty++;
          else { row += (empty ? String(empty) : '') + piece; empty = 0; }
        }
        ranks.push(row + (empty ? String(empty) : ''));
      }
      return ranks.join('/') + ' ' + this.turn;
    }

    targets(src) {
      if (!Number.isInteger(src) || src < 0 || src >= 90) return [];
      const p = this.board[src];
      if (p === '.') return [];
      const x = src % 9, y = Math.floor(src / 9), red = side(p) === 'w', kind = p.toLowerCase(), result = [];
      const add = (tx, ty) => {
        if (tx >= 0 && tx < 9 && ty >= 0 && ty < 10) {
          const dest = ty * 9 + tx;
          if (this.board[dest] === '.' || side(this.board[dest]) !== side(p)) result.push(dest);
        }
      };
      if (kind === 'r' || kind === 'c') {
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          let tx = x + dx, ty = y + dy, screen = false;
          while (tx >= 0 && tx < 9 && ty >= 0 && ty < 10) {
            const occupied = this.board[ty * 9 + tx] !== '.';
            if (!screen) {
              if (!occupied) add(tx, ty);
              else if (kind === 'r') { add(tx, ty); break; }
              else screen = true;
            } else if (occupied) { add(tx, ty); break; }
            tx += dx; ty += dy;
          }
        }
      } else if (kind === 'h') {
        for (const [dx, dy] of [[1, 2], [-1, 2], [1, -2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]) {
          const lx = x + (Math.abs(dx) === 2 ? dx / 2 : 0), ly = y + (Math.abs(dy) === 2 ? dy / 2 : 0);
          if (lx >= 0 && lx < 9 && ly >= 0 && ly < 10 && this.board[ly * 9 + lx] === '.') add(x + dx, y + dy);
        }
      } else if (kind === 'e') {
        for (const [dx, dy] of [[2, 2], [2, -2], [-2, 2], [-2, -2]]) {
          const tx = x + dx, ty = y + dy;
          if (tx >= 0 && tx < 9 && ty >= 0 && ty < 10 && (red ? ty >= 5 : ty <= 4) && this.board[(y + dy / 2) * 9 + x + dx / 2] === '.') add(tx, ty);
        }
      } else if (kind === 'k' || kind === 'a') {
        const steps = kind === 'k' ? [[1, 0], [-1, 0], [0, 1], [0, -1]] : [[1, 1], [1, -1], [-1, 1], [-1, -1]];
        for (const [dx, dy] of steps) {
          const tx = x + dx, ty = y + dy;
          if (tx >= 3 && tx <= 5 && (red ? ty >= 7 && ty <= 9 : ty >= 0 && ty <= 2)) add(tx, ty);
        }
        if (kind === 'k') {
          for (const dy of [-1, 1]) {
            let ty = y + dy;
            while (ty >= 0 && ty < 10) {
              const q = this.board[ty * 9 + x];
              if (q !== '.') { if (q.toLowerCase() === 'k' && side(q) !== side(p)) add(x, ty); break; }
              ty += dy;
            }
          }
        }
      } else if (kind === 'p') {
        add(x, red ? y - 1 : y + 1);
        if (red ? y <= 4 : y >= 5) { add(x - 1, y); add(x + 1, y); }
      }
      return result;
    }

    inCheck(color = this.turn) {
      const king = this.board.indexOf(color === 'w' ? 'K' : 'k');
      if (king === -1) return true;
      return this.board.some((piece, i) => piece !== '.' && side(piece) !== color && this.targets(i).includes(king));
    }

    afterUnchecked(move) {
      const [src, dst] = parseMove(move), board = this.board.slice();
      board[dst] = board[src]; board[src] = '.';
      return new Position(board, other(this.turn));
    }

    legalMoves() {
      const moves = [];
      this.board.forEach((p, src) => {
        if (p === '.' || side(p) !== this.turn) return;
        for (const dst of this.targets(src)) {
          if (this.board[dst].toLowerCase() === 'k') continue;
          const move = square(src) + square(dst);
          if (!this.afterUnchecked(move).inCheck(this.turn)) moves.push(move);
        }
      });
      return moves;
    }

    play(move) {
      parseMove(move);
      if (!this.legalMoves().includes(move)) throw new Error('Nước đi không hợp lệ. Hãy kiểm tra luật và an toàn của Tướng.');
      return this.afterUnchecked(move);
    }

    status() {
      if (!this.legalMoves().length) return { over: true, winner: other(this.turn), reason: this.inCheck() ? 'Chiếu hết' : 'Hết nước hợp lệ (thua theo luật cờ tướng)' };
      return { over: false, winner: null, reason: this.inCheck() ? 'Đang bị chiếu' : 'Đang chơi' };
    }
  }

  function describe(pos, move) {
    const [src, dst] = parseMove(move), piece = pos.board[src], captured = pos.board[dst];
    if (piece === '.') throw new Error('Ô xuất phát không có quân.');
    return NAMES[piece.toLowerCase()] + ' ' + square(src) + ' → ' + square(dst) + (captured !== '.' ? ' ăn ' + NAMES[captured.toLowerCase()] : '');
  }

  function evaluate(pos) {
    let total = 0;
    pos.board.forEach((piece, i) => {
      if (piece === '.') return;
      let value = VALUES[piece.toLowerCase()];
      if (piece.toLowerCase() === 'p' && (side(piece) === 'w' ? Math.floor(i / 9) <= 4 : Math.floor(i / 9) >= 5)) value += 40;
      total += side(piece) === pos.turn ? value : -value;
    });
    return total;
  }

  function ordered(pos, moves) {
    return moves.slice().sort((a, b) => (VALUES[pos.board[index(b.slice(2))].toLowerCase()] || 0) - (VALUES[pos.board[index(a.slice(2))].toLowerCase()] || 0));
  }
  function rank(lines) { return lines.sort((a, b) => b.score - a.score || (a.move < b.move ? -1 : a.move > b.move ? 1 : 0)); }

  // Iterative search keeps only fully completed root rankings. A timeout never
  // compares partially searched moves or labels a static score as depth 1/2.
  function analyze(position, options = {}) {
    const pos = typeof position === 'string' ? Position.fromFen(position) : position;
    const requestedDepth = options.depth === 1 ? 1 : 2;
    const maxMs = Number.isFinite(options.maxMs) ? Math.max(0, options.maxMs) : 400;
    const now = () => typeof performance !== 'undefined' ? performance.now() : Date.now();
    const deadline = now() + maxMs, roots = ordered(pos, pos.legalMoves());
    let nodes = 0;
    if (!roots.length) return { engine: ENGINE_VERSION, bestMove: null, score: -100000, ranked: [], depth: 0, requestedDepth, complete: true, truncated: false, fallback: true, nodes };
    const timeout = {};
    function search(state, depth, alpha, beta, ply) {
      nodes++;
      if (now() >= deadline) throw timeout;
      const moves = state.legalMoves();
      if (!moves.length) return { score: -100000 + ply, pv: [] };
      if (depth === 0) return { score: evaluate(state), pv: [] };
      let best = -1000000, pv = [];
      for (const move of ordered(state, moves)) {
        const child = search(state.afterUnchecked(move), depth - 1, -beta, -alpha, ply + 1), score = -child.score;
        if (score > best) { best = score; pv = [move, ...child.pv]; }
        alpha = Math.max(alpha, score);
        if (alpha >= beta) break;
      }
      return { score: best, pv };
    }
    let completed = rank(roots.map(move => ({ move, score: -evaluate(pos.afterUnchecked(move)), pv: [move] }))), reached = 0;
    for (let depth = 1; depth <= requestedDepth; depth++) {
      const iteration = [];
      try {
        for (const move of roots) {
          const child = search(pos.afterUnchecked(move), depth - 1, -1000000, 1000000, 1);
          iteration.push({ move, score: -child.score, pv: [move, ...child.pv] });
        }
      } catch (error) { if (error !== timeout) throw error; break; }
      completed = rank(iteration); reached = depth;
    }
    return { engine: ENGINE_VERSION, bestMove: completed[0].move, score: completed[0].score, ranked: completed, depth: reached, requestedDepth, complete: reached === requestedDepth, truncated: reached < requestedDepth, fallback: true, nodes };
  }

  const api = Object.freeze({ START_FEN, NAMES, VALUES, ENGINE_VERSION, Position, side, other, square, index, parseMove, describe, evaluate, analyze });
  root.XQ = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : window);
