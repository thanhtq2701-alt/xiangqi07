"""Run with python server.py. Local-only HTTP server, no third-party packages."""
import argparse
import json
import mimetypes
import re
import secrets
import traceback
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from app.storage import Repository
from app.service import Service
from app.learning import SKILLS, LESSONS
from app.engine import ENGINE_VERSION

ROOT = Path(__file__).resolve().parent


def make_server(port=8000, db_path=None):
    service = Service(Repository(db_path or ROOT / 'var/chill.sqlite3'))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            # Never log reflection, cookies, query strings or user data.
            pass

        def respond(self, status, payload, content_type='application/json; charset=utf-8'):
            body = json.dumps(payload, ensure_ascii=False).encode() if content_type.startswith('application/json') else payload
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if getattr(self, 'new_cookie', None):
                self.send_header('Set-Cookie', f'chill_guest={self.new_cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age=31536000')
            self.end_headers()
            self.wfile.write(body)

        def owner(self):
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get('Cookie', ''))
                token = cookie['chill_guest'].value if 'chill_guest' in cookie else ''
            except Exception:
                token = ''
            if not re.fullmatch('[0-9a-f]{64}', token):
                token = secrets.token_hex(32)
                self.new_cookie = token
            return token

        def valid_host(self):
            host = self.headers.get('Host', '')
            return host in (f'localhost:{self.server.server_port}', f'127.0.0.1:{self.server.server_port}')

        def do_GET(self):
            if not self.valid_host():
                return self.respond(403, {'error': 'Localhost only'})
            owner = self.owner()
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                with service.repo.connect() as db:
                    if path == '/api/bootstrap':
                        return self.respond(200, dict(dashboard=service.dashboard(db, owner), skills=SKILLS, lessons=LESSONS,
                                                     engine=ENGINE_VERSION, llm='template-v1', persistence='SQLite · khách trên thiết bị này'))
                    if path == '/api/dashboard':
                        return self.respond(200, service.dashboard(db, owner))
                    if path in ('/api/exercise', '/api/game'):
                        eid = parse_qs(parsed.query).get('id', [''])[0]
                        record = service.repo.get(db, owner, path.split('/')[-1], eid)
                        view = service.exercise_view(record) if path == '/api/exercise' else service.game_view(record)
                        return self.respond(200, view)
                    if path == '/api/export':
                        return self.respond(200, service.export(db, owner))
                static = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css', '/favicon.svg': 'favicon.svg'}
                if path not in static:
                    return self.respond(404, {'error': 'Không tìm thấy trang.'})
                file = ROOT / 'web' / static[path]
                mime = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
                if file.suffix == '.js':
                    mime = 'text/javascript'
                return self.respond(200, file.read_bytes(), mime + '; charset=utf-8')
            except LookupError as exc:
                self.respond(404, {'error': str(exc)})
            except Exception:
                traceback.print_exc()
                self.respond(500, {'error': 'Không đọc được dữ liệu. Hãy thử lại.'})

        def do_POST(self):
            if not self.valid_host() or self.headers.get('Origin', '') not in (f'http://localhost:{self.server.server_port}', f'http://127.0.0.1:{self.server.server_port}'):
                return self.respond(403, {'error': 'Yêu cầu phải đến từ trang đang mở.'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.respond(415, {'error': 'Cần JSON.'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 32768:
                    return self.respond(413, {'error': 'Dữ liệu quá lớn hoặc trống.'})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('JSON phải là object.')
                owner = self.owner()
                with service.repo.connect() as db:
                    db.execute('BEGIN IMMEDIATE')
                    result = service.dispatch(db, owner, urlparse(self.path).path, data)
                self.respond(200, result)
            except LookupError as exc:
                self.respond(404, {'error': str(exc)})
            except (ValueError, TypeError) as exc:
                self.respond(400, {'error': str(exc)})
            except Exception:
                traceback.print_exc()
                self.respond(500, {'error': 'Có lỗi xử lý. Dữ liệu chưa hoàn tất đã được hoàn tác. Hãy thử lại.'})

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Co Chill local prototype')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--db', default=None)
    args = parser.parse_args()
    server = make_server(args.port, args.db)
    print(f'Co Chill running at http://localhost:{server.server_port} (Ctrl+C to stop)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
