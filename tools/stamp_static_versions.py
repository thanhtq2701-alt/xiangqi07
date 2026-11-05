"""Stamp ?v=<content version> on the static files the frontend loads.

The server lets browsers cache a file for a year only when ?v= matches its current
content, so a changed file always reaches users once its reference is stamped again.

Run after editing anything in online-preview/:  python tools/stamp_static_versions.py
tools/run_checks.py runs this with --check and fails if a stamp is out of date.
"""
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.static_version import content_version  # noqa: E402

WEB = ROOT / 'online-preview'
STAMP = rb'(?:\?v=[0-9a-f]{8})?'
# Images referenced from scripts and stylesheets. They reference nothing, so they are versioned first.
IMAGE_REF = re.compile(rb'(?<![\w./-])([\w-]+\.(?:webp|svg|png|jpg|jpeg|ico))' + STAMP + rb'(?![\w.-])')
# Everything index.html loads. index.html itself is never cached, so it is stamped last.
INDEX_REF = re.compile(rb'((?:src|href)=")([\w-]+\.(?:js|css|webp|svg|png|jpg|jpeg|ico))' + STAMP + rb'"')


def planned_files(web=WEB):
    """Return {path: bytes} for every file whose stamped content differs from disk."""
    def stamp_image(match):
        target = web / match.group(1).decode('ascii')
        if not target.is_file():
            return match.group(0)
        return match.group(1) + b'?v=' + content_version(target.read_bytes()).encode('ascii')

    current, changed = {}, {}
    for path in sorted([*web.glob('*.js'), *web.glob('*.css')]):
        raw = path.read_bytes()
        current[path.name] = IMAGE_REF.sub(stamp_image, raw)
        if current[path.name] != raw:
            changed[path] = current[path.name]

    def stamp_index(match):
        name = match.group(2).decode('ascii')
        target = web / name
        if not target.is_file():
            raise SystemExit('index.html references a missing file: ' + name)
        raw = current.get(name, target.read_bytes())
        return match.group(1) + match.group(2) + b'?v=' + content_version(raw).encode('ascii') + b'"'

    index = web / 'index.html'
    raw = index.read_bytes()
    stamped = INDEX_REF.sub(stamp_index, raw)
    if stamped != raw:
        changed[index] = stamped
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if a stamp is out of date; change nothing')
    args = parser.parse_args()
    changed = planned_files()
    names = sorted(path.name for path in changed)
    if args.check:
        if changed:
            print('Static versions are out of date in: ' + ', '.join(names))
            print('Run: python tools/stamp_static_versions.py')
            return 1
        print('PASS: static file versions are current.')
        return 0
    for path, raw in changed.items():
        path.write_bytes(raw)
    print('Stamped: ' + ', '.join(names) if names else 'Already current.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
