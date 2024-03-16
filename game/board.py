from .pieces import Piece
from game.util.const import *

class Board:
    def __init__(self):
        self.board = [[None for _ in range(9)] for _ in range(10)]  # 中国象棋的棋盘为9x10
        self.pieces = {}  # 存储所有棋子的列表
        self.setup_pieces()

    def setup_pieces(self):
        # 用于初始化棋盘上的棋子位置和对象
        self.add_piece((0, 0), Piece('black', '车', (0, 0), '车'))
        self.add_piece((1, 0), Piece('black', '马', (1, 0), '马'))
        self.add_piece((2, 0), Piece('black', '相', (2, 0), '相'))
        self.add_piece((3, 0), Piece('black', '仕', (3, 0), '仕'))
        self.add_piece((4, 0), Piece('black', '帅', (4, 0), '帅'))
        self.add_piece((5, 0), Piece('black', '仕', (5, 0), '仕'))
        self.add_piece((6, 0), Piece('black', '相', (6, 0), '相'))
        self.add_piece((7, 0), Piece('black', '马', (7, 0), '马'))
        self.add_piece((8, 0), Piece('black', '车', (8, 0), '车'))
        self.add_piece((1, 2), Piece('black', '炮', (1, 2), '炮'))
        self.add_piece((7, 2), Piece('black', '炮', (7, 2), '炮'))
        self.add_piece((0, 3), Piece('black', '兵', (0, 3), '兵'))
        self.add_piece((2, 3), Piece('black', '兵', (2, 3), '兵'))
        self.add_piece((4, 3), Piece('black', '兵', (4, 3), '兵'))
        self.add_piece((6, 3), Piece('black', '兵', (6, 3), '兵'))
        self.add_piece((8, 3), Piece('black', '兵', (8, 3), '兵'))
        # 添加其他黑方棋子的初始化...
        self.add_piece((0, 9), Piece('red', '车', (0, 9), '车'))
        self.add_piece((1, 9), Piece('red', '马', (1, 9), '马'))
        self.add_piece((2, 9), Piece('red', '象', (2, 9), '象'))
        self.add_piece((3, 9), Piece('red', '士', (3, 9), '士'))
        self.add_piece((4, 9), Piece('red', '帅', (4, 9), '帅'))
        self.add_piece((5, 9), Piece('red', '士', (5, 9), '士'))
        self.add_piece((6, 9), Piece('red', '象', (6, 9), '象'))
        self.add_piece((7, 9), Piece('red', '马', (7, 9), '马'))
        self.add_piece((8, 9), Piece('red', '车', (8, 9), '车'))
        self.add_piece((1, 7), Piece('red', '炮', (1, 7), '炮'))
        self.add_piece((7, 7), Piece('red', '炮', (7, 7), '炮'))
        self.add_piece((0, 6), Piece('red', '兵', (0, 6), '兵'))
        self.add_piece((2, 6), Piece('red', '兵', (2, 6), '兵'))
        self.add_piece((4, 6), Piece('red', '兵', (4, 6), '兵'))
        self.add_piece((6, 6), Piece('red', '兵', (6, 6), '兵'))
        self.add_piece((8, 6), Piece('red', '兵', (8, 6), '兵'))


        # for pos, piece in positions:
        #     self.add_piece(pos, piece)

    def add_piece(self, position, piece):
        """在棋盘上添加一个棋子"""
        self.pieces[position] = piece
        # piece.position = position  # 假设Piece对象有一个属性来存储它的位置


    def get_piece_at(self, position):
        for pos in self.pieces:
            if pos == position:
                return self.pieces[pos]
        return None
    def remove_piece(self, position):
        """从棋盘上移除位于给定位置的棋子"""
        if position in self.pieces:
            del self.pieces[position]

    def set_piece_position(self, piece, target_x, target_y):
        """设置棋子的新位置"""
        # 先移除棋子当前的位置
        for pos, current_piece in self.pieces.items():
            if current_piece == piece:
                del self.pieces[pos]
                break
        # 在新位置放置棋子
        self.pieces[(target_x, target_y)] = piece
        # 更新棋子对象的位置属性（如果有）
        piece.position = (target_x, target_y)

    def move_piece(self, piece, target_x, target_y):
        # 检查目标位置是否为己方棋子
        target_piece = self.get_piece_at((target_x, target_y))
        if target_piece and target_piece.color == piece.color:
            print("不能吃掉己方棋子。")
            return False  # 阻止移动

        # 如果目标位置有对方棋子，则吃掉它
        if target_piece and target_piece.color != piece.color:
            print(f"吃掉对方的{target_piece.name}")
            self.remove_piece(target_piece)  # 假设有一个方法来处理棋子的移除

        # 更新棋子位置（假设有一个方法来设置棋子的新位置）
        self.set_piece_position(piece, target_x, target_y)
        
        # 确保移动的棋子不会消失，更新棋盘状态
        # 这可能涉及到在内部数据结构中更新棋子的位置
        
        return True  # 移动成功

    def get_all_possible_moves(self, piece):
        """获取给定棋子的所有可能移动位置"""
        possible_moves = []

        if piece.name == "炮":
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # 四个基本方向：右，左，下，上
            for dx, dy in directions:
                x, y = piece.position
                # 首先找到第一个棋子（炮架）
                found_barrier = False
                while True:
                    x += dx
                    y += dy
                    if not (0 <= x < 9 and 0 <= y < 10):  # 确保在棋盘范围内
                        break
                    if not found_barrier and not self.get_piece_at((x, y)):
                        possible_moves.append((x, y))  # 不吃子时的移动
                    elif self.get_piece_at((x, y)):
                        found_barrier = True
                        continue
                    elif found_barrier and self.get_piece_at((x, y)):
                        break  # 找到第二个棋子，停止搜索该方向
                    elif found_barrier and not self.get_piece_at((x, y)):
                        possible_moves.append((x, y))  # 吃子时的移动
        if piece.name == "车":
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # 四个基本方向：右，左，下，上
            for dx, dy in directions:
                x, y = piece.position
                while True:
                    x += dx
                    y += dy
                    if not (0 <= x < 9 and 0 <= y < 10):  # 确保在棋盘范围内
                        break
                    if self.get_piece_at((x, y)):
                        # “车”在遇到其他棋子时停止，可以吃掉对方的棋子
                        possible_moves.append((x, y))
                        break
                    else:
                        possible_moves.append((x, y))
        if piece.name == "马":
            # 马的移动可以是8个方向，每个方向由两部分组成：先一步再拐弯
            moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy
                
                # 确保目标位置在棋盘内
                if not (0 <= target_x < 9 and 0 <= target_y < 10):
                    continue
                
                # 检查“蹩马腿”位置是否有棋子阻挡
                leg_x = x + dx // 2 if dx % 2 == 0 else x
                leg_y = y + dy // 2 if dy % 2 == 0 else y
                
                if self.get_piece_at((leg_x, leg_y)):
                    # 如果“马腿”位置有棋子，不能移动
                    continue

                # 添加到可能的移动位置
                possible_moves.append((target_x, target_y))

        if piece.name in ["士", "仕"]:
            # 士的移动可以是4个斜向方向
            moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy
                
                # 确保目标位置在九宫内
                if piece.color == "red":
                    if 3 <= target_x <= 5 and 7 <= target_y <= 9:
                        possible_moves.append((target_x, target_y))
                else:  # 黑方士的九宫格范围
                    if 3 <= target_x <= 5 and 0 <= target_y <= 2:
                        possible_moves.append((target_x, target_y))

        if piece.name in ["象", "相"]:
            # 象的移动可以是4个方向，每个方向“田”字形
            moves = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy
                
                # 确保目标位置在棋盘内
                if not (0 <= target_x < 9 and 0 <= target_y < 10):
                    continue
                
                # 检查“象”是否过河
                if piece.color == "red" and target_y < 5:  # 红象不能移到y坐标小于5的区域
                    continue
                elif piece.color == "black" and target_y >= 5:  # 黑象不能移到y坐标大于或等于5的区域
                    continue
                
                # 检查“象眼”是否被阻挡
                eye_x = x + dx // 2
                eye_y = y + dy // 2
                if self.get_piece_at((eye_x, eye_y)):
                    # 如果“象眼”被阻挡，该移动不是可能的
                    continue
                
                # 如果“象眼”没有被阻挡，且不过河，该移动是可能的
                possible_moves.append((target_x, target_y))



        if piece.name in ["将", "帅"]:
            # 将/帅的移动可以是4个基本方向：上，下，左，右
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy
                
                # 确保目标位置在九宫内
                if piece.color == "red":
                    if 3 <= target_x <= 5 and 7 <= target_y <= 9:
                        possible_moves.append((target_x, target_y))
                else:  # 黑方帅的九宫格范围
                    if 3 <= target_x <= 5 and 0 <= target_y <= 2:
                        possible_moves.append((target_x, target_y))
        if piece.name in ["兵", "卒"]:
            x, y = piece.position
            moves = []

            # 根据兵/卒的颜色和位置判断可能的移动
            if piece.color == "red":
                # 红方兵未过河前只能向上移动
                moves.append((0, -1)) if y > 4 else moves.extend([(0, -1), (1, 0), (-1, 0)])
            else:  # 黑方卒未过河前只能向下移动
                moves.append((0, 1)) if y < 5 else moves.extend([(0, 1), (1, 0), (-1, 0)])

            # 检查每个可能的移动是否在棋盘范围内
            for dx, dy in moves:
                target_x = x + dx
                target_y = y + dy

                if 0 <= target_x < 9 and 0 <= target_y < 10:
                    possible_moves.append((target_x, target_y))

        return possible_moves
    


    def is_valid_move(self, piece, target_x, target_y):
        # 基本的移动规则验证逻辑
        if piece.name == "兵" or piece.name == "卒":
            return self.validate_soldier_move(piece, target_x, target_y)
        # 添加其他棋子的验证逻辑
        
        if piece.name == "车":
            return self.validate_chariot_move(piece, target_x, target_y)

        if piece.name == "马":
            return self.validate_knight_move(piece, target_x, target_y)


        if piece.name == "炮":
            return self.validate_cannon_move(piece, target_x, target_y)

        if piece.name in ["象", "相"]:
            return self.validate_elephant_move(piece, target_x, target_y)

        if piece.name in ["士", "仕"]:
            return self.validate_guard_move(piece, target_x, target_y)

        if piece.name in ["将", "帅"]:
            return self.validate_general_move(piece, target_x, target_y)

        # 其他棋子的验证逻辑...
        print('not valid move!')
        return False

    def validate_soldier_move(self, piece, target_x, target_y):
        # 兵（卒）的移动规则验证
        dx = target_x - piece.position[0]
        dy = target_y - piece.position[1]

        # 判断是否过河（以红方为例，假设红方在下方）
        crossed_river = piece.position[1] < 5 if piece.color == "red" else piece.position[1] >= 5

        if crossed_river:
            # 过河后，可以前进、左移、右移一格，但不允许后退或斜走
            # 对于红方兵，dy == -1 表示前进；对于黑方卒，dy == 1 表示前进
            if piece.color == "red":
                return (dx == 0 and dy == -1) or (abs(dx) == 1 and dy == 0)
            else:  # 黑方卒
                return (dx == 0 and dy == 1) or (abs(dx) == 1 and dy == 0)
        else:
            # 过河前，只能前进一格
            if piece.color == "red":
                # 红方兵只能向上（北）移动一格
                return dx == 0 and dy == -1
            else:
                # 黑方卒只能向下（南）移动一格
                return dx == 0 and dy == 1

        return False


    
    def is_path_clear(self, start_x, start_y, end_x, end_y):
        """检查从(start_x, start_y)到(end_x, end_y)的路径上是否有其他棋子阻挡。"""
        dx = end_x - start_x
        dy = end_y - start_y
        step_x = dx // abs(dx) if dx != 0 else 0
        step_y = dy // abs(dy) if dy != 0 else 0

        next_x = start_x + step_x
        next_y = start_y + step_y

        while (next_x, next_y) != (end_x, end_y):
            if self.get_piece_at((next_x, next_y)):
                return False
            next_x += step_x
            next_y += step_y

        return True
    def validate_chariot_move(self, piece, target_x, target_y):
        """验证'车'的移动规则。"""
        if piece.name != "车":
            return False  # 仅处理'车'

        dx = target_x - piece.position[0]
        dy = target_y - piece.position[1]

        # '车'只能在一条直线上移动
        if dx != 0 and dy != 0:
            return False  # '车'不能同时在x和y方向上移动

        # 检查移动路径上是否有其他棋子阻挡
        return self.is_path_clear(piece.position[0], piece.position[1], target_x, target_y)

    def validate_knight_move(self, piece, target_x, target_y):
        """验证'马'的移动规则。"""
        if piece.name != "马":
            return False  # 仅处理'马'

        dx = abs(target_x - piece.position[0])
        dy = abs(target_y - piece.position[1])

        # '马'移动符合“日”字形
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False

        # 检查是否有“蹩马腿”
        if dx == 2:  # 如果横向移动两格，检查中间的格子是否有棋子
            blocking_pos = (piece.position[0] + (target_x - piece.position[0]) // 2, piece.position[1])
        else:  # 如果纵向移动两格，检查中间的格子是否有棋子
            blocking_pos = (piece.position[0], piece.position[1] + (target_y - piece.position[1]) // 2)

        if self.get_piece_at(blocking_pos):
            return False  # 有“蹩马腿”，移动不合法

        return True

    def count_pieces_on_path(self, start_x, start_y, end_x, end_y):
        """计算从起点到终点路径上的棋子数量，不包括起点和终点。"""
        dx = end_x - start_x
        dy = end_y - start_y
        step_x = dx // abs(dx) if dx != 0 else 0
        step_y = dy // abs(dy) if dy != 0 else 0

        next_x = start_x + step_x
        next_y = start_y + step_y
        count = 0

        while (next_x, next_y) != (end_x, end_y):
            if self.get_piece_at((next_x, next_y)):
                count += 1
            next_x += step_x
            next_y += step_y

        return count
    def validate_cannon_move(self, piece, target_x, target_y):
        """验证'炮'的移动规则。"""
        if piece.name != "炮":
            return False

        dx = target_x - piece.position[0]
        dy = target_y - piece.position[1]

        # '炮'必须沿直线移动
        if dx != 0 and dy != 0:
            return False

        target_piece = self.get_piece_at((target_x, target_y))
        pieces_on_path = self.count_pieces_on_path(piece.position[0], piece.position[1], target_x, target_y)

        # 如果目标位置没有棋子，路径上不能有棋子（移动）
        if not target_piece and pieces_on_path == 0:
            return True
        # 如果目标位置有棋子，路径上必须正好有一个棋子（吃子）
        elif target_piece and pieces_on_path == 1 and target_piece.color != piece.color:
            return True

        return False

    def validate_elephant_move(self, piece, target_x, target_y):

        """验证'象'或'相'的移动规则。"""
        if piece.name not in ["象", "相"]:
            return False  # 仅处理'象'和'相'

        dx = abs(target_x - piece.position[0])
        dy = abs(target_y - piece.position[1])

        # '象'或'相'必须斜向移动两个格子，形成“田”字
        if dx != 2 or dy != 2:
            return False

        # 检查“象眼”是否被阻挡
        eye_x = piece.position[0] + (target_x - piece.position[0]) // 2
        eye_y = piece.position[1] + (target_y - piece.position[1]) // 2

        if self.get_piece_at((eye_x, eye_y)):
            return False  # “象眼”被阻挡，移动不合法

        # 红方“象”不应过河到y坐标小于5的区域
        # 黑方“象”不应过河到y坐标大于4的区域
        if (piece.color == "red" and target_y >= 5) or (piece.color == "black" and target_y <= 4):
            return True

        return False
    
    def validate_guard_move(self, piece, target_x, target_y):
        """验证'士'的移动规则。"""
        if piece.name not in ["士", "仕"]:
            return False  # 仅处理'士'和'仕'

        dx = abs(target_x - piece.position[0])
        dy = abs(target_y - piece.position[1])

        # '士'或'仕'必须斜向移动一个格子
        if dx != 1 or dy != 1:
            return False

        # 检查目标位置是否在九宫格内
        if piece.color == "red":
            if not (3 <= target_x <= 5 and 7 <= target_y <= 9):
                return False
        else:  # piece.color == "black"
            if not (3 <= target_x <= 5 and 0 <= target_y <= 2):
                return False

        return True
    
    def validate_general_move(self, piece, target_x, target_y):
        """验证'将/帅'的移动规则。"""
        if piece.name not in ["将", "帅"]:
            return False  # 仅处理'将'和'帅'

        dx = abs(target_x - piece.position[0])
        dy = abs(target_y - piece.position[1])

        # '将/帅'必须在九宫格内上下左右移动一格
        if dx + dy != 1:
            return False

        # 检查目标位置是否在九宫格内
        if piece.color == "red":
            if not (3 <= target_x <= 5 and 7 <= target_y <= 9):
                return False
        else:  # piece.color == "black"
            if not (3 <= target_x <= 5 and 0 <= target_y <= 2):
                return False

        return True
    
    def get_king_position(self, king_color):
        """获取王（将/帅）的位置"""
        for position, piece in self.pieces.items():
            if piece.color == king_color and piece.name in ["将", "帅"]:
                return position
        return None

    # def get_all_possible_moves(self, piece):
    #     """获取给定棋子的所有可能移动位置"""
    #     possible_moves = []

    #     if piece.name in ["兵", "卒"]:
    #         x, y = piece.position
    #         moves = []

    #         # 判断是否过河
    #         crossed_river = y > 4 if piece.color == "red" else y < 5

    #         # 未过河之前，只能前进
    #         if not crossed_river:
    #             step = -1 if piece.color == "red" else 1
    #             new_y = y + step
    #             if 0 <= new_y < 10:  # 确保不超出棋盘边界
    #                 possible_moves.append((x, new_y))
            
    #         # 过河后，可以左右移动
    #         else:
    #             steps = [(-1, 0), (1, 0)]  # 左右移动
    #             if piece.color == "red":
    #                 steps.append((0, -1))  # 红方向上移动
    #             else:
    #                 steps.append((0, 1))  # 黑方向下移动

    #             for dx, dy in steps:
    #                 new_x, new_y = x + dx, y + dy
    #                 if 0 <= new_x < 9 and 0 <= new_y < 10:  # 确保移动后仍在棋盘内
    #                     possible_moves.append((new_x, new_y))

    #     # 其他棋子的逻辑...
    #     # print('posible_moves:', possible_moves)
    #     return possible_moves

    def is_in_check(self, king_color):
        """检查王（将/帅）是否处于将军状态"""
        king_position = self.get_king_position(king_color)
        if not king_position:
            return False  # 如果找不到王，返回False（虽然在正常游戏中不应该发生）
        opponent_color = "red" if king_color == "black" else "black"
        for _, piece in self.pieces.items():
            if piece.color == opponent_color:
                possible_moves = self.get_all_possible_moves(piece)
                if king_position in possible_moves:
                    return True  # 如果对方有棋子能攻击到王的位置，则处于将军状态
        return False