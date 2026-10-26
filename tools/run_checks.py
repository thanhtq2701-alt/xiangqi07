"""Run the checks shipped in the V6 source pack. No downloaded dependencies."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON_TESTS = ['test_rules', 'test_cloud', 'test_pikafish', 'test_online_rooms', 'test_online_http']
JS_TESTS = ['test_preview_learning', 'test_preview_experience', 'test_preview_game_tools',
            'test_cloud_client', 'test_engine_client', 'test_v5_ui', 'test_v6_ui',
            'test_v6_learning', 'test_v6_online_ui', 'test_v6_learning_ui']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default=shutil.which('node'), help='Node executable (only needed for tests)')
    parser.add_argument('--report', help='Optional JSON result path, outside source recommended')
    args = parser.parse_args()
    if not args.node:
        parser.error('Install Node.js for checks or supply --node PATH. The app itself does not need Node.')
    # Compile without creating .pyc artifacts in the delivered source.
    sources = [ROOT / 'co_chill_server.py', *(ROOT / 'app').glob('*.py'),
               *(ROOT / 'tests').glob('*.py'), *(ROOT / 'tools').glob('*.py')]
    for source in sources:
        compile(source.read_bytes(), str(source), 'exec')
    commands = [[sys.executable, '-m', 'unittest', '-v', *('tests.' + x for x in PYTHON_TESTS)],
                [sys.executable, 'tools/check_online_preview.py'],
                [sys.executable, 'tools/check_browser_rules.py', '--node', args.node]]
    commands += [[args.node, '--check', str(p.relative_to(ROOT))] for p in sorted((ROOT / 'online-preview').glob('*.js'))]
    commands += [[args.node, 'tools/' + name + '.cjs'] for name in JS_TESTS]
    results = []
    for command in commands:
        started = time.monotonic()
        print('CHECK ' + ' '.join(command[1:]), flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            output = result.stdout + result.stderr
            code = result.returncode
        except subprocess.TimeoutExpired:
            output, code = 'Timed out after 600 seconds', 124
        print(output, end='' if output.endswith('\n') else '\n', flush=True)
        results.append({'command': command, 'exitCode': code, 'seconds': round(time.monotonic()-started, 2), 'output': output})
    report = {'passed': all(r['exitCode'] == 0 for r in results), 'pythonSourcesCompiled': len(sources), 'checks': results}
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('ALL CHECKS PASSED' if report['passed'] else 'FAILED: inspect output above')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
