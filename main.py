import pygame
import sys
from game.board import Board
from game.util.const import *
from ai.random_ai import RandomAI
from stable_baselines3 import PPO
from envs.chess_env import ChineseChessEnv

# 初始化pygame
print('pygame.init()...')
pygame.init()




# 创建棋盘
board = Board(pygame)
ai_player = RandomAI(board, "black")  # 创建AI实例



# current_player_color = "red"  # 游戏开始时红方先行

# 加载模型
print('PPO load...')
model = PPO.load("ppo_chinese_chess.zip")


# 初始化环境
print('ChineseChessEnv...')
env = ChineseChessEnv(board, render_delay=0.5)


selected_piece = None  # 选中的棋子
selected_pos = None  # 选中棋子的位置

last_obs = ''


while True:
    winner = board.check_for_victory()
    if winner:
        board.show_victory_message(winner)
        pygame.time.wait(500)
        break

    if board.current_player == "red":  # 人类玩家的回合
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
                        if (clicked_piece is None or clicked_piece.color != board.current_player) and board.is_valid_move(selected_piece, grid_x, grid_y):
                            # 执行移动，这里假设你有一个方法来实际移动棋子并更新棋盘状态
                            board.move_piece(selected_piece, grid_x, grid_y)
                            print(f"移动棋子到: {grid_x}, {grid_y}")
                           
                            # 检查对方是否将军
                            if board.check_for_check(board.current_player):
                                print(f"{board.current_player}方将军！")
 
                            # 轮换玩家
                            board.current_player = "black" if board.current_player == "red" else "red"
        
                            print('轮换玩家:', board.current_player)

                            selected_piece = None
                            selected_pos = None
                        else:
                            # 点击的是己方的另一个棋子，更新选中的棋子
                            if clicked_piece and clicked_piece.color == board.current_player:
                                selected_piece = clicked_piece
                                selected_pos = (grid_x, grid_y)
                            else:
                                selected_piece = None
                                selected_pos = None
                    else:
                        # 如果当前没有选中的棋子，检查点击的位置是否有当前玩家的棋子
                        if clicked_piece and clicked_piece.color == board.current_player:
                            selected_piece = clicked_piece
                            selected_pos = (grid_x, grid_y)
                else:
                    # 如果点击在棋盘外，取消选中状态
                    selected_piece = None
                    selected_pos = None

    elif board.current_player == "black":  # AI玩家的回合
        # 这里，我们将使用环境状态来预测AI的行动
        obs = env.get_observation()
        # import json
        # obs_str = json.dumps(obs, ensure_ascii=False)
        # print('!!!!!!!', obs_str == last_obs)
        # last_obs = obs_str
        # print('obs:', obs)
        action, _states = model.predict(obs, deterministic=True)
        print('action:', action)
        board.execute_action(action)  # 假设你有一个方法来根据AI的行动更新棋盘状态
        board.current_player = "red"


    # 绘制棋盘和棋子的代码
    board.draw_board()
    if selected_pos:
        board.draw_selection(selected_pos)
    board.draw_pieces(board.pieces)
    pygame.display.flip()

    # # 延迟
    # pygame.time.delay(50)
