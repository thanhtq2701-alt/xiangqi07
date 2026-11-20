"""Server room invariants using deterministic time and an isolated SQLite file."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from app.cloud_store import APIError
from app.online_rooms import DELETED_NAME, GUEST_PREFIX, OnlineRooms, MESSAGES
from app.rules import Position, START_FEN


class OnlineRoomTests(unittest.TestCase):
    def setUp(self):
        Path('var/tests').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='var/tests')
        self.path = Path(self.temp.name) / 'rooms.sqlite3'
        self.now = 1000.0
        self.rooms = OnlineRooms(self.path, clock=lambda: self.now)
        self.a = {'id': 'user_one', 'displayName': 'Một'}
        self.b = {'id': 'user_two', 'displayName': 'Hai'}
        self.c = {'id': 'viewer_three', 'displayName': 'Người xem'}
        self.counter = 0

    def tearDown(self):
        self.temp.cleanup()

    def started(self, **options):
        r = self.rooms.create(self.a, options)
        self.code = r['code']
        self.rooms.join(self.b, self.code)
        self.rooms.action(self.a, self.code, 'ready')
        r = self.rooms.action(self.b, self.code, 'ready')
        self.red = self.a if r['players']['w']['id'] == self.a['id'] else self.b
        self.black = self.b if self.red is self.a else self.a
        return r

    def move(self, user, move, **extra):
        self.counter += 1
        r = self.rooms.snapshot(user, self.code)
        data = {'move': move, 'nonce': f'nonce_{self.counter:05}', 'expectedRevision': r['revision'], **extra}
        return self.rooms.action(user, self.code, 'move', data)

    def assert_api(self, status, code, fn):
        with self.assertRaises(APIError) as caught:
            fn()
        self.assertEqual(caught.exception.status, status)
        if code:
            self.assertEqual(caught.exception.code, code)

    def test_private_room_not_listed_and_read_requires_join(self):
        r = self.rooms.create(self.a)
        self.assertEqual(self.rooms.list_public(self.b)['rooms'], [])
        self.assert_api(403, 'room_forbidden', lambda: self.rooms.snapshot(self.b, r['code']))
        self.assert_api(404, 'room_not_found', lambda: self.rooms.join(self.b, '../../file'))
        joined = self.rooms.join(self.b, r['code'].lower())
        self.assertNotEqual(joined['side'], r['side'])
        self.assert_api(409, 'room_full', lambda: self.rooms.join(self.c, r['code']))

    def test_untrusted_collection_fields_are_bad_requests_not_type_errors(self):
        self.assert_api(400, None, lambda: self.rooms.create(self.a, {'preset': []}))
        self.assert_api(400, None, lambda: self.rooms.create(self.a, {'visibility': []}))
        self.assert_api(400, None, lambda: self.rooms.match(self.a, {'preset': {}}))
        self.assert_api(400, None, lambda: self.rooms.create(self.a, []))
        self.assert_api(400, None, lambda: self.rooms.match(self.a, []))
        self.assert_api(400, None, lambda: self.rooms.action(self.a, '0000000000', 'chat', []))
        self.started()
        self.assert_api(400, 'canned_chat_only', lambda: self.rooms.action(
            self.a, self.code, 'chat', {'message': []}))
        self.assert_api(400, None, lambda: self.rooms.action(
            self.a, self.code, 'kick', {'userId': {}}))

    def test_both_ready_starts_game_without_client_fen(self):
        r = self.rooms.create(self.a, {'visibility': 'public', 'fen': 'fake'})
        self.code = r['code']
        self.assertEqual(r['fen'], START_FEN)
        self.assertEqual(len(self.rooms.list_public(self.b)['rooms']), 1)
        self.rooms.join(self.b, self.code)
        r = self.rooms.action(self.a, self.code, 'ready')
        self.assertEqual(r['status'], 'waiting')
        r = self.rooms.action(self.b, self.code, 'ready')
        self.assertEqual(r['status'], 'playing')
        self.assertFalse(r['ranked'])
        self.assertNotIn('seen', r)
        self.assertNotIn('nonces', r)

    def test_moves_validate_turn_legality_revision_and_nonce(self):
        r = self.started()
        self.assert_api(409, 'not_your_turn', lambda: self.move(self.black, 'a6a5'))
        self.assert_api(400, 'illegal_move', lambda: self.move(self.red, 'a3a5'))
        self.assert_api(409, 'stale_revision', lambda: self.rooms.action(self.red, self.code, 'move',
                        {'move': 'a3a4', 'nonce': 'nonce_unique', 'expectedRevision': -1}))
        r = self.rooms.snapshot(self.red, self.code)
        data = {'move': 'a3a4', 'nonce': 'nonce_unique', 'expectedRevision': r['revision']}
        result = self.rooms.action(self.red, self.code, 'move', data)
        retry = self.rooms.action(self.red, self.code, 'move', data)
        self.assertEqual(retry['moves'], ['a3a4'])
        self.assertEqual(retry['revision'], result['revision'])
        self.assert_api(409, 'nonce_reused', lambda: self.rooms.action(self.red, self.code, 'move',
                        dict(data, move='c3c4')))
        result = self.move(self.black, 'a6a5')
        self.assertEqual(result['fen'], Position.from_fen(START_FEN).play('a3a4').play('a6a5').fen())

    def test_server_clock_and_increment_ignore_client_values(self):
        self.started(preset='blitz')
        self.now += 10
        r = self.move(self.red, 'a3a4', clock={'w': 9999999}, seconds=999999)
        self.assertEqual(r['clock']['w'], 293000)
        self.assertEqual(r['clock']['b'], 300000)
        self.now += 5
        r = self.rooms.snapshot(self.red, self.code)
        self.assertEqual(r['clock']['b'], 295000)

    def test_timeout_record_once_and_reject_move(self):
        self.started(preset='bullet')
        for _ in range(7):
            self.now += 10
            self.rooms.snapshot(self.red, self.code)
            r = self.rooms.snapshot(self.black, self.code)
        self.assertEqual(r['result']['reason'], 'timeout')
        self.assertEqual(r['result']['winner'], 'b')
        self.assert_api(409, 'game_not_live', lambda: self.move(self.red, 'a3a4'))
        self.assertEqual(len(self.rooms.history(self.a)['games']), 1)
        self.assertEqual(len(self.rooms.history(self.b)['games']), 1)
        self.assertEqual(len(self.rooms.history(self.c)['games']), 0)

    def test_draw_requires_opponent_acceptance_before_15_seconds(self):
        self.started()
        r = self.rooms.action(self.red, self.code, 'draw')
        self.assertEqual(r['drawOffer']['expiresAt'], self.now + 15)
        self.assert_api(409, 'draw_expired', lambda: self.rooms.action(self.red, self.code, 'draw-accept'))
        self.now += 15
        self.assert_api(409, 'draw_expired', lambda: self.rooms.action(self.black, self.code, 'draw-accept'))
        self.rooms.action(self.black, self.code, 'draw')
        r = self.rooms.action(self.red, self.code, 'draw-accept')
        self.assertEqual(r['result'], {'over': True, 'winner': None, 'reason': 'draw_agreed'})

    def test_one_disconnected_seat_loses_after_30_seconds(self):
        self.started(preset='untimed')
        self.now += 20
        self.rooms.snapshot(self.black, self.code)
        self.now += 11
        r = self.rooms.snapshot(self.black, self.code)
        self.assertEqual(r['result']['reason'], 'disconnected')
        self.assertEqual(r['result']['winner'], 'b')
        self.assertEqual(self.rooms.snapshot(self.red, self.code)['status'], 'finished')

    def test_both_missing_pauses_without_arbitrary_winner(self):
        self.started()
        self.now += 40
        r = self.rooms.snapshot(self.red, self.code)
        self.assertEqual(r['status'], 'paused')
        self.assertFalse(r['result']['over'])
        self.assertEqual(self.rooms.history(self.a)['games'], [])
        self.rooms.action(self.red, self.code, 'ready')
        r = self.rooms.action(self.black, self.code, 'ready')
        self.assertEqual(r['status'], 'playing')

    def row(self):
        with self.rooms.connect(write=False) as db:
            return tuple(db.execute('SELECT updated_at, data FROM online_rooms WHERE code=?', (self.code,)).fetchone())

    def test_poll_is_a_read_but_still_counts_as_presence(self):
        """Load fix 2026-11-21: a poll writes nothing unless the room really changes."""
        self.started()
        saved = self.row()
        self.now += 5
        for _ in range(3):
            red = self.rooms.snapshot(self.red, self.code)
            self.rooms.snapshot(self.black, self.code)
        self.assertEqual(self.row(), saved, 'polling must not rewrite the room')
        self.assertLess(red['clock']['w'], 600000, 'the running clock is still computed for the snapshot')
        self.assertEqual(red['clock']['at'], self.now)
        # Only Red keeps polling. Red's presence lives in memory (the saved room still has
        # the time of 'ready'), so after 31 s it is Black, not both seats, that is missing.
        self.now += 20
        self.rooms.snapshot(self.red, self.code)
        self.now += 11
        r = self.rooms.snapshot(self.red, self.code)
        self.assertEqual((r['status'], r['result']['reason'], r['result']['winner']), ('finished', 'disconnected', 'w'))
        self.assertNotEqual(self.row(), saved, 'a finished game is saved')
        self.assertEqual(len(self.rooms.history(self.a)['games']), 1)

    def test_live_context_check_does_not_rewrite_unchanged_rooms(self):
        self.started()
        saved = self.row()
        self.now += 3
        self.assertTrue(self.rooms.has_live_context(self.a))
        self.rooms.list_public(self.c)
        self.assertEqual(self.row(), saved)

    def test_deleting_an_identity_forgets_its_presence(self):
        self.started()
        self.rooms.snapshot(self.red, self.code)
        self.rooms.delete_identity(self.red['id'])
        self.assertFalse(any(self.red['id'] in seats for seats in self.rooms._presence.values()))

    def test_paused_players_must_finish_before_leaving_seat(self):
        self.started()
        self.now += 40
        self.assertEqual(self.rooms.snapshot(self.a, self.code)['status'], 'paused')
        for player in (self.a, self.b):
            self.assert_api(409, 'game_live', lambda player=player: self.rooms.action(
                player, self.code, 'leave'))
        result = self.rooms.action(self.b, self.code, 'resign', {'confirm': True})
        self.assertEqual(result['status'], 'finished')
        self.rooms.action(self.b, self.code, 'leave')
        self.assertFalse(self.rooms.has_live_context(self.b))

    def test_restart_persists_moves_and_freezes_clock(self):
        self.started()
        self.move(self.red, 'a3a4')
        self.now += 3600
        other = OnlineRooms(self.path, clock=lambda: self.now)
        r = other.snapshot(self.red, self.code)
        self.assertEqual(r['status'], 'paused')
        self.assertEqual(r['pauseReason'], 'server_restart')
        self.assertEqual(r['moves'], ['a3a4'])
        self.assertFalse(r['result']['over'])

    def test_spectator_cannot_move_can_chat_and_owner_can_kick(self):
        self.started()
        self.rooms.join(self.c, self.code, spectator=True)
        self.assertTrue(self.rooms.has_live_context(self.c))
        self.assert_api(403, 'spectator_read_only', lambda: self.move(self.c, 'a3a4'))
        self.assert_api(400, 'canned_chat_only', lambda: self.rooms.action(self.c, self.code, 'chat', {'message': 'a3a4'}))
        r = self.rooms.action(self.c, self.code, 'chat', {'message': 'hello'})
        self.assertEqual(r['messages'][-1]['message'], MESSAGES['hello'])
        self.assert_api(403, None, lambda: self.rooms.action(self.b, self.code, 'kick', {'userId': self.c['id']}))
        self.rooms.action(self.a, self.code, 'kick', {'userId': self.c['id']})
        self.assertFalse(self.rooms.has_live_context(self.c))
        self.assert_api(403, 'room_forbidden', lambda: self.rooms.snapshot(self.c, self.code))
        self.assert_api(403, 'room_forbidden', lambda: self.rooms.join(self.c, self.code, spectator=True))

    def test_takeback_requires_consent_and_preserves_valid_position(self):
        self.started()
        self.move(self.red, 'a3a4')
        self.move(self.black, 'a6a5')
        self.rooms.action(self.red, self.code, 'takeback')
        self.assert_api(409, None, lambda: self.rooms.action(self.red, self.code, 'takeback-accept'))
        r = self.rooms.action(self.black, self.code, 'takeback-accept')
        self.assertEqual(r['moves'], [])
        self.assertEqual(r['fen'], START_FEN)
        with self.rooms.connect() as db:
            saved = json.loads(db.execute('SELECT data FROM online_rooms WHERE code=?', (self.code,)).fetchone()['data'])
        self.assertEqual(saved['events'][0]['removedMoves'], ['a3a4', 'a6a5'])

    def test_takeback_offer_expires_when_requester_moves_again(self):
        self.started()
        self.move(self.red, 'a3a4')
        self.rooms.action(self.red, self.code, 'takeback')
        self.move(self.black, 'a6a5')
        self.move(self.red, 'c3c4')
        self.assert_api(409, None, lambda: self.rooms.action(self.black, self.code, 'takeback-accept'))

    def test_resign_confirmation_and_rematch_new_record_swaps_sides(self):
        r = self.started()
        first_id, first_red = r['gameId'], r['players']['w']['id']
        self.move(self.red, 'a3a4')
        self.assert_api(400, 'confirmation_required', lambda: self.rooms.action(self.red, self.code, 'resign'))
        self.rooms.action(self.red, self.code, 'resign', {'confirm': True})
        r = self.rooms.action(self.red, self.code, 'rematch')
        self.assertEqual(r['status'], 'finished')
        r = self.rooms.action(self.black, self.code, 'rematch')
        self.assertEqual(r['status'], 'waiting')
        self.assertNotEqual(r['gameId'], first_id)
        self.assertEqual(r['players']['b']['id'], first_red)
        self.assertEqual(len(self.rooms.history(self.red)['games']), 1)
        self.assertEqual(self.rooms.history(self.red)['games'][0]['moves'][0]['move'], 'a3a4')

    def test_busy_player_cannot_take_second_seat_and_waiting_room_can_close(self):
        r = self.rooms.create(self.a)
        self.assert_api(409, 'already_in_room', lambda: self.rooms.create(self.a))
        self.rooms.action(self.a, r['code'], 'leave')
        r2 = self.rooms.create(self.a)
        self.assertNotEqual(r['code'], r2['code'])

    def test_deletion_removes_personal_rooms_results_and_chat(self):
        self.started()
        self.rooms.join(self.c, self.code, spectator=True)
        self.rooms.action(self.c, self.code, 'chat', {'message': 'hello'})
        self.rooms.delete_identity(self.c['id'])
        r = self.rooms.snapshot(self.a, self.code)
        self.assertEqual(r['messages'], [])
        self.assertEqual(r['spectators'], [])
        self.rooms.action(self.red, self.code, 'resign', {'confirm': True})
        self.rooms.delete_identity(self.red['id'])
        # Owner decision 19/11/2026: the opponent keeps the finished game, anonymized.
        games = self.rooms.history(self.black)['games']
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]['opponent'], DELETED_NAME)
        self.assertEqual(self.rooms.history(self.red)['games'], [])
        self.assert_api(404, 'room_not_found', lambda: self.rooms.snapshot(self.black, self.code))

    def finished(self, first, second):
        code = self.rooms.create(first)['code']
        self.rooms.join(second, code)
        self.rooms.action(first, code, 'ready')
        r = self.rooms.action(second, code, 'ready')
        red = first if r['players']['w']['id'] == first['id'] else second
        self.rooms.action(red, code, 'move', {'move': 'a3a4', 'nonce': 'n_' + code, 'expectedRevision': r['revision']})
        self.rooms.action(red, code, 'resign', {'confirm': True})
        return code

    def result_rows(self):
        with self.rooms.connect() as db:
            return [dict(row) for row in db.execute('SELECT game_id,red_id,black_id,ended_at,data FROM online_results ORDER BY ended_at')]

    def test_deleted_player_is_anonymized_everywhere_in_the_shared_record(self):
        self.started()
        self.move(self.red, 'a3a4')
        self.rooms.action(self.red, self.code, 'takeback')
        self.rooms.action(self.black, self.code, 'takeback-accept')
        self.rooms.action(self.red, self.code, 'resign', {'confirm': True})
        self.rooms.delete_identity(self.red['id'])
        [row] = self.result_rows()
        self.assertNotIn(self.red['id'], row['data'])
        self.assertNotIn(self.red['displayName'], row['data'])
        anon = row['red_id']
        self.assertTrue(anon.startswith('deleted_'))
        self.assertEqual(row['black_id'], self.black['id'])
        record = json.loads(row['data'])
        self.assertEqual(record['players']['w'], {'id': anon, 'displayName': DELETED_NAME})
        self.assertEqual(record['events'][0]['requestedBy'], anon, 'events point at the anonymous id')
        self.assertEqual(record['events'][0]['acceptedBy'], self.black['id'])
        review = self.rooms.history(self.black)['games'][0]
        self.assertEqual((review['player'], review['status']['winner'], review['opponent']), ('b', 'b', DELETED_NAME))

    def test_anonymous_ids_differ_per_game_and_a_record_nobody_can_read_is_deleted(self):
        self.finished(self.a, self.b)
        self.finished(self.a, self.b)
        self.rooms.delete_identity(self.a['id'])
        anon = {row['red_id'] if row['black_id'] == self.b['id'] else row['black_id'] for row in self.result_rows()}
        self.assertEqual(len(anon), 2, 'records cannot be linked back to one person')
        self.assertEqual(len(self.rooms.history(self.b)['games']), 2)
        self.rooms.delete_identity(self.b['id'])
        self.assertEqual(self.result_rows(), [])

    def test_prune_previews_then_removes_old_guest_data_and_idle_rooms(self):
        guest = {'id': GUEST_PREFIX + 'a1b2c3', 'displayName': 'Khách Lan'}
        guest2 = {'id': GUEST_PREFIX + 'd4e5f6', 'displayName': 'Khách Minh'}
        look_alike = {'id': 'guestX_not_a_guest', 'displayName': 'Tài khoản'}
        self.finished(guest, self.a)           # guest vs account: the account keeps it
        self.finished(guest, guest2)           # two guests: nobody keeps it
        self.finished(self.a, self.b)          # accounts only: untouched
        self.finished(look_alike, self.b)      # an id that only looks like a guest
        idle = self.rooms.create(self.c)['code']
        self.now += 31 * 86400
        recent = self.finished(guest, self.b)  # newer than 30 days: untouched
        before = self.result_rows()
        with self.rooms.connect() as db:
            preview = OnlineRooms.prune_in_db(db, now=self.now)
        self.assertEqual(preview, {'rooms': 5, 'guestGamesAnonymized': 1, 'guestGamesDeleted': 1, 'expiredGuestSessions': 0})
        self.assertEqual(self.result_rows(), before, 'preview changes nothing')
        with self.rooms.connect() as db:
            OnlineRooms.prune_in_db(db, now=self.now, confirm=True)
        rows = self.result_rows()
        self.assertEqual(len(rows), 4)
        self.assertFalse(any(guest2['id'] in r['data'] for r in rows))
        old = [r for r in rows if r['ended_at'] < self.now - 86400 and self.a['id'] in (r['red_id'], r['black_id']) and self.b['id'] not in (r['red_id'], r['black_id'])]
        self.assertEqual(len(old), 1)
        self.assertNotIn(guest['id'], old[0]['data'])
        self.assertNotIn('Khách Lan', old[0]['data'])
        self.assertIn(DELETED_NAME, [g['opponent'] for g in self.rooms.history(self.a)['games']])
        self.assertTrue(any(look_alike['id'] in r['data'] for r in rows))
        self.assertTrue(any(guest['id'] in r['data'] for r in rows), 'the recent guest game stays')
        self.assert_api(404, 'room_not_found', lambda: self.rooms.snapshot(self.c, idle))
        self.assertEqual(self.rooms.snapshot(self.b, recent)['status'], 'finished')
        with self.rooms.connect() as db:
            again = OnlineRooms.prune_in_db(db, now=self.now)
        self.assertEqual(again, {'rooms': 0, 'guestGamesAnonymized': 0, 'guestGamesDeleted': 0, 'expiredGuestSessions': 0})

    def test_prune_removes_expired_guest_sessions(self):
        with self.rooms.connect() as db:
            db.execute('CREATE TABLE room_guest_sessions (token_hash TEXT PRIMARY KEY, user_id TEXT UNIQUE NOT NULL, '
                       'display_name TEXT NOT NULL, csrf TEXT NOT NULL, created_at REAL NOT NULL, expires_at REAL NOT NULL)')
            db.execute("INSERT INTO room_guest_sessions VALUES ('t1','guest_old','Khách','c',?,?)", (self.now - 90000, self.now - 3600))
            db.execute("INSERT INTO room_guest_sessions VALUES ('t2','guest_new','Khách','c',?,?)", (self.now - 60, self.now + 86000))
            self.assertEqual(OnlineRooms.prune_in_db(db, now=self.now)['expiredGuestSessions'], 1)
            OnlineRooms.prune_in_db(db, now=self.now, confirm=True)
            self.assertEqual([r[0] for r in db.execute('SELECT user_id FROM room_guest_sessions')], ['guest_new'])

    def test_prune_rooms_command_previews_by_default_and_applies_with_confirm(self):
        guest = {'id': GUEST_PREFIX + 'a1b2c3', 'displayName': 'Khách Lan'}
        self.finished(guest, self.a)
        with self.rooms.connect() as db:
            db.execute('UPDATE online_results SET ended_at=ended_at-?', (40 * 86400,))
            db.execute('UPDATE online_rooms SET updated_at=updated_at-?', (40 * 86400,))
        root = Path(__file__).resolve().parents[1]
        command = [sys.executable, str(root / 'co_chill_server.py'), 'prune-rooms', '--db', str(self.path)]
        run = lambda extra=(): subprocess.run(command + list(extra), capture_output=True, text=True, encoding='utf-8', cwd=root)
        out = run().stdout
        self.assertIn('Rooms idle over 30 days: 1', out)
        self.assertIn('1 keep the account player', out)
        self.assertIn('Preview only', out)
        self.assertIn(guest['id'], self.result_rows()[0]['data'])
        out = run(['--confirm']).stdout
        self.assertIn('Done.', out)
        self.assertNotIn(guest['id'], self.result_rows()[0]['data'])
        self.assertNotEqual(run(['--days', '0']).returncode, 0)

    def test_static_identity_cleanup_uses_caller_transaction(self):
        self.started()
        self.rooms.join(self.c, self.code, spectator=True)
        self.rooms.action(self.c, self.code, 'chat', {'message': 'hello'})
        self.now += 1
        with self.rooms.connect() as db:
            OnlineRooms.delete_identity_in_db(db, self.c['id'], now=self.now)
            row = db.execute('SELECT updated_at,data FROM online_rooms WHERE code=?', (self.code,)).fetchone()
            room = json.loads(row['data'])
        self.assertEqual(row['updated_at'], self.now)
        self.assertEqual(room['spectators'], {})
        self.assertEqual(room['messages'], [])

    def test_concurrent_duplicate_move_is_applied_once(self):
        r = self.started()
        data = {'move': 'a3a4', 'nonce': 'same_network_retry', 'expectedRevision': r['revision']}
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: self.rooms.action(self.red, self.code, 'move', data), range(2)))
        self.assertTrue(all(reply['moves'] == ['a3a4'] for reply in replies))
        self.assertEqual(self.rooms.snapshot(self.red, self.code)['moves'], ['a3a4'])

    def test_concurrent_different_moves_cannot_overwrite(self):
        r = self.started()
        def submit(move):
            try:
                return self.rooms.action(self.red, self.code, 'move', {'move': move, 'nonce': 'request_' + move,
                                         'expectedRevision': r['revision']})
            except APIError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(submit, ['a3a4', 'c3c4']))
        self.assertEqual(sum(isinstance(reply, dict) for reply in replies), 1)
        self.assertIn('stale_revision', replies)
        self.assertEqual(len(self.rooms.snapshot(self.red, self.code)['moves']), 1)

    def test_community_matches_preset_requires_both_ready(self):
        a = self.rooms.match(self.a, {'preset': 'blitz'})
        c = self.rooms.match(self.c, {'preset': 'rapid'})
        b = self.rooms.match(self.b, {'preset': 'blitz'})
        self.assertEqual(a['code'], b['code'])
        self.assertNotEqual(a['code'], c['code'])
        self.assertEqual(b['status'], 'waiting')
        self.assertEqual(self.rooms.match(self.b, {'preset': 'blitz'})['code'], b['code'])

    def test_stale_ready_does_not_start_without_present_opponent(self):
        r = self.rooms.create(self.a)
        self.rooms.join(self.b, r['code'])
        self.rooms.action(self.a, r['code'], 'ready')
        self.now += 31
        waiting = self.rooms.action(self.b, r['code'], 'ready')
        self.assertEqual(waiting['status'], 'waiting')
        self.assertEqual(waiting['ready'], [self.b['id']])


if __name__ == '__main__':
    unittest.main()
