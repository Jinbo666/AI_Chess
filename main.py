import pygame
import sys
from game.board import Board
from game.util.const import *
from ai.random_ai import RandomAI

# 初始化pygame
pygame.init()
current_player_color = "red"  # 游戏开始时红方先行

# 设置窗口大小和标题
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Simple Chinese Chess')

# 创建棋盘
board = Board()
ai_player = RandomAI(board, "black")  # 创建AI实例


font_path = 'assets/font/微软雅黑.ttf'  # 字体文件路径，根据实际情况调整
font_gameover = pygame.font.Font(font_path, FONT_SIZE_CHUHE_HANJIE)  # 加载字体文件，40是字体大小

def draw_board(screen):
    """绘制棋盘背景和线条"""
    screen.fill(BG_COLOR)

    # 绘制棋盘的线条等

    # 定义棋盘的起始点和终点坐标
    start_x, start_y = BOARD_START_X, BOARD_START_Y
    end_x, end_y = WINDOW_WIDTH - BOARD_START_X, WINDOW_HEIGHT - BOARD_START_Y
    cell_width = (end_x - start_x) / 8
    cell_height = (end_y - start_y) / 9

    # 绘制棋盘的线条
    for i in range(10):  # 横线
        pygame.draw.line(screen, BLACK, (start_x, start_y + i*cell_height), (end_x, start_y + i*cell_height), 2)
    for i in range(9):  # 竖线
        if i == 0 or i == 8:  # 第一条和最后一条竖线贯穿整个棋盘
            pygame.draw.line(screen, BLACK, (start_x + i*cell_width, start_y), (start_x + i*cell_width, end_y), 2)
        else:  # 其他竖线只在楚河汉界两侧绘制
            pygame.draw.line(screen, BLACK, (start_x + i*cell_width, start_y), (start_x + i*cell_width, start_y + 4*cell_height), 2)
            pygame.draw.line(screen, BLACK, (start_x + i*cell_width, start_y + 5*cell_height), (start_x + i*cell_width, end_y), 2)

    # 绘制九宫格的斜线
    pygame.draw.line(screen, BLACK, (start_x + 3*cell_width, start_y), (start_x + 5*cell_width, start_y + 2*cell_height), 2)
    pygame.draw.line(screen, BLACK, (start_x + 3*cell_width, start_y + 2*cell_height), (start_x + 5*cell_width, start_y), 2)
    pygame.draw.line(screen, BLACK, (start_x + 3*cell_width, end_y - 2*cell_height), (start_x + 5*cell_width, end_y), 2)
    pygame.draw.line(screen, BLACK, (start_x + 3*cell_width, end_y), (start_x + 5*cell_width, end_y - 2*cell_height), 2)


    # 初始化字体
    font_path = 'assets/font/微软雅黑.ttf'  # 字体文件路径，根据实际情况调整
    font_chuhe_hanjie = pygame.font.Font(font_path, FONT_SIZE_CHUHE_HANJIE)  # 加载字体文件，40是字体大小

    # 渲染‘楚河’和‘汉界’文本
    text_chuhe = font_chuhe_hanjie.render('楚河', True, BLACK)
    text_hanjie = font_chuhe_hanjie.render('汉界', True, BLACK)

    # 计算文本位置
    text_chuhe_pos = ((WINDOW_WIDTH - text_chuhe.get_width()) / 2 - 80, (WINDOW_HEIGHT / 2 - text_chuhe.get_height() / 2))
    text_hanjie_pos = ((WINDOW_WIDTH - text_hanjie.get_width()) / 2 + 80, (WINDOW_HEIGHT / 2 - text_hanjie.get_height() / 2))

    # 绘制文本
    screen.blit(text_chuhe, text_chuhe_pos)
    screen.blit(text_hanjie, text_hanjie_pos)


def draw_pieces(screen, pieces):
    font_path = 'assets/font/微软雅黑.ttf'  # 字体文件的路径
    font = pygame.font.Font(font_path, FONT_SIZE_CHESS)  # 使用指定的中文字体和字体大小
    
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
            pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), CELL_SIZE // 2 - 5)  # 红色棋子
        else:
            pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), CELL_SIZE // 2 - 5)  # 黑色棋子

        # 绘制棋子上的文字
        text = font.render(piece.chinese_name, True, (255, 255, 255))  # 假设文字颜色为白色
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect)

def is_game_over():
    # 检查双方的“将”和“帅”是否还在棋盘上
    kings = {"red": False, "black": False}
    for piece in board.pieces.values():
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

def show_victory_message(screen, winner):
    message = f"{winner}方获胜！"
    text_surface = font_gameover.render(message, True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(400, 300))  # 假设屏幕尺寸为800x600
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.wait(5000)  # 显示5秒胜利信息


def draw_selection(screen, position):
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
        pygame.draw.lines(screen, (255, 0, 0), False, line[:2], 2)
        pygame.draw.lines(screen, (255, 0, 0), False, line[1:], 2)


selected_piece = None  # 选中的棋子
selected_pos = None  # 选中棋子的位置

while True:
    
    winner = is_game_over()
    if winner:
        show_victory_message(screen, winner)
        pygame.time.wait(5000)  # 等待一段时间后退出，或者处理其他的结束游戏逻辑
        break  # 跳出游戏循环

    # 处理玩家移动...
    # 处理人类玩家的操作
    # 例如，等待玩家点击棋盘并尝试移动棋子
    if current_player_color == "red":  # 人类玩家的回合
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                grid_x = round((x - BOARD_START_X) / CELL_SIZE)
                grid_y = round((y - BOARD_START_Y) / CELL_SIZE)

                if 0 <= grid_x < 9 and 0 <= grid_y < 10:  # 确保点击在棋盘内
                    clicked_piece = board.get_piece_at((grid_x, grid_y))
                    
                    if selected_piece:
                        if (clicked_piece is None or clicked_piece.color != current_player_color) and board.is_valid_move(selected_piece, grid_x, grid_y):
                            # 执行移动，这里假设你有一个方法来实际移动棋子并更新棋盘状态
                            board.move_piece(selected_piece, grid_x, grid_y)
                            print(f"移动棋子到: {grid_x}, {grid_y}")
                            # 轮换玩家
                            current_player_color = "black" if current_player_color == "red" else "red"
        
                            # 检查对方是否将军
                            if board.is_in_check(current_player_color):
                                print(f"{current_player_color}方将军！")

                            selected_piece = None
                            selected_pos = None
                        else:
                            # 点击的是己方的另一个棋子，更新选中的棋子
                            if clicked_piece and clicked_piece.color == current_player_color:
                                selected_piece = clicked_piece
                                selected_pos = (grid_x, grid_y)
                            else:
                                selected_piece = None
                                selected_pos = None
                    else:
                        # 如果当前没有选中的棋子，检查点击的位置是否有当前玩家的棋子
                        if clicked_piece and clicked_piece.color == current_player_color:
                            selected_piece = clicked_piece
                            selected_pos = (grid_x, grid_y)
                else:
                    # 如果点击在棋盘外，取消选中状态
                    selected_piece = None
                    selected_pos = None

    elif current_player_color == "black":  # AI玩家的回合
        ai_player.make_move()  # 让AI进行一次移动
        current_player_color = "red"  # 轮换到人类玩家
        # 可以在这里添加检查游戏状态的代码（如检查是否将军）            


    # 绘制棋盘和棋子的代码
    draw_board(screen)
    if selected_pos:
        draw_selection(screen, selected_pos)
    draw_pieces(screen, board.pieces)
    pygame.display.flip()

    # 延迟，让AI的移动有一个短暂的间隔，便于观察
    # pygame.time.delay(500)

