import pygame
import sys
import json
import importlib
from game.board import Board
from game.util.const import *
from game.game_state import GameState
import logging
logging.basicConfig(level=logging.INFO)
logging.info("This is an info message.")

# 初始化pygame
logging.info('pygame.init()...')
pygame.init()

# 创建一个时钟对象
clock = pygame.time.Clock()

# 创建棋盘
board = Board(pygame)
game_state = GameState()


# 读取配置文件，获取 AI 类名称
with open('config.json', 'r') as f:
    config = json.load(f)
ai_class_name = config.get('ai_class', 'Random_AI')  # 默认使用 RandomAI


# 动态导入 AI 模块并获取 AI 类
try:
    ai_module = importlib.import_module(f'ai.{ai_class_name.lower()}')
    AIClass = getattr(ai_module, ai_class_name)
except (ImportError, AttributeError) as e:
    print(f"Error importing AI class '{ai_class_name}': {e}")
    sys.exit(1)


# 创建 AI 实例
ai_player = AIClass(game_state, "black")  # 创建AI实例

selected_piece = None  # 选中的棋子
selected_pos = None  # 选中棋子的位置

while True:

    winner = game_state.check_for_victory()
    if winner:
        board.show_victory_message(winner)
        pygame.time.wait(500)
        break

    if game_state.current_player == "red":  # 人类玩家的回合
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                grid_x = round((x - BOARD_START_X) / CELL_SIZE)
                grid_y = round((y - BOARD_START_Y) / CELL_SIZE)

                if 0 <= grid_x < 9 and 0 <= grid_y < 10:  # 确保点击在棋盘内
                    clicked_piece = game_state.get_piece_at((grid_x, grid_y))

                    if selected_piece:
                        if (
                                clicked_piece is None or clicked_piece.color != game_state.current_player) and game_state.is_valid_move(
                                selected_piece, grid_x, grid_y):
                            # 执行移动
                            game_state.move_piece(selected_piece, grid_x, grid_y)
                            logging.info(f"红方移动棋子到: {grid_x}, {grid_y}")

                            # 检查胜利条件
                            winner = game_state.check_for_victory()
                            if winner:
                                board.show_victory_message(winner)
                                pygame.time.wait(500)
                                break  # 结束游戏循环

                            # 检查对方是否将军
                            if game_state.check_for_check(game_state.current_player):
                                logging.info(f"{game_state.current_player}方将军！")

                            # 轮换玩家
                            # game_state.current_player = "black"# if game_state.current_player == "red" else "red"

                            # logging.info(f'轮换玩家: {game_state.current_player}')

                            selected_piece = None
                            selected_pos = None
                        else:
                            # 点击的是己方的另一个棋子，更新选中的棋子
                            if clicked_piece and clicked_piece.color == game_state.current_player:
                                selected_piece = clicked_piece
                                selected_pos = (grid_x, grid_y)
                            else:
                                selected_piece = None
                                selected_pos = None
                    else:
                        # 如果当前没有选中的棋子，检查点击的位置是否有当前玩家的棋子
                        if clicked_piece and clicked_piece.color == game_state.current_player:
                            selected_piece = clicked_piece
                            selected_pos = (grid_x, grid_y)
                else:
                    # 如果点击在棋盘外，取消选中状态
                    selected_piece = None
                    selected_pos = None

    elif game_state.current_player == "black":  # AI玩家的回合
        # 检查胜利条件
        winner = game_state.check_for_victory()
        if winner:
            board.show_victory_message(winner)
            pygame.time.wait(500)
            break  # 结束游戏循环

        # 使用随机AI进行移动
        move_made = ai_player.make_move()
        if move_made:
            # 检查胜利条件
            winner = game_state.check_for_victory()
            if winner:
                board.show_victory_message(winner)
                pygame.time.wait(500)
                break  # 结束游戏循环

            # 检查对方是否将军
            if game_state.check_for_check(game_state.current_player):
                logging.info(f"{game_state.current_player}方将军！")
            # 轮换玩家
            # game_state.current_player = "red"
        else:
            logging.info("AI无法移动，游戏结束")
            break

    # 绘制棋盘和棋子的代码
    board.draw_board()
    if selected_pos:
        board.draw_selection(selected_pos)
    board.draw_pieces(game_state.pieces)
    pygame.display.flip()

    clock.tick(60)


# 游戏结束，退出Pygame
pygame.quit()
sys.exit()
