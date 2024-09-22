# ai/mcts_ai.py

from copy import deepcopy
import random
import math
import time
import logging

MAX_DEPTH = 20  # 20
MAX_CHILDREN = 5  # 5
MAX_ITERATION = 10 # 1000
C = 1.4  # 1.4

class MCTS_Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # 当前节点的游戏状态
        self.parent = parent  # 父节点
        self.children = []  # 子节点列表
        self.visits = 0  # 访问次数
        self.wins = 0  # 赢的次数
        self.aggressiveness = 0
        self.untried_actions = self.state.get_legal_actions()  # 尚未尝试的动作
        self.action = action  # 导致当前状态的动作

    def depth(self):
        depth = 0
        node = self
        while node.parent is not None:
            node = node.parent
            depth += 1
        return depth

    def calculate_aggressiveness(self):
        # 根据动作的类型计算进攻性
        if self.action is None:
            return 0
        target_piece = self.state.get_piece_at(self.action[1])
        if target_piece and target_piece.color != self.state.current_player:
            return 1  # 吃子动作进攻性高
        else:
            return 0  # 普通动作进攻性低

class MCTS_AI:
    def __init__(self, game_state, color, time_limit=1):
        self.game_state = game_state
        self.color = color
        self.time_limit = time_limit  # 给定的思考时间，单位为秒
        self.debug = True
        self.simulation_depth = 0  # 用于跟踪模拟深度
        logging.info('MCTS_AI initialized')

    def make_move(self):
        # 使用 MCTS 算法选择最佳动作
        best_action = self.mcts_search()
        if best_action:
            # 在实际的游戏状态中执行最佳动作
            piece = self.game_state.get_piece_at(best_action[0])
            move_successful = self.game_state.move_piece(piece, best_action[1][0], best_action[1][1])
            if move_successful:
                return True
        return False

    def mcts_search(self):
        # 创建根节点
        root = MCTS_Node(state=deepcopy(self.game_state))

        end_time = time.time() + self.time_limit
        max_iterations = MAX_ITERATION
        # if self.debug:
        #     max_iterations = 10  # 调试模式下限制模拟次数
        # else:
        #     max_iterations = 1000  # 正常模式下的模拟次数
        iteration = 0
        while time.time() < end_time and iteration < max_iterations:
            iteration += 1
            node = root
            state = deepcopy(self.game_state)

            state.is_simulation = True  # 开始模拟

            if self.debug:
                print(f"\nSimulation {iteration} start")

            # Selection
            print('>>>>>>>>Selection start')
            node, state = self.selection(node, state)
            print('<<<<<<<<Selection done')

            # Expansion
            print('>>>>>>>>Expansion start')
            node, state = self.expansion(node, state)
            print('<<<<<<<<Expansion done')

            # Simulation
            print('>>>>>>>>Simulation start')
            result = self.simulation(state)
            print('<<<<<<<<Simulation done')

            # Backpropagation
            print('>>>>>>>>Backpropagation start')
            self.backpropagation(node, result)
            print('<<<<<<<<Backpropagation done')

            state.is_simulation = False  # 模拟结束

            if self.debug:
                print(f"Simulation {iteration} end with result: {result}")

        # 选择访问次数最多的子节点对应的动作
        best_child = max(root.children, key=lambda c: c.visits)
        if self.debug:
            print(f"best_child.action: {best_child.action}")
        return best_child.action

    # 以下需要实现 selection、expansion、simulation、backpropagation 方法
    def selection(self, node, state):
        # 递归地选择子节点，直到到达一个未完全展开的节点
        while node.untried_actions == [] and node.children != []:
            # print('uct_select')
            node = self.uct_select(node)
            # 在模拟的状态中执行动作
            piece = state.get_piece_at(node.action[0])
            state.move_piece(piece, node.action[1][0], node.action[1][1])
            if self.debug:
                print(f"Selected node at depth {node.depth()}, action: {node.action}, visits: {node.visits}, wins: {node.wins}")
        return node, state

    def uct_select(self, node):
        c = C  # 调整探索常数。实验不同的 c 值：尝试不同的探索常数，观察对 AI 表现的影响。
        log_parent_visits = math.log(node.visits)
        best_score = -float('inf')
        best_child = None
        for child in node.children:
            # 防止除以零错误，如果 child.visits 为 0，设置一个非常小的数
            if child.visits == 0:
                exploitation = 0
            else:
                exploitation = child.wins / child.visits

            exploration = c * math.sqrt(math.log(node.visits) / (child.visits + 1e-6))
            aggressiveness = child.aggressiveness  # 进攻性因子

            # uct_score = (child.wins / child.visits) + \
            #             c * math.sqrt(log_parent_visits / child.visits)
            uct_score = exploitation + exploration + aggressiveness * 0.5  # 可调整系数

            if self.debug:
                print(f"At depth {child.depth()}, Child action: {child.action}, UCT score: {uct_score}, visits: {child.visits}, wins: {child.wins}")

            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        return best_child

    def expansion(self, node, state):
        if node.untried_actions:
            print('expansion node.untried_actions:', node.untried_actions)
            # 随机选择 MAX_CHILDREN 个动作进行扩展，增加探索的多样性
            actions_to_try = random.sample(node.untried_actions, min(len(node.untried_actions), MAX_CHILDREN))
            print('expansion actions_to_try:', actions_to_try)
            new_nodes = []
            moved_pieces_positions = set()  # 用于跟踪已经移动的棋子位置

            for action in actions_to_try:
                start_position = action[0]

                # 检查起始位置是否已经被移动过
                if start_position in moved_pieces_positions:
                    print(f"Expansion Skipping action {action} because piece at {start_position} has already moved.")
                    continue

                # 从未尝试动作中移除
                node.untried_actions.remove(action)

                # 获取棋子并确保棋子存在
                piece = state.get_piece_at(start_position)
                if piece is None:
                    print(f"Expansion Warning: No piece found at {start_position}. Skipping this action.")
                    continue  # 如果该位置没有棋子，跳过此动作

                # 执行动作，生成新的游戏状态
                move_successful = state.move_piece(piece, action[1][0], action[1][1])
                if not move_successful:
                    print(f"Expansion Move not successful for action {action}.")
                    continue  # 如果移动不成功，跳过此动作

                # 记录这个动作的起始位置，以避免后续动作再移动同一个位置
                moved_pieces_positions.add(start_position)

                # 创建新节点并添加到子节点列表中
                child_node = MCTS_Node(state=deepcopy(state), parent=node, action=action)
                node.children.append(child_node)

                # 收集新扩展的子节点
                new_nodes.append(child_node)

            # 返回最后一个扩展的子节点和更新后的状态
            if new_nodes:
                return new_nodes[-1], state  # 返回最后一个扩展的子节点
            else:
                return node, state  # 如果没有扩展任何节点，返回当前节点
        return node, state

    def simulation(self, state):
        max_depth = MAX_DEPTH
        current_depth = 0
        current_player = state.current_player #self.color
        simulation_path = []  # 用于记录模拟路径

        while not state.check_for_victory() and current_depth < max_depth:
            legal_actions = state.get_all_legal_actions(current_player)
            if not legal_actions:
                break
            # 使用启发式策略选择动作
            action = self.select_action(state, legal_actions, current_player)
            piece = state.get_piece_at(action[0])
            # print('simulation')
            state.move_piece(piece, action[1][0], action[1][1])
            # if self.debug:
            #     print(f"Simulation move: {action}")

            # 记录模拟路径
            simulation_path.append((current_player, piece.name, action))

            # # 打印当前深度和玩家
            # if self.debug:
            #     print(f"Simulation depth {current_depth}, Player {current_player}, Action: {action}")

            # 切换玩家
            current_player = 'black' if current_player == 'red' else 'red'
            current_depth += 1

        # 打印模拟路径
        if self.debug:
            print("Simulation path:")
            for i, step in enumerate(simulation_path):
                player, name, action = step
                print(f"  Step {i}: {'红' if player == 'red' else '黑'}{name}, Action: {action}")

        result = self.evaluate_state(state)

        if self.debug:
            print(f"Simulation result: {result}")
        return result

    def select_action(self, state, legal_actions, player_color):
        # 与之前的代码一致
        # 对于对手，使用相同的策略
        return self.opponent_select_action(state, legal_actions)

    def opponent_select_action(self, state, legal_actions):
        # 与 AI 相同的策略，优先吃子
        capture_actions = []
        normal_actions = []
        for action in legal_actions:
            target_piece = state.get_piece_at(action[1])
            if target_piece and target_piece.color != self.color:
                capture_actions.append(action)
            else:
                normal_actions.append(action)
        # print('capture_actions:', capture_actions)
        if capture_actions:
            return random.choice(capture_actions)
        else:
            return random.choice(normal_actions)

    def evaluate_state(self, state):
        """评估当前游戏状态，返回一个数值表示对当前玩家的有利程度。"""
        # 定义每种棋子的基础价值
        piece_values = {
            'che': 9,
            'ma': 5,
            'xiang': 3,
            'shi': 2,
            'jiang': 1000,
            'pao': 5,
            'bing': 1
        }

        # 进攻性奖励因子，可以根据棋子越靠近对方阵营给予更高奖励
        attack_bonus = {
            'red': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # y坐标为0-9，越靠近0分数越高
            'black': [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]  # y坐标为0-9，越靠近9分数越高
        }

        my_score = 0
        opponent_score = 0
        my_piece_count = 0
        opponent_piece_count = 0

        for piece in state.pieces.values():
            value = piece_values.get(piece.type, 0)  # 获取棋子的基础价值
            x, y = piece.position

            # 位置奖励，根据棋子的位置动态调整分数（可以进一步优化）
            position_value = attack_bonus[piece.color][y]

            # 计算棋子总价值
            total_value = value + position_value

            if piece.color == self.color:
                # 当前玩家的分数
                my_score += total_value
                my_piece_count += 1  # 统计当前玩家的棋子数量
            else:
                # 对手的分数
                opponent_score += total_value
                opponent_piece_count += 1  # 统计对手的棋子数量

        # 棋子数量加权因子，增加棋子越多方的得分
        if my_piece_count > 0 and opponent_piece_count > 0:
            my_score *= (my_piece_count / (my_piece_count + opponent_piece_count))
            opponent_score *= (opponent_piece_count / (my_piece_count + opponent_piece_count))

        # 归一化得分，范围在 -1 到 1 之间，并考虑棋子数量的加权
        return (my_score - opponent_score) / (my_score + opponent_score + 1e-6)

    def get_position_value(self, piece_type, x, y):
        # 根据棋子类型和位置，返回位置价值
        # 可以预先定义每种棋子在不同位置的价值表
        return 0  # 示例，具体实现需要您根据游戏策略设计

    def backpropagation(self, node, result):
        print("Backpropagation start")
        # 将结果反向传播到根节点
        while node is not None:
            node.visits += 1
            node.wins += result
            if self.debug:
                indent = '  ' * node.depth()
                # 获取执行动作的玩家
                if node.parent is not None:
                    action_player = 'black' if node.state.current_player == 'red' else 'red'
                else:
                    action_player = node.state.current_player  # 根节点
                print(f"{indent}Backpropagating at depth {node.depth()}, Player after move: {node.state.current_player}, Action by {action_player}: {node.action}, Visits: {node.visits}, Wins: {node.wins}")

            node = node.parent
        print("Backpropagation done!")