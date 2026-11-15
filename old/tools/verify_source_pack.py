"""Verify hashes and safe paths before extracting a V6 source archive to a NEW directory."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify(archive_path, extract_to=None):
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) > 1000:
            raise ValueError('Duplicate paths or excessive file count')
        for name in names:
            p = PurePosixPath(name)
            if p.is_absolute() or '\\' in name or ':' in name or '..' in p.parts or not p.parts:
                raise ValueError('Unsafe ZIP path')
            if any(part in {'.git', 'var', 'node_modules', '__pycache__'} for part in p.parts):
                raise ValueError('Runtime/private directory must not be in source ZIP')
            if p.suffix.lower() in {'.db', '.sqlite', '.sqlite3', '.pem', '.key', '.log'} or p.name == '.env':
                raise ValueError('Private/runtime file must not be in source ZIP')
        if sum(i.file_size for i in archive.infolist()) > 100_000_000:
            raise ValueError('Archive exceeds expected source size')
        manifest = json.loads(archive.read('MANIFEST_SHA256.json'))
        items = manifest['files']
        if set(names) != {i['path'] for i in items} | {'MANIFEST_SHA256.json'} or len(items) != len(names)-1:
            raise ValueError('Manifest membership mismatch')
        for item in items:
            data = archive.read(item['path'])
            if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('File checksum mismatch: '+item['path'])
        if archive.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        if extract_to:
            dest = Path(extract_to).resolve()
            # Never merge into an existing repository or overwrite the user's files.
            if dest.exists():
                raise ValueError('Extraction directory must not already exist')
            dest.mkdir(parents=True)
            for name in names:
                target = dest.joinpath(*PurePosixPath(name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
        return {'files': len(names), 'sha256': hashlib.sha256(Path(archive_path).read_bytes()).hexdigest(),
                'verified': True, 'extractedTo': str(extract_to) if extract_to else None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    parser.add_argument('--extract-to')
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.extract_to), ensure_ascii=True))
