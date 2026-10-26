"""Export original synthetic exercises with legal moves from the Python rules.

Run from any directory. This script does not download games or generate engine
claims: solutions are teaching examples, not asserted unique best moves.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.puzzles import PUZZLES
from app.rules import NAMES, Position, parse_move, square

SKILL_NAMES = {
    'material': 'Quan sát quân và đường đi',
    'cannon': 'Đường đi của Pháo',
    'horse': 'Đường đi của Mã',
    'safety': 'An toàn của Tướng',
}

# Neutral titles do not reveal the intended move before reflection.
TITLES = {
    'loose-rook': 'Quan sát toàn bàn',
    'loose-cannon': 'Dừng lại trước khi chọn',
    'sideways-rook': 'Nhìn từ một góc khác',
    'cannon-file': 'Một vị trí cần quan sát',
    'cannon-rank': 'Thêm một góc nhìn',
    'cannon-enemy-screen': 'Đọc kỹ cấu trúc bàn cờ',
    'horse-fork': 'Chọn một phương án',
    'horse-side': 'Đổi vị trí, giữ cách nghĩ',
    'horse-back': 'Quan sát đủ các hướng',
    'check-capture': 'Ưu tiên điều quan trọng',
    'check-cannon': 'Một quyết định cần kiểm tra',
    'check-blocker': 'Cân nhắc trước khi đi',
}


def intervening_squares(src, dst):
    """Straight-line interior squares; callers only use this for Rook/Cannon."""
    sx, sy, dx, dy = src % 9, src // 9, dst % 9, dst // 9
    assert sx == dx or sy == dy
    step = (1 if dx > sx else -1) if sy == dy else (9 if dy > sy else -9)
    return list(range(src + step, dst, step))


def make_fixtures():
    fixtures = []
    for puzzle in PUZZLES:
        pos = Position.from_fen(puzzle['fen'])
        src, dst = parse_move(puzzle['solution'])
        piece, captured = pos.board[src], pos.board[dst]
        after = pos.play(puzzle['solution'])
        assert captured != '.' and not after.in_check(pos.turn)
        move_label = f'{square(src)} → {square(dst)}'
        what = f'{NAMES[piece.lower()]} Đỏ đi {move_label}, ăn {NAMES[captured.lower()]} Đen.'
        if pos.in_check():
            what += ' Nước này đồng thời giúp Tướng Đỏ thoát chiếu.'
        if piece.lower() == 'r':
            route = intervening_squares(src, dst)
            assert not any(pos.board[i] != '.' for i in route)
            why = 'Xe đi thẳng theo hàng hoặc cột. Các ô giữa điểm xuất phát và điểm đến đều trống; ở đích là quân đối phương.'
            how = 'Kiểm tra Tướng có đang bị chiếu không. Sau đó nhìn dọc cả hàng và cột của Xe, kiểm tra vật cản và quân ở đích trước khi chọn nước.'
        elif piece.lower() == 'c':
            screens = [i for i in intervening_squares(src, dst) if pos.board[i] != '.']
            assert len(screens) == 1
            screen = screens[0]
            screen_color = 'Đỏ' if pos.board[screen].isupper() else 'Đen'
            why = f'Giữa Pháo và quân bị ăn có đúng một quân làm ngòi: {NAMES[pos.board[screen].lower()]} {screen_color} ở {square(screen)}. Pháo được ăn quân bằng cách nhảy qua đúng một ngòi; ngòi có thể thuộc một trong hai bên.'
            how = 'Với mỗi đường Pháo, đếm chính xác số quân nằm giữa Pháo và mục tiêu. Phân biệt nước đi không ăn quân với nước ăn quân, rồi kiểm tra an toàn của Tướng.'
        elif piece.lower() == 'h':
            dx, dy = dst % 9 - src % 9, dst // 9 - src // 9
            leg = src + (dx // 2 if abs(dx) == 2 else (dy // 2) * 9)
            assert pos.board[leg] == '.'
            why = f'Mã đi một bước thẳng rồi một bước chéo, tạo độ lệch 2–1. Ô chân Mã {square(leg)} đang trống nên đường đi tới {square(dst)} không bị cản.'
            how = 'Xem đủ các hướng Mã có thể đi, kể cả nước lùi. Với mỗi ô đích, kiểm tra chân Mã trước, rồi quân ở đích và an toàn của Tướng.'
        else:
            raise AssertionError('Add a verified movement explanation for this piece.')
        if pos.in_check():
            why += ' Bắt quân đang chiếu ở thế này loại bỏ đe dọa trực tiếp; bộ luật xác nhận Tướng Đỏ an toàn sau nước đi.'
            how = 'Khi bị chiếu, ưu tiên tìm nước hợp lệ để thoát chiếu: bắt quân chiếu, che đường chiếu khi có thể, hoặc di chuyển Tướng. Sau đó so sánh kết quả của từng phương án.'
        else:
            why += ' Bộ luật xác nhận nước mẫu không để Tướng Đỏ bị chiếu.'
        fixtures.append({
            'id': puzzle['id'], 'family': puzzle['family'],
            'skill': puzzle['skill'], 'skillName': SKILL_NAMES[puzzle['skill']],
            'title': TITLES[puzzle['id']],
            'description': 'Thế cờ tổng hợp ít quân để luyện quan sát và kiểm tra nước đi; không trích từ một ván đấu thật.',
            'goal': 'Chọn một nước hợp lệ có lợi về quân và giữ an toàn cho Tướng; giải thích lý do của bạn.',
            'fen': pos.fen(), 'turn': pos.turn,
            'pieces': {square(i): p for i, p in enumerate(pos.board) if p != '.'},
            'solution': puzzle['solution'], 'legal': pos.legal_moves(),
            'what': what, 'why': why, 'how': how,
            'source': puzzle['source'], 'phase': 'end',
            'phaseNote': 'Bài tập ít quân được xếp vào mục tàn cuộc để tiện tìm; không phải giáo trình tàn cuộc đã thẩm định.',
            'verification': 'Nước mẫu và toàn bộ nước hợp lệ được kiểm tra bằng bộ luật cục bộ; chưa được chuyên gia thẩm định, không khẳng định nước mẫu là đáp án tốt duy nhất.',
        })
    return fixtures


def main():
    target = ROOT / 'online-preview/fixtures.js'
    target.write_text('const FIXTURES = ' + json.dumps(make_fixtures(), ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    print(f'Exported {len(PUZZLES)} original synthetic exercises to online-preview/fixtures.js')


if __name__ == '__main__':
    main()
