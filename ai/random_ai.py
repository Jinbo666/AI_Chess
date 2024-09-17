# ai/random_ai.py
import random
import logging
logging.basicConfig(level=logging.INFO)
logging.info("This is an info message.")

class Random_AI:
    def __init__(self, game_state, color):
        self.game_state = game_state

        self.color = color
        logging.info('Random_AI')

    def get_all_possible_moves(self):
        """为当前AI的颜色收集所有合法移动，区分可以吃子的移动和普通移动"""
        capture_moves = []
        normal_moves = []
        for piece in self.game_state.pieces.values():
            if piece.color == self.color and piece.position is not None:
                moves = self.game_state.get_all_possible_moves(piece)
                for move in moves:
                    target_piece = self.game_state.get_piece_at(move)
                    if target_piece and target_piece.color != self.color:
                        # 这是一个可以吃子的移动
                        capture_moves.append((piece, move))
                    else:
                        # 普通的移动
                        normal_moves.append((piece, move))
        return capture_moves, normal_moves

    def make_move(self):
        """优先选择可以吃子的移动，否则随机选择一个合法移动"""
        capture_moves, normal_moves = self.get_all_possible_moves()
        if capture_moves:
            # 如果有可以吃子的移动，随机选择一个
            piece, (target_x, target_y) = random.choice(capture_moves)
            print(f"AI选择吃子：{piece.color} {piece.name} ({piece.type}) 从 {piece.position} 到 {(target_x, target_y)}")
        elif normal_moves:
            # 否则，随机选择一个普通移动
            piece, (target_x, target_y) = random.choice(normal_moves)
            print(f"AI随机移动：{piece.color} {piece.name} ({piece.type}) 从 {piece.position} 到 {(target_x, target_y)}")
        else:
            print("AI无法找到合法移动")
            return False

        move_successful = self.game_state.move_piece(piece, target_x, target_y)
        if move_successful:
            return True
        else:
            print("AI移动不合法，尝试其他移动")
            # 如果移动失败，可能是因为导致自我将军，递归尝试其他移动
            return self.make_move()


