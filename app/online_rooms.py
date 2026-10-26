"""Small, server-authoritative friendly Xiangqi rooms for a single-instance pilot.

Owns short SQLite transactions, but can join a caller's transaction for history
and identity deletion. Polling is transport only: seats, legal moves, clocks
and results live here.
Identity must come from a validated server session, never a request body.
"""
from contextlib import contextmanager, nullcontext
import hashlib
import json
from pathlib import Path
import re
import secrets
import sqlite3
import time

from app.cloud_store import APIError
from app.rules import Position, START_FEN, other

PRESETS = {'bullet': (60, 0), 'blitz': (300, 3), 'rapid': (600, 5), 'untimed': (0, 0)}
MESSAGES = {'hello': 'Chào bạn!', 'good_luck': 'Chúc bạn chơi vui!',
            'thanks': 'Cảm ơn bạn!', 'good_game': 'Cảm ơn vì ván đấu!',
            'please_wait': 'Bạn chờ một chút nhé.', 'bye': 'Hẹn gặp lại!'}
DISCONNECT_SECONDS = 30
DRAW_SECONDS = 15


class OnlineRooms:
    def __init__(self, db_path, clock=None):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.clock = clock or time.time
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS online_rooms (
                    code TEXT PRIMARY KEY, visibility TEXT NOT NULL,
                    status TEXT NOT NULL, updated_at REAL NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS online_results (
                    game_id TEXT PRIMARY KEY, room_code TEXT NOT NULL,
                    red_id TEXT NOT NULL, black_id TEXT NOT NULL,
                    ended_at REAL NOT NULL, data TEXT NOT NULL);
            ''')
            # A restarted service cannot distinguish player silence from its own
            # outage. Freeze active games; both seats must agree before resuming.
            for row in db.execute("SELECT data FROM online_rooms WHERE status='playing'").fetchall():
                room = json.loads(row['data'])
                room.update(status='paused', ready=[], pauseReason='server_restart')
                room['clock']['at'] = self.clock()
                room['revision'] += 1
                self._save(db, room)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def identity(user):
        user = dict(user) if user is not None else {}
        uid = user.get('id')
        if not isinstance(uid, str) or not re.fullmatch(r'[A-Za-z0-9_-]{3,100}', uid):
            raise APIError(401, 'Hãy chọn tài khoản hoặc phiên khách trước khi vào phòng.', 'authentication_required')
        name = user.get('displayName', user.get('display_name', user.get('username', 'Người chơi')))
        return {'id': uid, 'displayName': str(name).strip()[:60] or 'Người chơi'}

    def _save(self, db, room):
        db.execute('INSERT INTO online_rooms VALUES (?,?,?,?,?) ON CONFLICT(code) DO UPDATE SET '
                   'visibility=excluded.visibility,status=excluded.status,updated_at=excluded.updated_at,data=excluded.data',
                   (room['code'], room['visibility'], room['status'], self.clock(), json.dumps(room, ensure_ascii=False)))

    @staticmethod
    def _load(db, code):
        if not isinstance(code, str) or not re.fullmatch(r'[A-Fa-f0-9]{10}', code):
            raise APIError(404, 'Không tìm thấy phòng.', 'room_not_found')
        row = db.execute('SELECT data FROM online_rooms WHERE code=?', (code.upper(),)).fetchone()
        if not row:
            raise APIError(404, 'Không tìm thấy phòng.', 'room_not_found')
        return json.loads(row['data'])

    @staticmethod
    def _side(room, uid):
        return next((s for s, person in room['players'].items() if person and person['id'] == uid), None)

    @staticmethod
    def _member(room, uid):
        return OnlineRooms._side(room, uid) or uid in room['spectators']

    def _require_member(self, room, uid):
        if uid in room['banned'] or not self._member(room, uid):
            raise APIError(403, 'Bạn chưa vào phòng hoặc đã được mời rời phòng.', 'room_forbidden')

    def _require_player(self, room, uid):
        self._require_member(room, uid)
        side = self._side(room, uid)
        if not side:
            raise APIError(403, 'Chỉ hai người chơi được thực hiện thao tác này.', 'spectator_read_only')
        return side

    def _busy_elsewhere(self, db, uid, except_code=None):
        for row in db.execute("SELECT data FROM online_rooms WHERE status IN ('waiting','playing','paused')"):
            room = json.loads(row['data'])
            if room['code'] != except_code and self._side(room, uid):
                return True
        return False

    def _record(self, db, room):
        if room['status'] != 'finished' or not all(room['players'].values()):
            return
        record = {k: room[k] for k in ('gameId', 'code', 'initialFen', 'fen', 'moves', 'players', 'result', 'options', 'startedAt')}
        record['events'] = room.get('events', [])
        record['endedAt'] = self.clock()
        db.execute('INSERT OR IGNORE INTO online_results VALUES (?,?,?,?,?,?)',
                   (room['gameId'], room['code'], room['players']['w']['id'], room['players']['b']['id'],
                    self.clock(), json.dumps(record, ensure_ascii=False)))

    def _finish(self, db, room, winner, reason):
        if room['status'] == 'finished':
            return
        room.update(status='finished', result={'over': True, 'winner': winner, 'reason': reason},
                    drawOffer=None, takebackOffer=None, ready=[])
        room['revision'] += 1
        self._record(db, room)

    def _tick(self, db, room, now):
        if room.get('drawOffer') and room['drawOffer']['expiresAt'] <= now:
            room['drawOffer'] = None
            room['revision'] += 1
        if room['status'] != 'playing':
            return
        # Presence from polling is not an infallible network detector. If both
        # seats disappeared, pause instead of assigning an arbitrary winner.
        ages = {s: max(0, now - room['seen'].get(p['id'], now)) for s, p in room['players'].items()}
        if all(age >= DISCONNECT_SECONDS for age in ages.values()):
            room.update(status='paused', ready=[], pauseReason='connection_interrupted')
            room['clock']['at'] = now
            room['revision'] += 1
            return
        # If a service request gap occurs and one seat remains connected, the
        # deadline order decides the result; no client-supplied clock is trusted.
        turn = Position.from_fen(room['fen']).turn
        clock = room['clock']
        timeout_at = clock['at'] + clock[turn] / 1000 if room['options']['seconds'] else float('inf')
        disconnected = [(room['seen'].get(room['players'][s]['id'], now) + DISCONNECT_SECONDS, s)
                        for s, age in ages.items() if age >= DISCONNECT_SECONDS]
        offline_at, offline_side = min(disconnected, default=(float('inf'), None))
        if min(timeout_at, offline_at) <= now:
            if timeout_at <= offline_at:
                clock[turn] = 0
                self._finish(db, room, other(turn), 'timeout')
            else:
                self._finish(db, room, other(offline_side), 'disconnected')
            clock['at'] = now
            return
        if room['options']['seconds']:
            clock[turn] = max(0, clock[turn] - max(0, now - clock['at']) * 1000)
        clock['at'] = now

    def _snapshot(self, room, uid):
        side = self._side(room, uid)
        spectators = [{'id': x['id'], 'displayName': x['displayName']} for x in room['spectators'].values()]
        return {'code': room['code'], 'gameId': room['gameId'], 'ownerId': room['ownerId'],
                'visibility': room['visibility'], 'status': room['status'], 'revision': room['revision'],
                'players': room['players'], 'spectators': spectators, 'side': side,
                'options': room['options'], 'ready': room['ready'], 'fen': room['fen'],
                'initialFen': room['initialFen'], 'moves': [x['move'] for x in room['moves']],
                'clock': room['clock'], 'serverNow': self.clock(), 'result': room['result'],
                'drawOffer': room['drawOffer'], 'takebackOffer': room['takebackOffer'],
                'pauseReason': room.get('pauseReason'), 'messages': room['messages'][-40:],
                'rematch': room['rematch'], 'chatOptions': MESSAGES,
                'ranked': False, 'rulesNotice': 'Giao hữu thử nghiệm; luật chiếu đuổi và lặp giải đấu chưa được kiểm chứng đầy đủ.'}

    def create(self, user, data=None):
        person, data = self.identity(user), data or {}
        if not isinstance(data, dict):
            raise APIError(400, 'Thiết lập phòng không hợp lệ.')
        preset = data.get('preset', 'rapid')
        if preset not in PRESETS:
            raise APIError(400, 'Chọn chế độ thời gian hợp lệ.')
        seconds, increment = PRESETS[preset]
        if 'seconds' in data or 'increment' in data:
            seconds, increment = data.get('seconds', seconds), data.get('increment', increment)
            if type(seconds) is not int or type(increment) is not int or seconds not in (0, *range(60, 3601, 60)) or not 0 <= increment <= 30:
                raise APIError(400, 'Thời gian từ 1 đến 60 phút hoặc không giờ; cộng tối đa 30 giây.')
            if seconds == 0:
                increment = 0
            preset = 'custom'
        visibility = data.get('visibility', 'private')
        if visibility not in ('private', 'public'):
            raise APIError(400, 'Loại phòng không hợp lệ.')
        now, code = self.clock(), secrets.token_hex(5).upper()
        side = secrets.choice(('w', 'b'))
        room = {'code': code, 'gameId': secrets.token_hex(16), 'ownerId': person['id'],
                'visibility': visibility, 'status': 'waiting', 'revision': 0,
                'players': {side: person, other(side): None}, 'spectators': {}, 'banned': [],
                'options': {'preset': preset, 'seconds': seconds, 'increment': increment},
                'ready': [], 'initialFen': START_FEN, 'fen': START_FEN, 'moves': [],
                'clock': {'w': seconds * 1000, 'b': seconds * 1000, 'at': now},
                'seen': {person['id']: now}, 'result': {'over': False, 'winner': None, 'reason': 'waiting'},
                'drawOffer': None, 'takebackOffer': None, 'messages': [], 'nonces': {},
                'createdAt': now, 'startedAt': None, 'rematch': [], 'events': []}
        with self.connect() as db:
            if self._busy_elsewhere(db, person['id']):
                raise APIError(409, 'Bạn đã có phòng đang chờ hoặc đang chơi.', 'already_in_room')
            self._save(db, room)
        return self._snapshot(room, person['id'])

    def list_public(self, user):
        person = self.identity(user)
        with self.connect() as db:
            rooms = []
            for row in db.execute("SELECT data FROM online_rooms WHERE visibility='public' AND status!='finished' ORDER BY updated_at DESC LIMIT 50").fetchall():
                room = json.loads(row['data'])
                self._tick(db, room, self.clock())
                self._save(db, room)
                if person['id'] not in room['banned'] and room['status'] != 'finished':
                    rooms.append({'code': room['code'], 'players': room['players'], 'status': room['status'],
                                  'options': room['options'], 'openSeat': any(p is None for p in room['players'].values())})
            mine = []
            for row in db.execute("SELECT data FROM online_rooms WHERE status IN ('waiting','playing','paused')"):
                room = json.loads(row['data'])
                if self._side(room, person['id']):
                    mine.append({'code': room['code'], 'status': room['status']})
            return {'rooms': rooms, 'mine': mine, 'chatOptions': MESSAGES, 'ranked': False}

    def match(self, user, data=None):
        """Pilot community matching by time preset, then explicit mutual ready.

        No inferred Elo: the current learner levels are not calibrated ratings.
        A concurrent seat claim is retried by checking the next available room.
        """
        person, data = self.identity(user), data or {}
        preset = data.get('preset', 'rapid')
        if preset not in PRESETS:
            raise APIError(400, 'Chọn chế độ thời gian hợp lệ.')
        listing = self.list_public(user)
        if listing['mine']:
            return self.snapshot(user, listing['mine'][0]['code'])
        for room in reversed(listing['rooms']):
            if room['status'] == 'waiting' and room['openSeat'] and room['options']['preset'] == preset:
                try:
                    return self.join(person, room['code'])
                except APIError as error:
                    if error.code != 'room_full':
                        raise
        return self.create(person, {'preset': preset, 'visibility': 'public'})

    def join(self, user, code, spectator=False):
        person = self.identity(user)
        with self.connect() as db:
            room, now = self._load(db, code), self.clock()
            self._tick(db, room, now)
            if person['id'] in room['banned']:
                raise APIError(403, 'Chủ phòng đã mời bạn rời phòng.', 'room_forbidden')
            if self._side(room, person['id']):
                pass
            elif spectator:
                if len(room['spectators']) >= 30 and person['id'] not in room['spectators']:
                    raise APIError(409, 'Phòng đã đủ người xem.')
                room['spectators'][person['id']] = person
                room['revision'] += 1
            else:
                if room['status'] != 'waiting' or all(room['players'].values()):
                    raise APIError(409, 'Phòng đã đủ người chơi hoặc ván đã bắt đầu.', 'room_full')
                if self._busy_elsewhere(db, person['id'], room['code']):
                    raise APIError(409, 'Hãy rời phòng trước trước khi nhận lời mời này.', 'already_in_room')
                room['players'][next(s for s, p in room['players'].items() if p is None)] = person
                room['spectators'].pop(person['id'], None)
                room['ready'] = []
                room['revision'] += 1
            room['seen'][person['id']] = now
            self._save(db, room)
            return self._snapshot(room, person['id'])

    def snapshot(self, user, code):
        person = self.identity(user)
        with self.connect() as db:
            room, now = self._load(db, code), self.clock()
            self._require_member(room, person['id'])
            self._tick(db, room, now)
            room['seen'][person['id']] = now
            self._save(db, room)
            return self._snapshot(room, person['id'])

    def action(self, user, code, action, data=None):
        person, data = self.identity(user), data or {}
        if not isinstance(data, dict):
            raise APIError(400, 'Dữ liệu thao tác không hợp lệ.')
        with self.connect() as db:
            room, now = self._load(db, code), self.clock()
            self._require_member(room, person['id'])
            self._tick(db, room, now)
            # Persist timeouts even if the attempted action is no longer legal.
            self._save(db, room)
            db.commit()
            db.execute('BEGIN IMMEDIATE')
            room = self._load(db, code)
            self._require_member(room, person['id'])
            now = self.clock()
            room['seen'][person['id']] = now
            nonce = data.get('nonce')
            if action == 'move' and (not isinstance(nonce, str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,80}', nonce)):
                raise APIError(400, 'Nước đi cần mã yêu cầu duy nhất.', 'nonce_required')
            digest = hashlib.sha256(json.dumps({'action': action, 'move': data.get('move')}, sort_keys=True).encode()).hexdigest()
            nonce_key = person['id'] + ':' + nonce if isinstance(nonce, str) else None
            if nonce_key and nonce_key in room['nonces']:
                if room['nonces'][nonce_key] != digest:
                    raise APIError(409, 'Mã yêu cầu đã dùng cho thao tác khác.', 'nonce_reused')
                return self._snapshot(room, person['id'])
            side = self._side(room, person['id'])
            if action == 'ready':
                self._require_player(room, person['id'])
                if room['status'] not in ('waiting', 'paused') or not all(room['players'].values()):
                    raise APIError(409, 'Phòng cần đủ hai người trước khi sẵn sàng.')
                room['ready'] = [uid for uid in room['ready'] if now - room['seen'].get(uid, 0) < DISCONNECT_SECONDS]
                if person['id'] not in room['ready']:
                    room['ready'].append(person['id'])
                if len(room['ready']) == 2:
                    room.update(status='playing', pauseReason=None)
                    room['startedAt'] = room['startedAt'] or now
                    room['clock']['at'] = now
                    room['seen'].update({p['id']: now for p in room['players'].values()})
            elif action == 'move':
                self._require_player(room, person['id'])
                self._playing(room)
                if type(data.get('expectedRevision')) is not int or data['expectedRevision'] != room['revision']:
                    raise APIError(409, 'Bàn cờ đã thay đổi. Hãy lấy trạng thái mới.', 'stale_revision', revision=room['revision'])
                pos = Position.from_fen(room['fen'])
                if pos.turn != side:
                    raise APIError(409, 'Chưa đến lượt bạn.', 'not_your_turn')
                if len(room['moves']) >= 600:
                    raise APIError(409, 'Ván quá dài cho bản thử; hãy thỏa thuận hòa hoặc đầu hàng.', 'move_limit')
                try:
                    after = pos.play(data.get('move'))
                except (ValueError, TypeError):
                    raise APIError(400, 'Nước đi không hợp lệ.', 'illegal_move')
                before_clock = dict(room['clock'])
                room['moves'].append({'move': data['move'], 'side': side, 'fenBefore': room['fen'],
                                      'clockBefore': before_clock, 'at': now})
                room['fen'] = after.fen()
                if room['options']['seconds']:
                    room['clock'][side] += room['options']['increment'] * 1000
                room['clock']['at'] = now
                # A player's next move closes their earlier takeback window.
                if room['takebackOffer'] and room['takebackOffer']['by'] == person['id']:
                    room['takebackOffer'] = None
                outcome = after.status()
                if outcome['over']:
                    self._finish(db, room, outcome['winner'], outcome['reason'])
            elif action == 'resign':
                self._require_player(room, person['id'])
                if room['status'] not in ('playing', 'paused'):
                    raise APIError(409, 'Ván chưa bắt đầu hoặc đã kết thúc.', 'game_not_live')
                if data.get('confirm') is not True:
                    raise APIError(400, 'Xác nhận trước khi đầu hàng.', 'confirmation_required')
                self._finish(db, room, other(side), 'resigned')
            elif action in ('draw', 'draw-accept', 'draw-decline'):
                self._require_player(room, person['id'])
                self._playing(room)
                if action == 'draw':
                    if room['drawOffer']:
                        raise APIError(409, 'Đã có lời mời hòa đang chờ.')
                    room['drawOffer'] = {'by': person['id'], 'expiresAt': now + DRAW_SECONDS}
                else:
                    offer = room['drawOffer']
                    if not offer or offer['by'] == person['id'] or offer['expiresAt'] <= now:
                        raise APIError(409, 'Không có lời mời hòa còn hạn từ đối thủ.', 'draw_expired')
                    if action == 'draw-accept':
                        self._finish(db, room, None, 'draw_agreed')
                    room['drawOffer'] = None
            elif action in ('takeback', 'takeback-accept', 'takeback-decline'):
                self._require_player(room, person['id'])
                self._playing(room)
                if action == 'takeback':
                    indices = [i for i, m in enumerate(room['moves']) if m['side'] == side]
                    if not indices or len(room['moves']) - indices[-1] > 2:
                        raise APIError(409, 'Chưa có nước vừa đi để xin đi lại.')
                    if room['takebackOffer']:
                        raise APIError(409, 'Đã có yêu cầu đi lại đang chờ.')
                    room['takebackOffer'] = {'by': person['id'], 'targetPly': indices[-1], 'requestedAt': now}
                else:
                    offer = room['takebackOffer']
                    if not offer or offer['by'] == person['id']:
                        raise APIError(409, 'Không có yêu cầu đi lại từ đối thủ.')
                    if action == 'takeback-accept':
                        target = offer['targetPly']
                        undone = room['moves'][target]
                        room.setdefault('events', []).append({'type': 'takeback_accepted', 'at': now,
                            'requestedBy': offer['by'], 'acceptedBy': person['id'],
                            'removedMoves': [m['move'] for m in room['moves'][target:]]})
                        room['fen'] = undone['fenBefore']
                        room['clock'] = dict(undone['clockBefore'], at=now)
                        room['moves'] = room['moves'][:target]
                        room['drawOffer'] = None
                    room['takebackOffer'] = None
            elif action == 'chat':
                message = data.get('message')
                if message not in MESSAGES:
                    raise APIError(400, 'Chọn lời nhắn nhanh; bản thử chưa nhận chat tự do.', 'canned_chat_only')
                recent = [m for m in room['messages'] if m['userId'] == person['id'] and now - m['at'] < 10]
                if len(recent) >= 3:
                    raise APIError(429, 'Hãy đợi một chút trước khi gửi tiếp.', 'chat_limited')
                room['messages'].append({'id': secrets.token_hex(8), 'userId': person['id'],
                                         'displayName': person['displayName'], 'message': MESSAGES[message], 'at': now})
                room['messages'] = room['messages'][-100:]
            elif action == 'kick':
                if person['id'] != room['ownerId']:
                    raise APIError(403, 'Chỉ chủ phòng được mời người xem rời phòng.')
                target = data.get('userId')
                if target not in room['spectators']:
                    raise APIError(400, 'Chỉ được mời người xem rời phòng.')
                room['spectators'].pop(target)
                room['seen'].pop(target, None)
                room['banned'].append(target)
            elif action == 'leave':
                if side and room['status'] == 'playing':
                    raise APIError(409, 'Hãy đầu hàng hoặc hoàn tất ván trước khi rời ghế.', 'game_live')
                if side:
                    if person['id'] == room['ownerId'] and room['status'] in ('waiting', 'paused'):
                        self._finish(db, room, None, 'room_closed')
                    elif room['status'] == 'waiting':
                        room['players'][side] = None
                        room['ready'] = []
                else:
                    room['spectators'].pop(person['id'], None)
                room['seen'].pop(person['id'], None)
            elif action == 'rematch':
                self._require_player(room, person['id'])
                if room['status'] != 'finished':
                    raise APIError(409, 'Ván hiện tại chưa kết thúc.')
                if self._busy_elsewhere(db, person['id'], room['code']):
                    raise APIError(409, 'Bạn đang có một ván khác.', 'already_in_room')
                if person['id'] not in room['rematch']:
                    room['rematch'].append(person['id'])
                if len(room['rematch']) == 2:
                    for player in room['players'].values():
                        if self._busy_elsewhere(db, player['id'], room['code']):
                            raise APIError(409, 'Đối thủ đang có một ván khác.', 'opponent_busy')
                    room['players'] = {'w': room['players']['b'], 'b': room['players']['w']}
                    seconds = room['options']['seconds']
                    room.update(gameId=secrets.token_hex(16), status='waiting', ready=[], rematch=[],
                                fen=START_FEN, initialFen=START_FEN, moves=[], drawOffer=None, takebackOffer=None,
                                events=[],
                                result={'over': False, 'winner': None, 'reason': 'waiting'}, startedAt=None,
                                clock={'w': seconds * 1000, 'b': seconds * 1000, 'at': now})
            else:
                raise APIError(404, 'Thao tác phòng chưa được hỗ trợ.', 'unknown_room_action')
            room['revision'] += 1
            if nonce_key:
                room['nonces'][nonce_key] = digest
                room['nonces'] = dict(list(room['nonces'].items())[-128:])
            self._save(db, room)
            return self._snapshot(room, person['id'])

    @staticmethod
    def _playing(room):
        if room['status'] != 'playing':
            raise APIError(409, 'Ván chưa bắt đầu, đã tạm dừng hoặc đã kết thúc.', 'game_not_live')

    def has_live_context(self, user):
        uid = self.identity(user)['id']
        with self.connect() as db:
            for row in db.execute("SELECT data FROM online_rooms WHERE status IN ('playing','paused')").fetchall():
                room = json.loads(row['data'])
                self._tick(db, room, self.clock())
                self._save(db, room)
                if room['status'] in ('playing', 'paused') and self._member(room, uid):
                    return True
        return False

    def history(self, user, db=None):
        uid = self.identity(user)['id']
        connection = nullcontext(db) if db is not None else self.connect()
        with connection as connection_db:
            records = [json.loads(row['data']) for row in connection_db.execute(
                'SELECT data FROM online_results WHERE red_id=? OR black_id=? ORDER BY ended_at DESC LIMIT 100', (uid, uid))]
        return {'games': [self._review_record(x, uid) for x in records]}

    @staticmethod
    def _review_record(record, uid):
        side = 'w' if record['players']['w']['id'] == uid else 'b'
        return {'id': 'online-' + record['gameId'], 'gameId': record['gameId'], 'roomCode': record['code'],
                'mode': 'online', 'player': side, 'initialFen': record['initialFen'],
                'moves': [{'move': m['move'], 'side': m['side'], 'at': m['at']} for m in record['moves']],
                'status': record['result'], 'startedAt': record['startedAt'], 'endedAt': record['endedAt'],
                'opponent': record['players'][other(side)]['displayName'], 'serverVerified': True}

    def delete_identity(self, user_id, db=None):
        """Explicit account deletion helper; do not silently retain identifiers."""
        connection = nullcontext(db) if db is not None else self.connect()
        with connection as connection_db:
            # Retain no personal game record on account deletion in this pilot.
            connection_db.execute('DELETE FROM online_results WHERE red_id=? OR black_id=?', (user_id, user_id))
            for row in connection_db.execute('SELECT code,data FROM online_rooms').fetchall():
                room = json.loads(row['data'])
                if self._side(room, user_id):
                    connection_db.execute('DELETE FROM online_rooms WHERE code=?', (row['code'],))
                elif user_id in room['spectators'] or user_id in room['banned'] or any(m['userId'] == user_id for m in room['messages']):
                    room['spectators'].pop(user_id, None)
                    room['seen'].pop(user_id, None)
                    room['banned'] = [x for x in room['banned'] if x != user_id]
                    room['messages'] = [m for m in room['messages'] if m['userId'] != user_id]
                    room['nonces'] = {key: value for key, value in room['nonces'].items()
                                      if not key.startswith(user_id + ':')}
                    room['revision'] += 1
                    self._save(connection_db, room)
