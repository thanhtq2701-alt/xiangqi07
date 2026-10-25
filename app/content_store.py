"""Owner-authored exercises with legal-move validation and explicit versions.

The validator proves move legality, not the correctness of a strategic claim or
the right to reuse a source. Publishing is an explicit owner review decision.
"""
import json
import secrets
import time

from app.cloud_store import APIError, utc
from app.rules import Position, square

SKILLS = {'material': 'Quan sát và bảo vệ quân', 'cannon': 'Đường Pháo và quân ngòi',
          'horse': 'Đường Mã và chân Mã', 'safety': 'An toàn của Tướng'}
FIELDS = {'title', 'fen', 'solution', 'alternatives', 'skill', 'what', 'why', 'how', 'source',
          'goal', 'description', 'phase', 'difficulty', 'pv', 'rights', 'status', 'version'}


def install(db):
    db.executescript('''
        CREATE TABLE IF NOT EXISTS content (
            id TEXT PRIMARY KEY, version INTEGER NOT NULL, status TEXT NOT NULL,
            data TEXT NOT NULL, created_at REAL NOT NULL, updated_at REAL NOT NULL,
            author_id TEXT REFERENCES users(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS content_history (
            content_id TEXT NOT NULL REFERENCES content(id) ON DELETE CASCADE,
            version INTEGER NOT NULL, status TEXT NOT NULL, data TEXT NOT NULL,
            updated_at REAL NOT NULL, PRIMARY KEY(content_id,version));
    ''')


def text(data, key, limit, required=False, default=''):
    value = data.get(key, default)
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise APIError(400, f'Mục {key} cần là văn bản từ {1 if required else 0} đến {limit} ký tự.', 'content_invalid')
    if any(ord(c) < 32 and c not in '\n\r\t' for c in value):
        raise APIError(400, f'Mục {key} chứa ký tự không hợp lệ.', 'content_invalid')
    return value.strip()


def validate(data):
    if set(data) - FIELDS:
        raise APIError(400, 'Có trường nội dung chưa được hỗ trợ.', 'content_invalid')
    result = {key: text(data, key, limit, required) for key, limit, required in (
        ('title', 120, True), ('what', 3000, True), ('why', 3000, True), ('how', 3000, True), ('source', 3000, True),
        ('goal', 500, False), ('description', 1000, False), ('rights', 1000, False))}
    skill = data.get('skill', 'material')
    if not isinstance(skill, str) or skill not in SKILLS:
        raise APIError(400, 'Kỹ năng chưa được hỗ trợ.', 'content_invalid')
    phase = data.get('phase', 'end')
    if phase not in ('opening', 'middle', 'end'):
        raise APIError(400, 'Giai đoạn ván không hợp lệ.', 'content_invalid')
    difficulty = data.get('difficulty', 'unrated')
    if difficulty not in ('unrated', 'beginner', 'intermediate', 'advanced'):
        raise APIError(400, 'Mức độ bài chưa hợp lệ.', 'content_invalid')
    try:
        pos = Position.from_fen(data.get('fen'))
    except ValueError as exc:
        raise APIError(400, str(exc), 'content_invalid_fen')
    legal = pos.legal_moves()
    solution = data.get('solution')
    alternatives = data.get('alternatives', [])
    if not isinstance(solution, str) or solution not in legal:
        raise APIError(400, 'Nước mẫu không hợp lệ trong thế cờ này.', 'content_illegal_move')
    if not isinstance(alternatives, list) or len(alternatives) > 20 or any(not isinstance(move, str) or move not in legal for move in alternatives):
        raise APIError(400, 'Mọi nước chấp nhận phải hợp lệ tại cùng thế; tối đa 20 nước.', 'content_illegal_move')
    pv = data.get('pv', [solution])
    if not isinstance(pv, list) or not 1 <= len(pv) <= 30 or pv[0] != solution:
        raise APIError(400, 'Biến minh họa cần bắt đầu bằng nước mẫu và tối đa 30 nửa nước.', 'content_invalid_variation')
    line = pos
    try:
        for move in pv:
            line = line.play(move)
    except (ValueError, TypeError):
        raise APIError(400, 'Biến minh họa có nước sai luật.', 'content_invalid_variation')
    result.update(fen=pos.fen(), turn=pos.turn, pieces={square(i): p for i, p in enumerate(pos.board) if p != '.'},
                  solution=solution, alternatives=list(dict.fromkeys(alternatives)), legal=legal, skill=skill, skillName=SKILLS[skill],
                  phase=phase, difficulty=difficulty, pv=pv,
                  verification='Đã kiểm tra FEN, các nước được chấp nhận và biến bằng luật; nhận định và quyền dùng nguồn do chủ sở hữu duyệt. Chưa chứng nhận tối ưu bằng engine.',
                  provenance={'kind': 'owner-authored', 'rulesValidated': True, 'engineVerified': False, 'trainingData': False})
    return result


def view(row):
    result = json.loads(row['data'])
    result.update(id=row['id'], family=row['id'], version=row['version'], status=row['status'],
                  createdAt=utc(row['created_at']), updatedAt=utc(row['updated_at']))
    return result


def list_content(db, published=False):
    query = 'SELECT * FROM content' + (" WHERE status='published'" if published else '') + ' ORDER BY updated_at DESC LIMIT 500'
    return [view(row) for row in db.execute(query)]


def create(db, uid, data):
    if data.get('status', 'draft') != 'draft':
        raise APIError(400, 'Bài mới cần lưu nháp trước khi duyệt xuất bản.', 'content_requires_draft')
    clean = validate(data)
    identity, now = 'custom-' + secrets.token_hex(16), time.time()
    serialized = json.dumps(clean, ensure_ascii=False)
    db.execute('INSERT INTO content VALUES (?,1,?,?,?,?,?)', (identity, 'draft', serialized, now, now, uid))
    db.execute('INSERT INTO content_history VALUES (?,1,?,?,?)', (identity, 'draft', serialized, now))
    db.execute('INSERT INTO audit(actor_id,action,created_at) VALUES (?,?,?)', (uid, 'content-draft', now))
    return view(db.execute('SELECT * FROM content WHERE id=?', (identity,)).fetchone())


def update(db, uid, identity, data):
    row = db.execute('SELECT * FROM content WHERE id=?', (identity,)).fetchone()
    if not row:
        raise APIError(404, 'Không có bài học này.')
    # Publication is a content edit too: a stale tab must never publish a draft
    # the operator has not reviewed, or overwrite a newer correction.
    version = data.get('version')
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise APIError(400, 'Cần phiên bản nội dung đang xem trước khi sửa hoặc xuất bản.', 'content_version_required')
    if version != row['version']:
        raise APIError(409, 'Nội dung đã có bản mới. Hãy tải lại trước khi sửa.', 'content_version_conflict', version=row['version'])
    status = data.get('status', row['status'])
    if status not in ('draft', 'published', 'withdrawn'):
        raise APIError(400, 'Trạng thái nội dung không hợp lệ.')
    if set(data) - FIELDS:
        raise APIError(400, 'Có trường nội dung chưa được hỗ trợ.')
    old = json.loads(row['data'])
    merged = {key: value for key, value in old.items() if key in FIELDS}
    merged.update(data)
    # The simple editor does not expose variations. A line belongs to its exact
    # root and model move; retaining it after either changes can block a valid
    # correction (or present a stale continuation). Keep only the new model move
    # unless the caller explicitly supplies a replacement line to validate.
    if 'pv' not in data and any(key in data and data[key] != old.get(key) for key in ('fen', 'solution')):
        merged['pv'] = [merged.get('solution')]
    clean = validate(merged)
    # Editing a published exercise requires a new review; never silently change
    # an answer already being studied. Owner must explicitly republish.
    edits = set(data) - {'status', 'version'}
    if edits and row['status'] == 'published':
        status = 'draft'
    now, version = time.time(), row['version'] + 1
    serialized = json.dumps(clean, ensure_ascii=False)
    db.execute('UPDATE content SET version=?,status=?,data=?,updated_at=? WHERE id=?', (version, status, serialized, now, identity))
    db.execute('INSERT INTO content_history VALUES (?,?,?,?,?)', (identity, version, status, serialized, now))
    db.execute('INSERT INTO audit(actor_id,action,created_at) VALUES (?,?,?)', (uid, 'content-' + status, now))
    return view(db.execute('SELECT * FROM content WHERE id=?', (identity,)).fetchone())
