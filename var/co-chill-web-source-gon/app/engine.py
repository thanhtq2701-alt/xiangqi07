"""Replaceable, bounded local search; not Pikafish or a trained model."""
from functools import lru_cache
from time import monotonic
from typing import Protocol
from app.rules import Position, parse_move, side

VALUES = {'k': 0, 'r': 900, 'c': 450, 'h': 400, 'e': 200, 'a': 200, 'p': 100}
ENGINE_VERSION = 'chill-local-1.0'


class EngineAdapter(Protocol):
    def analyze(self, fen: str) -> dict: ...


def evaluate(pos):
    """Material and a small crossed-river pawn bonus, from side-to-move."""
    total = 0
    for i, p in enumerate(pos.board):
        if p == '.':
            continue
        val = VALUES[p.lower()]
        if p.lower() == 'p':
            val += 40 if (i // 9 <= 4 if side(p) == 'w' else i // 9 >= 5) else 0
        total += val if side(p) == pos.turn else -val
    return total


def ordered(pos, moves):
    return sorted(moves, key=lambda m: -VALUES.get(pos.board[parse_move(m)[1]].lower(), 0))


class LocalEngine:
    """Complete each iteration before replacing the previous result.

    Every root move uses the same depth. PVs are produced only by legal search.
    A timeout discards the whole incomplete iteration, avoiding unfair swings.
    """
    def __init__(self, max_depth=2, seconds=2.0):
        self.max_depth = max_depth
        self.seconds = seconds

    @lru_cache(maxsize=512)
    def analyze(self, fen):
        pos = Position.from_fen(fen)
        roots = ordered(pos, pos.legal_moves())
        if not roots:
            return dict(engine=ENGINE_VERSION, depth=0, score=-100000, lines=[], nodes=0, fallback=True, truncated=False)
        deadline, nodes = monotonic() + self.seconds, 0

        def search(state, depth, alpha, beta, ply):
            nonlocal nodes
            nodes += 1
            if monotonic() > deadline:
                raise TimeoutError
            moves = state.legal_moves()
            if not moves:
                return -100000 + ply, []
            if depth == 0:
                return evaluate(state), []
            best, pv = -1000000, []
            for move in ordered(state, moves):
                score, child = search(state.after_unchecked(move), depth - 1, -beta, -alpha, ply + 1)
                score = -score
                if score > best:
                    best, pv = score, [move] + child
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return best, pv

        # Always a legal bounded fallback; depth 0 is explicitly marked.
        completed = sorted([dict(move=m, score=-evaluate(pos.after_unchecked(m)), pv=[m]) for m in roots], key=lambda x: (-x['score'], x['move']))
        reached = 0
        for depth in range(1, self.max_depth + 1):
            iteration = []
            try:
                for move in roots:
                    score, pv = search(pos.after_unchecked(move), depth - 1, -1000000, 1000000, 1)
                    iteration.append(dict(move=move, score=-score, pv=[move] + pv))
            except TimeoutError:
                break
            completed = sorted(iteration, key=lambda x: (-x['score'], x['move']))
            reached = depth
        return dict(engine=ENGINE_VERSION, depth=reached, score=completed[0]['score'], lines=completed, nodes=nodes, fallback=True, truncated=reached < self.max_depth)


def validate_analysis(pos, analysis):
    legal = pos.legal_moves()
    if not analysis.get('engine') or not isinstance(analysis.get('depth'), int):
        raise ValueError('Engine metadata missing')
    if len(analysis['lines']) != len(legal) or {x['move'] for x in analysis['lines']} != set(legal):
        raise ValueError('Engine must rank every legal root move')
    for line in analysis['lines']:
        if not isinstance(line['score'], (int, float)) or not line['pv'] or line['pv'][0] != line['move']:
            raise ValueError('Invalid engine line')
        state = pos
        for move in line['pv']:
            state = state.play(move)
    return analysis
