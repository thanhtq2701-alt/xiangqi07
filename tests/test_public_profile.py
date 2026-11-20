"""Public profile: owner decisions 19/11/2026 (random id, online games only, opponent privacy)."""
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

from app.cloud_store import CloudStore
from tests.test_online_http import Engine, HttpClient
from co_chill_server import CloudApplication


class PublicProfileTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='var/tests')
        self.path = Path(self.temp.name) / 'data.sqlite3'
        self.app = CloudApplication(self.path, public_origin='', admin_totp_secret='', engine=Engine())
        self.a, self.b, self.c, self.anon = [HttpClient(self.app, '127.0.0.' + str(i)) for i in (1, 2, 3, 4)]

    def tearDown(self):
        self.temp.cleanup()

    def me(self, client):
        return client.request('/api/session')[1]['user']

    def play(self, first, second, loser=None):
        status, room, _ = first.request('/api/rooms', 'POST', {'preset': 'untimed'})
        self.assertEqual(status, 201, room)
        code = room['code']
        self.assertEqual(second.request(f'/api/rooms/{code}/join', 'POST')[0], 200)
        first.request(f'/api/rooms/{code}/ready', 'POST')
        second.request(f'/api/rooms/{code}/ready', 'POST')
        status, result, _ = (loser or first).request(f'/api/rooms/{code}/resign', 'POST', {'confirm': True})
        self.assertEqual(status, 200, result)
        self.assertEqual(result['status'], 'finished')

    def public(self, client, public_id):
        return client.request('/api/public/' + public_id)

    def test_new_accounts_are_public_with_a_random_id_not_the_username(self):
        self.a.register('alice')
        user = self.me(self.a)
        self.assertEqual(user['profileVisibility'], 'public')
        self.assertRegex(user['publicId'], r'^[0-9a-f]{12}$')
        self.assertNotIn('alice', user['publicId'])
        status, profile, _ = self.public(self.anon, user['publicId'])
        self.assertEqual(status, 200, profile)
        self.assertEqual(profile['displayName'], 'alice')
        self.assertEqual(profile['joined'], time.strftime('%Y-%m', time.gmtime()))
        self.assertEqual(profile['totals'], {'games': 0, 'wins': 0, 'losses': 0, 'draws': 0})
        text = json.dumps(profile)
        self.assertNotIn(user['id'], text)
        self.assertNotIn('"username"', text)

    def test_existing_accounts_start_unset_and_are_not_public_until_they_choose(self):
        old = Path(self.temp.name) / 'old.sqlite3'
        db = sqlite3.connect(old)
        try:
            db.executescript('''CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                display_name TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('user','admin','report')),
                created_at REAL NOT NULL, last_login REAL, last_activity REAL, locked_until REAL, lock_reason TEXT NOT NULL DEFAULT '',
                totp_step INTEGER NOT NULL DEFAULT -1, test_account INTEGER NOT NULL DEFAULT 0);''')
            db.execute("INSERT INTO users(id,username,display_name,password_hash,role,created_at) VALUES ('u1','olduser','Cũ','x','user',1)")
            db.execute("INSERT INTO users(id,username,display_name,password_hash,role,created_at) VALUES ('u2','other','Khác','x','user',1)")
            db.commit()
        finally:
            db.close()
        store = CloudStore(old)
        CloudStore(old)  # running the migration twice is harmless
        with store.connect() as db:
            rows = db.execute('SELECT public_id, profile_visibility FROM users ORDER BY id').fetchall()
            self.assertEqual([r['profile_visibility'] for r in rows], ['unset', 'unset'])
            self.assertTrue(all(len(r['public_id']) == 12 for r in rows))
            self.assertNotEqual(rows[0]['public_id'], rows[1]['public_id'])
            self.assertIsNone(store.public_user(db, rows[0]['public_id']))

    def test_games_and_opponents_follow_each_players_own_setting(self):
        self.a.register('alice')
        self.b.register('bobby')
        self.play(self.a, self.b, loser=self.b)
        self.play(self.a, self.b, loser=self.a)
        alice, bobby = self.me(self.a), self.me(self.b)
        profile = self.public(self.anon, alice['publicId'])[1]
        self.assertEqual(profile['totals'], {'games': 2, 'wins': 1, 'losses': 1, 'draws': 0})
        self.assertEqual([g['outcome'] for g in profile['games']], ['loss', 'win'])
        self.assertEqual(profile['games'][0]['opponent'], {'name': 'bobby', 'kind': 'public', 'publicId': bobby['publicId']})
        self.assertEqual(profile['games'][0]['reason'], 'resigned')
        self.assertEqual(self.b.request('/api/account/visibility', 'POST', {'visibility': 'private'})[0], 200)
        profile = self.public(self.anon, alice['publicId'])[1]
        self.assertEqual(profile['games'][0]['opponent'], {'name': 'Người chơi ẩn', 'kind': 'private', 'publicId': None})
        self.assertNotIn('bobby', json.dumps(profile, ensure_ascii=False))
        self.assertEqual(self.public(self.anon, bobby['publicId'])[0], 404)

    def test_guest_and_deleted_opponents_get_neutral_labels(self):
        self.a.register('alice')
        self.c.guest('Khách Lan')
        self.play(self.a, self.c)
        self.b.register('bobby')
        self.play(self.a, self.b)
        self.assertEqual(self.b.request('/api/account', 'DELETE', {'password': 'online-test-password-strong'})[0], 200)
        profile = self.public(self.anon, self.me(self.a)['publicId'])[1]
        self.assertEqual([g['opponent']['kind'] for g in profile['games']], ['deleted', 'guest'])
        self.assertEqual([g['opponent']['name'] for g in profile['games']], ['Người chơi đã xóa', 'Khách'])
        self.assertNotIn('Khách Lan', json.dumps(profile, ensure_ascii=False))

    def test_private_unknown_malformed_locked_and_operator_profiles_answer_the_same_404(self):
        self.a.register('alice')
        alice = self.me(self.a)
        answers = [self.public(self.anon, x) for x in ('0' * 12, '../etc', 'ABCDEF123456', alice['publicId'] + '0')]
        self.a.request('/api/account/visibility', 'POST', {'visibility': 'private'})
        answers.append(self.public(self.anon, alice['publicId']))
        self.a.request('/api/account/visibility', 'POST', {'visibility': 'public'})
        with self.app.store.connect(True) as db:
            db.execute('UPDATE users SET locked_until=? WHERE id=?', (time.time() + 3600, alice['id']))
            admin = self.app.store.create_user(db, {'username': 'owner1', 'password': 'owner-password-strong'}, 'admin')
            self.assertEqual(admin['profile_visibility'], 'private')
        answers.append(self.public(self.anon, alice['publicId']))
        answers.append(self.public(self.anon, admin['public_id']))
        self.assertEqual({(s, p['code']) for s, p, _ in answers}, {(404, 'profile_not_found')})

    def test_visibility_change_needs_a_signed_in_owner_and_a_valid_value(self):
        self.a.register('alice')
        self.assertEqual(self.anon.request('/api/account/visibility', 'POST', {'visibility': 'private'})[0], 401)
        self.assertEqual(self.a.request('/api/account/visibility', 'POST', {'visibility': 'private'}, csrf=False)[0], 403)
        for bad in ({'visibility': 'everyone'}, {'visibility': 'private', 'extra': 1}, {}):
            self.assertEqual(self.a.request('/api/account/visibility', 'POST', bad)[0], 400)
        status, result, _ = self.a.request('/api/account/visibility', 'POST', {'visibility': 'private'})
        self.assertEqual((status, result['user']['profileVisibility']), (200, 'private'))

    def test_public_list_is_capped_and_carries_replayable_moves(self):
        self.a.register('alice')
        self.b.register('bobby')
        for _ in range(21):
            self.play(self.a, self.b)
        profile = self.public(self.anon, self.me(self.a)['publicId'])[1]
        self.assertEqual(profile['totals']['games'], 21)
        self.assertEqual(len(profile['games']), 20)
        game = profile['games'][0]
        self.assertEqual(game['moves'], [])
        self.assertTrue(game['initialFen'])
        self.assertFalse(profile['ranked'])


if __name__ == '__main__':
    unittest.main()
