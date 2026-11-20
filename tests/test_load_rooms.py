"""tools/load_rooms.py: local-only guard and a short real run against a throwaway server."""
from pathlib import Path
import contextlib
import io
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import load_rooms  # noqa: E402


class LoadRoomsTests(unittest.TestCase):
    def test_refuses_any_host_that_is_not_this_machine(self):
        for url in ('https://cochill.vn', 'http://10.0.0.5:8000', 'http://example.com'):
            with self.subTest(url=url), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    load_rooms.main(['--url', url, '--rooms', '1', '--seconds', '1'])

    def test_one_room_polls_moves_and_cleans_up(self):
        result = load_rooms.scenario(rooms=1, spectators=1, seconds=3)
        self.assertEqual(result['people'], 3)
        snapshots = result['requests']['snapshot']
        self.assertGreaterEqual(snapshots['requests'], 3)
        self.assertEqual(set(snapshots['status']), {200})
        self.assertEqual(result['rooms_at_end'], {'playing': 1})
        self.assertEqual(load_rooms.problems(result), [])


if __name__ == '__main__':
    unittest.main()
