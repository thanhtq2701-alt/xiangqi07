"""Pilot account persistence. SQLite is authoritative; learner state is client-reported.

No external auth, email, telemetry or model training is performed here. Sessions are
opaque random tokens (only hashes are stored). Use one durable SQLite volume.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
import math
import re
import secrets
import sqlite3
import struct
import time
from pathlib import Path

USERNAME = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{2,29}\Z")
SESSION_SECONDS = 7 * 86400
MAX_STATE_BYTES = 2 * 1024 * 1024
FORBIDDEN_KEYS = {'__proto__', 'prototype', 'constructor'}
# OWASP's 16 MiB scrypt configuration keeps pilot RAM bounded while using the
# corresponding CPU work factor. Existing p=1 pilot hashes upgrade at login.
# https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt
SCRYPT_PREFIX = 'scrypt$16384$8$5$'


class APIError(Exception):
    def __init__(self, status, message, code='invalid_request', **extra):
        super().__init__(message)
        self.status, self.message, self.code, self.extra = status, message, code, extra


def utc(value=None):
    return datetime.fromtimestamp(time.time() if value is None else value, timezone.utc).isoformat().replace('+00:00', 'Z')


def sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def password_hash(password):
    if not isinstance(password, str) or not 10 <= len(password) <= 256:
        raise APIError(400, 'Mật khẩu cần từ 10 đến 256 ký tự.', 'password_policy')
    salt = secrets.token_hex(16)
    try:
        encoded = password.encode('utf-8')
    except UnicodeEncodeError:
        raise APIError(400, 'Mật khẩu chứa ký tự không hợp lệ.', 'password_policy')
    derived = hashlib.scrypt(encoded, salt=bytes.fromhex(salt), n=16384, r=8, p=5, dklen=32)
    return SCRYPT_PREFIX + salt + '$' + derived.hex()


def verify_password(password, encoded):
    if not isinstance(password, str) or len(password) > 256:
        return False
    try:
        algorithm, n, r, p, salt, expected = encoded.split('$')
        if algorithm != 'scrypt' or (n, r, p) not in (('16384', '8', '1'), ('16384', '8', '5')):
            return False
        actual = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def totp(secret, step):
    """RFC 6238 SHA-1, six digits. Secret is injected by operator, never persisted."""
    key = base64.b32decode(secret.upper() + '=' * (-len(secret) % 8))
    digest = hmac.new(key, struct.pack('>Q', step), hashlib.sha1).digest()
    offset = digest[-1] & 15
    return f'{(struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff) % 1000000:06d}'


def valid_totp_secret(secret):
    try:
        return len(base64.b32decode(secret.upper() + '=' * (-len(secret) % 8))) >= 20
    except Exception:
        return False


def validate_json(value, depth=0):
    if depth > 20:
        raise APIError(400, 'Dữ liệu có quá nhiều tầng lồng nhau.')
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    if isinstance(value, list):
        if len(value) > 20000:
            raise APIError(400, 'Danh sách quá dài.')
        for item in value:
            validate_json(item, depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > 10000:
            raise APIError(400, 'Quá nhiều mục dữ liệu.')
        for key, item in value.items():
            if key in FORBIDDEN_KEYS or not isinstance(key, str) or len(key) > 200:
                raise APIError(400, 'Khóa dữ liệu không hợp lệ.')
            validate_json(item, depth + 1)
        return
    raise APIError(400, 'Dữ liệu JSON không hợp lệ.')


def username(value):
    if not isinstance(value, str) or not USERNAME.fullmatch(value):
        raise APIError(400, 'Tên đăng nhập dùng 3–30 chữ Latin, số, dấu chấm, gạch dưới hoặc gạch ngang.')
    return value.lower()


def display_name(value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 60 or any(ord(c) < 32 for c in value):
        raise APIError(400, 'Tên hiển thị cần từ 1 đến 60 ký tự.')
    return value.strip()


def metrics(state):
    """Count synced observations; never certify skill or include free-text answers."""
    if not isinstance(state, dict):
        state = {}
    state = state.get('learning', state.get('state', state))
    if not isinstance(state, dict):
        state = {}
    games = state.get('games', [])
    games = games if isinstance(games, list) else []
    records = state.get('records', {})
    records = records if isinstance(records, dict) else {}
    attempts = []
    independent = []
    seen = set()
    for record in records.values():
        if not isinstance(record, dict):
            continue
        independent_recorded = False
        for attempt in record.get('attempts', []) if isinstance(record.get('attempts'), list) else []:
            if not isinstance(attempt, dict):
                continue
            identity = attempt.get('id')
            if not isinstance(identity, str) or identity in seen:
                continue
            seen.add(identity)
            attempts.append(attempt)
            if not independent_recorded and attempt.get('assisted') is False and attempt.get('firstExposure') is True:
                independent.append(attempt)
                independent_recorded = True
    correct = sum(a.get('success') is True for a in independent)
    current = state.get('session')
    return {
        'games': len(games), 'finishedGames': sum(isinstance(g, dict) and isinstance(g.get('status'), dict) and g['status'].get('over') is True for g in games),
        'learningAttempts': len(attempts), 'reviews': sum(a.get('source') == 'review' for a in attempts),
        'completedPositions': sum(isinstance(r, dict) and bool(r.get('completedAt')) for r in records.values()),
        'assistedAttempts': sum(a.get('assisted') is True for a in attempts),
        'independentSamples': len(independent), 'independentCorrect': correct,
        'independentRate': correct / len(independent) if len(independent) >= 6 else None,
        'unfinished': bool(isinstance(current, dict) and current.get('stage') not in ('complete', 'summary')),
        'verifiedLevel': None, 'source': 'client-reported',
    }


def personal_export(value):
    """Export personal observations, not answer keys carried by internal sync.

    This is not a database backup/import format. Generated lesson snapshots,
    evaluation branches and dynamic review moments must not reveal an unopened
    answer through the ordinary account export button. Learner answers, chosen
    moves, attempts, pending drafts and their schedule remain intact.
    """
    generated = {'puzzle', 'moments', 'solution', 'alternatives', 'legal', 'pv',
                 'what', 'why', 'how', 'engine', 'candidates',
                 'best_move', 'bestMove', 'ranked', 'score', 'score_type', 'loss'}
    if isinstance(value, list):
        return [personal_export(item) for item in value]
    if isinstance(value, dict):
        return {key: personal_export(item) for key, item in value.items() if key not in generated}
    return value


class CloudStore:
    def __init__(self, path, admin_totp_secret=''):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.admin_totp_secret = admin_totp_secret.strip().upper()
        if self.admin_totp_secret and not valid_totp_secret(self.admin_totp_secret):
            raise ValueError('CO_CHILL_ADMIN_TOTP_SECRET must be a base32 secret of at least 20 bytes.')
        # Constant synthetic hash keeps unknown-account login work comparable.
        self.dummy_hash = password_hash(secrets.token_hex(20))
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    display_name TEXT NOT NULL, password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','admin','report')),
                    created_at REAL NOT NULL, last_login REAL, last_activity REAL,
                    locked_until REAL, lock_reason TEXT NOT NULL DEFAULT '',
                    totp_step INTEGER NOT NULL DEFAULT -1, test_account INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY, user_id TEXT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    csrf TEXT NOT NULL, expires_at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS states (
                    user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL DEFAULT 0, data TEXT NOT NULL DEFAULT '{}', updated_at REAL);
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    category TEXT NOT NULL, message TEXT NOT NULL, context TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new', created_at REAL NOT NULL, updated_at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                    subject_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    action TEXT NOT NULL, created_at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS rate_limits (
                    bucket TEXT PRIMARY KEY, starts_at REAL NOT NULL, count INTEGER NOT NULL);
            ''')
            db.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('rate_key', secrets.token_hex(32)))
            self.rate_key = db.execute("SELECT value FROM settings WHERE key='rate_key'").fetchone()[0]
            from app.content_store import install
            install(db)

    @contextmanager
    def connect(self, transaction=False):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA secure_delete=ON')
        try:
            if transaction:
                db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def throttle(self, scope, identity, maximum, period):
        # Separate transaction means failed login still consumes rate-limit budget.
        key = hmac.new(self.rate_key.encode(), (scope + ':' + identity).encode(), hashlib.sha256).hexdigest()
        now = time.time()
        with self.connect(True) as db:
            db.execute('DELETE FROM rate_limits WHERE starts_at < ?', (now - 86400,))
            row = db.execute('SELECT * FROM rate_limits WHERE bucket=?', (key,)).fetchone()
            if row and row['starts_at'] + period > now:
                if row['count'] >= maximum:
                    raise APIError(429, 'Có nhiều yêu cầu liên tiếp. Hãy chờ rồi thử lại.', 'rate_limited', retryAfter=max(1, int(row['starts_at'] + period - now)))
                db.execute('UPDATE rate_limits SET count=count+1 WHERE bucket=?', (key,))
            else:
                db.execute('INSERT OR REPLACE INTO rate_limits VALUES (?,?,1)', (key, now))

    @staticmethod
    def user_view(row):
        return {'id': row['id'], 'username': row['username'], 'displayName': row['display_name'], 'role': row['role'], 'createdAt': utc(row['created_at']), 'emailVerified': False, 'authMethod': 'password', 'mfaRequired': row['role'] == 'admin', 'testAccount': bool(row['test_account'])}

    def create_user(self, db, data, role='user'):
        name = username(data.get('username'))
        display = display_name(data.get('displayName', name))
        hashed = password_hash(data.get('password'))
        uid, now = secrets.token_hex(16), time.time()
        try:
            db.execute('INSERT INTO users(id,username,display_name,password_hash,role,created_at,last_activity) VALUES (?,?,?,?,?,?,?)', (uid, name, display, hashed, role, now, now))
        except sqlite3.IntegrityError:
            raise APIError(409, 'Tên đăng nhập đã được dùng. Hãy chọn tên khác.', 'username_taken')
        db.execute('INSERT INTO states(user_id) VALUES (?)', (uid,))
        return db.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()

    def new_session(self, db, user):
        token, csrf = secrets.token_hex(32), secrets.token_hex(32)
        now = time.time()
        db.execute('DELETE FROM sessions WHERE user_id=? OR expires_at<?', (user['id'], now))
        db.execute('INSERT INTO sessions VALUES (?,?,?,?)', (sha(token), user['id'], csrf, now + SESSION_SECONDS))
        db.execute('UPDATE users SET last_login=?,last_activity=? WHERE id=?', (now, now, user['id']))
        return token, csrf

    def login(self, db, data):
        value = data.get('username')
        value = value.lower() if isinstance(value, str) else ''
        row = db.execute('SELECT * FROM users WHERE username=?', (value,)).fetchone()
        valid = verify_password(data.get('password'), row['password_hash'] if row else self.dummy_hash)
        if not row or not valid:
            raise APIError(401, 'Tên đăng nhập, mật khẩu hoặc mã xác thực chưa đúng.', 'invalid_credentials')
        if row['locked_until'] and row['locked_until'] > time.time():
            raise APIError(403, 'Tài khoản đang tạm khóa. Liên hệ quản trị để được hỗ trợ.', 'account_locked', reason=row['lock_reason'], until=utc(row['locked_until']))
        if row['role'] == 'admin':
            code = data.get('totpCode', '')
            step = int(time.time() / 30)
            match = None
            if self.admin_totp_secret and isinstance(code, str) and re.fullmatch(r'\d{6}', code):
                for candidate in (step - 1, step, step + 1):
                    if candidate > row['totp_step'] and hmac.compare_digest(totp(self.admin_totp_secret, candidate), code):
                        match = candidate
                        break
            if match is None:
                raise APIError(401, 'Tên đăng nhập, mật khẩu hoặc mã xác thực chưa đúng.', 'invalid_credentials')
            db.execute('UPDATE users SET totp_step=? WHERE id=?', (match, row['id']))
        if not row['password_hash'].startswith(SCRYPT_PREFIX):
            db.execute('UPDATE users SET password_hash=? WHERE id=?', (password_hash(data['password']), row['id']))
            row = db.execute('SELECT * FROM users WHERE id=?', (row['id'],)).fetchone()
        return row

    def session(self, db, token):
        if not isinstance(token, str) or not re.fullmatch(r'[0-9a-f]{64}', token):
            return None
        row = db.execute('SELECT u.*, s.csrf, s.expires_at FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=?', (sha(token),)).fetchone()
        if not row or row['expires_at'] <= time.time() or (row['locked_until'] and row['locked_until'] > time.time()):
            return None
        return row

    def state(self, db, uid):
        row = db.execute('SELECT * FROM states WHERE user_id=?', (uid,)).fetchone()
        return {'revision': row['revision'], 'state': json.loads(row['data']), 'updatedAt': utc(row['updated_at']) if row['updated_at'] else None}

    def save_state(self, db, uid, data):
        revision, value = data.get('revision'), data.get('state')
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0 or not isinstance(value, dict):
            raise APIError(400, 'Cần phiên bản revision và state dạng object.')
        validate_json(value)
        serialized = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
        if len(serialized.encode('utf-8')) > MAX_STATE_BYTES:
            raise APIError(413, 'Dữ liệu vượt giới hạn 2 MB. Hãy xuất bản sao và giảm dữ liệu trước khi đồng bộ.', 'state_too_large')
        now = time.time()
        cursor = db.execute('UPDATE states SET data=?,revision=revision+1,updated_at=? WHERE user_id=? AND revision=?', (serialized, now, uid, revision))
        if cursor.rowcount != 1:
            current = self.state(db, uid)
            raise APIError(409, 'Có bản mới trên máy chủ. Giữ nháp và chọn dữ liệu cần dùng.', 'revision_conflict', revision=current['revision'], updatedAt=current['updatedAt'])
        db.execute('UPDATE users SET last_activity=? WHERE id=?', (now, uid))
        return {'revision': revision + 1, 'updatedAt': utc(now)}

    def update_account(self, db, user, data):
        allowed = {'displayName', 'username', 'currentPassword', 'newPassword'}
        if set(data) - allowed:
            raise APIError(400, 'Trường tài khoản không được hỗ trợ.')
        new_username = username(data['username']) if 'username' in data else user['username']
        sensitive = new_username != user['username'] or 'newPassword' in data
        if sensitive and not verify_password(data.get('currentPassword'), user['password_hash']):
            raise APIError(401, 'Mật khẩu hiện tại chưa đúng.', 'invalid_credentials')
        if 'displayName' in data:
            db.execute('UPDATE users SET display_name=? WHERE id=?', (display_name(data['displayName']), user['id']))
        if 'username' in data:
            try:
                db.execute('UPDATE users SET username=? WHERE id=?', (new_username, user['id']))
            except sqlite3.IntegrityError:
                raise APIError(409, 'Tên đăng nhập đã được dùng.', 'username_taken')
        if 'newPassword' in data:
            db.execute('UPDATE users SET password_hash=? WHERE id=?', (password_hash(data['newPassword']), user['id']))
        return db.execute('SELECT * FROM users WHERE id=?', (user['id'],)).fetchone()

    def admin_users(self, db, query, limit=50, offset=0):
        # Search uses bound literals; no reflected free-text learner content.
        rows = db.execute('SELECT u.*, s.data, s.updated_at FROM users u LEFT JOIN states s ON s.user_id=u.id ORDER BY u.created_at DESC').fetchall()
        matching = [row for row in rows if query.lower() in row['username'].lower() or query.lower() in row['display_name'].lower()]
        items = []
        for row in matching[offset:offset + limit]:
            item = self.user_view(row)
            item.update(lastLogin=utc(row['last_login']) if row['last_login'] else None, lastActivity=utc(row['last_activity']) if row['last_activity'] else None,
                        locked=bool(row['locked_until'] and row['locked_until'] > time.time()), lockedUntil=utc(row['locked_until']) if row['locked_until'] else None,
                        metrics=metrics(json.loads(row['data'] or '{}')))
            items.append(item)
        return {'users': items, 'total': len(matching), 'offset': offset, 'limit': limit, 'updatedAt': utc(), 'source': 'client-reported'}

    def stats(self, db, days):
        now, since = time.time(), time.time() - days * 86400
        rows = db.execute('SELECT u.*, s.data FROM users u JOIN states s ON s.user_id=u.id').fetchall()
        # Lifetime activity counts are not falsely described as period-filtered.
        totals = {'games': 0, 'learningAttempts': 0, 'reviews': 0, 'assistedAttempts': 0, 'completedPositions': 0}
        for row in rows:
            if row['test_account']:
                continue
            value = metrics(json.loads(row['data']))
            for key in totals:
                totals[key] += value[key]
        return {'accounts': len(rows), 'newAccounts': sum(row['created_at'] >= since and not row['test_account'] for row in rows),
                'activeAccounts': sum(bool(row['last_activity'] and row['last_activity'] >= since) and not row['test_account'] for row in rows),
                'testAccounts': sum(bool(row['test_account']) for row in rows), 'days': days,
                'since': utc(since), 'updatedAt': utc(now), 'timezone': 'Asia/Ho_Chi_Minh', 'totals': totals,
                'activityCountScope': 'all-synced-history', 'activityDefinition': 'Đăng ký, đăng nhập hoặc đồng bộ tiến độ.',
                'source': 'client-reported', 'notice': 'Số đếm từ dữ liệu đã đồng bộ; chưa xác minh kỹ năng, Elo hoặc hiệu quả học.'}

    def delete_user(self, db, uid):
        # Cascades remove state, sessions, feedback and subject-specific audit.
        db.execute('DELETE FROM users WHERE id=?', (uid,))

    def backup(self, output):
        target = Path(output)
        if target.exists():
            raise ValueError('Backup destination already exists.')
        target.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            destination = sqlite3.connect(target)
            try:
                db.backup(destination)
            finally:
                destination.close()

