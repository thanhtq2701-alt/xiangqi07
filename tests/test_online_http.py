"""Direct WSGI integration tests for account and expiring guest room sessions."""
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from urllib.parse import urlsplit

from app.cloud_store import sha
from app.rules import START_FEN
from co_chill_server import CloudApplication, COOKIE, ROOM_COOKIE, GUEST_ROOM_SECONDS

PASSWORD = 'online-test-password-strong'


class Engine:
    def __init__(self):
        self.calls = 0
        self.callback = None

    def status(self):
        return {'configured': False, 'fallback': True}

    def analyze(self, fen, **kwargs):
        self.calls += 1
        if self.callback:
            self.callback()
        return {'best_move': 'a0a1', 'engine': 'test', 'fallback': True,
                'score': 1, 'candidates': [{'move': 'a0a1', 'score': 1}]}


class HttpClient:
    def __init__(self, app, ip):
        self.app, self.ip = app, ip
        self.cookies, self.csrf, self.uid = {}, '', None

    def request(self, path, method='GET', data=None, *, csrf=True, origin='http://localhost:8769', host='localhost:8769'):
        raw = json.dumps(data or {}).encode()
        target = urlsplit(path)
        env = {'REQUEST_METHOD': method, 'PATH_INFO': target.path, 'QUERY_STRING': target.query,
               'SERVER_NAME': 'localhost', 'SERVER_PORT': '8769', 'HTTP_HOST': host,
               'wsgi.url_scheme': 'http', 'wsgi.input': io.BytesIO(raw), 'CONTENT_TYPE': 'application/json',
               'CONTENT_LENGTH': str(len(raw)), 'REMOTE_ADDR': self.ip,
               'HTTP_COOKIE': '; '.join(k + '=' + v for k, v in self.cookies.items())}
        if origin is not None:
            env['HTTP_ORIGIN'] = origin
        if csrf:
            env['HTTP_X_CSRF_TOKEN'] = self.csrf
        response = {}
        def start(status, headers):
            response['status'] = int(status.split()[0])
            response['headers'] = dict(headers)
            for name, value in headers:
                if name == 'Set-Cookie':
                    key, val = value.split(';', 1)[0].split('=', 1)
                    if 'Max-Age=0;' in value or value.endswith('Max-Age=0'):
                        self.cookies.pop(key, None)
                    else:
                        self.cookies[key] = val
        payload = json.loads(b''.join(self.app(env, start)))
        if payload.get('csrf'):
            self.csrf = payload['csrf']
        if payload.get('user'):
            self.uid = payload['user']['id']
        return response['status'], payload, response['headers']

    def register(self, name):
        return self.request('/api/auth/register', 'POST', {'username': name, 'password': PASSWORD, 'displayName': name})

    def guest(self, name='Khách kiểm thử', **extra):
        return self.request('/api/rooms/guest', 'POST', {'displayName': name, **extra})


class OnlineHttpTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='var/tests')
        self.path = Path(self.temp.name) / 'data.sqlite3'
        self.engine = Engine()
        self.app = CloudApplication(self.path, public_origin='', admin_totp_secret='', engine=self.engine)
        self.a, self.b, self.c = [HttpClient(self.app, '127.0.0.' + str(i)) for i in (1, 2, 3)]

    def tearDown(self):
        self.temp.cleanup()

    def started(self, guests=False):
        for client, name in ((self.a, 'alice'), (self.b, 'bobby')):
            status, _, _ = client.guest(name) if guests else client.register(name)
            self.assertEqual(status, 201)
        status, r, _ = self.a.request('/api/rooms', 'POST', {'preset': 'rapid'})
        self.assertEqual(status, 201, r)
        self.code = r['code']
        self.assertEqual(self.b.request(f'/api/rooms/{self.code}/join', 'POST')[0], 200)
        self.assertEqual(self.a.request(f'/api/rooms/{self.code}/ready', 'POST')[0], 200)
        status, r, _ = self.b.request(f'/api/rooms/{self.code}/ready', 'POST')
        self.assertEqual(status, 200, r)
        self.red = self.a if r['players']['w']['id'] == self.a.uid else self.b
        self.black = self.b if self.red is self.a else self.a
        return r

    def test_capabilities_and_anonymous_room_boundary(self):
        self.assertTrue(self.a.request('/api/health')[1]['rooms']['enabled'])
        self.assertTrue(self.a.request('/api/session')[1]['capabilities']['onlineRooms'])
        self.assertFalse(self.a.request('/api/rooms/session')[1]['authenticated'])
        self.assertEqual(self.a.request('/api/rooms')[0], 401)
        self.assertEqual(self.a.request('/api/rooms', 'POST')[0], 401)
        self.assertEqual(self.a.request('/api/rooms/guest', 'POST', origin='https://evil.example')[0], 403)
        self.assertEqual(self.a.request('/api/rooms/session', host='evil.example')[0], 403)

    def test_guest_token_hashed_httponly_and_no_account_privileges(self):
        status, result, headers = self.a.guest(id='attacker', role='admin', csrf='chosen')
        self.assertEqual(status, 201)
        self.assertTrue(result['guest'])
        self.assertFalse(result['authenticated'])
        self.assertNotEqual(result['user']['id'], 'attacker')
        self.assertNotEqual(result['csrf'], 'chosen')
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Strict', headers['Set-Cookie'])
        token = self.a.cookies[ROOM_COOKIE]
        self.assertNotIn(token, json.dumps(result))
        with self.app.store.connect() as db:
            row = db.execute('SELECT * FROM room_guest_sessions').fetchone()
            self.assertEqual(row['token_hash'], sha(token))
            self.assertAlmostEqual(row['expires_at'] - row['created_at'], GUEST_ROOM_SECONDS)
        for path in ('/api/state', '/api/export', '/api/admin/users', '/api/engine/status'):
            self.assertEqual(self.a.request(path)[0], 401, path)
        self.assertEqual(self.a.request('/api/engine/analyze', 'POST', {'fen': START_FEN, 'purpose': 'bot'})[0], 401)

    def test_guest_reuse_expiry_csrf_and_forged_identity(self):
        self.a.guest()
        first = self.a.uid
        self.assertEqual(self.a.guest()[1]['user']['id'], first)
        self.assertEqual(self.a.request('/api/rooms', 'POST', csrf=False)[0], 403)
        status, r, _ = self.a.request('/api/rooms', 'POST', {'user': {'id': 'pretend'}, 'ownerId': 'pretend'})
        self.assertEqual(status, 201)
        self.assertEqual(r['ownerId'], first)
        with self.app.store.connect(True) as db:
            db.execute('UPDATE room_guest_sessions SET expires_at=?', (time.time() - 1,))
        self.assertIsNone(self.a.request('/api/rooms/session')[1]['user'])
        self.assertEqual(self.a.request('/api/rooms')[0], 401)
        self.assertNotEqual(self.a.guest()[1]['user']['id'], first)

    def test_two_authenticated_accounts_play_move_and_private_history_export(self):
        r = self.started()
        status, r, _ = self.red.request(f'/api/rooms/{self.code}/move', 'POST',
            {'move': 'a3a4', 'expectedRevision': r['revision'], 'nonce': 'http_move_001'})
        self.assertEqual(status, 200, r)
        self.assertEqual(r['moves'], ['a3a4'])
        status, r, _ = self.red.request(f'/api/rooms/{self.code}/resign', 'POST', {'confirm': True})
        self.assertEqual(status, 200, r)
        self.assertEqual(r['status'], 'finished')
        red_history = self.red.request('/api/rooms/history')[1]['games']
        black_history = self.black.request('/api/rooms/history')[1]['games']
        self.assertEqual(len(red_history), 1)
        self.assertEqual(red_history[0]['player'], 'w')
        self.assertEqual(black_history[0]['player'], 'b')
        self.assertEqual(self.red.request('/api/export')[1]['onlineGames'], red_history)
        self.c.register('viewer')
        self.assertEqual(self.c.request('/api/rooms/history')[1]['games'], [])

    def test_guest_game_plays_without_cloud_account_and_deletes_explicitly(self):
        r = self.started(guests=True)
        status, r, _ = self.red.request(f'/api/rooms/{self.code}/move', 'POST',
            {'move': 'a3a4', 'expectedRevision': r['revision'], 'nonce': 'guest_move_001'})
        self.assertEqual(status, 200, r)
        self.assertEqual(self.a.request('/api/rooms/guest', 'DELETE', csrf=False)[0], 403)
        self.assertEqual(self.a.request('/api/rooms/guest', 'DELETE')[0], 200)
        self.assertNotIn(ROOM_COOKIE, self.a.cookies)
        self.assertEqual(self.b.request(f'/api/rooms/{self.code}')[0], 404)
        with self.app.store.connect() as db:
            self.assertFalse(db.execute('SELECT 1 FROM room_guest_sessions WHERE user_id=?', (self.a.uid,)).fetchone())

    def test_player_and_spectator_cannot_call_engine_for_any_purpose(self):
        self.started()
        self.c.register('watcher')
        self.assertEqual(self.c.request(f'/api/rooms/{self.code}/watch', 'POST')[0], 200)
        for client in (self.a, self.b, self.c):
            for purpose in ('bot', 'practice', 'review', 'review-scan'):
                status, result, _ = client.request('/api/engine/analyze', 'POST', {'purpose': purpose, 'fen': START_FEN})
                self.assertEqual(status, 409, result)
                self.assertEqual(result['code'], 'live_online_no_coaching')
        self.assertEqual(self.engine.calls, 0)
        self.assertEqual(self.a.request('/api/engine/analyze', 'POST', {'purpose': 'bot'}, csrf=False)[0], 403)
        self.assertEqual(self.c.request(f'/api/rooms/{self.code}/leave', 'POST')[0], 200)
        self.assertNotEqual(self.c.request('/api/engine/analyze', 'POST', {'purpose': 'bot', 'fen': START_FEN})[1]['code'], 'live_online_no_coaching')

    def test_late_engine_result_discarded_if_online_game_starts_during_search(self):
        self.a.register('alice')
        self.b.register('bobby')
        game = {'id': 'botgame', 'mode': 'bot', 'player': 'b', 'status': {'over': False}, 'initialFen': START_FEN, 'moves': []}
        self.a.request('/api/state', 'PUT', {'revision': 0, 'state': {'games': [game]}})
        r = self.a.request('/api/rooms', 'POST')[1]
        code = r['code']
        self.b.request(f'/api/rooms/{code}/join', 'POST')
        self.a.request(f'/api/rooms/{code}/ready', 'POST')
        self.engine.callback = lambda: self.b.request(f'/api/rooms/{code}/ready', 'POST')
        status, result, _ = self.a.request('/api/engine/analyze', 'POST', {'purpose': 'bot', 'fen': START_FEN, 'gameId': 'botgame'})
        self.assertEqual(status, 409, result)
        self.assertEqual(result['code'], 'live_online_no_coaching')
        self.assertNotIn('best_move', result)

    def test_account_delete_is_atomic_and_removes_room_identity(self):
        self.started()
        uid = self.a.uid
        self.assertEqual(self.a.request('/api/account', 'DELETE', {'password': 'wrong'})[0], 401)
        self.assertEqual(self.b.request(f'/api/rooms/{self.code}')[0], 200)
        self.assertEqual(self.a.request('/api/account', 'DELETE', {'password': PASSWORD})[0], 200)
        self.assertEqual(self.b.request(f'/api/rooms/{self.code}')[0], 404)
        with self.app.store.connect() as db:
            self.assertFalse(db.execute('SELECT 1 FROM users WHERE id=?', (uid,)).fetchone())
            self.assertFalse(db.execute('SELECT 1 FROM online_results WHERE red_id=? OR black_id=?', (uid, uid)).fetchone())

    def test_account_session_precedence_and_no_silent_guest_downgrade(self):
        self.a.guest()
        guest_id = self.a.uid
        self.a.register('alice')
        account_id = self.a.uid
        result = self.a.request('/api/rooms/session')[1]
        self.assertEqual(result['user']['id'], account_id)
        self.assertNotEqual(account_id, guest_id)
        self.assertTrue(result['authenticated'])
        with self.app.store.connect(True) as db:
            db.execute('DELETE FROM sessions')
        self.assertEqual(self.a.request('/api/rooms/session')[0], 401)

    def test_cannot_switch_guest_identity_during_live_game(self):
        self.started(guests=True)
        status, result, _ = self.a.register('alice')
        self.assertEqual(status, 409)
        self.assertEqual(result['code'], 'guest_game_live')

    def test_online_review_uses_server_record_not_forged_synced_history(self):
        r = self.started()
        self.red.request(f'/api/rooms/{self.code}/move', 'POST',
                         {'move': 'a3a4', 'expectedRevision': r['revision'], 'nonce': 'review_move_001'})
        self.red.request(f'/api/rooms/{self.code}/resign', 'POST', {'confirm': True})
        game = self.red.request('/api/rooms/history')[1]['games'][0]
        # No client state import is required to analyze an owned completed game.
        base = {'purpose': 'review-scan', 'gameId': game['id'], 'fen': START_FEN, 'moves': [], 'selectedMove': 'a3a4'}
        self.assertEqual(self.red.request('/api/engine/analyze', 'POST', base)[0], 200)
        forged = dict(game, moves=[{'move': 'c3c4'}])
        self.red.request('/api/state', 'PUT', {'revision': 0, 'state': {'games': [forged]}})
        status, result, _ = self.red.request('/api/engine/analyze', 'POST', dict(base, selectedMove='c3c4'))
        self.assertEqual(status, 409, result)
        self.assertEqual(result['code'], 'position_mismatch')
        self.c.register('outsider')
        self.assertEqual(self.c.request('/api/engine/analyze', 'POST', base)[1]['code'], 'online_game_not_finished')

    def test_guest_cookie_is_secure_for_https_origin(self):
        app = CloudApplication(self.path, public_origin='https://cochill.example', admin_totp_secret='', engine=self.engine)
        c = HttpClient(app, '127.0.0.5')
        status, _, headers = c.request('/api/rooms/guest', 'POST', origin='https://cochill.example', host='cochill.example')
        self.assertEqual(status, 201)
        self.assertIn('; Secure', headers['Set-Cookie'])

    def test_strong_engine_policy_rejects_fallback_without_leaking_analysis(self):
        self.a.register('alice')
        game = {'id': 'botgame', 'mode': 'bot', 'player': 'b', 'status': {'over': False}, 'initialFen': START_FEN, 'moves': []}
        self.a.request('/api/state', 'PUT', {'revision': 0, 'state': {'games': [game]}})
        request = {'purpose': 'bot', 'fen': START_FEN, 'gameId': 'botgame', 'requireStrong': True}
        status, result, headers = self.a.request('/api/engine/analyze', 'POST', request)
        self.assertEqual(status, 503, result)
        self.assertEqual(result['code'], 'engine_unavailable')
        self.assertNotIn('best_move', result)
        self.assertNotIn('score', result)
        self.assertNotIn('candidates', result)
        self.assertEqual(headers['Retry-After'], '5')
        self.assertEqual(self.a.request('/api/engine/analyze', 'POST', dict(request, requireStrong='true'))[0], 400)
        self.assertEqual(self.a.request('/api/engine/analyze', 'POST', dict(request, requireStrong=False))[0], 200)
        self.engine.analyze = lambda fen, **kwargs: {'fallback': False, 'best_move': 'a3a4', 'score': 5}
        status, result, _ = self.a.request('/api/engine/analyze', 'POST', request)
        self.assertEqual(status, 200, result)
        self.assertEqual(result['best_move'], 'a3a4')
        self.assertNotIn('score', result)


if __name__ == '__main__':
    unittest.main()
