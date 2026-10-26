"""Run the portable web package checks without installing dependencies.

Usage: python tools/check_all.py [--node PATH_TO_NODE]
Requires Python 3.10+ and Node.js 18+. Does not modify source or access a network.
"""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_NAMES = ('xiangqi.js', 'game-tools.js', 'fixtures.js', 'learning.js', 'experience.js', 'app.js')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default='node', help='Node executable name or full path (default: node on PATH)')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10 or newer is required.')
    node = shutil.which(args.node)
    if not node:
        parser.error('Node.js was not found. Install a supported Node release or supply --node PATH.')
    try:
        version = subprocess.check_output([node, '--version'], text=True, timeout=15).strip()
    except (OSError, subprocess.SubprocessError) as error:
        parser.error('Cannot start Node.js: ' + str(error))
    match = re.fullmatch(r'v(\d+)\.\d+\.\d+(?:[-+].*)?', version)
    if not match or int(match.group(1)) < 18:
        parser.error('Node.js 18 or newer is required; found ' + version)
    commands = [(f'JavaScript syntax: {name}', [node, '--check', str(ROOT / 'online-preview' / name)]) for name in SCRIPT_NAMES]
    commands.extend((name, [node, str(ROOT / 'tools' / name)]) for name in (
        'test_preview_learning.cjs', 'test_preview_game_tools.cjs', 'test_preview_experience.cjs'))
    commands.extend([
        ('Python reference rules', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_rules.py', '-v']),
        ('Exported exercises match source', [sys.executable, str(ROOT / 'tools/check_online_preview.py')]),
        ('Browser/Python rule and engine parity', [sys.executable, str(ROOT / 'tools/check_browser_rules.py'), '--node', node]),
    ])
    failures = []
    began = time.monotonic()
    print(f'Python {sys.version.split()[0]} | Node {version} | {len(commands)} checks', flush=True)
    for number, (label, command) in enumerate(commands, 1):
        print(f'\n[{number}/{len(commands)}] {label}', flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, timeout=300, check=False)
            if result.returncode:
                failures.append((label, f'exit {result.returncode}'))
            else:
                print('PASS', flush=True)
        except (OSError, subprocess.TimeoutExpired) as error:
            failures.append((label, str(error)))
            print('FAIL: ' + str(error), flush=True)
    elapsed = time.monotonic() - began
    print(f'\nResult: {len(commands) - len(failures)}/{len(commands)} checks passed in {elapsed:.1f}s', flush=True)
    for label, reason in failures:
        print(f'FAIL: {label}: {reason}', flush=True)
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
