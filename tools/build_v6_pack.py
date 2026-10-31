"""Build a clean V6 GitHub/Claude source ZIP using an explicit file allowlist."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import zipfile
from verify_source_pack import verify

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'README.md', 'AGENTS.md', 'CLAUDE.md', '.gitignore', '.gitattributes', '.env.example', '.nvmrc',
    'co_chill_server.py', 'requirements.txt', 'Mo_Co_Chill_V6.cmd',
    'AI_USAGE.md', 'IMPLEMENTATION_REPORT_CODEX.md', 'TEST_REPORT_CODEX.md',
    'KNOWN_LIMITATIONS.md', 'PRIVACY.md', 'THIRD_PARTY_NOTICES.md',
    'deploy/cochill.service', 'deploy/cochill-gunicorn.service.example',
    'deploy/nginx-cochill.conf', 'deploy/cochill.env.example', 'deploy/DEPLOY_GCP_VI.md',
    *('app/'+name+'.py' for name in ['__init__','cloud_store','content_store','online_rooms','pikafish','rules','engine','puzzles']),
    *('online-preview/'+name for name in ['index.html','style.css','v5.css','v6.css','app.js',
        'xiangqi.js','game-tools.js','fixtures.js','learning.js','experience.js','cloud-client.js',
        'engine-client.js','v5-ui.js','v6-ui.js','curriculum.js','line-practice.js',
        'online-play.js','v6-learning-ui.js','favicon.svg','logo-co-chill.png','cover-co-chill.png']),
    *('tests/'+name+'.py' for name in ['__init__','test_rules','test_cloud','test_pikafish','test_online_rooms','test_online_http']),
    *('tools/'+name for name in ['build_v6_pack.py','verify_source_pack.py','run_checks.py',
        'check_online_preview.py','check_browser_rules.py','export_preview_fixtures.py',
        'test_preview_learning.cjs','test_preview_experience.cjs','test_preview_game_tools.cjs',
        'test_cloud_client.cjs','test_engine_client.cjs','test_v5_ui.cjs','test_v6_ui.cjs',
        'test_v6_learning.cjs','test_v6_online_ui.cjs','test_v6_learning_ui.cjs']),
    *('docs/'+name+'.md' for name in ['V6_DECISIONS','CLAUDE_HANDOFF_V6','GITHUB_V6_CHO_NGUOI_MOI',
        'DEPLOY_GCP_V6','PIKAFISH_SETUP_V5']),
]
# Immutable supplied specifications; current owner decisions take precedence.
FILES += ['docs/spec/'+name for name in [
    '00_START_HERE.md','01_PRODUCT_SPEC.md','02_FEEDBACK_AND_CORRECTIONS.md','03_ARCHITECTURE.md',
    '04_PROTOTYPE_7_DAY.md','05_MILESTONES.md','06_ROADMAP.md','07_LEARNING_MODEL_SPACED_REPETITION.md',
    '08_AI_ML_PLAN.md','09_DATA_LICENSE_SOURCES.md','10_README_VI_DRAFT.md','11_DAILY_UPDATE_TEMPLATE.md',
    '12_SETUP_CHECKLIST.md','13_CLAUDE_TRACK.md','14_CODEX_TRACK.md','15_PARALLEL_COMPARISON_SCORECARD.md',
    '16_FUTURE_FEATURE_BACKLOG.md','17_ACTION_ITEMS_BEFORE_CODE.md']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = Path(args.output).resolve()
    if target.suffix.lower() != '.zip' or target.exists():
        raise SystemExit('Choose a NEW .zip path; no overwriting previous releases.')
    entries = {}
    for name in FILES:
        path = ROOT / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise SystemExit('Missing/unsafe source file: '+name)
        entries[name] = path.read_bytes()
    manifest = {'createdAt': datetime.now(timezone(timedelta(hours=7))).isoformat(),
                'kind':'co-chill-v6-source-only', 'containsUserData':False,
                'files':[{'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
                         for name,data in sorted(entries.items())]}
    entries['MANIFEST_SHA256.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    result = verify(target)
    result.update(archive=str(target), bytes=target.stat().st_size)
    target.with_suffix('.sha256.txt').write_text(result['sha256']+'  '+target.name+'\n', encoding='ascii')
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
