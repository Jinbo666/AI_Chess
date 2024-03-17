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

# 定义所有棋子的初始位置和属性
initial_pieces = [
    {'color': 'black', 'type': '车', 'position': (0, 0)},
    {'color': 'black', 'type': '马', 'position': (1, 0)},
    {'color': 'black', 'type': '相', 'position': (2, 0)},
    {'color': 'black', 'type': '仕', 'position': (3, 0)},
    {'color': 'black', 'type': '将', 'position': (4, 0)},
    {'color': 'black', 'type': '仕', 'position': (5, 0)},
    {'color': 'black', 'type': '相', 'position': (6, 0)},
    {'color': 'black', 'type': '马', 'position': (7, 0)},
    {'color': 'black', 'type': '车', 'position': (8, 0)},
    {'color': 'black', 'type': '炮', 'position': (1, 2)},
    {'color': 'black', 'type': '炮', 'position': (7, 2)},
    {'color': 'black', 'type': '卒', 'position': (0, 3)},
    {'color': 'black', 'type': '卒', 'position': (2, 3)},
    {'color': 'black', 'type': '卒', 'position': (4, 3)},
    {'color': 'black', 'type': '卒', 'position': (6, 3)},
    {'color': 'black', 'type': '卒', 'position': (8, 3)},
    # 添加其他棋子的定义...
    {'color': 'red', 'type': '车', 'position': (0, 9)},
    {'color': 'red', 'type': '马', 'position': (1, 9)},
    {'color': 'red', 'type': '象', 'position': (2, 9)},
    {'color': 'red', 'type': '士', 'position': (3, 9)},
    {'color': 'red', 'type': '帅', 'position': (4, 9)},
    {'color': 'red', 'type': '士', 'position': (5, 9)},
    {'color': 'red', 'type': '象', 'position': (6, 9)},
    {'color': 'red', 'type': '马', 'position': (7, 9)},
    {'color': 'red', 'type': '车', 'position': (8, 9)},
    {'color': 'red', 'type': '炮', 'position': (1, 7)},
    {'color': 'red', 'type': '炮', 'position': (7, 7)},
    {'color': 'red', 'type': '兵', 'position': (0, 6)},
    {'color': 'red', 'type': '兵', 'position': (2, 6)},
    {'color': 'red', 'type': '兵', 'position': (4, 6)},
    {'color': 'red', 'type': '兵', 'position': (6, 6)},
    {'color': 'red', 'type': '兵', 'position': (8, 6)},
]


# 棋子类型到状态数组第三维索引的映射
# 假设：红方棋子索引为偶数，黑方棋子索引为奇数
piece_type_to_index = {
    '红车': 0, '黑车': 1,
    '红马': 2, '黑马': 3,
    # 完成其他棋子的映射...
    '红炮': 4, '黑炮': 5,
    '红象': 6, '黑相': 7,  # 注意北方方言中称为“相”，南方方言中称为“象”
    '红士': 8, '黑仕': 9,
    '红帅': 10, '黑将': 11,
    '红兵': 12, '黑卒': 13
}
