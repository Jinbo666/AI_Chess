# game/game_state.py

import collections
import logging
from game.pieces import Piece
from game.util.const import *
from copy import deepcopy
logging.basicConfig(level=logging.INFO)
logging.info("This is an info message.")

class GameState:
    def __init__(self):
        self.board = [[None for _ in range(9)] for _ in range(10)]  # 9x10的棋盘
        self.pieces = {}  # 存储所有棋子的字典
        self.current_player = 'red'  # 当前玩家，红方先行
        self.last_captured_piece = None  # 存储最后被捕获的棋子信息
        self.is_simulation = False  # 默认不处于模拟状态
        self.setup_pieces()

    # 以下是从 Board 类中移动过来的方法

    def setup_pieces(self):
        self.pieces = {}
        # 使用 initial_pieces 来初始化棋盘上的棋子
        for piece_info in initial_pieces:
            position = piece_info['position']
            piece = Piece(
                color=piece_info['color'],
                type=piece_info['type'],
                position=position,
                name=piece_info['name']
            )
            self.add_piece(position, piece)

    def add_piece(self, position, piece):
        """在棋盘上添加一个棋子"""
        self.pieces[position] = piece
        piece.position = position  # 设置棋子的位置

    def get_piece_at(self, position):
        return self.pieces.get(position, None)

    def remove_piece(self, position):
        """从棋盘上移除位于给定位置的棋子"""
        if position in self.pieces:
            piece = self.pieces[position]
            del self.pieces[position]
            piece.position = None  # 设置棋子的位置为 None，表示已被移除

    def set_piece_position(self, piece, target_x, target_y):
        """设置棋子的新位置"""
        # 获取棋子的旧位置
        old_position = piece.position
        # 从旧位置移除棋子
        if old_position in self.pieces:
            del self.pieces[old_position]
        # 将棋子添加到新位置
        self.pieces[(target_x, target_y)] = piece
        # 更新棋子对象的位置属性
        piece.position = (target_x, target_y)

    def last_move_captured_piece(self):
        # 返回最后一次移动捕获的棋子对象
        return self.last_captured_piece

    def move_piece(self, piece, target_x, target_y):
        # 重置最后被捕获的棋子信息
        self.last_captured_piece = None

        (start_x, start_y) = piece.position

        # 检查目标位置是否为己方棋子
        target_piece = self.get_piece_at((target_x, target_y))
        if target_piece and target_piece.color == piece.color:
            return False  # 阻止移动
        if start_x == target_x and start_y == target_y:
            return False
        if self.check_for_check(piece.color):
            logging.info("检查被将军！")
        # 获取执行动作前的玩家
        previous_player = self.current_player

        # 如果目标位置有对方棋子，则吃掉它
        if target_piece and target_piece.color != piece.color:
            self.last_captured_piece = target_piece
            self.remove_piece((target_x, target_y))
        else:
            self.last_captured_piece = None

        # 移动棋子
        self.set_piece_position(piece, target_x, target_y)

        # 检查是否导致自我将军
        if self.check_for_check(piece.color):
            logging.info("移动不合法，导致自我将军")
            # # 撤销移动
            # self.set_piece_position(piece, start_x, start_y)
            # if self.last_captured_piece:
            #     self.add_piece((target_x, target_y), self.last_captured_piece)
            # return False  # 移动不合法

        # 切换当前玩家
        self.current_player = 'black' if self.current_player == 'red' else 'red'

        # 根据是否处于模拟状态，决定是否输出日志
        if not self.is_simulation:
            logging.info(f'Player {previous_player} moved {piece.type} from {piece.position} to ({target_x}, {target_y})')
            logging.info(f'Next player: {self.current_player}')
        return True  # 移动成功

    def get_all_possible_moves(self, piece):
        """获取给定棋子的所有可能移动位置"""
        possible_moves = []

        if piece.type == PAO:
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
                    current_piece = self.get_piece_at((x, y))
                    if not found_barrier and not current_piece:
                        possible_moves.append((x, y))  # 不吃子时的移动
                    elif current_piece:
                        found_barrier = True
                        continue
                    elif found_barrier and current_piece:
                        # 找到第二个棋子，停止搜索该方向
                        if current_piece.color != piece.color:
                            possible_moves.append((x, y))  # 吃子时的移动
                        break  # 无论是否吃子，都应停止搜索该方向
                    # elif found_barrier and not current_piece:
                    #     possible_moves.append((x, y))  # 吃子时的移动
        if piece.type == CHE:
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
                        if self.get_piece_at((x, y)).color != piece.color:
                            possible_moves.append((x, y))
                        break
                    else:
                        possible_moves.append((x, y))
        if piece.type == MA:
            # 马的移动可以是8个方向，每个方向由两部分组成：先一步再拐弯
            moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy

                # 确保目标位置在棋盘内
                if not (0 <= target_x < 9 and 0 <= target_y < 10):
                    continue

                # 计算“蹩马腿”的位置。对于横向移动两格的情况，蹩马腿位于横向中间；纵向移动两格的情况类似。
                if abs(dx) == 2:  # 如果是横向移动两格
                    leg_x, leg_y = x + dx // 2, y
                else:  # 如果是纵向移动两格
                    leg_x, leg_y = x, y + dy // 2

                if self.get_piece_at((leg_x, leg_y)):
                    # 如果“马腿”位置有棋子，不能移动
                    continue

                target_piece = self.get_piece_at((target_x, target_y))
                # 检查目标位置是否为空或被对方棋子占据
                if not target_piece or (target_piece and target_piece.color != piece.color):
                    possible_moves.append((target_x, target_y))

        if piece.type == SHI:
            # 士的移动可以是4个斜向方向
            moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy

                target_piece = self.get_piece_at((target_x, target_y))
                # 确保目标位置在九宫内
                if piece.color == "red":
                    if 3 <= target_x <= 5 and 7 <= target_y <= 9 and (not target_piece or target_piece.color != piece.color):
                        possible_moves.append((target_x, target_y))
                else:  # 黑方士的九宫格范围
                    if 3 <= target_x <= 5 and 0 <= target_y <= 2 and (not target_piece or target_piece.color != piece.color):
                        possible_moves.append((target_x, target_y))

        if piece.type == XIANG:
            # 象的移动可以是4个方向，每个方向“田”字形
            moves = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy

                # 确保目标位置在棋盘内
                if not (0 <= target_x < 9 and 0 <= target_y < 10):
                    continue

                # 检查目标位置是否被己方棋子占据
                target_piece = self.get_piece_at((target_x, target_y))
                if target_piece and target_piece.color == piece.color:
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

        if piece.type == JIANG:
            # 将/帅的移动可以是4个基本方向：上，下， 左，右
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy

                # 确保目标位置在九宫内
                if piece.color == "red" and not (3 <= target_x <= 5 and 7 <= target_y <= 9):
                    continue
                elif piece.color == "black" and not (3 <= target_x <= 5 and 0 <= target_y <= 2):
                    continue

                # 检查目标位置是否被己方棋子占据
                target_piece = self.get_piece_at((target_x, target_y))
                if target_piece and target_piece.color == piece.color:
                    continue

                # 模拟执行这个移动
                original_position = piece.position
                piece.position = (target_x, target_y)  # 暂时更新位置来检查将帅面对面规则
                if self.check_generals_face_to_face():
                    piece.position = original_position  # 如果会导致将帅面对面，则撤销模拟移动
                    continue  # 跳过这个移动
                piece.position = original_position  # 撤销模拟移动

                # 如果移动合法，则添加到可能的移动位置
                possible_moves.append((target_x, target_y))
        if piece.type == BING:
            x, y = piece.position
            forward = -1 if piece.color == 'red' else 1  # 红方向上移动，黑方向下移动

            # 前进
            if 0 <= y + forward < 10:
                if not self.get_piece_at((x, y + forward)):
                    possible_moves.append((x, y + forward))

            # 过河后的左右移动
            if (piece.color == 'red' and y < 5) or (piece.color == 'black' and y >= 5):
                # 左移动
                if x > 0 and not self.get_piece_at((x - 1, y)):
                    possible_moves.append((x - 1, y))
                # 右移动
                if x < 8 and not self.get_piece_at((x + 1, y)):
                    possible_moves.append((x + 1, y))

        return possible_moves

    def print_board_state(self):
        logging.info("当前棋盘状态：")
        for position, piece in self.pieces.items():
            logging.info(f"位置：{position}, 棋子：{piece.color}{piece.name}")

    def check_generals_face_to_face(self):
        # 找到“将”和“帅”的位置
        red_general_position = None
        black_general_position = None
        for position, piece in self.pieces.items():
            if piece.type == JIANG and piece.color == "red":
                red_general_position = position
            elif piece.type == JIANG and piece.color == "black":
                black_general_position = position

        # 如果任一方的将/帅不在棋盘上，则不需要进一步检查
        if not red_general_position or not black_general_position:
            return False

        # 检查是否在同一列
        if red_general_position[0] != black_general_position[0]:
            return False

        # 遍历两者之间的格子
        start_y = min(red_general_position[1], black_general_position[1]) + 1
        end_y = max(red_general_position[1], black_general_position[1])
        for y in range(start_y, end_y):
            if self.get_piece_at((red_general_position[0], y)):
                # 如果这一列中间有任何棋子，将/帅不算面对面
                return False

        # 如果这一列中间没有任何棋子，将/帅算作面对面
        return True

    def is_valid_move(self, piece, target_x, target_y):
        # 基本的移动规则验证逻辑
        if piece.type == BING:
            return self.validate_soldier_move(piece, target_x, target_y)
        # 添加其他棋子的验证逻辑

        if piece.type == CHE:
            return self.validate_chariot_move(piece, target_x, target_y)

        if piece.type == MA:
            return self.validate_knight_move(piece, target_x, target_y)

        if piece.type == PAO:
            return self.validate_cannon_move(piece, target_x, target_y)

        if piece.type in XIANG:
            return self.validate_elephant_move(piece, target_x, target_y)

        if piece.type in SHI:
            return self.validate_guard_move(piece, target_x, target_y)

        if piece.type in JIANG:
            return self.validate_general_move(piece, target_x, target_y)

        # 其他棋子的验证逻辑...
        logging.info('not valid move!')
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
        if piece.type != CHE:
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
        if piece.type != MA:
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
        if piece.type != PAO:
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
        if piece.type != XIANG:
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
        if piece.type != SHI:
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
        if piece.type != JIANG:
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
        """获取指定颜色的王（将/帅）的位置"""
        for position, piece in self.pieces.items():
            if piece.color == king_color and piece.type == "jiang":
                return position
        return None

    def check_for_check(self, king_color):
        """检查指定颜色的王（将/帅）是否处于被将军的状态"""
        king_position = self.get_king_position(king_color)
        if not king_position:
            return False  # 如果找不到王，返回False（虽然在正常游戏中不应该发生）
        opponent_color = "red" if king_color == "black" else "black"
        for piece in self.pieces.values():
            if piece.color == opponent_color:
                possible_moves = self.get_all_possible_moves(piece)
                if king_position in possible_moves:
                    print(piece, '将军！！！')
                    return True  # 如果对方有棋子能攻击到王的位置，则处于将军状态
        return False

    # ====== MCTS =======#
    def check_for_victory(self):
        # 检查双方的“将”和“帅”是否还在棋盘上
        kings = {"red": False, "black": False}
        for piece in self.pieces.values():
            if piece.type == JIANG and piece.color == "red":
                kings["red"] = True
            elif piece.type == JIANG and piece.color == "black":
                kings["black"] = True

        # 如果任一方的“将”或“帅”不在棋盘上，则游戏结束
        if not kings["red"]:
            return "black"
        elif not kings["black"]:
            return "red"
        return None

    def get_legal_actions(self):
        legal_actions = []
        for piece in self.pieces.values():
            if piece.color == self.current_player:
                moves = self.get_all_possible_moves(piece)
                for move in moves:
                    action = ((piece.position[0], piece.position[1]), move)
                    # 为动作赋予一个优先级
                    priority = self.evaluate_action(piece, move)
                    legal_actions.append((priority, action))
        # 按照优先级排序
        legal_actions.sort(reverse=True)
        # 只返回动作
        return [action for _, action in legal_actions]

    def evaluate_action(self, piece, move):
        # 简单评估动作的好坏，例如：
        target_piece = self.get_piece_at(move)
        if target_piece and target_piece.color != piece.color:
            return 10  # 吃子动作优先级高
        else:
            return 1  # 普通移动

    def get_all_legal_actions(self, player_color):
        """获取指定玩家的所有合法动作"""
        legal_actions = []
        for piece in self.pieces.values():
            if piece.color == player_color:
                moves = self.get_all_possible_moves(piece)
                for move in moves:
                    legal_actions.append(((piece.position[0], piece.position[1]), move))
        return legal_actions

    def clone(self):
        """创建当前游戏状态的深拷贝"""
        return deepcopy(self)