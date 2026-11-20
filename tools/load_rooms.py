"""Measure online-room polling load on a LOCAL server with a throwaway database.

    python tools/load_rooms.py                          # 5, 10, 25, 50 rooms, 60 s each
    python tools/load_rooms.py --rooms 10 --spectators 2 --seconds 120
    python tools/load_rooms.py --rooms 25 --json var\\load-25.json

For each scenario the tool starts its own `co_chill_server.py serve` on a free
loopback port with a new temporary SQLite file (deleted afterwards), the same
threaded server and the same `CO_CHILL_TRUSTED_PROXIES=127.0.0.1` setting as
production behind Nginx. It never talks to another host: an explicit --url must
be a loopback address, and it refuses an existing database file.

Each simulated person is a room guest with its own X-Real-IP (as Nginx would
send), polls `GET /api/rooms/<code>` every 2 seconds like web/online-play.js,
checks `GET /api/rooms/session` every 10 seconds, and plays a random legal move
on its turn about every 8 seconds. Rooms use the rapid preset (10 min + 5 s).

Numbers measured on a laptop are not the 2 vCPU VM; they show how the cost
grows with the number of people and where SQLite write contention starts.
Exit code 0 when every scenario had no server error and no game was lost to a
false disconnection, 1 otherwise.
"""
from pathlib import Path
import argparse
import http.client
import json
import os
import random
import secrets
import socket
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.rules import Position  # noqa: E402

COOKIE = 'co_chill_room_guest'
POLL_SECONDS = 2.0          # web/online-play.js setInterval(…, 2000)
SESSION_SECONDS = 10.0      # identity() is refreshed after 10 s
MOVE_SECONDS = 8.0


class Client:
    """One browser: a guest cookie, a CSRF token and a fake client IP."""

    def __init__(self, base, ip, stats):
        parts = urlsplit(base)
        self.host, self.port, self.origin = parts.hostname, parts.port, f'{parts.scheme}://{parts.netloc}'
        self.ip, self.stats, self.cookie, self.csrf = ip, stats, '', ''

    def call(self, kind, method, path, body=None):
        headers = {'X-Real-IP': self.ip, 'Accept': 'application/json'}
        if self.cookie:
            headers['Cookie'] = f'{COOKIE}={self.cookie}'
        data = None
        if method != 'GET':
            data = json.dumps(body or {}).encode()
            headers.update({'Content-Type': 'application/json', 'Origin': self.origin})
            if self.csrf:
                headers['X-CSRF-Token'] = self.csrf
        started = time.perf_counter()
        status, payload = 0, {}
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=30)
            conn.request(method, '/api/rooms' + path, body=data, headers=headers)
            response = conn.getresponse()
            raw, status = response.read(), response.status
            for name, value in response.getheaders():
                if name.lower() == 'set-cookie' and value.startswith(COOKIE + '='):
                    self.cookie = value.split('=', 1)[1].split(';', 1)[0]
            conn.close()
            payload = json.loads(raw or b'{}')
        except (OSError, http.client.HTTPException, ValueError):
            status = -1
        self.stats.add(kind, status, time.perf_counter() - started)
        return status, payload


class Stats:
    def __init__(self):
        self.lock, self.rows = threading.Lock(), []

    def add(self, kind, status, seconds):
        with self.lock:
            self.rows.append((kind, status, seconds))

    def summary(self, duration):
        out = {}
        for kind in sorted({r[0] for r in self.rows}):
            rows = [r for r in self.rows if r[0] == kind]
            times = sorted(r[2] * 1000 for r in rows)
            pick = lambda q: times[min(len(times) - 1, int(q * len(times)))]
            codes = {}
            for r in rows:
                codes[r[1]] = codes.get(r[1], 0) + 1
            out[kind] = {'requests': len(rows), 'perSecond': round(len(rows) / duration, 1),
                         'p50ms': round(pick(0.50), 1), 'p95ms': round(pick(0.95), 1), 'p99ms': round(pick(0.99), 1),
                         'maxms': round(times[-1], 1), 'meanms': round(statistics.fmean(times), 1), 'status': codes}
        return out


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def start_server(db):
    port = free_port()
    env = dict(os.environ, CO_CHILL_TRUSTED_PROXIES='127.0.0.1', CO_CHILL_PUBLIC_ORIGIN='')
    proc = subprocess.Popen([sys.executable, str(ROOT / 'co_chill_server.py'), 'serve', '--host', '127.0.0.1',
                             '--port', str(port), '--db', str(db)], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://127.0.0.1:{port}'
    for _ in range(100):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                return proc, base
        except OSError:
            if proc.poll() is not None:
                raise SystemExit('Server failed to start (is the port or the database in use?).')
            time.sleep(0.1)
    proc.kill()
    raise SystemExit('Server did not start in 10 seconds.')


def setup(base, rooms, spectators, stats):
    """Guests, private rapid rooms, both players ready; returns [(client, code, role)]."""
    people, n = [], 0

    def guest():
        nonlocal n
        n += 1
        client = Client(base, f'10.{n // 65536 % 256}.{n // 256 % 256}.{n % 256}', stats)
        status, body = client.call('setup', 'POST', '/guest', {'displayName': f'Tải {n}'})
        if status not in (200, 201):
            raise SystemExit(f'Could not create a guest session (HTTP {status}): {body}')
        client.csrf = body['csrf']
        return client

    for _ in range(rooms):
        red, black = guest(), guest()
        status, room = red.call('setup', 'POST', '', {'preset': 'rapid', 'visibility': 'private'})
        if status not in (200, 201):
            raise SystemExit(f'Could not create a room (HTTP {status}): {room}')
        code = room['code']
        assert black.call('setup', 'POST', f'/{code}/join')[0] == 200
        for player in (red, black):
            assert player.call('setup', 'POST', f'/{code}/ready')[0] == 200
        people += [(red, code, 'player'), (black, code, 'player')]
        for _ in range(spectators):
            viewer = guest()
            assert viewer.call('setup', 'POST', f'/{code}/watch')[0] == 200
            people.append((viewer, code, 'spectator'))
    return people


def person(client, code, role, stop, last, rng):
    """One browser tab: poll, refresh the session, move on its turn."""
    next_poll = time.monotonic() + rng.uniform(0, POLL_SECONDS)
    next_session = time.monotonic() + rng.uniform(0, SESSION_SECONDS)
    next_move = time.monotonic() + rng.uniform(2, MOVE_SECONDS)
    while not stop.is_set():
        now = time.monotonic()
        if now >= next_session:
            client.call('session', 'GET', '/session')
            next_session += SESSION_SECONDS
        if now >= next_poll:
            status, snap = client.call('snapshot', 'GET', f'/{code}')
            if status == 200:
                last[client.ip] = snap
            next_poll += POLL_SECONDS
        snap = last.get(client.ip)
        if role == 'player' and snap and now >= next_move and snap.get('status') == 'playing' and snap.get('side'):
            pos = Position.from_fen(snap['fen'])
            if pos.turn == snap['side'] and pos.legal_moves():
                status, body = client.call('move', 'POST', f'/{code}/move', {
                    'move': rng.choice(pos.legal_moves()), 'expectedRevision': snap['revision'],
                    'nonce': secrets.token_hex(8)})
                if status == 200:
                    last[client.ip] = body
            next_move = now + MOVE_SECONDS
        stop.wait(max(0.01, min(next_poll, next_session, next_move) - time.monotonic()))


def scenario(rooms, spectators, seconds, url=None):
    stats, db_dir = Stats(), None
    proc = None
    if url:
        base = url
    else:
        db_dir = tempfile.mkdtemp(prefix='cochill-load-')
        proc, base = start_server(Path(db_dir) / 'load.sqlite3')
    try:
        people = setup(base, rooms, spectators, stats)
        setup_rows = len(stats.rows)
        stats.rows.clear()
        stop, last, threads = threading.Event(), {}, []
        rng = random.Random(rooms * 1000 + spectators)
        for client, code, role in people:
            t = threading.Thread(target=person, args=(client, code, role, stop, last, random.Random(rng.random())), daemon=True)
            t.start()
            threads.append(t)
        started = time.monotonic()
        stop.wait(seconds)
        stop.set()
        for t in threads:
            t.join(timeout=35)
        duration = time.monotonic() - started
        finals = {}
        for client, code, role in people:
            if role == 'player':
                snap = last.get(client.ip) or {}
                result = snap.get('result') or {}
                key = snap.get('status', '?') + ('/' + result['reason'] if snap.get('status') == 'finished' else '')
                finals[code] = key
        outcome = {}
        for key in finals.values():
            outcome[key] = outcome.get(key, 0) + 1
        db_bytes = sum(f.stat().st_size for f in Path(db_dir).glob('load.sqlite3*')) if db_dir else None
        return {'rooms': rooms, 'people': len(people), 'spectatorsPerRoom': spectators, 'seconds': round(duration, 1),
                'setupRequests': setup_rows, 'requests': stats.summary(duration), 'rooms_at_end': outcome,
                'databaseBytes': db_bytes}
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        if db_dir:
            for f in Path(db_dir).glob('*'):
                f.unlink()
            os.rmdir(db_dir)


def problems(result):
    bad = []
    for kind, row in result['requests'].items():
        errors = {code: n for code, n in row['status'].items() if code == -1 or code >= 500 or code == 429}
        if errors:
            bad.append(f'{kind}: {errors}')
    lost = {k: n for k, n in result['rooms_at_end'].items() if 'disconnected' in k or k.startswith('paused')}
    if lost:
        bad.append(f'rooms lost to disconnection/pause: {lost}')
    return bad


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--rooms', default='5,10,25,50', help='Comma-separated room counts (2 players each)')
    parser.add_argument('--spectators', type=int, default=0, help='Spectators per room')
    parser.add_argument('--seconds', type=float, default=60, help='Measured seconds per scenario')
    parser.add_argument('--url', help='An already running LOCAL server (loopback only); default starts its own')
    parser.add_argument('--json', help='Also write the results to this file')
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    if args.url:
        host = urlsplit(args.url).hostname or ''
        if host not in ('127.0.0.1', 'localhost', '::1'):
            parser.error('Only a local server may be load-tested (127.0.0.1 / localhost). Never point this at production.')
    results = []
    for rooms in [int(x) for x in args.rooms.split(',') if x.strip()]:
        print(f'\n== {rooms} rooms, {rooms * 2} players, {args.spectators} spectators/room, {args.seconds:g} s', flush=True)
        result = scenario(rooms, args.spectators, args.seconds, args.url)
        results.append(result)
        print(f'{"request":<9} {"req/s":>6} {"p50 ms":>8} {"p95 ms":>8} {"p99 ms":>8} {"max ms":>8}  status')
        for kind, row in result['requests'].items():
            print(f'{kind:<9} {row["perSecond"]:>6} {row["p50ms"]:>8} {row["p95ms"]:>8} {row["p99ms"]:>8} {row["maxms"]:>8}  {row["status"]}')
        print('rooms at end:', result['rooms_at_end'], '| database + WAL:', result['databaseBytes'], 'bytes')
        for line in problems(result):
            print('PROBLEM', line)
    if args.json:
        Path(args.json).write_bytes((json.dumps(results, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return 1 if any(problems(r) for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
