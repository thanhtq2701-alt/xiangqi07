"""Cờ Chill pilot WSGI server: same-origin website, accounts and SQLite sync.

Local: python co_chill_server.py serve --port 8769
Production (single instance, persistent volume): gunicorn co_chill_server:application
The legacy server.py and its learning API remain separate and unchanged.
"""
import argparse
import base64
import getpass
import hmac
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, unquote, urlsplit
from wsgiref.simple_server import make_server, WSGIRequestHandler

from app.cloud_store import APIError, CloudStore, MAX_STATE_BYTES, SESSION_SECONDS, metrics, personal_export, sha, utc, verify_password
from app import content_store
from app.rules import Position

ROOT = Path(__file__).resolve().parent
COOKIE = 'co_chill_session'
MAX_BODY = MAX_STATE_BYTES + 65536


class CloudApplication:
    def __init__(self, db_path=None, public_origin=None, admin_totp_secret=None, static_root=None, engine=None):
        self.store = CloudStore(db_path or os.environ.get('CO_CHILL_DB_PATH', str(ROOT / 'var/co_chill_accounts.sqlite3')),
                                os.environ.get('CO_CHILL_ADMIN_TOTP_SECRET', '') if admin_totp_secret is None else admin_totp_secret)
        self.public_origin = (os.environ.get('CO_CHILL_PUBLIC_ORIGIN', '') if public_origin is None else public_origin).rstrip('/')
        if self.public_origin:
            parsed = urlsplit(self.public_origin)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username:
                raise ValueError('CO_CHILL_PUBLIC_ORIGIN must be one exact origin, for example https://co-chill.example.com.')
            if parsed.scheme != 'https' and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
                raise ValueError('Public origin requires HTTPS.')
        self.static_root = (Path(static_root) if static_root else ROOT / 'online-preview').resolve()
        if engine is None:
            from app.pikafish import AnalysisEngine
            engine = AnalysisEngine()
        self.engine = engine

    def valid_host(self, environ):
        host = environ.get('HTTP_HOST', '')
        if self.public_origin:
            return host.lower() == urlsplit(self.public_origin).netloc.lower()
        try:
            parsed = urlsplit('http://' + host)
            return parsed.hostname in ('localhost', '127.0.0.1', '::1') and not parsed.username and not parsed.path and not parsed.query and not parsed.fragment
        except ValueError:
            return False

    def expected_origin(self, environ):
        return self.public_origin or environ.get('wsgi.url_scheme', 'http') + '://' + environ.get('HTTP_HOST', '')

    def cookie(self, token='', clear=False):
        value = f'{COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={0 if clear else SESSION_SECONDS}'
        if self.public_origin.startswith('https://'):
            value += '; Secure'
        return value

    @staticmethod
    def read_cookie(environ):
        cookie = SimpleCookie()
        try:
            cookie.load(environ.get('HTTP_COOKIE', ''))
            return cookie[COOKIE].value if COOKIE in cookie else ''
        except Exception:
            return ''

    @staticmethod
    def body(environ):
        if environ.get('CONTENT_TYPE', '').split(';')[0].strip().lower() != 'application/json':
            raise APIError(415, 'Yêu cầu cần JSON.')
        try:
            size = int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            raise APIError(400, 'Độ dài yêu cầu không hợp lệ.')
        if not 0 < size <= MAX_BODY:
            raise APIError(413, 'Yêu cầu trống hoặc quá lớn.')
        try:
            raw = environ['wsgi.input'].read(size)
            if len(raw) != size:
                raise ValueError('short body')
            data = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (UnicodeDecodeError, ValueError, RecursionError):
            raise APIError(400, 'JSON không hợp lệ.')
        if not isinstance(data, dict):
            raise APIError(400, 'JSON phải là object.')
        return data

    def response(self, start_response, status, payload, mime='application/json; charset=utf-8', headers=None):
        raw = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode('utf-8') if mime.startswith('application/json') else payload
        response_headers = [('Content-Type', mime), ('Content-Length', str(len(raw))), ('Cache-Control', 'no-store'),
                            ('X-Content-Type-Options', 'nosniff'), ('Referrer-Policy', 'no-referrer'), ('X-Frame-Options', 'DENY'),
                            ('Permissions-Policy', 'camera=(), microphone=(), geolocation=()'),
                            ('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")]
        if self.public_origin.startswith('https://'):
            response_headers.append(('Strict-Transport-Security', 'max-age=31536000'))
        response_headers.extend(headers or [])
        start_response(f'{status} {HTTPStatus(status).phrase}', response_headers)
        return [raw]

    def __call__(self, environ, start_response):
        try:
            if not self.valid_host(environ):
                raise APIError(403, 'Địa chỉ máy chủ chưa được cấu hình.', 'invalid_host')
            path, method = environ.get('PATH_INFO', '/'), environ.get('REQUEST_METHOD', 'GET').upper()
            if not path.startswith('/api/'):
                if method not in ('GET', 'HEAD'):
                    raise APIError(405, 'Phương thức không được hỗ trợ.')
                relative = 'index.html' if path == '/' else unquote(path).lstrip('/')
                if '\\' in relative or any(part.startswith('.') for part in relative.split('/')):
                    raise APIError(404, 'Không tìm thấy trang.')
                file = (self.static_root / relative).resolve()
                if not file.is_relative_to(self.static_root) or file.suffix.lower() not in {'.html', '.js', '.css', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico', '.woff2'} or not file.is_file():
                    raise APIError(404, 'Không tìm thấy trang.')
                mime = {'.js': 'text/javascript', '.css': 'text/css'}.get(file.suffix, mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
                if mime.startswith('text/'):
                    mime += '; charset=utf-8'
                return self.response(start_response, 200, b'' if method == 'HEAD' else file.read_bytes(), mime)
            write = method in ('POST', 'PUT', 'PATCH', 'DELETE')
            if method not in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
                raise APIError(405, 'Phương thức không được hỗ trợ.')
            if write and (environ.get('HTTP_ORIGIN', '') != self.expected_origin(environ) or environ.get('HTTP_SEC_FETCH_SITE', '') == 'cross-site'):
                raise APIError(403, 'Yêu cầu phải đến từ trang Cờ Chill đang mở.', 'origin_rejected')
            data = self.body(environ) if write else {}
            ip = environ.get('REMOTE_ADDR', 'unknown')
            if path.startswith('/api/auth/') and write:
                self.store.throttle('auth-ip', ip, 40, 900)
                if path == '/api/auth/login':
                    identity = data.get('username', '')
                    identity = identity.lower() if isinstance(identity, str) else ''
                    self.store.throttle('auth-user', identity[:100], 10, 900)
                elif path == '/api/auth/register':
                    self.store.throttle('register-ip', ip, 20, 3600)
            token = self.read_cookie(environ)
            # Rate-limit before transaction: failure counters survive rollback.
            if path in ('/api/account', '/api/engine/analyze', '/api/feedback') and write:
                self.store.throttle('action-' + path, sha(token) if token else ip, 30 if path == '/api/engine/analyze' else 20, 60)
            with self.store.connect(transaction=write and path != '/api/engine/analyze') as db:
                user = self.store.session(db, token)
                if write and path not in ('/api/auth/register', '/api/auth/login'):
                    if not user:
                        raise APIError(401, 'Phiên đã hết hạn hoặc tài khoản vừa đăng nhập ở thiết bị khác.', 'session_expired')
                    csrf = environ.get('HTTP_X_CSRF_TOKEN', '')
                    if not csrf or not hmac.compare_digest(csrf, user['csrf']):
                        raise APIError(403, 'Mã bảo vệ phiên không hợp lệ. Hãy tải lại trang.', 'csrf_rejected')
                status, result, extra = self.dispatch(db, user, token, path, method, data, environ)
            return self.response(start_response, status, result, headers=extra)
        except APIError as exc:
            headers = [('Retry-After', str(exc.extra['retryAfter']))] if 'retryAfter' in exc.extra else []
            return self.response(start_response, exc.status, dict(error=exc.message, code=exc.code, **exc.extra), headers=headers)
        except Exception:
            # No request body, cookies, passwords, raw exception or learner text in logs.
            return self.response(start_response, 500, {'error': 'Không xử lý được yêu cầu. Dữ liệu chưa lưu đã được hoàn tác.', 'code': 'server_error'})

    def session_result(self, user, csrf=None):
        return {'authenticated': bool(user), 'user': self.store.user_view(user) if user else None, 'csrf': csrf or (user['csrf'] if user else None),
                'capabilities': {'accounts': True, 'cloudSync': True, 'passwordLogin': True, 'emailLogin': False, 'oauth': False, 'passwordRecovery': False, 'adminMfa': True, 'guestCloudSync': False},
                'privacy': {'training': False, 'guestStorage': 'browser-only', 'deletion': 'server-hard-delete', 'maxStateBytes': MAX_STATE_BYTES}}

    def dispatch(self, db, user, token, path, method, data, environ):
        headers = []
        if path == '/api/health' and method == 'GET':
            return 200, {'ok': True, 'service': 'co-chill-v5', 'persistence': 'sqlite-single-instance'}, headers
        if path == '/api/session' and method == 'GET':
            return 200, self.session_result(user), headers
        if path == '/api/content' and method == 'GET':
            return 200, {'puzzles': content_store.list_content(db, published=True), 'updatedAt': utc()}, headers
        if path in ('/api/auth/register', '/api/auth/login') and method == 'POST':
            if user:
                raise APIError(409, 'Hãy đăng xuất trước khi đổi tài khoản.', 'already_authenticated')
            if path.endswith('register'):
                user = self.store.create_user(db, data)
            else:
                user = self.store.login(db, data)
            new_token, csrf = self.store.new_session(db, user)
            headers.append(('Set-Cookie', self.cookie(new_token)))
            return (201 if path.endswith('register') else 200), self.session_result(user, csrf), headers
        if not user:
            raise APIError(401, 'Hãy đăng nhập để dùng tính năng này.', 'authentication_required')
        uid = user['id']
        if path == '/api/auth/logout' and method == 'POST':
            db.execute('DELETE FROM sessions WHERE token_hash=?', (sha(token),))
            headers.append(('Set-Cookie', self.cookie(clear=True)))
            return 200, {'ok': True}, headers
        if path == '/api/account' and method == 'PATCH':
            updated = self.store.update_account(db, user, data)
            if 'newPassword' in data:
                new_token, csrf = self.store.new_session(db, updated)
                headers.append(('Set-Cookie', self.cookie(new_token)))
                return 200, self.session_result(updated, csrf), headers
            return 200, {'user': self.store.user_view(updated)}, headers
        if path == '/api/account' and method == 'DELETE':
            if not verify_password(data.get('password'), user['password_hash']):
                raise APIError(401, 'Mật khẩu hiện tại chưa đúng.', 'invalid_credentials')
            if user['role'] == 'admin':
                raise APIError(409, 'Tài khoản chủ quản trị cần được bàn giao quyền trên máy chủ trước khi xóa.', 'owner_deletion_requires_operator')
            self.store.delete_user(db, uid)
            headers.append(('Set-Cookie', self.cookie(clear=True)))
            return 200, {'ok': True, 'deleted': True, 'notice': 'Đã xóa tài khoản, tiến độ và phản hồi trên cơ sở dữ liệu đang chạy. Bản xuất hoặc bản sao lưu do người vận hành giữ cần được xóa riêng.'}, headers
        if path == '/api/state' and method == 'GET':
            return 200, self.store.state(db, uid), headers
        if path == '/api/state' and method == 'PUT':
            return 200, self.store.save_state(db, uid, data), headers
        if path == '/api/export' and method == 'GET':
            state = self.store.state(db, uid)
            state['state'] = personal_export(state['state'])
            feedback = [self.feedback_view(row) for row in db.execute('SELECT id,category,message,context,status,created_at,updated_at FROM feedback WHERE user_id=? ORDER BY created_at', (uid,))]
            return 200, {'format': 'co-chill-account-export-v1', 'exportedAt': utc(), 'account': self.store.user_view(user), **state, 'feedback': feedback,
                         'answerKeysIncluded': False, 'notice': 'Bản sao dữ liệu cá nhân để đọc; không bao gồm khóa đáp án hoặc dùng như bản sao lưu toàn database.'}, headers
        if path == '/api/feedback' and method == 'POST':
            category, message = data.get('category', 'other'), data.get('message')
            if category not in ('rules', 'analysis', 'interface', 'account', 'content', 'other') or not isinstance(message, str) or not 1 <= len(message.strip()) <= 3000:
                raise APIError(400, 'Chọn loại phản hồi và viết từ 1 đến 3.000 ký tự.')
            context = data.get('context', '')
            if isinstance(context, dict):
                if set(context) - {'route', 'puzzleId'} or any(value is not None and (not isinstance(value, str) or len(value) > 200) for value in context.values()):
                    raise APIError(400, 'Phản hồi chỉ đính kèm trang và mã bài; không đính kèm câu trả lời riêng tư.')
                context = json.dumps(context, ensure_ascii=False)
            if not isinstance(context, str) or len(context) > 500:
                raise APIError(400, 'Thông tin vị trí phản hồi quá dài.')
            fid, now = secrets.token_hex(16), time.time()
            db.execute('INSERT INTO feedback VALUES (?,?,?,?,?,?,?,?)', (fid, uid, category, message.strip(), context, 'new', now, now))
            return 201, {'id': fid, 'status': 'new', 'createdAt': utc(now)}, headers
        if path == '/api/feedback' and method == 'GET':
            return 200, {'feedback': [self.feedback_view(row) for row in db.execute('SELECT id,category,message,context,status,created_at,updated_at FROM feedback WHERE user_id=? ORDER BY created_at DESC LIMIT 100', (uid,))]}, headers
        if path == '/api/engine/status' and method == 'GET':
            return 200, self.engine.status(), headers
        if path == '/api/engine/analyze' and method == 'POST':
            purpose = data.get('purpose', 'review-scan')
            if purpose not in ('review', 'review-scan', 'practice', 'bot'):
                raise APIError(400, 'Mục đích phân tích không hợp lệ.')
            state = self.store.state(db, uid)['state']
            state = state.get('learning', state.get('state', state))
            games = state.get('games', []) if isinstance(state, dict) else []
            games = games if isinstance(games, list) else []
            active = any(isinstance(g, dict) and isinstance(g.get('status'), dict) and g['status'].get('over') is not True for g in games)
            if active and purpose != 'bot':
                raise APIError(409, 'Kết thúc ván đang chơi trước khi mở phân tích hoặc hướng dẫn.', 'live_game_no_coaching')
            self.validate_engine_context(state, games, data, purpose)
            if data.get('mode', 'quick') not in ('quick', 'deep'):
                raise APIError(400, 'Chế độ phân tích không hợp lệ.')
            try:
                result = self.engine.analyze(data.get('fen'), moves=data.get('moves'), selected_move=data.get('selected_move', data.get('selectedMove')), mode=data.get('mode', 'quick'))
            except ValueError as exc:
                raise APIError(400, str(exc), 'invalid_position')
            except Exception as exc:
                if exc.__class__.__name__ == 'EngineUnavailable':
                    raise APIError(429, 'Máy phân tích đang bận. Bản nháp của bạn vẫn được giữ.', 'engine_busy', retryAfter=5)
                raise
            if purpose == 'bot':
                result = {key: result.get(key) for key in ('best_move', 'engine', 'engine_name', 'fallback', 'status', 'warnings', 'provenance')}
            return 200, result, headers
        if not path.startswith('/api/admin/'):
            raise APIError(404, 'Không tìm thấy chức năng.')
        if user['role'] not in ('admin', 'report'):
            raise APIError(403, 'Bạn không có quyền quản trị.', 'forbidden')
        if method != 'GET' and user['role'] != 'admin':
            raise APIError(403, 'Vai trò này chỉ được xem báo cáo.', 'read_only_role')
        if user['role'] == 'report' and not (path in ('/api/admin/stats', '/api/admin/users') or re.fullmatch(r'/api/admin/users/[0-9a-f]{32}', path)):
            raise APIError(403, 'Vai trò báo cáo chỉ xem thống kê, danh sách tài khoản và biên bản; không xem phản hồi riêng hoặc bản nháp nội dung.', 'report_scope')
        query = parse_qs(environ.get('QUERY_STRING', ''))
        if path == '/api/admin/stats' and method == 'GET':
            try:
                days = int(query.get('days', ['7'])[0])
            except ValueError:
                raise APIError(400, 'Số ngày không hợp lệ.')
            if days not in (1, 7, 30, 90, 365):
                raise APIError(400, 'Chọn 1, 7, 30, 90 hoặc 365 ngày.')
            return 200, self.store.stats(db, days), headers
        if path == '/api/admin/users' and method == 'GET':
            try:
                offset = max(0, int(query.get('offset', ['0'])[0]))
                limit = min(100, max(1, int(query.get('limit', ['50'])[0])))
            except ValueError:
                raise APIError(400, 'Phân trang không hợp lệ.')
            return 200, self.store.admin_users(db, query.get('q', [''])[0][:100], limit, offset), headers
        match = re.fullmatch(r'/api/admin/users/([0-9a-f]{32})(/lock)?', path)
        if match:
            target = db.execute('SELECT * FROM users WHERE id=?', (match[1],)).fetchone()
            if not target:
                raise APIError(404, 'Không có tài khoản này.')
            if not match[2] and method == 'GET':
                state = self.store.state(db, target['id'])['state']
                state = state.get('learning', state.get('state', state))
                games = state.get('games', []) if isinstance(state, dict) else []
                public_games = []
                for g in games if isinstance(games, list) else []:
                    if not isinstance(g, dict):
                        continue
                    moves = g.get('moves', [])
                    moves = [m.get('move') if isinstance(m, dict) else m for m in moves] if isinstance(moves, list) else []
                    public_games.append({'id': str(g.get('id', ''))[:100], 'title': str(g.get('title', 'Ván đã đồng bộ'))[:120], 'fen': str(g.get('fen', ''))[:200], 'initialFen': str(g.get('initialFen', g.get('startFen', '')))[:200],
                                         'moves': [m for m in moves if isinstance(m, str) and re.fullmatch('[a-i][0-9][a-i][0-9]', m)],
                                         'over': bool(isinstance(g.get('status'), dict) and g['status'].get('over'))})
                return 200, {'user': self.store.user_view(target), 'metrics': metrics(state), 'games': public_games, 'privateAnswersIncluded': False}, headers
            if match[2] and method == 'POST':
                if target['role'] == 'admin' or target['id'] == uid:
                    raise APIError(409, 'Không khóa tài khoản quản trị bằng chức năng này.')
                if not isinstance(data.get('locked'), bool):
                    raise APIError(400, 'Cần chọn khóa hoặc mở khóa.')
                locked = data['locked']
                until = None
                reason = data.get('reason', '')
                if locked:
                    if not isinstance(reason, str) or not 3 <= len(reason.strip()) <= 500:
                        raise APIError(400, 'Cần nêu lý do khóa từ 3 đến 500 ký tự.')
                    try:
                        from datetime import datetime
                        expires = datetime.fromisoformat(str(data.get('until', '')).replace('Z', '+00:00'))
                        if expires.tzinfo is None:
                            raise ValueError('timezone required')
                        until = expires.timestamp()
                    except (ValueError, OverflowError):
                        raise APIError(400, 'Cần thời điểm kết thúc khóa có múi giờ.')
                    if not time.time() < until <= time.time() + 365 * 86400:
                        raise APIError(400, 'Thời hạn khóa cần ở tương lai và không quá một năm.')
                db.execute('UPDATE users SET locked_until=?,lock_reason=? WHERE id=?', (until, reason.strip() if locked else '', target['id']))
                db.execute('DELETE FROM sessions WHERE user_id=?', (target['id'],))
                db.execute('INSERT INTO audit(actor_id,subject_id,action,created_at) VALUES (?,?,?,?)', (uid, target['id'], 'lock' if locked else 'unlock', time.time()))
                return 200, {'ok': True, 'locked': locked, 'until': utc(until) if until else None}, headers
        if path == '/api/admin/feedback' and method == 'GET':
            return 200, {'feedback': [self.feedback_view(row) for row in db.execute('SELECT id,user_id,category,message,context,status,created_at,updated_at FROM feedback ORDER BY created_at DESC LIMIT 200')]}, headers
        if path == '/api/admin/content' and method == 'GET':
            return 200, {'content': content_store.list_content(db)}, headers
        if path == '/api/admin/content' and method == 'POST':
            return 201, {'content': content_store.create(db, uid, data)}, headers
        match = re.fullmatch(r'/api/admin/content/(custom-[0-9a-f]{32})', path)
        if match and method == 'PATCH':
            return 200, {'content': content_store.update(db, uid, match[1], data)}, headers
        match = re.fullmatch(r'/api/admin/feedback/([0-9a-f]{32})', path)
        if match and method == 'PATCH':
            if data.get('status') not in ('new', 'reviewing', 'resolved', 'declined'):
                raise APIError(400, 'Trạng thái phản hồi không hợp lệ.')
            cursor = db.execute('UPDATE feedback SET status=?,updated_at=? WHERE id=?', (data['status'], time.time(), match[1]))
            if not cursor.rowcount:
                raise APIError(404, 'Không tìm thấy phản hồi.')
            db.execute('INSERT INTO audit(actor_id,action,created_at) VALUES (?,?,?)', (uid, 'feedback-status', time.time()))
            return 200, {'ok': True, 'status': data['status']}, headers
        raise APIError(404, 'Không tìm thấy chức năng.')

    @staticmethod
    def feedback_view(row):
        result = dict(row)
        result['createdAt'] = utc(result.pop('created_at'))
        result['updatedAt'] = utc(result.pop('updated_at'))
        if 'user_id' in result:
            result['userId'] = result.pop('user_id')
        return result

    @staticmethod
    def validate_engine_context(state, games, data, purpose):
        """Validate analysis against synced context, not a client 'reflected' flag.

        Review scans necessarily send candidate analysis to the frontend before
        reflection; the UI must keep it hidden. This is an educational boundary,
        not server-authoritative anti-cheat (the user's own sync state is editable).
        """
        try:
            requested = Position.from_fen(data.get('fen'))
        except ValueError as exc:
            raise APIError(400, str(exc), 'invalid_position')
        moves = data.get('moves') or []
        if not isinstance(moves, list) or len(moves) > 600 or any(not isinstance(m, str) for m in moves):
            raise APIError(400, 'Lịch sử nước đi không hợp lệ.', 'invalid_history')
        if purpose == 'practice':
            session = state.get('session') if isinstance(state, dict) else None
            session = session if isinstance(session, dict) else {}
            answers = session.get('firstAnswers') or session.get('answers')
            responded = session.get('unknown') is True or (isinstance(answers, list) and len(answers) == 3 and all(isinstance(a, str) and a.strip() for a in answers))
            puzzle = session.get('puzzle')
            try:
                expected = Position.from_fen(puzzle.get('fen') if isinstance(puzzle, dict) else None)
            except ValueError:
                expected = None
            candidate = session.get('firstCandidate') or session.get('candidate')
            responded = responded and (session.get('unknown') is True or (expected is not None and candidate in expected.legal_moves()))
            if session.get('stage') not in ('explain', 'retry', 'complete', 'summary') or not responded or not expected or expected.fen() != requested.fen() or moves:
                raise APIError(409, 'Hãy gửi suy nghĩ hoặc xin trợ giúp trong bài trước khi mở phân tích.', 'reflection_required')
            return
        game = next((g for g in games if isinstance(g, dict) and g.get('id') == data.get('gameId')), None)
        if not game:
            raise APIError(409, 'Đồng bộ ván trước khi yêu cầu máy phân tích.', 'game_not_synced')
        recorded = game.get('moves', [])
        if not isinstance(recorded, list) or len(recorded) > 600:
            raise APIError(400, 'Lịch sử ván quá dài hoặc chưa hợp lệ.', 'invalid_history')
        recorded = [m.get('move') if isinstance(m, dict) else m for m in recorded]
        if any(not isinstance(m, str) for m in recorded):
            raise APIError(400, 'Lịch sử ván chưa hợp lệ.', 'invalid_history')
        status = game.get('status')
        status = status if isinstance(status, dict) else {}
        try:
            initial = Position.from_fen(game.get('initialFen', game.get('startFen')))
            if purpose == 'bot':
                current = initial
                for move in recorded:
                    current = current.play(move)
                if status.get('over') is True or game.get('mode') != 'bot' or game.get('player') not in ('w', 'b') or current.turn == game['player']:
                    raise APIError(409, 'Chỉ tính nước cho lượt của máy trong ván đang chơi.', 'not_bot_turn')
                if not ((requested.fen() == current.fen() and not moves) or (requested.fen() == initial.fen() and moves == recorded)):
                    raise APIError(409, 'Thế cờ không khớp lượt máy đã đồng bộ.', 'position_mismatch')
            else:
                if status.get('over') is not True:
                    raise APIError(409, 'Ván chưa kết thúc.', 'live_game_no_coaching')
                if requested.fen() != initial.fen() or len(moves) > len(recorded) or moves != recorded[:len(moves)]:
                    raise APIError(409, 'Vị trí phân tích không khớp biên bản đã đồng bộ.', 'position_mismatch')
                selected = data.get('selected_move', data.get('selectedMove'))
                if selected is not None and (len(moves) >= len(recorded) or selected != recorded[len(moves)]):
                    raise APIError(409, 'Nước cần so sánh không khớp biên bản.', 'position_mismatch')
                current = initial
                for move in moves:
                    current = current.play(move)
                if selected is not None:
                    current.play(selected)
        except (ValueError, TypeError) as exc:
            raise APIError(400, 'Biên bản hoặc thế cờ chứa nước không hợp lệ.', 'invalid_history') from exc


_application = None


def application(environ, start_response):
    """Lazy factory avoids creating a database just by importing test helpers."""
    global _application
    if _application is None:
        _application = CloudApplication()
    return _application(environ, start_response)


class QuietHandler(WSGIRequestHandler):
    def log_message(self, fmt, *args):
        pass  # Never log cookies, query strings or learner content.


def main():
    parser = argparse.ArgumentParser(description='Cờ Chill accounts, sync and website (single-instance SQLite pilot)')
    parser.add_argument('command', nargs='?', choices=('serve', 'create-admin', 'create-report', 'backup', 'prune-inactive', 'generate-admin-totp'), default='serve')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8769')))
    parser.add_argument('--db', default=os.environ.get('CO_CHILL_DB_PATH', str(ROOT / 'var/co_chill_accounts.sqlite3')))
    parser.add_argument('--username')
    parser.add_argument('--output')
    parser.add_argument('--confirm', action='store_true')
    args = parser.parse_args()
    if args.command == 'generate-admin-totp':
        print('Keep this setup secret private. Add it to your authenticator and CO_CHILL_ADMIN_TOTP_SECRET environment variable; never commit it:')
        print(base64.b32encode(secrets.token_bytes(20)).decode().rstrip('='))
        return
    if args.command == 'serve':
        app = CloudApplication(db_path=args.db)
        with make_server(args.host, args.port, app, handler_class=QuietHandler) as server:
            print(f'Co Chill: http://{args.host}:{server.server_port} (Ctrl+C to stop)', flush=True)
            server.serve_forever()
        return
    store = CloudStore(args.db, os.environ.get('CO_CHILL_ADMIN_TOTP_SECRET', ''))
    if args.command in ('create-admin', 'create-report'):
        if not args.username:
            parser.error('--username is required')
        if args.command == 'create-admin' and not store.admin_totp_secret:
            parser.error('Set CO_CHILL_ADMIN_TOTP_SECRET first; owner admin requires an authenticator.')
        password = getpass.getpass('Password (10+ characters, hidden): ')
        if password != getpass.getpass('Confirm password: '):
            parser.error('Passwords do not match')
        with store.connect(True) as db:
            if args.command == 'create-admin' and db.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
                parser.error('An owner admin already exists. Do not create a backdoor account.')
            user = store.create_user(db, {'username': args.username, 'password': password}, 'admin' if args.command == 'create-admin' else 'report')
            print('Created ' + user['role'] + ' account: ' + user['username'])
    elif args.command == 'backup':
        if not args.output:
            parser.error('--output is required (new path only)')
        store.backup(args.output)
        print('Backup created. It contains private user data; protect it and apply deletion requests to backups separately.')
    elif args.command == 'prune-inactive':
        with store.connect(True) as db:
            ids = [row['id'] for row in db.execute("SELECT id FROM users WHERE role!='admin' AND last_activity<?", (time.time() - 365 * 86400,))]
            if args.confirm:
                for uid in ids:
                    store.delete_user(db, uid)
            print(f'{len(ids)} inactive accounts ' + ('deleted.' if args.confirm else 'eligible. Run with --confirm to delete. Admin owner is excluded.'))


if __name__ == '__main__':
    main()
