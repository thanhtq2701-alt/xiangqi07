"""Check exported public demo fixtures against the real local rules (no network)."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.puzzles import PUZZLES, BASE, DEFINITIONS
from app.rules import Position


def main():
    source = (ROOT / 'online-preview/fixtures.js').read_text(encoding='utf-8')
    fixtures = json.loads(source.removeprefix('const FIXTURES = ').strip().removesuffix(';'))
    assert len(fixtures) == 2
    for i, fixture in enumerate(fixtures):
        original = PUZZLES[i]
        pos = Position.from_fen(original['fen'])
        assert fixture['id'] == original['id']
        assert fixture['pieces'] == BASE | DEFINITIONS[i][3]
        assert fixture['solution'] == original['solution']
        assert set(fixture['legal']) == set(pos.legal_moves())
        pos.play(fixture['solution'])
    print('PASS: two demo fixtures and their complete legal-move sets match project rules.')


if __name__ == '__main__':
    main()
