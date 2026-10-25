"""Deterministic Xiangqi movement. Coordinates: a0 = red's bottom left.

Board indexing is top-down (black at y=0); red moves toward smaller y.
Tournament perpetual-check/chase adjudication is deliberately not implemented.
"""
from dataclasses import dataclass

START_FEN = 'rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w'
NAMES = {'k': 'Tướng', 'a': 'Sĩ', 'e': 'Tượng', 'r': 'Xe', 'h': 'Mã', 'c': 'Pháo', 'p': 'Tốt'}


def side(piece):
    return 'w' if piece.isupper() else 'b'


def other(turn):
    return 'b' if turn == 'w' else 'w'


def square(index):
    return chr(97 + index % 9) + str(9 - index // 9)


def index(sq):
    if not isinstance(sq, str) or len(sq) != 2 or sq[0] not in 'abcdefghi' or sq[1] not in '0123456789':
        raise ValueError('Ô cờ phải có dạng a0 đến i9.')
    return (9 - int(sq[1])) * 9 + ord(sq[0]) - 97


def parse_move(move):
    if not isinstance(move, str) or len(move) != 4:
        raise ValueError('Nước đi phải có dạng a0a1.')
    return index(move[:2]), index(move[2:])


@dataclass(frozen=True)
class Position:
    board: tuple
    turn: str = 'w'

    @classmethod
    def from_fen(cls, fen):
        if not isinstance(fen, str) or len(fen) > 200:
            raise ValueError('FEN không hợp lệ.')
        fields = fen.strip().split()
        if len(fields) not in (2, 6) or fields[1] not in ('w', 'b'):
            raise ValueError('FEN cần bàn cờ và lượt w hoặc b.')
        ranks = fields[0].split('/')
        if len(ranks) != 10:
            raise ValueError('FEN cần đúng 10 hàng.')
        board = []
        for rank in ranks:
            row = []
            for c in rank:
                c = {'n': 'h', 'N': 'H', 'b': 'e', 'B': 'E'}.get(c, c)
                if c in '123456789':
                    row.extend(['.'] * int(c))
                elif c in 'rheakcpRHEAKCP':
                    row.append(c)
                else:
                    raise ValueError('Ký hiệu FEN không hợp lệ.')
            if len(row) != 9:
                raise ValueError('Mỗi hàng FEN cần đúng 9 ô.')
            board.extend(row)
        pos = cls(tuple(board), fields[1])
        for color in ('w', 'b'):
            for p, maximum in [('k', 1), ('r', 2), ('h', 2), ('c', 2), ('a', 2), ('e', 2), ('p', 5)]:
                count = board.count(p.upper() if color == 'w' else p)
                if count > maximum or (p == 'k' and count != 1):
                    raise ValueError('Số quân không hợp lệ; mỗi bên cần một Tướng.')
        for i, p in enumerate(board):
            if p == '.':
                continue
            x, y = i % 9, i // 9
            red = side(p) == 'w'
            if p.lower() in ('k', 'a') and not (3 <= x <= 5 and (7 <= y <= 9 if red else 0 <= y <= 2)):
                raise ValueError('Tướng và Sĩ phải ở trong cung.')
            if p.lower() == 'a' and (x + y) % 2 != (0 if red else 1):
                raise ValueError('Sĩ không ở điểm hợp lệ trong cung.')
            if p.lower() == 'e' and (x, y) not in ({(2, 9), (6, 9), (0, 7), (4, 7), (8, 7), (2, 5), (6, 5)} if red else {(2, 0), (6, 0), (0, 2), (4, 2), (8, 2), (2, 4), (6, 4)}):
                raise ValueError('Tượng không ở điểm hợp lệ bên mình.')
            if p.lower() == 'p' and ((red and y > 6) or (not red and y < 3) or ((y >= 5 if red else y <= 4) and x % 2)):
                raise ValueError('Tốt chưa qua sông phải nằm trên lộ xuất phát.')
        if pos.in_check(other(pos.turn)):
            raise ValueError('FEN không hợp lệ: bên vừa đi vẫn bị chiếu hoặc hai Tướng đối mặt.')
        return pos

    def fen(self):
        ranks = []
        for y in range(10):
            row, empty = '', 0
            for p in self.board[y * 9:y * 9 + 9]:
                if p == '.':
                    empty += 1
                else:
                    row += (str(empty) if empty else '') + p
                    empty = 0
            ranks.append(row + (str(empty) if empty else ''))
        return '/'.join(ranks) + ' ' + self.turn

    def targets(self, src):
        p = self.board[src]
        if p == '.':
            return []
        x, y, red = src % 9, src // 9, side(p) == 'w'
        result = []

        def add(tx, ty):
            if 0 <= tx < 9 and 0 <= ty < 10:
                dest = ty * 9 + tx
                if self.board[dest] == '.' or side(self.board[dest]) != side(p):
                    result.append(dest)

        kind = p.lower()
        if kind in ('r', 'c'):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                tx, ty, screen = x + dx, y + dy, False
                while 0 <= tx < 9 and 0 <= ty < 10:
                    dest = ty * 9 + tx
                    occupied = self.board[dest] != '.'
                    if not screen:
                        if not occupied:
                            add(tx, ty)
                        elif kind == 'r':
                            add(tx, ty)
                            break
                        else:
                            screen = True
                    elif occupied:
                        add(tx, ty)
                        break
                    tx, ty = tx + dx, ty + dy
        elif kind == 'h':
            for dx, dy in ((1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)):
                lx, ly = x + (dx // 2 if abs(dx) == 2 else 0), y + (dy // 2 if abs(dy) == 2 else 0)
                if 0 <= lx < 9 and 0 <= ly < 10 and self.board[ly * 9 + lx] == '.':
                    add(x + dx, y + dy)
        elif kind == 'e':
            for dx, dy in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
                tx, ty = x + dx, y + dy
                if 0 <= tx < 9 and 0 <= ty < 10 and (ty >= 5 if red else ty <= 4) and self.board[(y + dy // 2) * 9 + x + dx // 2] == '.':
                    add(tx, ty)
        elif kind in ('k', 'a'):
            steps = ((1, 0), (-1, 0), (0, 1), (0, -1)) if kind == 'k' else ((1, 1), (1, -1), (-1, 1), (-1, -1))
            for dx, dy in steps:
                tx, ty = x + dx, y + dy
                if 3 <= tx <= 5 and (7 <= ty <= 9 if red else 0 <= ty <= 2):
                    add(tx, ty)
            if kind == 'k':
                for dy in (-1, 1):
                    ty = y + dy
                    while 0 <= ty < 10:
                        q = self.board[ty * 9 + x]
                        if q != '.':
                            if q.lower() == 'k' and side(q) != side(p):
                                add(x, ty)
                            break
                        ty += dy
        elif kind == 'p':
            add(x, y - 1 if red else y + 1)
            if y <= 4 if red else y >= 5:
                add(x - 1, y)
                add(x + 1, y)
        return result

    def in_check(self, color=None):
        color = color or self.turn
        general = 'K' if color == 'w' else 'k'
        if general not in self.board:
            return True
        king = self.board.index(general)
        return any(king in self.targets(i) for i, p in enumerate(self.board) if p != '.' and side(p) != color)

    def after_unchecked(self, move):
        src, dst = parse_move(move)
        board = list(self.board)
        board[dst], board[src] = board[src], '.'
        return Position(tuple(board), other(self.turn))

    def legal_moves(self):
        moves = []
        for src, p in enumerate(self.board):
            if p == '.' or side(p) != self.turn:
                continue
            for dst in self.targets(src):
                if self.board[dst].lower() == 'k':
                    continue  # end at mate, never remove a general
                move = square(src) + square(dst)
                if not self.after_unchecked(move).in_check(self.turn):
                    moves.append(move)
        return moves

    def play(self, move):
        parse_move(move)
        if move not in self.legal_moves():
            raise ValueError('Nước đi không hợp lệ. Hãy kiểm tra luật và an toàn của Tướng.')
        return self.after_unchecked(move)

    def status(self):
        if not self.legal_moves():
            return {'over': True, 'winner': other(self.turn), 'reason': 'Chiếu hết' if self.in_check() else 'Hết nước hợp lệ (thua theo luật cờ tướng)'}
        return {'over': False, 'winner': None, 'reason': 'Đang bị chiếu' if self.in_check() else 'Đang chơi'}


def describe(pos, move):
    src, dst = parse_move(move)
    piece, captured = pos.board[src], pos.board[dst]
    return f'{NAMES[piece.lower()]} {square(src)} → {square(dst)}' + (f' ăn {NAMES[captured.lower()]}' if captured != '.' else '')
