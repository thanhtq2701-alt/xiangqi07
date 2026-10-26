import unittest
from app.rules import Position, START_FEN, index, square, parse_move


def setup(pieces, turn='w'):
    board = ['.'] * 90
    for sq, p in {'e0': 'K', 'e9': 'k', 'e4': 'P', **pieces}.items():
        board[index(sq)] = p
    return Position(tuple(board), turn)


class RulesTests(unittest.TestCase):
    def test_coordinate_roundtrip(self):
        for i in range(90):
            self.assertEqual(index(square(i)), i)

    def test_invalid_coordinates(self):
        for value in ('a10', 'j1', '-1', '', None, '11'):
            with self.assertRaises(ValueError):
                index(value)

    def test_fen_roundtrip(self):
        self.assertEqual(Position.from_fen(START_FEN).fen(), START_FEN)

    def test_initial_legal_count(self):
        self.assertEqual(len(Position.from_fen(START_FEN).legal_moves()), 44)

    def test_initial_perft_two(self):
        pos = Position.from_fen(START_FEN)
        self.assertEqual(sum(len(pos.play(m).legal_moves()) for m in pos.legal_moves()), 1920)

    def test_general_palace(self):
        pos = setup({})
        self.assertTrue({'e0d0', 'e0f0', 'e0e1'} <= set(pos.legal_moves()))
        self.assertNotIn('e0e3', pos.legal_moves())

    def test_general_cannot_exit_palace(self):
        pos = setup({'e0': '.', 'd0': 'K'})
        self.assertNotIn('d0c0', pos.legal_moves())

    def test_advisor_diagonal_and_palace(self):
        pos = setup({'d0': 'A'})
        self.assertIn('d0e1', pos.legal_moves())
        self.assertNotIn('d0c1', pos.legal_moves())
        self.assertNotIn('d0d1', pos.legal_moves())

    def test_elephant_eye(self):
        self.assertIn('c0e2', setup({'c0': 'E'}).legal_moves())
        self.assertNotIn('c0e2', setup({'c0': 'E', 'd1': 'R'}).legal_moves())

    def test_elephant_river(self):
        self.assertNotIn('c4e6', setup({'c4': 'E'}).legal_moves())

    def test_black_elephant_river(self):
        self.assertNotIn('c5e3', setup({'c5': 'e'}, 'b').legal_moves())

    def test_horse_leg_each_direction(self):
        for dest, leg in [('d5','c4'),('b5','c4'),('e4','d3'),('e2','d3'),('d1','c2'),('b1','c2'),('a2','b3'),('a4','b3')]:
            self.assertIn('c3'+dest, setup({'c3':'H','e4':'.','e5':'P'}).legal_moves())
            self.assertNotIn('c3'+dest, setup({'c3':'H','e4':'.','e5':'P',leg:'P'}).legal_moves())

    def test_rook_blocker(self):
        pos = setup({'a1':'R','a3':'P','d1':'r'})
        self.assertIn('a1d1', pos.legal_moves())
        self.assertNotIn('a1e1', pos.legal_moves())
        self.assertNotIn('a1a4', pos.legal_moves())
        self.assertNotIn('a1b2', pos.legal_moves())

    def test_cannon_exactly_one_screen(self):
        for screens, expected in [({},False),({'a3':'P'},True),({'a3':'P','a4':'p'},False)]:
            pos=setup({'a1':'C','a6':'r',**screens})
            self.assertEqual('a1a6' in pos.legal_moves(), expected)

    def test_cannon_cannot_jump_to_empty(self):
        pos=setup({'a1':'C','a3':'p'})
        self.assertNotIn('a1a4',pos.legal_moves())
        self.assertNotIn('a1a3',pos.legal_moves())

    def test_red_pawn_before_river(self):
        moves=setup({'a3':'P'}).legal_moves()
        self.assertIn('a3a4',moves)
        self.assertNotIn('a3b3',moves)
        self.assertNotIn('a3a2',moves)

    def test_red_pawn_after_river(self):
        moves=setup({'b5':'P'}).legal_moves()
        self.assertTrue({'b5a5','b5c5','b5b6'} <= set(moves))
        self.assertNotIn('b5b4',moves)

    def test_black_pawn_direction(self):
        self.assertIn('a6a5',setup({'a6':'p'},'b').legal_moves())
        self.assertNotIn('a6b6',setup({'a6':'p'},'b').legal_moves())
        self.assertIn('a4b4',setup({'a4':'p'},'b').legal_moves())

    def test_pawn_last_rank_sideways(self):
        self.assertTrue({'b9a9','b9c9'} <= set(setup({'b9':'P'}).legal_moves()))

    def test_flying_general_blocks_exposure(self):
        pos=setup({})
        self.assertNotIn('e4d4',pos.legal_moves())
        self.assertTrue(setup({'e4':'.'}).in_check('w'))
        self.assertTrue(setup({'e4':'.'}).in_check('b'))

    def test_no_general_capture(self):
        self.assertNotIn('e0e9',setup({'e4':'.'}).legal_moves())

    def test_self_check_rejected(self):
        pos=setup({'a0':'r','b0':'R'})
        self.assertNotIn('b0b1',pos.legal_moves())
        self.assertIn('b0a0',pos.legal_moves())

    def test_check_requires_response(self):
        pos=setup({'a0':'r','b3':'R'})
        self.assertTrue(pos.in_check())
        self.assertNotIn('b3b4',pos.legal_moves())
        self.assertIn('e0e1',pos.legal_moves())

    def test_stalemate_is_loss(self):
        pos=setup({'d2':'r','f2':'r','e2':'p','e4':'.'})
        self.assertFalse(pos.in_check())
        self.assertEqual(pos.legal_moves(),[])
        self.assertEqual(pos.status()['winner'],'b')

    def test_mate_is_loss(self):
        pos=setup({'d1':'r','f1':'r','e1':'p','e4':'.'})
        self.assertTrue(pos.in_check())
        self.assertEqual(pos.status()['reason'],'Chiếu hết')

    def test_illegal_does_not_mutate(self):
        pos=Position.from_fen(START_FEN)
        with self.assertRaises(ValueError):pos.play('a0a9')
        self.assertEqual(pos.fen(),START_FEN)

    def test_turn_and_capture(self):
        pos=setup({'a2':'R','a7':'r'})
        result=pos.play('a2a7')
        self.assertEqual(result.board[index('a7')],'R')
        self.assertEqual(result.board[index('a2')],'.')
        self.assertEqual(result.turn,'b')

    def test_invalid_fen_rejected(self):
        for fen in ('9/9 w',START_FEN.replace(' w',' x'),START_FEN.replace('K','R'),START_FEN.replace('9','8',1),'9/9/9/9/9/9/9/9/9/9 w', setup({'e4':'.'}).fen(),setup({'b6':'p'}).fen(),setup({'c0':'.','c2':'E'}).fen()):
            with self.subTest(fen=fen),self.assertRaises(ValueError):Position.from_fen(fen)

    def test_move_input(self):
        for m in ('a0',None,123,'a0j9'):
            with self.assertRaises(ValueError):parse_move(m)

    def test_legal_play_sequence_preserves_generals(self):
        pos=Position.from_fen(START_FEN)
        for _ in range(40):
            moves=pos.legal_moves()
            if not moves:break
            pos=pos.play(moves[len(moves)//2])
            self.assertFalse(pos.in_check('w' if pos.turn=='b' else 'b'))
            self.assertEqual(pos.board.count('K'),1)
            self.assertEqual(pos.board.count('k'),1)


if __name__=='__main__':unittest.main()
