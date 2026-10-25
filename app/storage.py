"""SQLite repository. One transaction per HTTP request, guest ownership enforced."""
import json
import sqlite3
from pathlib import Path


class ClosingConnection(sqlite3.Connection):
    """SQLite's default context manager commits but does not close."""
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class Repository:
    def __init__(self, path='var/chill.sqlite3'):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY, owner TEXT NOT NULL, kind TEXT NOT NULL,
                    data TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS owner_kind ON records(owner, kind);
            ''')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        return db

    def put(self, db, owner, kind, ident, data):
        db.execute('INSERT INTO records(id,owner,kind,data) VALUES (?,?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data WHERE records.owner=excluded.owner',
                   (ident, owner, kind, json.dumps(data, ensure_ascii=False)))

    def get(self, db, owner, kind, ident):
        row = db.execute('SELECT data FROM records WHERE id=? AND owner=? AND kind=?', (ident, owner, kind)).fetchone()
        if row is None:
            raise LookupError('Không tìm thấy dữ liệu của phiên này.')
        return json.loads(row['data'])

    def list(self, db, owner, kind):
        return [json.loads(row['data']) for row in db.execute('SELECT data FROM records WHERE owner=? AND kind=? ORDER BY created,id', (owner, kind))]

    def delete_owner(self, db, owner):
        db.execute('DELETE FROM records WHERE owner=?', (owner,))

    def export(self, db, owner):
        return [dict(kind=row['kind'], data=json.loads(row['data'])) for row in db.execute('SELECT kind,data FROM records WHERE owner=?', (owner,))]
