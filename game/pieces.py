class Piece:
    def __init__(self, color, name, position, chinese_name):
        self.color = color
        self.name = name
        self.position = position  # 位置以棋盘上的格子坐标表示，例如 (0, 0)
        self.chinese_name = chinese_name  # 增加中文名字属性
