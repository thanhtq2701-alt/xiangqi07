"""Original synthetic teaching fixtures, not human games or a gold dataset."""
from app.rules import Position, index


def position(pieces, turn='w'):
    board = ['.'] * 90
    for sq, piece in pieces.items():
        board[index(sq)] = piece
    return Position.from_fen(Position(tuple(board), turn).fen()).fen()


BASE = {'e0': 'K', 'e9': 'k', 'e4': 'P'}
DEFINITIONS = [
    ('loose-rook', 'material', 'Nhìn cả hai cánh', {'a2': 'R', 'a7': 'r', 'i6': 'p'}, 'a2a7', 'a2b2'),
    ('loose-cannon', 'material', 'Đếm quân trước khi đi', {'h2': 'R', 'h7': 'c', 'a6': 'p'}, 'h2h7', 'h2g2'),
    ('sideways-rook', 'material', 'Thay đổi hướng quan sát', {'b3': 'R', 'g3': 'r', 'a6': 'p'}, 'b3g3', 'b3b2'),
    ('cannon-file', 'cannon', 'Một quân ngòi', {'b2': 'C', 'b4': 'H', 'b7': 'r', 'i6': 'p'}, 'b2b7', 'b2a2'),
    ('cannon-rank', 'cannon', 'Ngòi trên hàng ngang', {'a3': 'C', 'c3': 'H', 'h3': 'r', 'a6': 'p'}, 'a3h3', 'a3a2'),
    ('cannon-enemy-screen', 'cannon', 'Quân đối thủ cũng là ngòi', {'g2': 'C', 'g4': 'p', 'g7': 'r', 'a6': 'p'}, 'g2g7', 'g2h2'),
    ('horse-fork', 'horse', 'Đường Mã thông thoáng', {'c3': 'H', 'd5': 'r', 'a6': 'p'}, 'c3d5', 'c3a2'),
    ('horse-side', 'horse', 'Mã hướng sang cánh', {'f3': 'H', 'h4': 'c', 'a6': 'p'}, 'f3h4', 'f3d2'),
    ('horse-back', 'horse', 'Không bỏ qua nước lùi', {'g5': 'H', 'e6': 'r', 'a6': 'p'}, 'g5e6', 'g5i4'),
    ('check-capture', 'safety', 'Thoát chiếu chủ động', {'a0': 'r', 'a2': 'R', 'i6': 'p'}, 'a2a0', 'e0e1'),
    ('check-cannon', 'safety', 'Gỡ chiếu ở hàng cuối', {'i0': 'r', 'i2': 'R', 'a6': 'p'}, 'i2i0', 'e0e1'),
    ('check-blocker', 'safety', 'Kiểm tra mọi cách thoát chiếu', {'e2': 'r', 'a2': 'R', 'i6': 'p'}, 'a2e2', 'e0d0'),
]


def bank():
    return [dict(id=pid, family=pid, skill=skill, title=title,
                 fen=position(BASE | pieces), solution=solution, demo_mistake=mistake,
                 source='synthetic-codex-v1', verification='legal rules + local depth-2 search; owner review pending', level='Cơ bản')
            for pid, skill, title, pieces, solution, mistake in DEFINITIONS]


PUZZLES = bank()

