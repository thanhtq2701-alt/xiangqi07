"""Optional, bounded UCI engine integration; local search is always labelled.

This adapter does not replace ``engine.validate_analysis``: MultiPV is a shortlist,
not an exhaustive ranking of legal root moves. All scores are from the player to
move in the final input position, including the separately searched selected move.
No executable, network, or model weights are downloaded by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import atexit
import math
import os
from pathlib import Path
import queue
import random
import re
import subprocess
import threading
from time import monotonic
from typing import Mapping

from app.engine import ENGINE_VERSION, LocalEngine
from app.rules import Position, parse_move

ADAPTER_VERSION = 'co-chill-uci-1'
MAX_HISTORY = 600
MAX_PV = 20  # Half-moves shown to learners, not full move pairs.
MAX_ENGINE_PV = 128
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_LINE_BYTES = 16384
MOVE_RE = re.compile(r'^[a-i][0-9][a-i][0-9]$')
# Who waits first for the single engine: a learner waiting for the bot's move,
# then someone reading an analysis, then a whole-game scan (docs/BOT_LEVELS.md §4).
PRIORITY = {'bot': 0, 'review': 1, 'practice': 1, 'review-scan': 2}


# Bot levels (docs/BOT_LEVELS.md §3; starting values, NOT calibrated, no Elo).
# level: (nodes or None for the full-strength quick search, MultiPV, temperature in cp
#         (0 = uniform choice, None = always the best line), largest loss allowed in cp)
BOT_LEVELS = {
    1: (2000, 5, 0, 400),
    2: (5000, 5, 0, 300),
    3: (10000, 4, 150, 250),
    # 4–6 softened on 21/11/2026 after the owner's first games: 2–3 felt right, 4 too strong.
    4: (15000, 4, 120, 200),
    5: (30000, 4, 100, 150),
    6: (100000, 3, 60, 100),
    7: (None, 1, None, 0),
}
LEVEL_TIME_CAP_MS = 3000   # a node-limited search never runs longer than this
MATE_VALUE = 30000
LEVEL_ONE_MISSES_MATE = 0.5  # owner decision 21/11/2026: only level 1 may miss a mate in one


def _value(candidate):
    """Comparable value for the side to move: mates beat any centipawn score, faster mates more."""
    if candidate['score_type'] == 'mate':
        n = candidate['score']
        return MATE_VALUE - abs(n) if n > 0 else -MATE_VALUE + abs(n)
    return candidate['score']


def immediate_mates(state):
    """Legal moves that checkmate at once, proven by the rules (not by the engine)."""
    mates = []
    for move in state.legal_moves():
        after = state.after_unchecked(move)   # already legal: no second legality check
        if after.in_check() and not after.legal_moves():
            mates.append(move)
    return mates


def choose_level_move(candidates, level, rng, avoid=()):
    """Pick the bot's move among the engine's MultiPV lines for this level.

    Lines worse than the best by more than the level's cap are dropped; the rest are
    chosen uniformly (temperature 0) or with softmax weights exp(-(loss)/T). Returns
    (candidate, rank starting at 1, loss in cp). `avoid` lists moves to skip when
    another line is available (level 1 passing over a mate in one).
    """
    _nodes, _multipv, temperature, cap = BOT_LEVELS[level]
    pool = [c for c in candidates if c['move'] not in avoid] or list(candidates)
    best = max(_value(c) for c in pool)
    pool = [c for c in pool if best - _value(c) <= cap] if temperature is not None else [max(pool, key=_value)]
    if temperature:
        weights = [math.exp(-(best - _value(c)) / temperature) for c in pool]
    else:
        weights = [1.0] * len(pool)
    chosen = rng.choices(pool, weights=weights, k=1)[0]
    rank = next(i for i, c in enumerate(candidates, 1) if c['move'] == chosen['move'])
    return chosen, rank, best - _value(chosen)


class _Ticket:
    def __init__(self, priority, seq, owner, estimate):
        self.priority, self.seq, self.owner, self.estimate, self.started = priority, seq, owner, estimate, None


class _EngineQueue:
    """One search at a time on the VM's spare CPU, in priority order.

    A request that cannot finish before its deadline (queue wait + own search) is
    refused at once with 'busy' instead of waiting in vain; each owner may have one
    request queued or running; at most `limit` wait.
    """

    def __init__(self, limit=8):
        self.cond, self.waiting, self.running, self.limit, self.seq = threading.Condition(), [], None, limit, 0

    def snapshot(self):
        with self.cond:
            return {'waiting': len(self.waiting), 'running': self.running is not None, 'limit': self.limit}

    def enter(self, priority, owner, estimate, deadline):
        with self.cond:
            if owner is not None and (any(t.owner == owner for t in self.waiting)
                                      or (self.running is not None and self.running.owner == owner)):
                raise EngineUnavailable('busy')
            if len(self.waiting) >= self.limit:
                raise EngineUnavailable('busy')
            now = monotonic()
            running_left = max(0.0, self.running.started + self.running.estimate - now) if self.running else 0.0
            ahead = sum(t.estimate for t in self.waiting if t.priority <= priority)
            if now + running_left + ahead + estimate > deadline:
                raise EngineUnavailable('busy')
            self.seq += 1
            ticket = _Ticket(priority, self.seq, owner, estimate)
            self.waiting.append(ticket)
            while True:
                head = min(self.waiting, key=lambda t: (t.priority, t.seq))
                if self.running is None and head is ticket:
                    break
                latest_start = deadline - estimate - monotonic()
                if latest_start <= 0:
                    self.waiting.remove(ticket)
                    self.cond.notify_all()
                    raise EngineUnavailable('busy')
                self.cond.wait(timeout=latest_start)
            self.waiting.remove(ticket)
            ticket.started = monotonic()
            self.running = ticket
            return ticket

    def leave(self, ticket):
        with self.cond:
            if self.running is ticket:
                self.running = None
            self.cond.notify_all()


_QUEUE = _EngineQueue()


class EngineUnavailable(RuntimeError):
    """A safe reason code, never a child process log or local file path."""


def _env_int(env, name, default, minimum, maximum):
    try:
        return max(minimum, min(maximum, int(env.get(name, default))))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class EngineConfig:
    # Constructor command injection is only for trusted application/test code.
    # HTTP input must never populate command, path, cwd or environment settings.
    command: tuple[str, ...] = ()
    nnue_path: str = ''
    quick_ms: int = 600
    deep_ms: int = 2000
    handshake_seconds: float = 2.0
    # Starting a process loads the ~50 MB NNUE network (Pikafish reads pikafish.nnue from
    # its folder before answering uci, then EvalFile): 1-6 s measured on a busy laptop
    # (21/11/2026), so 2 s timed out many restarts. Still capped by the request deadline.
    startup_seconds: float = 8.0
    request_seconds: float = 10.0
    multipv: int = 3
    threads: int = 1
    hash_mb: int = 32
    # Restart the long-lived process after this many searches (no swap on the VM).
    max_searches: int = 500

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None):
        env = os.environ if env is None else env
        path = env.get('PIKAFISH_PATH', '').strip()
        return cls(
            command=(path,) if path else (),
            nnue_path=env.get('PIKAFISH_NNUE_PATH', '').strip(),
            quick_ms=_env_int(env, 'PIKAFISH_QUICK_MS', 600, 50, 3000),
            deep_ms=_env_int(env, 'PIKAFISH_DEEP_MS', 2000, 100, 5000),
            threads=_env_int(env, 'PIKAFISH_THREADS', 1, 1, 2),
            hash_mb=_env_int(env, 'PIKAFISH_HASH_MB', 32, 16, 128),
        )

    def availability(self):
        if not self.command:
            return 'not_configured'
        if (any(not isinstance(arg, str) or '\n' in arg or '\r' in arg or '\x00' in arg for arg in self.command)
                or not Path(self.command[0]).is_absolute()):
            return 'invalid_configuration'
        if not Path(self.command[0]).is_file():
            return 'binary_missing'
        if self.nnue_path and ('\n' in self.nnue_path or '\r' in self.nnue_path or '\x00' in self.nnue_path
                               or not Path(self.nnue_path).is_absolute() or not Path(self.nnue_path).is_file()):
            return 'network_missing'
        return 'configured_unverified'


def _position(fen, moves):
    base = Position.from_fen(fen)
    if moves is None:
        moves = []
    if not isinstance(moves, (list, tuple)) or len(moves) > MAX_HISTORY:
        raise ValueError('Lịch sử phải là danh sách tối đa 600 nước đi.')
    state = base
    for move in moves:
        state = state.play(move)
    # Normalize all user input before it reaches the line-oriented UCI protocol.
    # Pikafish uses n/b for horse/elephant; this app stores h/e.
    board, turn = base.fen().split()
    board = board.translate(str.maketrans('hHeE', 'nNbB'))
    halfmove, fullmove = '0', '1'
    fields = fen.split()
    if len(fields) == 6:
        if fields[2:4] != ['-', '-'] or not fields[4].isdigit() or not fields[5].isdigit():
            raise ValueError('Phần lịch sử của FEN không hợp lệ.')
        if not (0 <= int(fields[4]) <= 1000000 and 1 <= int(fields[5]) <= 1000000):
            raise ValueError('Bộ đếm FEN nằm ngoài giới hạn.')
        halfmove, fullmove = str(int(fields[4])), str(int(fields[5]))
    command = f'position fen {board} {turn} - - {halfmove} {fullmove}'
    if moves:
        command += ' moves ' + ' '.join(moves)
    return state, command, len(moves)


def _parse_info(line):
    """Read only score-bearing PV records; no evaluation inferred from bestmove."""
    fields = line.split()
    if not fields or fields[0] != 'info' or 'pv' not in fields or 'score' not in fields:
        return None
    try:
        pv_index = fields.index('pv')
        prefix, pv = fields[:pv_index], fields[pv_index + 1:]
        score_index = prefix.index('score')
        kind, score = prefix[score_index + 1], int(prefix[score_index + 2])
        depth = int(prefix[prefix.index('depth') + 1])
        rank = int(prefix[prefix.index('multipv') + 1]) if 'multipv' in prefix else 1
        nodes = int(prefix[prefix.index('nodes') + 1]) if 'nodes' in prefix else 0
        if (kind not in ('cp', 'mate') or abs(score) > 10000000 or not 0 <= depth <= 256
                or not 1 <= rank <= 8 or not 0 <= nodes <= 10**15 or not pv
                or len(pv) > MAX_ENGINE_PV or any(not MOVE_RE.fullmatch(m) for m in pv)):
            return None
        bounds = [name for name in ('lowerbound', 'upperbound') if name in prefix]
        if len(bounds) > 1:
            return None
        return dict(move=pv[0], score=score, score_type=kind, pv=pv, depth=depth,
                    rank=rank, nodes=nodes, bound=bounds[0] if bounds else 'exact')
    except (ValueError, IndexError):
        return None


def _candidate(state, line):
    verify = state
    try:
        for move in line['pv']:
            verify = verify.play(move)
    except (TypeError, ValueError) as error:
        raise EngineUnavailable('illegal_variation') from error
    src, dst = parse_move(line['move'])
    return dict(move=line['move'], **{'from': src, 'to': dst},
                score=line['score'], score_type=line['score_type'],
                pv=line['pv'][:MAX_PV], pv_truncated=len(line['pv']) > MAX_PV,
                depth=line['depth'], bound=line.get('bound', 'exact'),
                perspective=state.turn)


class _UciProcess:
    """A UCI process with bounded output per request and guaranteed cleanup.

    AnalysisEngine keeps one alive between requests and replaces it after a failure.
    """

    def __init__(self, config, deadline):
        self.config, self.deadline = config, deadline
        self.output_bytes = 0  # per request: reset each time a long-lived process is reused
        self.output = queue.Queue(maxsize=512)
        self.failure = None
        self.process = None
        self.reader = None
        self.name = 'UCI engine'
        self.options = set()

    def __enter__(self):
        try:
            self.process = subprocess.Popen(
                list(self.config.command), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, shell=False,
                cwd=str(Path(self.config.command[0]).parent),
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
            self.reader = threading.Thread(target=self._read, daemon=True, name='co-chill-uci-reader')
            self.reader.start()
            self.send('uci')
            # Pikafish loads pikafish.nnue from its own folder before answering uci.
            deadline = min(self.deadline, monotonic() + self.config.startup_seconds)
            while True:
                line = self.next_line(deadline)
                if line == 'uciok':
                    break
                if line.startswith('id name '):
                    self.name = ''.join(c for c in line[8:168] if c.isprintable()) or 'UCI engine'
                if line.startswith('option name ') and ' type ' in line:
                    self.options.add(line[12:].split(' type ', 1)[0])
            for name, value in [('Threads', max(1, min(2, self.config.threads))),
                                ('Hash', max(16, min(128, self.config.hash_mb))), ('Ponder', 'false')]:
                if name in self.options:
                    self.option(name, value)
            if self.config.nnue_path:
                if 'EvalFile' not in self.options:
                    raise EngineUnavailable('network_option_unavailable')
                self.option('EvalFile', self.config.nnue_path)
            self.send('ucinewgame')
            self.ready(self.config.startup_seconds)
            return self
        except (OSError, EngineUnavailable) as error:
            self.close()
            if isinstance(error, EngineUnavailable):
                raise
            raise EngineUnavailable('start_failed') from error

    def _read(self):
        try:
            while True:
                data = self.process.stdout.readline(MAX_LINE_BYTES + 1)
                if not data:
                    return
                self.output_bytes += len(data)
                if len(data) > MAX_LINE_BYTES or self.output_bytes > MAX_OUTPUT_BYTES:
                    self.failure = 'output_limit'
                    self.process.kill()
                    return
                line = data.decode('utf-8', errors='replace').strip()
                try:
                    self.output.put(line, timeout=.2)
                except queue.Full:
                    self.failure = 'output_limit'
                    self.process.kill()
                    return
        except (OSError, ValueError):
            return

    def send(self, command):
        if '\n' in command or '\r' in command:
            raise EngineUnavailable('invalid_command')
        try:
            self.process.stdin.write((command + '\n').encode('utf-8'))
            self.process.stdin.flush()
        except (OSError, ValueError) as error:
            raise EngineUnavailable('process_exited') from error

    def next_line(self, deadline):
        while monotonic() < deadline:
            if self.failure:
                raise EngineUnavailable(self.failure)
            try:
                return self.output.get(timeout=min(.05, max(.001, deadline - monotonic())))
            except queue.Empty:
                if self.failure:
                    raise EngineUnavailable(self.failure)
                if self.process.poll() is not None:
                    raise EngineUnavailable('process_exited')
        raise EngineUnavailable('timeout')

    def option(self, name, value):
        self.send(f'setoption name {name} value {value}')

    def ready(self, seconds=None):
        self.send('isready')
        deadline = min(self.deadline, monotonic() + (self.config.handshake_seconds if seconds is None else seconds))
        while self.next_line(deadline) != 'readyok':
            pass

    def search(self, state, position_command, movetime_ms, multipv, selected=None, nodes=None):
        """nodes: stop after this many nodes (bot levels); movetime_ms still caps the time."""
        if 'MultiPV' in self.options:
            self.option('MultiPV', 1 if selected else multipv)
        self.ready()
        self.send(position_command)
        command = f'go nodes {int(nodes)} movetime {movetime_ms}' if nodes else f'go movetime {movetime_ms}'
        if selected:
            command += ' searchmoves ' + selected
        self.send(command)
        deadline = min(self.deadline, monotonic() + movetime_ms / 1000 + 1.0)
        records = {}
        best = None
        nodes = 0
        while True:
            line = self.next_line(deadline)
            if line.startswith('bestmove '):
                values = line.split()
                best = values[1] if len(values) > 1 else None
                break
            record = _parse_info(line)
            if record is not None:
                records.setdefault(record['depth'], {})[record['rank']] = record
                nodes = max(nodes, record['nodes'])
        if best not in state.legal_moves() or (selected is not None and best != selected):
            raise EngineUnavailable('illegal_bestmove')
        # Only show candidates from one completed depth and matching bestmove.
        # Never fill missing slots by combining old and new iteration scores.
        depth = next((d for d in sorted(records, reverse=True)
                      if 1 in records[d] and records[d][1]['move'] == best), None)
        if depth is None:
            raise EngineUnavailable('missing_analysis')
        raw = [r for rank, r in sorted(records[depth].items()) if rank <= (1 if selected else multipv)]
        if len({r['move'] for r in raw}) != len(raw):
            raise EngineUnavailable('duplicate_variation')
        return [_candidate(state, row) for row in raw], depth, nodes

    def close(self):
        if self.process is None:
            return
        if self.process.poll() is None:
            try:
                self.send('stop')
                self.send('quit')
                self.process.wait(timeout=.2)
            except (EngineUnavailable, subprocess.TimeoutExpired):
                self.process.kill()
                try:
                    self.process.wait(timeout=.5)
                except subprocess.TimeoutExpired:
                    pass
        if self.reader is not None:
            self.reader.join(timeout=.3)
        for pipe in (self.process.stdin, self.process.stdout):
            if pipe is not None:
                try:
                    pipe.close()
                except (OSError, ValueError):
                    pass

    def __exit__(self, *_):
        self.close()


class AnalysisEngine:
    """Optional UCI integration for the V5 API, independent of legacy Service.

    An unavailable external engine returns honest local heuristic analysis. The
    caller must not certify free-text understanding or definitive mistakes from
    fallback scores, and must enforce reflection / live-game gates itself.
    """

    def __init__(self, config=None, local_engine=None, queue=None):
        self.config = config or EngineConfig.from_env()
        self.local = local_engine or LocalEngine(max_depth=2, seconds=.35)
        self.last_status = None
        self.queue = queue or _QUEUE
        # One long-lived UCI process (docs/BOT_LEVELS.md §4): no NNUE reload per move.
        # Only the queue's running request touches it.
        self._process, self._searches = None, 0
        self._seconds = {}  # moving average of how long each kind of request takes
        self.rng = random.SystemRandom()  # bot choices; never seeded from a request
        atexit.register(self.close)

    def close(self):
        process, self._process = self._process, None
        if process is not None:
            process.close()

    def _uci(self, deadline):
        if self._process is not None and (self._process.process.poll() is not None
                                          or self._searches >= max(1, self.config.max_searches)):
            self.close()
        if self._process is None:
            process = _UciProcess(self.config, deadline)
            process.__enter__()
            self._process, self._searches = process, 0
        self._process.deadline = deadline
        self._process.output_bytes = 0
        return self._process

    def _estimate(self, kind, movetime):
        if kind in self._seconds:
            return self._seconds[kind]
        if kind[0] == 'level':
            nodes = BOT_LEVELS[kind[1]][0]
            # ~250k nodes/s on one thread until real measurements replace this guess.
            return (min(LEVEL_TIME_CAP_MS / 1000, nodes / 250000) if nodes else movetime / 1000) + 0.5
        return movetime / 1000 * (2 if kind[1] else 1) + 0.5

    def _measured(self, kind, seconds):
        self._seconds[kind] = seconds if kind not in self._seconds else .7 * self._seconds[kind] + .3 * seconds

    def status(self):
        reason = self.config.availability()
        return dict(configured=reason == 'configured_unverified', status=reason,
                    verified=False, last_result=self.last_status, adapter=ADAPTER_VERSION,
                    fallback=ENGINE_VERSION, max_pv_plies=MAX_PV, queue=self.queue.snapshot(),
                    note='Có cấu hình chưa có nghĩa đã chạy hoặc kiểm chứng sức mạnh engine.')

    def analyze(self, fen, *, moves=None, selected_move=None, mode='quick', purpose='review-scan', owner=None, level=None):
        """level 1–7: the bot's move for that level (docs/BOT_LEVELS.md); None: plain analysis."""
        started = monotonic()
        if level is not None and (type(level) is not int or level not in BOT_LEVELS):
            raise ValueError('Cấp máy phải là số nguyên từ 1 đến 7.')
        if mode not in ('quick', 'deep'):
            raise ValueError('Chế độ phân tích phải là quick hoặc deep.')
        state, command, history_count = _position(fen, moves)
        legal = state.legal_moves()
        if selected_move is not None and selected_move not in legal:
            raise ValueError('Nước cần đánh giá không hợp lệ ở thế cờ này.')
        if not legal:
            return self._terminal(state, started, history_count)
        avoid = ()
        if level is not None:
            # The rules settle these without the engine: a forced move, or a mate in one
            # (always played from level 2; level 1 misses it half of the time).
            mates = immediate_mates(state)
            if len(legal) == 1:
                return self._ruled_move(state, legal[0], level, 'only_legal_move', started, history_count)
            if mates and (level >= 2 or self.rng.random() >= LEVEL_ONE_MISSES_MATE):
                return self._ruled_move(state, mates[0], level, 'mate_in_one', started, history_count)
            avoid = tuple(mates)
        reason = self.config.availability()
        if reason != 'configured_unverified':
            return self._fallback(state, selected_move, mode, reason, started, history_count)
        movetime = max(50, min(5000, self.config.deep_ms if mode == 'deep' else self.config.quick_ms))
        multipv = max(1, min(3, self.config.multipv))
        deadline = started + max(.1, min(15.0, self.config.request_seconds))
        kind = (mode, bool(selected_move))
        level_nodes = None
        if level is not None:
            level_nodes, multipv = BOT_LEVELS[level][0], BOT_LEVELS[level][1]
            if level_nodes:
                movetime = LEVEL_TIME_CAP_MS
            kind, selected_move = ('level', level), None
        # Raises EngineUnavailable('busy') when the queue cannot meet the deadline;
        # the server turns that into 429 engine_busy, never a silent local answer.
        ticket = self.queue.enter(PRIORITY.get(purpose, PRIORITY['review-scan']), owner,
                                  self._estimate(kind, movetime), deadline)
        try:
            began = monotonic()
            engine = self._uci(deadline)
            engine.send('ucinewgame')  # each request starts from an empty hash table
            lines, depth, nodes = engine.search(state, command, movetime, multipv, nodes=level_nodes)
            selected = None
            if selected_move:
                # Same root/side; do not negate a child score or assume that
                # absence from MultiPV means the chosen move is a mistake.
                chosen, chosen_depth, chosen_nodes = engine.search(state, command, movetime, 1, selected_move)
                selected = chosen[0]
                selected['search'] = {'restricted_root': True, 'movetime_ms': movetime,
                                      'depth': chosen_depth, 'nodes': chosen_nodes}
                nodes += chosen_nodes
            result = dict(engine=ADAPTER_VERSION, engine_name=engine.name,
                          fallback=False, status='ready', confidence='engine_search',
                          fen=state.fen(), turn=state.turn, score=lines[0]['score'],
                          score_type=lines[0]['score_type'], best_move=lines[0]['move'],
                          candidates=lines, lines=lines, selected=selected,
                          search=dict(mode=mode, movetime_ms=movetime, depth=depth,
                                      nodes=nodes, elapsed_ms=round((monotonic() - started) * 1000),
                                      exhaustive_root=False, max_pv_plies=MAX_PV,
                                      history_plies=history_count),
                          warnings=['Điểm và biến là kết quả tìm kiếm hữu hạn; chưa thay thế duyệt bài học.'],
                          provenance=dict(version=engine.name, adapter=ADAPTER_VERSION,
                                          source='configured_uci_binary', repetition_history=bool(history_count)))
            if level is not None:
                chosen, rank, loss = choose_level_move(lines, level, self.rng, avoid)
                result['best_move'] = chosen['move']
                result['bot'] = dict(level=level, rank=rank, loss_cp=loss, nodes_limit=level_nodes,
                                     multipv=multipv, calibrated=False)
                result['provenance']['bot_level'] = level
                result['warnings'] = [f'Cấp {level} · chưa hiệu chỉnh; không phải Elo.']
            self.last_status = 'ready'
            return result
        except EngineUnavailable as error:
            # A failed or slow process is not reused: the next request starts a fresh one.
            self.close()
            return self._fallback(state, selected_move, mode, str(error), started, history_count)
        finally:
            self._searches += 1
            self._measured(kind, monotonic() - began)
            self.queue.leave(ticket)

    def _ruled_move(self, state, move, level, reason, started, history_count):
        """A bot move proven by the rules alone (the only legal move, or a mate in one)."""
        return dict(engine='co-chill-rules', engine_name='Luật cờ Cờ Chill', fallback=False, status='ready',
                    confidence='rules', fen=state.fen(), turn=state.turn, score=None, score_type=None,
                    best_move=move, candidates=[], lines=[], selected=None,
                    bot=dict(level=level, rank=None, loss_cp=0, nodes_limit=0, multipv=0, calibrated=False, reason=reason),
                    search=dict(depth=0, nodes=0, elapsed_ms=round((monotonic() - started) * 1000),
                                exhaustive_root=True, history_plies=history_count),
                    warnings=[f'Cấp {level} · chưa hiệu chỉnh; không phải Elo.'],
                    provenance=dict(version=ADAPTER_VERSION, source='rules', bot_level=level))

    def _fallback(self, state, selected_move, mode, reason, started, history_count):
        raw = self.local.analyze(state.fen())
        all_lines = [_candidate(state, dict(row, score_type='heuristic_cp', depth=raw['depth']))
                     for row in raw['lines']]
        lines = all_lines[:3]
        selected = next((row for row in all_lines if row['move'] == selected_move), None)
        self.last_status = 'fallback'
        return dict(engine=ENGINE_VERSION, engine_name='Máy cơ bản Cờ Chill', fallback=True,
                    status='fallback', fallback_reason=reason, confidence='limited',
                    fen=state.fen(), turn=state.turn, score=raw['score'], score_type='heuristic_cp',
                    best_move=lines[0]['move'] if lines else None, candidates=lines, lines=lines,
                    selected=selected, search=dict(mode=mode, movetime_ms=0, depth=raw['depth'],
                                                  nodes=raw['nodes'], elapsed_ms=round((monotonic() - started) * 1000),
                                                  truncated=raw['truncated'], exhaustive_root=False,
                                                  history_plies=history_count, max_pv_plies=MAX_PV),
                    warnings=['Đang dùng máy cơ bản, chưa có phân tích mạnh. Không dùng điểm này để kết luận chắc chắn nước sai hoặc trình độ.'],
                    provenance=dict(version=ENGINE_VERSION, adapter=ADAPTER_VERSION,
                                    source='local_heuristic', repetition_history=False))

    def _terminal(self, state, started, history_count):
        outcome = state.status()
        return dict(engine='co-chill-rules', engine_name='Luật cờ Cờ Chill', fallback=False,
                    status='terminal', confidence='rules', fen=state.fen(), turn=state.turn,
                    score=None, score_type=None, best_move=None, candidates=[], lines=[], selected=None,
                    outcome=outcome, search=dict(depth=0, nodes=0, elapsed_ms=round((monotonic() - started) * 1000),
                                                exhaustive_root=True, history_plies=history_count),
                    warnings=[], provenance=dict(version=ADAPTER_VERSION, source='rules'))
