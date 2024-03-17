import gym
from gym import spaces
import numpy as np
from game.util.const import *
from game.board import Board

class ChineseChessEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    
    def __init__(self, board):
        super(ChineseChessEnv, self).__init__()
        # 定义动作空间和观察空间        self.state = None  # 初始化状态
        self.board = board if board is not None else Board()  #Board()  # 创建棋盘实例
        # self.current_player = 'red'  # 假设红方先行

        self.no_capture_step_limit = 50  # 设置无吃子步数限制，这里以50步为例
        self.no_capture_step_count = 0  # 用于记录自上次吃子以来的步数

        self.legal_moves = self.compute_legal_moves()
        
        if self.legal_moves and len(self.legal_moves) > 0:
            self.action_space = spaces.Discrete(len(self.legal_moves))
        else:
            self.action_space = spaces.Discrete(0)
        # self.action_space = spaces.Discrete(len(self.legal_moves))#(90*90)  # 假设有90*90种可能的动作
        self.observation_space = spaces.Box(low=0, high=1, shape=(10, 9, 14), dtype=np.float32)  # 示例观察空间


    def seed(self, seed=None):
        pass

    def reset(self):

        # 重置环境状态，包括棋盘上的棋子和当前行动方
        # 重置无吃子步数计数器
        self.no_capture_step_count = 0

        # 重置环境状态
        self.state = self._get_initial_state()
        self.board.setup_pieces()  # 确保棋盘状态也被重置
        # 动态更新合法动作列表
        self.update_legal_moves()
        return self.state

    def step(self, action):
        # print('step is called!')
        info = {}  # 可以包含额外的调试信息
        # 执行动作，更新状态
        valid_action = self._take_action(action)
        done = self._check_done()
        if not valid_action:
            return self.state, -50, done, info
        if done:
            return self.reset(), 0, done, info
        

        # 动态更新合法动作列表
        self.update_legal_moves()

        reward = self._get_reward()
        if done:
            return self.reset(), 0, done, info
        return self.state, reward, done, info

    def render(self, mode='human', close=False):
        # print('ChineseChessEnv render is called:', mode)
        # 可视化当前环境状态
        if mode == 'human':
            self.board.render_human()
    
    
    def get_observation(self):
        # 创建一个10x9x14的数组来表示棋盘状态，初始化为0
        observation = [[[0 for _ in range(14)] for _ in range(9)] for _ in range(10)]
        
        for position, piece in self.board.pieces.items():
            x, y = position
            color_prefix = '红' if piece.color == 'red' else '黑'
            piece_type = color_prefix + piece.name
            index = piece_type_to_index.get(piece_type, -1)
            if index != -1:
                observation[y][x][index] = 1

        return observation
    
    
    def compute_legal_moves(self):
        # 利用Board类的方法计算当前状态下的所有合法移动
        legal_moves = []
        for piece in self.board.pieces.values():
            if piece.color == self.board.current_player:
                (start_x, start_y) = piece.position
                for move in self.board.get_all_possible_moves(piece):
                    (end_x, end_y) = move
                    # legal_moves.append((piece.position, move))
                    if (start_x, start_y, end_x, end_y) not in legal_moves:
                        # print(piece.name, piece.color, start_x, start_y, end_x, end_y)
                        legal_moves.append((start_x, start_y, end_x, end_y))
        # print(len(legal_moves))
        return legal_moves
    
    def update_legal_moves(self):
        # 根据当前棋盘状态动态更新合法动作列表
        self.legal_moves = self.compute_legal_moves()
        # if len(self.legal_moves) < 1:
        #     self.reset()
        # 也可能需要更新动作空间的大小
        if self.legal_moves and len(self.legal_moves) > 0:
            self.action_space = spaces.Discrete(len(self.legal_moves))
        else:
            self.action_space = spaces.Discrete(0)

    def _get_initial_state(self):
        # 初始化状态
        state = np.zeros(self.observation_space.shape, dtype=np.float32)
        for piece_info in initial_pieces:
            x, y = piece_info['position']
            # 根据piece_info更新state
            # 注意: 你需要根据棋子的类型和颜色确定如何在state中表示该棋子
            color = '红' if piece_info['color'] == 'red' else '黑'
            piece_type = color + piece_info['type']
            index = piece_type_to_index[piece_type]
            state[y, x, index] = 1
            
        return state


    def _take_action(self, action):
        # 解码动作
        # 假设action是一个编码了起始位置和目标位置的整数
        # 这里你需要根据你的动作空间设计来解码动作
        start_x, start_y, end_x, end_y = self.board.decode_action(action)
        
        # 从起始位置获取棋子对象
        moving_piece = self.board.get_piece_at((start_x, start_y))
        if moving_piece is None or moving_piece.color != self.board.current_player:
            # print('无效行动或尝试移动对方棋子', self.current_player, start_x, start_y, end_x, end_y)
            return False  # 无效行动或尝试移动对方棋子
        
        # 执行动作：移动棋子
        # 这需要你的Board类有方法来支持移动棋子
        move_successful = self.board.move_piece(moving_piece, end_x, end_y)
        if not move_successful:
            # 如果移动失败（例如，试图吃掉己方棋子），也可以返回一个负奖励
            # print('移动失败（例如，试图吃掉己方棋子）')
            return False
        
        captured_piece = self.board.last_move_captured_piece()
        if captured_piece:
            self.no_capture_step_count = 0  # 如果这一步吃掉了棋子，重置计数器
        else:
            self.no_capture_step_count += 1  # 否则，计数器加1

        # 获取当前行动方的颜色（假设行动完成后轮到对方行动）
        # self.current_player = 'black' if self.current_player == 'red' else 'red'
        self.board.current_player = 'black' if self.board.current_player == 'red' else 'red'

        return True

    def _get_reward(self):
        # 基于游戏进展情况计算奖励
        captured_piece = self.board.last_move_captured_piece()
        
        # 获取当前行动方的颜色（由于是行动后评估奖励，所以需要检查对方是否将军）
        # 注意：这里假设有某种方式可以获取当前玩家的颜色，可能需要你根据实际逻辑进行调整
        # current_player_color = "red" if self.current_player == "black" else "black"
        is_check = self.board.check_for_check(self.board.current_player)
        
        has_won = self.board.check_for_victory()

        reward = 0

        if captured_piece:
            # 根据被吃掉的棋子类型赋予不同的奖励值
            reward += self._reward_for_capturing_piece(captured_piece)

        if is_check:
            # 如果将军，获得奖励
            reward += 2  # 示例：将军获得2分奖励

        if has_won:
            # 如果赢得比赛，获得更大的奖励
            reward += 100  # 示例：赢得比赛获得100分奖励

        return reward


    def _reward_for_capturing_piece(self, piece):
        # 根据被吃掉的棋子类型赋予奖励值
        # 这里你可以根据棋子的重要性给予不同的奖励值
        if piece.name in ['将', '帅']:
            return 100
        elif piece.name == '车' :
            return 50
        elif piece.name in ['马', '炮']:
            return 25
        elif piece.name in ['象', '相', '士', '仕']:
            return 10
        elif piece.name == '兵':
            return 5
        # 添加其他棋子类型的奖励逻辑
        return 1  # 默认奖励值

    def _check_done(self):
        # 检查是否有一方胜利
        if self.board.check_for_victory():
            return True

        # 如果有其他结束游戏的条件，也可以在这里检查
        # 例如和棋（双方都没有合法移动）

        # 检查游戏是否结束...
        # 如果无吃子步数达到限制，判定为和棋
        if self.no_capture_step_count >= self.no_capture_step_limit:
            return True

        # 检查当前玩家是否有合法动作可执行
        if not self.compute_legal_moves():
            # 如果没有合法动作，可以根据游戏规则处理。这里假设游戏直接结束。
            # 注意：具体是否判定为失败，以及是哪一方失败，取决于你的游戏规则。
            return True

        return False

