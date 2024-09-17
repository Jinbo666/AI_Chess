# const.py

# 窗口配置
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 800

# 棋盘配置
BOARD_START_X = 80
BOARD_START_Y = 80
CELL_SIZE = 70
CHESS_HALF_DIAMETER = 30
BOARD_WIDTH = CELL_SIZE * 8
BOARD_HEIGHT = CELL_SIZE * 9

# 颜色配置
LINE_COLOR = (0, 0, 0)
BG_COLOR = (255, 206, 158)
TEXT_COLOR = (0, 0, 0)
BLACK = (0, 0, 0)  # 黑色
WHITE = (255, 255, 255)  # 白色
RED = (255, 0, 0)

# 字体配置
FONT_SIZE_CHUHE_HANJIE = 40
FONT_SIZE_CHESS = 30

# 定义棋子类型常量
CHE = 'che'       # 车
MA = 'ma'         # 马
XIANG = 'xiang'   # 相（黑方）/ 象（红方）
SHI = 'shi'       # 士 / 仕
JIANG = 'jiang'   # 将（黑方）
# SHUAI = 'shuai'   # 帅（红方）
PAO = 'pao'       # 炮
BING = 'bing'     # 兵 / 卒


# 定义所有棋子的初始位置和属性
initial_pieces = [
    {'color': 'black', 'type': CHE, 'name': '车', 'position': (0, 0)},
    {'color': 'black', 'type': MA, 'name': '马', 'position': (1, 0)},
    {'color': 'black', 'type': XIANG, 'name': '相', 'position': (2, 0)},
    {'color': 'black', 'type': SHI, 'name': '仕', 'position': (3, 0)},
    {'color': 'black', 'type': JIANG, 'name': '将', 'position': (4, 0)},
    {'color': 'black', 'type': SHI, 'name': '仕', 'position': (5, 0)},
    {'color': 'black', 'type': XIANG, 'name': '相', 'position': (6, 0)},
    {'color': 'black', 'type': MA, 'name': '马', 'position': (7, 0)},
    {'color': 'black', 'type': CHE, 'name': '车', 'position': (8, 0)},
    {'color': 'black', 'type': PAO, 'name': '炮', 'position': (1, 2)},
    {'color': 'black', 'type': PAO, 'name': '炮', 'position': (7, 2)},
    {'color': 'black', 'type': BING, 'name': '卒', 'position': (0, 3)},
    {'color': 'black', 'type': BING, 'name': '卒', 'position': (2, 3)},
    {'color': 'black', 'type': BING, 'name': '卒', 'position': (4, 3)},
    {'color': 'black', 'type': BING, 'name': '卒', 'position': (6, 3)},
    {'color': 'black', 'type': BING, 'name': '卒', 'position': (8, 3)},
    # 添加其他棋子的定义...
    {'color': 'red', 'type': CHE, 'name': '车', 'position': (0, 9)},
    {'color': 'red', 'type': MA, 'name': '马', 'position': (1, 9)},
    {'color': 'red', 'type': XIANG, 'name': '象', 'position': (2, 9)},
    {'color': 'red', 'type': SHI, 'name': '士', 'position': (3, 9)},
    {'color': 'red', 'type': JIANG, 'name': '帅', 'position': (4, 9)},
    {'color': 'red', 'type': SHI, 'name': '士', 'position': (5, 9)},
    {'color': 'red', 'type': XIANG, 'name': '象', 'position': (6, 9)},
    {'color': 'red', 'type': MA, 'name': '马', 'position': (7, 9)},
    {'color': 'red', 'type': CHE, 'name': '车', 'position': (8, 9)},
    {'color': 'red', 'type': PAO, 'name': '炮', 'position': (1, 7)},
    {'color': 'red', 'type': PAO, 'name': '炮', 'position': (7, 7)},
    {'color': 'red', 'type': BING, 'name': '兵', 'position': (0, 6)},
    {'color': 'red', 'type': BING, 'name': '兵', 'position': (2, 6)},
    {'color': 'red', 'type': BING, 'name': '兵', 'position': (4, 6)},
    {'color': 'red', 'type': BING, 'name': '兵', 'position': (6, 6)},
    {'color': 'red', 'type': BING, 'name': '兵', 'position': (8, 6)},
]


# 棋子类型到状态数组第三维索引的映射
# 假设：红方棋子索引为偶数，黑方棋子索引为奇数
piece_type_to_index = {
    'red_che': 0, 'black_che': 1,
    'red_ma': 2, 'black_ma': 3,
    'red_pao': 4, 'black_pao': 5,
    'red_xiang': 6, 'black_xiang': 7,
    'red_shi': 8, 'black_shi': 9,
    'red_jiang': 10, 'black_jiang': 11,
    'red_bing': 12, 'black_bing': 13
}

def position_to_index(x, y):
    return y * 9 + x

def index_to_position(index):
    x = index % 9
    y = index // 9
    return x, y

class CONST():
    num_episodes = 0