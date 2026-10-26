"""Local acceptance fixture only. Never use this server/database/credentials for real users."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from co_chill_server import CloudApplication, QuietHandler
from wsgiref.simple_server import make_server
app=CloudApplication(db_path='var/v5-acceptance.sqlite3',public_origin='',admin_totp_secret='GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ')
with app.store.connect(True) as db:
    if not db.execute("SELECT 1 FROM users WHERE username='qa_owner'").fetchone():
        app.store.create_user(db, {'username':'qa_owner','displayName':'Quản trị kiểm thử','password':'QA-only-1024!local'},'admin')
    db.execute('UPDATE users SET test_account=1')
print('QA only: http://127.0.0.1:8771',flush=True)
with make_server('127.0.0.1',8771,app,handler_class=QuietHandler) as server:server.serve_forever()
