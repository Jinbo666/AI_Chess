# ai/random_ai.py
import random

class RandomAI:
    def __init__(self, board, color):
        self.board = board
        self.color = color


    def get_all_possible_moves(self):
        """为当前AI的颜色收集所有不会吃掉己方棋子的合法移动"""
        all_possible_moves = []  # 存储形式为 [(piece, (target_x, target_y)), ...]
        for piece in self.board.pieces.values():
            if piece.color == self.color:
                moves = self.board.get_all_possible_moves(piece)  # 获取合法移动
                for move in moves:
                    target_piece = self.board.get_piece_at(move)
                    # 只添加不会吃掉己方棋子的移动
                    if not target_piece or target_piece.color != self.color:
                        all_possible_moves.append((piece, move))
        return all_possible_moves

    def make_move(self):
        """随机选择并执行一个移动"""
        all_possible_moves = self.get_all_possible_moves()
        if all_possible_moves:
            piece, (target_x, target_y) = random.choice(all_possible_moves)
            self.board.move_piece(piece, target_x, target_y)  # 直接使用目标位置作为参数
            return True
        return False
