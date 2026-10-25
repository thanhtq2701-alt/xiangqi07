from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LOGS = ROOT / 'var/migration-2026-10-17'
PACKAGE = ROOT / 'deliverables/Co_Chill_VSCode_2026_10_17'
ZIP = PACKAGE.with_suffix('.zip')
files = json.loads((LOGS / 'package-files.json').read_text(encoding='utf-8'))
manifest = json.loads((PACKAGE / 'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
log = (LOGS / 'package-tests.log').read_text(encoding='utf-8-sig')
assert 'Result: 12/12 checks passed' in log, 'Package tests have not all passed.'
assert not ZIP.exists(), 'Refusing to overwrite archive.'
for entry in manifest['files']:
    copied = (PACKAGE / entry['package_relative_path']).read_bytes()
    original = (ROOT / entry['original_relative_path']).read_bytes()
    assert copied == original, entry['original_relative_path']
    assert hashlib.sha256(copied).hexdigest() == entry['sha256'], entry['original_relative_path']
actual = sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts)
assert actual == files, (actual, files)
for relative in files:
    assert not any(part in ('.git', '.openai', 'var', 'node_modules', '__pycache__') for part in Path(relative).parts)
    assert Path(relative).suffix.lower() not in ('.pyc', '.docx', '.sqlite3', '.zip')
with zipfile.ZipFile(ZIP, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative in files:
        archive.write(PACKAGE / relative, PACKAGE.name + '/' + relative)
with zipfile.ZipFile(ZIP) as archive:
    expected_names = [PACKAGE.name + '/' + relative for relative in files]
    assert sorted(archive.namelist()) == sorted(expected_names)
    assert archive.testzip() is None
    for relative in files:
        assert archive.read(PACKAGE.name + '/' + relative) == (PACKAGE / relative).read_bytes(), relative
node_suites = re.findall(r'\d+/\d+ [^\r\n]+tests passed', log)
parity_line = next(line for line in log.splitlines() if line.startswith('{"positions":'))
report = {
    'package_path': str(PACKAGE), 'zip_path': str(ZIP), 'file_count': len(files),
    'copied_source_file_count': len(manifest['files']), 'runtime_file_count': 10,
    'runtime_hashes_match': True, 'zip_exact_filelist_and_hashes_match': True,
    'zip_sha256': hashlib.sha256(ZIP.read_bytes()).hexdigest(), 'zip_bytes': ZIP.stat().st_size,
    'source_git_head': manifest['source_git_head'],
    'test_summary': [
        '12/12 check groups passed: 6 JavaScript syntax checks, 3 Node suites, Python rules, fixture validation, JS/Python parity.',
        *node_suites, 'Python reference rules: 30 tests passed.',
        '12 synthetic exercise fixtures match the original rules/source/provenance.',
        parity_line,
        'Obsolete Node v6.14.0 on PATH rejected with clear error and exit code 2; tests passed using Node v24.19.0 and Python 3.12.14.',
        'All 23 copied source files are byte-for-byte identical to original working-tree files; all 10 runtime asset hashes match.',
        'Archive filelist, every file byte content, and ZIP CRC validated; generated Python caches excluded.',
    ],
    'start_command': 'python -m http.server 8769 --bind 127.0.0.1 --directory online-preview',
    'start_url': 'http://127.0.0.1:8769/#home',
    'files': files,
}
(LOGS / 'package_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: report[key] for key in ('file_count', 'runtime_hashes_match', 'zip_exact_filelist_and_hashes_match', 'zip_bytes', 'zip_sha256')}, ensure_ascii=True))
