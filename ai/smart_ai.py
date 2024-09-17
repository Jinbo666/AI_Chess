import copy
import random
import logging
logging.basicConfig(level=logging.INFO)
logging.info("This is an info message.")

PIECE_VALUES = {
    'jiang': 1000,
    'che': 9,
    'ma': 4.5,
    'pao': 4.5,
    'xiang': 2,
    'shi': 2,
    'bing': 1
}

class Smart_AI:
    def __init__(self, board, color):
        self.board = board
        self.color = color
        logging.info('Smart_AI')

    def evaluate_board(self):
        """评估当前棋盘局面，返回AI的得分减去对方的得分"""
        score = 0
        for piece in self.board.pieces.values():
            value = PIECE_VALUES.get(piece.type, 0)
            if piece.color == self.color:
                score += value
            else:
                score -= value
        return score

    import copy

    def make_move(self):
        """在所有合法移动中，选择使自己得分最高的移动，考虑对方的反应"""
        all_moves = []
        for piece in list(self.board.pieces.values()):
            if piece.color == self.color and piece.position is not None:
                moves = self.board.get_all_possible_moves(piece)
                for move in moves:
                    all_moves.append((piece, move))

        best_score = float('-inf')
        best_moves = []

        for piece, (target_x, target_y) in all_moves:
            # 模拟AI的移动
            captured_piece = self.board.get_piece_at((target_x, target_y))
            original_position = piece.position
            self.board.set_piece_position(piece, target_x, target_y)
            if captured_piece:
                self.board.remove_piece((target_x, target_y))

            # 模拟对方的最佳反应
            opponent_best_score = float('inf')
            # 在这里创建对方棋子的列表副本
            opponent_pieces = [p for p in self.board.pieces.values() if
                               p.color != self.color and p.position is not None]
            for opp_piece in opponent_pieces:
                opp_moves = self.board.get_all_possible_moves(opp_piece)
                for opp_move in opp_moves:
                    opp_captured_piece = self.board.get_piece_at(opp_move)
                    opp_original_position = opp_piece.position
                    self.board.set_piece_position(opp_piece, opp_move[0], opp_move[1])
                    if opp_captured_piece:
                        self.board.remove_piece(opp_move)

                    # 评估对方移动后的局面
                    score = self.evaluate_board()

                    # 撤销对方的移动
                    self.board.set_piece_position(opp_piece, opp_original_position[0], opp_original_position[1])
                    if opp_captured_piece:
                        self.board.add_piece(opp_move, opp_captured_piece)

                    if score < opponent_best_score:
                        opponent_best_score = score

            # 撤销AI的移动
            self.board.set_piece_position(piece, original_position[0], original_position[1])
            if captured_piece:
                self.board.add_piece((target_x, target_y), captured_piece)

            # 评估此移动的最终得分
            final_score = opponent_best_score

            if final_score > best_score:
                best_score = final_score
                best_moves = [(piece, (target_x, target_y))]
            elif final_score == best_score:
                best_moves.append((piece, (target_x, target_y)))

        if best_moves:
            # 在最佳移动中随机选择一个
            piece, (target_x, target_y) = random.choice(best_moves)
            print(
                f"AI选择最佳移动：{piece.color} {piece.name} ({piece.type}) 从 {piece.position} 到 {(target_x, target_y)}")
            move_successful = self.board.move_piece(piece, target_x, target_y)
            if move_successful:
                return True
            else:
                print("AI移动不合法，尝试其他移动")
                return self.make_move()
        else:
            print("AI无法找到合法移动")
            return False



