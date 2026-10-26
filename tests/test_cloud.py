"""Account/sync/security tests against the actual WSGI routes and isolated SQLite."""
import io
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from app.cloud_store import CloudStore, totp, verify_password, metrics, SCRYPT_PREFIX
from co_chill_server import CloudApplication
from app.rules import START_FEN

# Test-only RFC-style secret. No production credentials are embedded here.
TEST_TOTP = 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ'
PASSWORD = 'test-password-strong'


class FakeEngine:
    def status(self):
        return {'available': False, 'fallback': True}

    def analyze(self, fen, **kwargs):
        if fen not in ('test-fen', START_FEN):
            raise ValueError('FEN không hợp lệ.')
        return {'best_move': 'a0a1', 'engine': 'test-engine', 'fallback': True,
                'score': 12, 'candidates': [{'move': 'a0a1', 'score': 12}]}


class Client:
    def __init__(self, app, ip='127.0.0.1'):
        self.app, self.ip, self.cookie, self.csrf = app, ip, '', ''

    def request(self, path, method='GET', data=None, origin='http://localhost:8769', csrf=True, host='localhost:8769', content_type='application/json', raw=None):
        body = raw if raw is not None else json.dumps(data or {}, ensure_ascii=False).encode()
        target = urlsplit(path)
        env = {'REQUEST_METHOD': method, 'PATH_INFO': target.path, 'QUERY_STRING': target.query,
               'SERVER_NAME': 'localhost', 'SERVER_PORT': '8769', 'HTTP_HOST': host,
               'wsgi.url_scheme': 'http', 'wsgi.input': io.BytesIO(body), 'CONTENT_TYPE': content_type,
               'CONTENT_LENGTH': str(len(body)), 'REMOTE_ADDR': self.ip, 'HTTP_COOKIE': self.cookie}
        if origin is not None:
            env['HTTP_ORIGIN'] = origin
        if csrf:
            env['HTTP_X_CSRF_TOKEN'] = self.csrf
        result = {}

        def start(status, headers):
            result['status'], result['headers'] = int(status.split()[0]), dict(headers)

        output = b''.join(self.app(env, start))
        if 'Set-Cookie' in result['headers']:
            self.cookie = result['headers']['Set-Cookie'].split(';')[0]
        payload = json.loads(output) if result['headers']['Content-Type'].startswith('application/json') else output
        if isinstance(payload, dict) and payload.get('csrf'):
            self.csrf = payload['csrf']
        return result['status'], payload, result['headers']

    def register(self, name='player1', **extra):
        return self.request('/api/auth/register', 'POST', {'username': name, 'password': PASSWORD, 'displayName': 'Người chơi', **extra})


class CloudTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='var/tests')
        self.db_path = Path(self.temp.name) / 'cloud.sqlite3'
        self.app = CloudApplication(self.db_path, public_origin='', admin_totp_secret=TEST_TOTP, engine=FakeEngine())
        self.client = Client(self.app)

    def tearDown(self):
        self.temp.cleanup()

    def admin(self):
        with self.app.store.connect(True) as db:
            admin = self.app.store.create_user(db, {'username': 'owner', 'password': PASSWORD}, 'admin')
        client = Client(self.app, '127.0.0.2')
        status, result, _ = client.request('/api/auth/login', 'POST', {'username': 'owner', 'password': PASSWORD, 'totpCode': totp(TEST_TOTP, int(time.time() / 30))})
        self.assertEqual(status, 200, result)
        return client, admin['id']

    def test_registration_hash_permissions_cookie(self):
        status, result, headers = self.client.register(role='admin', emailVerified=True)
        self.assertEqual(status, 201)
        self.assertEqual(result['user']['role'], 'user')
        self.assertFalse(result['user']['emailVerified'])
        self.assertFalse(result['capabilities']['passwordRecovery'])
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Strict', headers['Set-Cookie'])
        with self.app.store.connect() as db:
            row = db.execute('SELECT * FROM users').fetchone()
            self.assertNotEqual(row['password_hash'], PASSWORD)
            self.assertTrue(row['password_hash'].startswith(SCRYPT_PREFIX))
            self.assertTrue(verify_password(PASSWORD, row['password_hash']))
            self.assertNotIn(self.client.cookie.split('=')[1], db.execute('SELECT token_hash FROM sessions').fetchone()[0])
        self.assertNotIn('password_hash', json.dumps(result))
        self.assertEqual(self.client.request('/api/admin/stats')[0], 403)

    def test_guest_static_and_private_files(self):
        self.assertFalse(self.client.request('/api/session')[1]['authenticated'])
        for path in ('/', '/app.js', '/learning.js', '/style.css'):
            status, _, headers = self.client.request(path)
            self.assertEqual(status, 200, path)
            self.assertIn('Content-Security-Policy', headers)
        for path in ('/co_chill_server.py', '/README.md', '/var/co_chill_accounts.sqlite3', '/.env', '/%2e%2e/server.py'):
            self.assertEqual(self.client.request(path)[0], 404, path)
        for path in ('/api/state', '/api/export', '/api/admin/users'):
            self.assertEqual(self.client.request(path)[0], 401, path)

    def test_origin_csrf_host_json_size_and_unsafe_json(self):
        self.assertEqual(self.client.request('/api/auth/register', 'POST', {'username': 'bad', 'password': PASSWORD}, origin='https://evil.example')[0], 403)
        self.assertEqual(self.client.request('/api/session', host='evil.example')[0], 403)
        self.client.register()
        self.assertEqual(self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {}}, csrf=False)[0], 403)
        self.assertEqual(self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {}}, origin=None)[0], 403)
        self.assertEqual(self.client.request('/api/state', 'PUT', content_type='text/plain')[0], 415)
        self.assertEqual(self.client.request('/api/state', 'PUT', raw=b'{broken')[0], 400)
        self.assertEqual(self.client.request('/api/state', 'PUT', raw=b'[]')[0], 400)
        self.assertEqual(self.client.request('/api/state', 'PUT', raw=b'{"revision":0,"state":{"score":NaN}}')[0], 400)
        self.assertEqual(self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'__proto__': {'admin': True}}})[0], 400)
        self.assertEqual(self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'large': 'x' * (2 * 1024 * 1024)}})[0], 413)

    def test_single_session_and_expiry(self):
        self.client.register()
        second = Client(self.app, '127.0.0.2')
        self.assertEqual(second.request('/api/auth/login', 'POST', {'username': 'PLAYER1', 'password': PASSWORD})[0], 200)
        self.assertFalse(self.client.request('/api/session')[1]['authenticated'])
        self.assertEqual(self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {}})[0], 401)
        with self.app.store.connect(True) as db:
            db.execute('UPDATE sessions SET expires_at=?', (time.time() - 1,))
        self.assertFalse(second.request('/api/session')[1]['authenticated'])

    def test_state_isolation_revision_and_cross_device_sync(self):
        self.client.register()
        state = {'games': [{'id': 'g1'}], 'records': {}, 'session': {'answers': ['private answer']}, 'prefs': {'theme': 'dark'}}
        self.assertEqual(self.client.request('/api/state')[1]['revision'], 0)
        status, result, _ = self.client.request('/api/state', 'PUT', {'revision': 0, 'state': state})
        self.assertEqual((status, result['revision']), (200, 1))
        conflict = self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'lost': True}})
        self.assertEqual(conflict[0], 409)
        self.assertEqual(self.client.request('/api/state')[1]['state'], state)
        other = Client(self.app, '127.0.0.2')
        other.register('player2')
        self.assertEqual(other.request('/api/state')[1]['state'], {})
        device = Client(self.app, '127.0.0.3')
        device.request('/api/auth/login', 'POST', {'username': 'player1', 'password': PASSWORD})
        self.assertEqual(device.request('/api/state')[1]['state'], state)

    def test_generic_login_errors_and_throttling(self):
        self.client.register()
        attacker = Client(self.app, '127.0.0.4')
        unknown = attacker.request('/api/auth/login', 'POST', {'username': 'unknown', 'password': 'incorrect'})
        wrong = attacker.request('/api/auth/login', 'POST', {'username': 'player1', 'password': 'incorrect'})
        self.assertEqual(unknown[:2], wrong[:2])
        for _ in range(9):
            attacker.request('/api/auth/login', 'POST', {'username': 'player1', 'password': 'incorrect'})
        status, payload, headers = attacker.request('/api/auth/login', 'POST', {'username': 'player1', 'password': PASSWORD})
        self.assertEqual(status, 429)
        self.assertIn('Retry-After', headers)

    def test_password_change_rotates_session_and_username_requires_old_password(self):
        self.client.register()
        original_cookie = self.client.cookie
        self.assertEqual(self.client.request('/api/account', 'PATCH', {'username': 'player1', 'displayName': 'Đổi tên hiển thị'})[0], 200)
        self.assertEqual(self.client.request('/api/account', 'PATCH', {'username': 'renamed'})[0], 401)
        self.assertEqual(self.client.request('/api/account', 'PATCH', {'role': 'admin'})[0], 400)
        status, payload, _ = self.client.request('/api/account', 'PATCH', {'username': 'renamed', 'displayName': 'Tên mới', 'currentPassword': PASSWORD, 'newPassword': 'new-password-long'})
        self.assertEqual(status, 200, payload)
        self.assertNotEqual(self.client.cookie, original_cookie)
        self.assertEqual(payload['user']['username'], 'renamed')
        self.client.request('/api/auth/logout', 'POST')
        self.assertFalse(self.client.request('/api/session')[1]['authenticated'])
        self.assertEqual(self.client.request('/api/auth/login', 'POST', {'username': 'renamed', 'password': PASSWORD})[0], 401)
        self.assertEqual(self.client.request('/api/auth/login', 'POST', {'username': 'renamed', 'password': 'new-password-long'})[0], 200)

    def test_mfa_required_and_replay_protection(self):
        # Replaying means the SAME code, even when slow CI crosses a 30s boundary.
        # Also prove that a genuinely new time-step code is accepted exactly once.
        with patch('time.time', return_value=1793000000.0) as clock:
            admin, _ = self.admin()
            used_code = totp(TEST_TOTP, int(clock.return_value / 30))
            other = Client(self.app, '127.0.0.3')
            self.assertEqual(other.request('/api/auth/login', 'POST', {'username': 'owner', 'password': PASSWORD})[0], 401)
            self.assertEqual(other.request('/api/auth/login', 'POST', {'username': 'owner', 'password': PASSWORD, 'totpCode': used_code})[0], 401)
            self.assertEqual(admin.request('/api/admin/stats')[0], 200)
            self.assertNotIn(TEST_TOTP, json.dumps(admin.request('/api/export')[1]))
            clock.return_value += 30
            self.assertEqual(other.request('/api/auth/login', 'POST', {'username': 'owner', 'password': PASSWORD, 'totpCode': used_code})[0], 401)
            fresh_code = totp(TEST_TOTP, int(clock.return_value / 30))
            self.assertEqual(other.request('/api/auth/login', 'POST', {'username': 'owner', 'password': PASSWORD, 'totpCode': fresh_code})[0], 200)
            replay_client = Client(self.app, '127.0.0.4')
            self.assertEqual(replay_client.request('/api/auth/login', 'POST', {'username': 'owner', 'password': PASSWORD, 'totpCode': fresh_code})[0], 401)

    def test_legacy_password_upgrades_only_after_valid_login(self):
        self.client.register()
        self.client.request('/api/auth/logout', 'POST')
        salt = '01' * 16
        legacy = 'scrypt$16384$8$1$' + salt + '$' + hashlib.scrypt(PASSWORD.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1, dklen=32).hex()
        with self.app.store.connect(True) as db:
            db.execute("UPDATE users SET password_hash=? WHERE username='player1'", (legacy,))
        self.assertEqual(self.client.request('/api/auth/login', 'POST', {'username': 'player1', 'password': 'incorrect'})[0], 401)
        with self.app.store.connect() as db:
            self.assertEqual(db.execute('SELECT password_hash FROM users').fetchone()[0], legacy)
        self.assertEqual(self.client.request('/api/auth/login', 'POST', {'username': 'player1', 'password': PASSWORD})[0], 200)
        with self.app.store.connect() as db:
            updated = db.execute('SELECT password_hash FROM users').fetchone()[0]
            self.assertTrue(updated.startswith(SCRYPT_PREFIX))
            self.assertTrue(verify_password(PASSWORD, updated))

    def test_owner_deletion_block_and_account_mutation_rollback(self):
        admin, owner_id = self.admin()
        self.assertEqual(admin.request('/api/account', 'DELETE', {'password': 'incorrect'})[0], 401)
        self.assertEqual(admin.request('/api/account', 'DELETE', {'password': PASSWORD})[0], 409)
        self.assertEqual(admin.request('/api/session')[1]['user']['id'], owner_id)
        self.client.register()
        original = self.client.request('/api/session')[1]['user']
        failed = self.client.request('/api/account', 'PATCH', {'displayName': 'Should not persist', 'username': 'owner', 'currentPassword': PASSWORD})
        self.assertEqual(failed[0], 409)
        self.assertEqual(self.client.request('/api/session')[1]['user'], original)
        with self.app.store.connect() as db:
            self.assertNotIn(PASSWORD, '\n'.join(db.iterdump()))

    def test_admin_private_answers_excluded_and_report_cannot_mutate(self):
        self.client.register()
        state = {'games': [{'id': 'g1', 'fen': 'fen', 'moves': ['a0a1'], 'notes': 'private game note'}], 'session': {'answers': ['private answer']}, 'records': {}}
        self.client.request('/api/state', 'PUT', {'revision': 0, 'state': state})
        user_id = self.client.request('/api/session')[1]['user']['id']
        admin, _ = self.admin()
        status, detail, _ = admin.request('/api/admin/users/' + user_id)
        self.assertEqual(status, 200)
        self.assertNotIn('private answer', json.dumps(detail))
        self.assertNotIn('private game note', json.dumps(detail))
        self.assertFalse(detail['privateAnswersIncluded'])
        with self.app.store.connect(True) as db:
            self.app.store.create_user(db, {'username': 'reporter', 'password': PASSWORD}, 'report')
        reporter = Client(self.app, '127.0.0.3')
        reporter.request('/api/auth/login', 'POST', {'username': 'reporter', 'password': PASSWORD})
        self.assertEqual(reporter.request('/api/admin/users')[0], 200)
        self.assertEqual(reporter.request('/api/admin/stats')[0], 200)
        self.assertEqual(reporter.request('/api/admin/users/' + user_id)[0], 200)
        self.assertEqual(reporter.request('/api/admin/content')[0], 403)
        self.assertEqual(reporter.request('/api/admin/feedback')[0], 403)
        self.assertEqual(admin.request('/api/admin/content')[0], 200)
        self.assertEqual(admin.request('/api/admin/feedback')[0], 200)
        self.assertEqual(reporter.request('/api/admin/users/' + user_id + '/lock', 'POST', {'locked': False})[0], 403)

    def test_lock_revokes_session_has_reason_and_unlock(self):
        self.client.register()
        uid = self.client.request('/api/session')[1]['user']['id']
        admin, _ = self.admin()
        from app.cloud_store import utc
        status = admin.request('/api/admin/users/' + uid + '/lock', 'POST', {'locked': True, 'until': utc(time.time() + 3600), 'reason': 'Kiểm tra tài khoản'})[0]
        self.assertEqual(status, 200)
        self.assertFalse(self.client.request('/api/session')[1]['authenticated'])
        other = Client(self.app, '127.0.0.3')
        status, result, _ = other.request('/api/auth/login', 'POST', {'username': 'player1', 'password': PASSWORD})
        self.assertEqual(status, 403)
        self.assertEqual(result['reason'], 'Kiểm tra tài khoản')
        admin.request('/api/admin/users/' + uid + '/lock', 'POST', {'locked': False})
        self.assertEqual(other.request('/api/auth/login', 'POST', {'username': 'player1', 'password': PASSWORD})[0], 200)

    def test_feedback_export_and_true_deletion(self):
        self.client.register()
        self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'session': {'draft': 'sensitive'}}})
        status, feedback, _ = self.client.request('/api/feedback', 'POST', {'category': 'interface', 'message': 'Nút khó bấm', 'context': {'route': '#learn', 'puzzleId': 'test'}})
        self.assertEqual(status, 201)
        admin, _ = self.admin()
        self.assertEqual(admin.request('/api/admin/feedback/' + feedback['id'], 'PATCH', {'status': 'reviewing'})[0], 200)
        exported = self.client.request('/api/export')[1]
        self.assertEqual(exported['feedback'][0]['status'], 'reviewing')
        self.assertNotIn('password', json.dumps(exported).replace('passwordLogin', '').replace('passwordRecovery', '').replace('"password"', ''))
        self.assertEqual(self.client.request('/api/account', 'DELETE', {'password': PASSWORD})[0], 200)
        self.assertFalse(self.client.request('/api/session')[1]['authenticated'])
        with self.app.store.connect() as db:
            self.assertFalse(db.execute("SELECT 1 FROM users WHERE username='player1'").fetchone())
            self.assertEqual(db.execute('SELECT COUNT(*) FROM feedback').fetchone()[0], 0)
            self.assertNotIn('sensitive', '\n'.join(r[0] for r in db.execute('SELECT data FROM states')))

    def test_account_export_preserves_personal_work_without_unopened_answer_keys(self):
        self.client.register()
        draft = {'puzzleId': 'pending', 'stage': 'reflect', 'answers': ['my reasoning'], 'candidate': 'a0a1', 'selected': 'a0',
                 'puzzle': {'solution': 'hidden-solution', 'why': 'hidden-explanation'}}
        state = {'games': [{'moves': [{'move': 'a0a1', 'before': START_FEN}], 'moments': [{'solution': 'hidden-moment'}]}],
                 'preferences': {'theme': 'dark'}, 'session': draft,
                 'records': {'pending': {'dueAt': '2026-10-25T10:00:00Z', 'attempts': [{'answers': ['my old reasoning'], 'firstCandidate': 'a0a1'}],
                                         'pendingReview': {'dueAt': '2026-10-25T10:00:00Z', 'session': draft}}}}
        self.assertEqual(self.client.request('/api/state', 'PUT', {'revision': 0, 'state': state})[0], 200)
        exported = self.client.request('/api/export')[1]
        self.assertFalse(exported['answerKeysIncluded'])
        self.assertNotIn('hidden-', json.dumps(exported))
        personal = exported['state']
        self.assertEqual(personal['session']['answers'], ['my reasoning'])
        self.assertEqual(personal['session']['candidate'], 'a0a1')
        self.assertEqual(personal['session']['selected'], 'a0')
        self.assertEqual(personal['records']['pending']['pendingReview']['session']['answers'], ['my reasoning'])
        self.assertEqual(personal['records']['pending']['pendingReview']['dueAt'], '2026-10-25T10:00:00Z')
        self.assertEqual(personal['records']['pending']['attempts'][0]['firstCandidate'], 'a0a1')
        self.assertEqual(personal['preferences']['theme'], 'dark')
        self.assertEqual(personal['games'][0]['moves'][0]['move'], 'a0a1')
        # Export redaction must not mutate the internal persistence needed to resume.
        self.assertEqual(self.client.request('/api/state')[1]['state'], state)

    def test_engine_no_live_coaching_and_bot_redaction(self):
        self.client.register()
        game = {'id': 'live', 'mode': 'bot', 'player': 'b', 'status': {'over': False}, 'initialFen': START_FEN, 'fen': START_FEN, 'moves': []}
        self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'games': [game]}})
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', {'fen': START_FEN, 'gameId': 'live', 'purpose': 'review-scan'})[0], 409)
        status, result, _ = self.client.request('/api/engine/analyze', 'POST', {'fen': START_FEN, 'gameId': 'live', 'purpose': 'bot'})
        self.assertEqual(status, 200)
        self.assertEqual(result['best_move'], 'a0a1')
        self.assertNotIn('score', result)
        self.assertNotIn('candidates', result)
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', {'fen': START_FEN, 'gameId': 'other', 'purpose': 'bot'})[0], 409)

    def test_engine_review_scan_validates_game_history(self):
        self.client.register()
        game = {'id': 'finished', 'status': {'over': True}, 'initialFen': START_FEN, 'moves': [{'move': 'a0a1'}]}
        self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'games': [game]}})
        base = {'fen': START_FEN, 'gameId': 'finished', 'purpose': 'review-scan', 'moves': [], 'selectedMove': 'a0a1'}
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', base)[0], 200)
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', {**base, 'selectedMove': 'h2e2'})[0], 409)
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', {**base, 'moves': ['h2e2']})[0], 409)

    def test_engine_practice_requires_synced_reflection(self):
        self.client.register()
        request = {'fen': START_FEN, 'purpose': 'practice'}
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', request)[0], 409)
        session = {'stage': 'reflect', 'puzzle': {'fen': START_FEN}, 'answers': ['a', 'b', 'c'], 'candidate': 'a0a1'}
        self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'session': session}})
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', request)[0], 409)
        session['stage'] = 'explain'
        self.client.request('/api/state', 'PUT', {'revision': 1, 'state': {'session': session}})
        self.assertEqual(self.client.request('/api/engine/analyze', 'POST', request)[0], 200)

    def test_content_draft_validation_publish_edit_withdraw(self):
        self.assertEqual(self.client.request('/api/content')[1]['puzzles'], [])
        admin, _ = self.admin()
        content = {'title': 'Bài tự soạn', 'fen': START_FEN, 'solution': 'a0a1', 'alternatives': ['a0a2'],
                   'skill': 'material', 'what': 'Tự quan sát', 'why': 'Kiểm tra đường Xe', 'how': 'Kiểm tra đối phương', 'source': 'Tự soạn, không trích sách'}
        self.assertEqual(admin.request('/api/admin/content', 'POST', {**content, 'solution': 'a0b1'})[0], 400)
        self.assertEqual(admin.request('/api/admin/content', 'POST', {**content, 'alternatives': ['a0b1']})[0], 400)
        self.assertEqual(admin.request('/api/admin/content', 'POST', {**content, 'pv': ['a0a1', 'a0a2']})[0], 400)
        self.assertEqual(admin.request('/api/admin/content', 'POST', {**content, 'status': 'published'})[0], 400)
        status, result, _ = admin.request('/api/admin/content', 'POST', content)
        self.assertEqual(status, 201, result)
        identity = result['content']['id']
        self.assertEqual(result['content']['version'], 1)
        self.assertEqual(self.client.request('/api/content')[1]['puzzles'], [])
        path = '/api/admin/content/' + identity
        for version in (None, True, '1', 0):
            self.assertEqual(admin.request(path, 'PATCH', {'status': 'published', 'version': version})[0], 400)
        self.assertEqual(admin.request(path, 'PATCH', {'status': 'published', 'version': 1})[0], 200)
        published = self.client.request('/api/content')[1]['puzzles']
        self.assertEqual(len(published), 1)
        self.assertEqual(published[0]['solution'], 'a0a1')
        self.assertFalse(published[0]['provenance']['engineVerified'])
        self.assertEqual(admin.request(path, 'PATCH', {'version': 1, 'status': 'withdrawn'})[0], 409)
        status, result, _ = admin.request(path, 'PATCH', {'title': 'Sửa bài', 'version': 2})
        self.assertEqual(status, 200, result)
        self.assertEqual(result['content']['status'], 'draft')
        self.assertEqual(self.client.request('/api/content')[1]['puzzles'], [])
        self.assertEqual(admin.request(path, 'PATCH', {'status': 'published', 'version': 2})[0], 409)
        self.assertEqual(admin.request(path, 'PATCH', {'status': 'published', 'version': 3})[0], 200)
        self.assertEqual(admin.request(path, 'PATCH', {'status': 'withdrawn', 'version': 4})[0], 200)
        self.assertEqual(self.client.request('/api/content')[1]['puzzles'], [])
        with self.app.store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM content_history WHERE content_id=?', (identity,)).fetchone()[0], 5)
        ordinary = Client(self.app, '127.0.0.4')
        ordinary.register()
        self.assertEqual(ordinary.request('/api/admin/content', 'POST', content)[0], 403)

    def test_content_correction_replaces_stale_variation_and_requires_review(self):
        admin, _ = self.admin()
        content = {'title': 'Bài sửa đáp án', 'fen': START_FEN, 'solution': 'a0a1',
                   'pv': ['a0a1', 'a9a8'], 'skill': 'material', 'what': 'Quan sát',
                   'why': 'Kiểm tra Xe', 'how': 'Xem phản ứng', 'source': 'Tự soạn'}
        status, created, _ = admin.request('/api/admin/content', 'POST', content)
        self.assertEqual(status, 201, created)
        path = '/api/admin/content/' + created['content']['id']
        self.assertEqual(admin.request(path, 'PATCH', {'version': 1, 'status': 'published'})[0], 200)
        status, updated, _ = admin.request(path, 'PATCH', {'version': 2, 'solution': 'a0a2'})
        self.assertEqual(status, 200, updated)
        self.assertEqual(updated['content']['pv'], ['a0a2'])
        self.assertEqual(updated['content']['status'], 'draft')
        self.assertEqual(self.client.request('/api/content')[1]['puzzles'], [])
        # An explicitly supplied replacement still has to be legal; it cannot
        # use the automatic reset to bypass validation or advance the version.
        status, _, _ = admin.request(path, 'PATCH', {'version': 3, 'solution': 'a0a1', 'pv': ['a0a2']})
        self.assertEqual(status, 400)
        status, updated, _ = admin.request(path, 'PATCH', {'version': 3, 'fen': START_FEN.replace(' w', ' b'), 'solution': 'a9a8'})
        self.assertEqual(status, 200, updated)
        self.assertEqual(updated['content']['pv'], ['a9a8'])

    def test_backup_can_restore_state_and_https_cookie(self):
        self.client.register()
        self.client.request('/api/state', 'PUT', {'revision': 0, 'state': {'version': 3}})
        path = Path(self.temp.name) / 'backup.sqlite3'
        self.app.store.backup(path)
        restored = CloudStore(path)
        with restored.connect() as db:
            row = db.execute("SELECT id FROM users WHERE username='player1'").fetchone()
            self.assertEqual(restored.state(db, row['id'])['state']['version'], 3)
        secure = CloudApplication(Path(self.temp.name) / 'https.sqlite3', public_origin='https://chill.example', admin_totp_secret=TEST_TOTP, engine=FakeEngine())
        status, _, headers = Client(secure).request('/api/auth/register', 'POST', {'username': 'secure', 'password': PASSWORD}, origin='https://chill.example', host='chill.example')
        self.assertEqual(status, 201)
        self.assertIn('; Secure', headers['Set-Cookie'])
        self.assertIn('Strict-Transport-Security', headers)

    def test_metric_threshold_dedup_and_no_fake_level(self):
        first = {'id': 'a1', 'success': True, 'assisted': False, 'firstExposure': True}
        state = {'records': {'p1': {'attempts': [first, first]}}}
        self.assertEqual(metrics(state)['learningAttempts'], 1)
        self.assertIsNone(metrics(state)['independentRate'])
        self.assertIsNone(metrics(state)['verifiedLevel'])

    def test_multistep_metrics_deduplicate_without_inventing_proficiency(self):
        first = {'id': 'line-a', 'puzzleId': 'line-1', 'success': True, 'completedAt': '2026-10-26T00:00:00Z',
                 'assisted': False, 'firstExposure': True, 'source': 'practice'}
        review = {**first, 'id': 'line-b', 'source': 'review', 'assisted': True}
        unfinished = {**first, 'id': 'line-c', 'completedAt': None}
        raw = {'records': {}, 'lineAttempts': [first, first, review, unfinished, None], 'lineSession': {'stage': 'parked'}}
        counts = metrics({'learning': raw})
        self.assertEqual(counts['learningAttempts'], 2)
        self.assertEqual(counts['completedPositions'], 1)
        self.assertEqual(counts['lineAttempts'], 2)
        self.assertEqual(counts['lineCompletedPositions'], 1)
        self.assertEqual(counts['assistedAttempts'], 1)
        self.assertEqual(counts['reviews'], 1)
        self.assertTrue(counts['unfinished'])
        self.assertEqual(counts['independentSamples'], 0)
        self.assertIsNone(counts['independentRate'])
        self.assertIsNone(counts['verifiedLevel'])
        raw['lineSession']['stage'] = 'finished'
        self.assertFalse(metrics(raw)['unfinished'])


if __name__ == '__main__':
    unittest.main()
