"""Check exported public demo fixtures against the real local rules (no network)."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.puzzles import PUZZLES, BASE, DEFINITIONS
from app.rules import Position
from export_preview_fixtures import make_fixtures, SKILL_NAMES


def main():
    source = (ROOT / 'online-preview/fixtures.js').read_text(encoding='utf-8')
    fixtures = json.loads(source.removeprefix('const FIXTURES = ').strip().removesuffix(';'))
    assert len(fixtures) == len(PUZZLES) == 12
    assert len({f['id'] for f in fixtures}) == len(fixtures)
    assert fixtures == make_fixtures(), 'Export is stale; run tools/export_preview_fixtures.py'
    for i, fixture in enumerate(fixtures):
        original = PUZZLES[i]
        pos = Position.from_fen(original['fen'])
        assert fixture['id'] == original['id']
        assert fixture['fen'] == original['fen']
        assert fixture['turn'] == pos.turn
        assert fixture['pieces'] == BASE | DEFINITIONS[i][3]
        assert fixture['solution'] == original['solution']
        assert len(fixture['legal']) == len(set(fixture['legal']))
        assert set(fixture['legal']) == set(pos.legal_moves())
        after = pos.play(fixture['solution'])
        assert not after.in_check(pos.turn)
        assert fixture['skill'] == original['skill']
        assert fixture['skillName'] == SKILL_NAMES[original['skill']]
        assert fixture['source'] == original['source'] == 'synthetic-codex-v1'
        assert fixture['phase'] in ('middle', 'end')
        for field in ('title', 'description', 'goal', 'what', 'why', 'how', 'phaseNote', 'verification'):
            assert isinstance(fixture[field], str) and fixture[field].strip()
        assert fixture['solution'] not in fixture['title']
    assert {f['skill'] for f in fixtures} == set(SKILL_NAMES)
    print('PASS: all 12 synthetic fixtures, grounded text, provenance and complete legal-move sets match project rules.')


if __name__ == '__main__':
    main()
