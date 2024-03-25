# import pygame
import collections
from .pieces import Piece
from game.util.const import *

class Board:
    def __init__(self, pygame):
        self.board = [[None for _ in range(9)] for _ in range(10)]  # 中国象棋的棋盘为9x10
        self.pieces = {}  # 存储所有棋子的列表
        self.last_captured_piece = None  # 存储最后被捕获的棋子信息
        self.setup_pieces()
        self.legal_moves = []  # 存储合法移动的列表
        self.current_player = 'red'  # 假设红方先行
        
        self.pygame = pygame
        # 设置窗口大小和标题
        self.screen = self.pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.pygame.display.set_caption('中国象棋')
        
        self.font_path = 'assets/font/微软雅黑.ttf'  # 字体文件路径，根据实际情况调整

        


    def setup_pieces(self):
        self.pieces = {}
        # 使用initial_pieces来初始化棋盘上的棋子
        for piece_info in initial_pieces:
            position = piece_info['position']
            piece = Piece(piece_info['color'], piece_info['type'], position, piece_info['type'])
            self.add_piece(position, piece)


    def add_piece(self, position, piece):
        """在棋盘上添加一个棋子"""
        self.pieces[position] = piece
        # piece.position = position  # 假设Piece对象有一个属性来存储它的位置


    def get_piece_at(self, position):
       return self.pieces.get(position, None)
    
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

    def last_move_captured_piece(self):
        # 返回最后一次移动捕获的棋子对象
        return self.last_captured_piece

    def move_piece(self, piece, target_x, target_y):
        # 假设在每次移动前，重置最后被捕获的棋子信息
        self.last_captured_piece = None

        # 假设self.pieces以某种方式存储了棋子的位置和对象
        (start_x, start_y) = piece.position
        moving_piece = self.pieces.get((start_x, start_y))
        color = '黑'
        if piece.color=='red':
            color = '红'
        print("episode:", CONST.num_episodes, color+piece.name, start_x, start_y, target_x, target_y)
        # 检查目标位置是否为己方棋子
        target_piece = self.get_piece_at((target_x, target_y))
        if target_piece and target_piece.color == piece.color:
            print("不能吃掉己方棋子。")
            return False  # 阻止移动
        if start_x == target_x and start_y == target_y:
            print("不能吃掉自己。")
            return False

        # 如果目标位置有对方棋子，则吃掉它, 则视为被捕获
        if target_piece and target_piece.color != piece.color:
            self.last_captured_piece = target_piece
            print(f"episode: {CONST.num_episodes}, 吃掉对方的{target_piece.name}！！！")

            self.remove_piece(target_piece)  # 假设有一个方法来处理棋子的移除


            # 打印对方和己方 给剩下什么棋子
            color2pieces = collections.defaultdict(list)
            for _, piece in self.pieces.items():
                color2pieces[piece.color].append(piece.name)
            for color in color2pieces:
                c = '黑'
                if color == 'red':
                    c = '红'
                print(c, ':', len(color2pieces[color]),  color2pieces[color])
        else:
            self.last_captured_piece = None

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
                        if self.get_piece_at((x, y)).color != piece.color:
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

        if piece.name in ["士", "仕"]:
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

        if piece.name in ["将", "帅"]:
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
        
        if piece.name in ["将", "帅"]:
            # 将/帅的移动可以是4个基本方向：上，下，左，右
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in moves:
                x, y = piece.position
                target_x = x + dx
                target_y = y + dy
                
                # 确保目标位置在九宫内
                if piece.color == "red":
                    if not (3 <= target_x <= 5 and 7 <= target_y <= 9):
                        continue
                else:  # 黑方帅的九宫格范围
                    if not (3 <= target_x <= 5 and 0 <= target_y <= 2):
                        continue
                        
                target_piece = self.get_piece_at((target_x, target_y))
                # 检查目标位置是否被己方棋子占据
                if target_piece and target_piece.color == piece.color:
                    continue
                        
                # 添加到可能的移动位置
                possible_moves.append((target_x, target_y))

        return possible_moves
    

    def check_generals_face_to_face(self):
        # 找到“将”和“帅”的位置
        red_general_position = None
        black_general_position = None
        for position, piece in self.pieces.items():
            if piece.name in ["将", "帅"] and piece.color == "red":
                red_general_position = position
            elif piece.name in ["将", "帅"] and piece.color == "black":
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


    def check_for_check(self, king_color):
        """检查王（将/帅）是否处于将军状态"""
        king_position = self.get_king_position(king_color)
        if not king_position:
            return False  # 如果找不到王，返回False（虽然在正常游戏中不应该发生）
        opponent_color = "red" if king_color == "black" else "black"
        for _, piece in self.pieces.items():
            if piece.color == opponent_color:
                possible_moves = self.get_all_possible_moves(piece)
                # print(piece.name, piece.color, possible_moves)
                if king_position in possible_moves:
                    return True  # 如果对方有棋子能攻击到王的位置，则处于将军状态
        return False
    
    def check_for_victory(self):
        # 检查双方的“将”和“帅”是否还在棋盘上
        kings = {"red": False, "black": False}
        for piece in self.pieces.values():
            if (piece.name in ["将", "帅"]) and piece.color == "red":
                kings["red"] = True
            elif (piece.name in ["将", "帅"]) and piece.color == "black":
                kings["black"] = True

        # 如果任一方的“将”或“帅”不在棋盘上，则游戏结束
        if not kings["red"]:
            return "black"
        elif not kings["black"]:
            return "red"
        return None

    def draw_board(self):
        """绘制棋盘背景和线条"""
        self.screen.fill(BG_COLOR)

        # 绘制棋盘的线条等

        # 定义棋盘的起始点和终点坐标
        start_x, start_y = BOARD_START_X, BOARD_START_Y
        end_x, end_y = WINDOW_WIDTH - BOARD_START_X, WINDOW_HEIGHT - BOARD_START_Y
        cell_width = (end_x - start_x) / 8
        cell_height = (end_y - start_y) / 9

        # 绘制棋盘的线条
        for i in range(10):  # 横线
            self.pygame.draw.line(self.screen, BLACK, (start_x, start_y + i*cell_height), (end_x, start_y + i*cell_height), 2)
        for i in range(9):  # 竖线
            if i == 0 or i == 8:  # 第一条和最后一条竖线贯穿整个棋盘
                self.pygame.draw.line(self.screen, BLACK, (start_x + i*cell_width, start_y), (start_x + i*cell_width, end_y), 2)
            else:  # 其他竖线只在楚河汉界两侧绘制
                self.pygame.draw.line(self.screen, BLACK, (start_x + i*cell_width, start_y), (start_x + i*cell_width, start_y + 4*cell_height), 2)
                self.pygame.draw.line(self.screen, BLACK, (start_x + i*cell_width, start_y + 5*cell_height), (start_x + i*cell_width, end_y), 2)

        # 绘制九宫格的斜线
        self.pygame.draw.line(self.screen, BLACK, (start_x + 3*cell_width, start_y), (start_x + 5*cell_width, start_y + 2*cell_height), 2)
        self.pygame.draw.line(self.screen, BLACK, (start_x + 3*cell_width, start_y + 2*cell_height), (start_x + 5*cell_width, start_y), 2)
        self.pygame.draw.line(self.screen, BLACK, (start_x + 3*cell_width, end_y - 2*cell_height), (start_x + 5*cell_width, end_y), 2)
        self.pygame.draw.line(self.screen, BLACK, (start_x + 3*cell_width, end_y), (start_x + 5*cell_width, end_y - 2*cell_height), 2)


        # 初始化字体
        font_chuhe_hanjie = self.pygame.font.Font(self.font_path, FONT_SIZE_CHUHE_HANJIE)  # 加载字体文件，40是字体大小

        # 渲染‘楚河’和‘汉界’文本
        text_chuhe = font_chuhe_hanjie.render('楚河', True, BLACK)
        text_hanjie = font_chuhe_hanjie.render('汉界', True, BLACK)

        # 计算文本位置
        text_chuhe_pos = ((WINDOW_WIDTH - text_chuhe.get_width()) / 2 - 80, (WINDOW_HEIGHT / 2 - text_chuhe.get_height() / 2))
        text_hanjie_pos = ((WINDOW_WIDTH - text_hanjie.get_width()) / 2 + 80, (WINDOW_HEIGHT / 2 - text_hanjie.get_height() / 2))

        # 绘制文本
        self.screen.blit(text_chuhe, text_chuhe_pos)
        self.screen.blit(text_hanjie, text_hanjie_pos)


    def draw_pieces(self, pieces):
        font_piece = self.pygame.font.Font(self.font_path, FONT_SIZE_CHESS)  # 使用指定的中文字体和字体大小
        
        """绘制棋子，适应新的窗口大小"""
        for position in pieces:
            piece = pieces[position]
            # print(piece)
            x, y = position #piece.position
            # 假设每个格子大小为 80 像素，调整棋子的绘制位置
            # 这里的 40 是新格子尺寸的一半，用于计算棋子的中心位置
            
            center_x = (x * CELL_SIZE) + BOARD_START_X# + CELL_SIZE // 2
            center_y = (y * CELL_SIZE) + BOARD_START_Y# + CELL_SIZE // 2

            
            # 绘制棋子背景圆形
            
            if piece.color == 'red':
                self.pygame.draw.circle(self.screen, (255, 0, 0), (center_x, center_y), CELL_SIZE // 2 - 5)  # 红色棋子
            else:
                self.pygame.draw.circle(self.screen, (0, 0, 0), (center_x, center_y), CELL_SIZE // 2 - 5)  # 黑色棋子

            # 绘制棋子上的文字
            text = font_piece.render(piece.chinese_name, True, (255, 255, 255))  # 假设文字颜色为白色
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)


    def draw_selection(self, position):
        x, y = position
        x -= 0.5
        y -= 0.5
        mark_length = 10  # 线段长度
        # 定义四组线段的坐标，每组对应一个角落的两条线
        lines = [
            # 左上角
            ((x * CELL_SIZE + BOARD_START_X, y * CELL_SIZE + BOARD_START_Y + mark_length),
            (x * CELL_SIZE + BOARD_START_X, y * CELL_SIZE + BOARD_START_Y),
            (x * CELL_SIZE + BOARD_START_X + mark_length, y * CELL_SIZE + BOARD_START_Y)),
            
            # 右上角
            ((x * CELL_SIZE + BOARD_START_X + CELL_SIZE - mark_length, y * CELL_SIZE + BOARD_START_Y),
            (x * CELL_SIZE + BOARD_START_X + CELL_SIZE, y * CELL_SIZE + BOARD_START_Y),
            (x * CELL_SIZE + BOARD_START_X + CELL_SIZE, y * CELL_SIZE + BOARD_START_Y + mark_length)),
            
            # 左下角
            ((x * CELL_SIZE + BOARD_START_X, y * CELL_SIZE + BOARD_START_Y + CELL_SIZE - mark_length),
            (x * CELL_SIZE + BOARD_START_X, y * CELL_SIZE + BOARD_START_Y + CELL_SIZE),
            (x * CELL_SIZE + BOARD_START_X + mark_length, y * CELL_SIZE + BOARD_START_Y + CELL_SIZE)),
            
            # 右下角
            ((x * CELL_SIZE + BOARD_START_X + CELL_SIZE - mark_length, y * CELL_SIZE + BOARD_START_Y + CELL_SIZE),
            (x * CELL_SIZE + BOARD_START_X + CELL_SIZE, y * CELL_SIZE + BOARD_START_Y + CELL_SIZE),
            (x * CELL_SIZE + BOARD_START_X + CELL_SIZE, y * CELL_SIZE + BOARD_START_Y + CELL_SIZE - mark_length)),
        ]
        
        for line in lines:
            self.pygame.draw.lines(self.screen, (255, 0, 0), False, line[:2], 2)
            self.pygame.draw.lines(self.screen, (255, 0, 0), False, line[1:], 2)


    def show_victory_message(self, winner):
        message = f"{winner}方获胜！"


        font_gameover = self.pygame.font.Font(self.font_path, FONT_SIZE_CHUHE_HANJIE)  # 加载字体文件，40是字体大小

        text_surface = font_gameover.render(message, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(400, 300))  # 假设屏幕尺寸为800x600
        self.screen.blit(text_surface, text_rect)
        self.pygame.display.flip()
        self.pygame.time.wait(5000)  # 显示5秒胜利信息

    def render_human(self):
        self.draw_board()
        self.draw_pieces(self.pieces)
        self.pygame.display.flip()


    def update_legal_moves(self):
        # 清空当前合法移动列表
        self.legal_moves.clear()

        # 假设有一个方法来计算每个棋子的合法移动，并将它们添加到列表中
        for piece in self.pieces.values():
            if piece.color == self.current_player:  # 这里检查棋子颜色是否匹配当前行动方
                piece_legal_moves = self.get_all_possible_moves(piece)
                (start_x, start_y) = piece.position
                for move in piece_legal_moves:
                    (end_x, end_y) = move
                    if (start_x, start_y, end_x, end_y) not in self.legal_moves:
                        self.legal_moves.append((start_x, start_y, end_x, end_y))


    def decode_action(self, action_index):
        board_width = 9
        board_height = 10
        total_positions = board_width * board_height

        start_pos = action_index // total_positions
        end_pos = action_index % total_positions

        start_x = start_pos % board_width
        start_y = start_pos // board_width
        end_x = end_pos % board_width
        end_y = end_pos // board_height

        return start_x, start_y, end_x, end_y


    
    
    def execute_action(self, action):
        # 解码动作以获取起始位置和目标位置
        # 这里的解码逻辑取决于你是如何编码你的动作的
        print('execute_action:', action)
        start_x, start_y, end_x, end_y = self.decode_action(action)

        print("decode_action:", start_x, start_y, end_x, end_y)
        # 找到起始位置的棋子
        piece = self.get_piece_at((start_x, start_y))
        if piece:
            # 移动棋子到目标位置，并处理任何可能的捕获
            self.move_piece(piece, end_x, end_y)
        else:
            print("无法执行动作：起始位置没有棋子。")