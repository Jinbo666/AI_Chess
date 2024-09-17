import pygame
import sys

from game.util.const import *
import logging
logging.basicConfig(level=logging.INFO)
logging.info("This is an info message.")

class Board:
    def __init__(self, pygame):
        self.pygame = pygame
        # 设置窗口大小和标题
        self.screen = self.pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.pygame.display.set_caption('中国象棋')
        self.font_path = 'assets/font/微软雅黑.ttf'  # 字体文件路径，根据实际情况调整


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
            # logging.info(piece)
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
            text = font_piece.render(piece.name, True, (255, 255, 255))  # 假设文字颜色为白色
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

        font_piece = self.pygame.font.Font(self.font_path, FONT_SIZE_CHESS)  # 使用指定的中文字体和字体大小

        text = f"{'红方' if winner == 'red' else '黑方'}获胜！点击任意键退出游戏。"
        text_surface = font_piece.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # 在文字位置绘制一个矩形背景
        # 可以稍微增加矩形的尺寸，以增加边距
        background_rect = text_rect.inflate(20, 20)  # 在宽度和高度上各增加20像素
        pygame.draw.rect(self.screen, BG_COLOR, background_rect)

        self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # 等待玩家点击任意键或关闭窗口
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

        # 玩家确认后，退出游戏
        pygame.quit()
        sys.exit()
