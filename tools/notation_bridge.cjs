#!/usr/bin/env node
/* Bridge for tools/import_positions.py: turns Vietnamese notation (P2-5, M8.7,
 * Xt.1, V3.5) into board moves and back, using the same web/game-tools.js the
 * app uses. Python re-checks every move with app/rules.py afterwards.
 * stdin:  {"lines":[{"fen":"...","tokens":["P2-5","h2e2",...]}]}
 * stdout: {"lines":[{"moves":[...],"notations":[...]} | {"error":"...","ply":N}]}
 */
'use strict';
const CC = require('../web/game-tools.js');
const XQ = require('../web/xiangqi.js');

const COORD = /^[a-i][0-9][a-i][0-9]$/;

function convert(line) {
  let pos;
  try { pos = XQ.Position.fromFen(line.fen); } catch (error) { return { error: 'FEN: ' + error.message, ply: 0 }; }
  const moves = [], notations = [];
  for (let i = 0; i < line.tokens.length; i++) {
    const token = String(line.tokens[i]).trim();
    let move;
    try {
      move = COORD.test(token) ? token : CC.parseNotation(pos, token);
      notations.push(CC.notateMove(pos, move));
      pos = pos.play(move);
    } catch (error) {
      return { error: error.message, ply: i + 1, token };
    }
    moves.push(move);
  }
  return { moves, notations };
}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  const request = JSON.parse(input);
  process.stdout.write(JSON.stringify({ lines: request.lines.map(convert) }));
});
