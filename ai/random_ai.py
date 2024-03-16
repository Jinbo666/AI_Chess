# ai/random_ai.py
import random

class RandomAI:
    def __init__(self, board, color):
        self.board = board
        self.color = color

    def make_move(self):
        # 假设get_all_possible_moves返回的是(piece, (target_x, target_y))的列表
        possible_moves = self.board.get_all_possible_moves(self.color)
        if possible_moves:
            piece, move = random.choice(possible_moves)
            self.board.move_piece(piece.position, move)
            return True
        return False
