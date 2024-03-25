import gym
from gym import spaces
import numpy as np
import time
from game.util.const import *
from game.board import Board
# from gymnasium.spaces import Discrete



class ChineseChessEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # num_episodes = 0
    
    def __init__(self, board, render_delay=0):
        super(ChineseChessEnv, self).__init__()
        # 定义动作空间和观察空间        self.state = None  # 初始化状态
        self.board = board if board is not None else Board()  #Board()  # 创建棋盘实例
        # self.current_player = 'red'  # 假设红方先行
        self.render_delay = render_delay

        self.no_capture_step_limit = 50  # 设置无吃子步数限制，这里以50步为例
        self.no_capture_step_count = 0  # 用于记录自上次吃子以来的步数

        self.legal_moves = self.compute_legal_moves()
        
        # if self.legal_moves and len(self.legal_moves) > 0:
        #     self.action_space = spaces.Discrete(len(self.legal_moves))
        # else:
        #     self.action_space = spaces.Discrete(0)
        self.action_space = spaces.Discrete(90*90)  # 假设有90*90种可能的动作
        self.action_mask = np.zeros(self.action_space.n, dtype=np.bool_)  # 初始化动作掩码
        self.observation_space = spaces.Box(low=0, high=1, shape=(10, 9, 14), dtype=np.float32)  # 示例观察空间


        self.action_history = []
        self.action_history_N = 5

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
        self.update_legal_moves_and_action_mask()
        info = {'action_mask': self.action_mask}
        print('reset:', self.action_mask.shape)
        return self.state#, info

    def update_reward_with_repetition_penalty(self, reward, current_action, repetition_penalty=0.1):
        # 假设actions是一个列表或数组，包含一系列动作
        # unique_actions, counts = np.unique(actions, return_counts=True)
        # prob_actions = counts / counts.sum()
        # entropy = -np.sum(prob_actions * np.log(prob_actions + 1e-6))  # 计算熵
        # entropy_bonus = entropy * entropy_bonus_weight
        #
        # # 将熵奖励加到原始奖励上
        # updated_rewards = rewards + entropy_bonus
        # print('_get_reward:', rewards, 'entropy_bonus:', round(entropy_bonus, 3), 'updated_rewards:', round(updated_rewards, 3))
        # 检查是否与上一步动作的结束位置相同
        if len(self.action_history) >= 2:  # 确保至少有两步动作记录
            last_action = self.action_history[-2]  # 获取上一步动作
            if current_action[:2] == last_action[2:]:
                # 如果当前动作的起始位置与上一动作的结束位置相同，则应用惩罚
                reward -= repetition_penalty
        return reward

    def step(self, action):
        # print('step is called!', self.no_capture_step_count)
        info = {}  # 可以包含额外的调试信息
        # 执行动作，更新状态
        start_x, start_y, end_x, end_y = self._take_action(action)
        # print(start_x, start_y, end_x, end_y)

        # 记录动作到历史列表中
        current_action = (start_x, start_y, end_x, end_y)
        self.action_history.append(current_action)

        if len(self.action_history) > self.action_history_N:  # 保持动作历史的长度为N
            self.action_history.pop(0)

        done = self._check_done()
        if not start_x and not start_y and not end_x and not end_y:
            info = {'illegal_action': True}
            return self.state, -1, done, info
        
        # print('self.state:', self.state)
        # 更新环境状态
        self.state = self._update_state_after_action(start_x, start_y, end_x, end_y)

        # 基于动作历史计算熵
        reward = self.update_reward_with_repetition_penalty(self._get_reward(), current_action, 0.1)


        if done:
            CONST.num_episodes += 1
            print('================================================================================')
            print('CONST.num_episodes:', CONST.num_episodes)
            print('================================================================================')
            return self.reset(), reward, done, info
        

        # 动态更新合法动作列表
        self.update_legal_moves_and_action_mask()
        # print('step:', self.action_mask.shape)
        info = {'action_mask': self.action_mask}
        
        # 根据render_delay停顿一下
        if self.render_delay > 0:
            time.sleep(self.render_delay)

        if done:
            return self.reset(), 0, done, info
        return self.state, reward, done, info
    
    def action_to_index(self, start_x, start_y, end_x, end_y):
        # 假设棋盘大小为9x10
        board_width = 9
        start_pos = start_y * board_width + start_x
        end_pos = end_y * board_width + end_x
        return start_pos * (board_width * 10) + end_pos
    
    def index_to_action(self, index):
        board_width = 9
        total_positions = board_width * 10
        start_pos = index // total_positions
        end_pos = index % total_positions
        start_x = start_pos % board_width
        start_y = start_pos // board_width
        end_x = end_pos % board_width
        end_y = end_pos // board_width
        return start_x, start_y, end_x, end_y

    def generate_action_mask(self):
        legal_moves = self.compute_legal_moves()
        # 初始化一个全为False的掩码
        mask = np.zeros(self.action_space.n, dtype=np.bool)
        # 根据当前状态更新掩码，这里仅为示例
        # 假设self.legal_moves包含所有合法动作的编码索引
        for move in legal_moves:
            index = self.action_to_index(*move)
            mask[index] = True
        return mask

    def _update_state_after_action(self, start_x, start_y, end_x, end_y):
        # 首先，找到开始位置的棋子类型和颜色
        piece_index = np.argmax(self.state[start_y, start_x])
        [piece_color, piece_type] = self._index_to_piece_type(piece_index)

        # 清除开始位置的棋子信息
        self.state[start_y, start_x, :] = 0

        # 如果结束位置有棋子（即吃子），也清除结束位置的棋子信息
        # 注意：这个示例不区分吃子或普通移动，因为状态更新的关键在于最终的棋盘布局
        self.state[end_y, end_x, :] = 0

        # 将棋子移动到新的位置
        new_piece_index = self._piece_type_to_index(piece_color, piece_type)
        self.state[end_y, end_x, new_piece_index] = 1

        # 返回更新后的状态
        return self.state

    def _index_to_piece_type(self, index):
        # 找到索引对应的棋子类型和颜色
        for piece_type, idx in piece_type_to_index.items():
            if idx == index:
                # 假设piece_type的格式是"颜色类型"，如"红车"
                return [piece_type[:1], piece_type[1:]]  # 分割字符串
        # 如果未找到，可以抛出异常或返回一个明确的错误值
        raise ValueError(f"Index {index} not found in piece_type_to_index mapping.")


    def _piece_type_to_index(self, color, type):
        # 这个方法根据棋子的颜色和类型返回对应的索引
        return piece_type_to_index[color + type]
    
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
    
    def update_legal_moves_and_action_mask(self):
        # 重置动作掩码
        self.action_mask.fill(False)
        
        # 根据当前状态下所有合法动作更新动作掩码
        legal_moves = self.compute_legal_moves()  # 假设这个方法返回所有合法动作的列表
        for move in legal_moves:
            action_index = self.action_to_index(*move)  # 将动作转换为动作空间中的索引
            self.action_mask[action_index] = True  # 标记为合法动作


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
            return None, None, None, None  # 无效行动或尝试移动对方棋子
        
        
        # 检查移动是否合法（根据你的棋盘规则）
        if not self.board.is_valid_move(moving_piece, end_x, end_y):
            # print('不合法的移动')
            return None, None, None, None  # 不合法的移动
        
        # 执行动作：移动棋子
        # 这需要你的Board类有方法来支持移动棋子
        move_successful = self.board.move_piece(moving_piece, end_x, end_y)
        if not move_successful:
            # 如果移动失败（例如，试图吃掉己方棋子），也可以返回一个负奖励
            # print('移动失败（例如，试图吃掉己方棋子）')
            return None, None, None, None
        
        captured_piece = self.board.last_move_captured_piece()
        if captured_piece:
            self.no_capture_step_count = 0  # 如果这一步吃掉了棋子，重置计数器
        else:
            self.no_capture_step_count += 1  # 否则，计数器加1

        # 获取当前行动方的颜色（假设行动完成后轮到对方行动）
        # self.current_player = 'black' if self.current_player == 'red' else 'red'
        self.board.current_player = 'black' if self.board.current_player == 'red' else 'red'

        return start_x, start_y, end_x, end_y

    def _get_reward(self):
        # 基于游戏进展情况计算奖励
        captured_piece = self.board.last_move_captured_piece()
        
        # 获取当前行动方的颜色（由于是行动后评估奖励，所以需要检查对方是否将军）
        # 注意：这里假设有某种方式可以获取当前玩家的颜色，可能需要你根据实际逻辑进行调整
        # current_player_color = "red" if self.current_player == "black" else "black"
        is_check = self.board.check_for_check(self.board.current_player)
        
        has_won = self.board.check_for_victory()

        reward = 1

        if captured_piece:
            # 根据被吃掉的棋子类型赋予不同的奖励值
            reward += self._reward_for_capturing_piece(captured_piece)

        if is_check:
            # 如果将军，获得奖励
            reward += 150  # 示例：将军获得2分奖励

        if has_won:
            # 如果赢得比赛，获得更大的奖励
            reward += 1000  # 示例：赢得比赛获得100分奖励

        return reward


    def _reward_for_capturing_piece(self, piece):
        # 根据被吃掉的棋子类型赋予奖励值
        # 这里你可以根据棋子的重要性给予不同的奖励值
        if piece.name in ['将', '帅']:
            return 200
        elif piece.name == '车':
            return 100
        elif piece.name in ['马', '炮']:
            return 50
        elif piece.name in ['象', '相', '士', '仕']:
            return 20
        elif piece.name == '兵':
            return 10
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
        # print('self.no_capture_step_count:', self.no_capture_step_count)
        if self.no_capture_step_count >= self.no_capture_step_limit:
            return True

        # 检查当前玩家是否有合法动作可执行
        if not self.compute_legal_moves():
            # 如果没有合法动作，可以根据游戏规则处理。这里假设游戏直接结束。
            # 注意：具体是否判定为失败，以及是哪一方失败，取决于你的游戏规则。
            return True

        return False

