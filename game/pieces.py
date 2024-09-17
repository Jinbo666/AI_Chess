# game/piece.py

class Piece:
    def __init__(self, color, type, position, name):
        self.color = color
        self.type = type  # 统一的类型标识，如 'che', 'ma', etc.
        self.name = name        # 中文名称，如 '车', '马', etc.
        self.position = position  # 位置以棋盘上的格子坐标表示，例如 (0, 0)
    # No references to unpickleable objects

    def __str__(self):
        return f"{self.color} {self.name} at {self.position}"
