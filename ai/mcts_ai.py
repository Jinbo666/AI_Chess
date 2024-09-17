# ai/mcts_ai.py

from copy import deepcopy
import random
import math
import time
import logging

MAX_DEPTH = 20  # 20
MAX_CHILDREN = 16  # 5
MAX_ITERATION = 1000
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
            node, state = self.selection(node, state)

            # Expansion
            node, state = self.expansion(node, state)

            # Simulation
            result = self.simulation(state)

            # Backpropagation
            self.backpropagation(node, result)

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
        print("Selected start")
        while node.untried_actions == [] and node.children != []:
            # print('uct_select')
            node = self.uct_select(node)
            # 在模拟的状态中执行动作
            piece = state.get_piece_at(node.action[0])
            state.move_piece(piece, node.action[1][0], node.action[1][1])
            if self.debug:
                print(f"Selected node at depth {node.depth()}, action: {node.action}, visits: {node.visits}, wins: {node.wins}")
        print("Selected done")
        return node, state

    def uct_select(self, node):
        c = C  # 调整探索常数。实验不同的 c 值：尝试不同的探索常数，观察对 AI 表现的影响。
        log_parent_visits = math.log(node.visits)
        best_score = -float('inf')
        best_child = None
        for child in node.children:

            exploitation = child.wins / child.visits
            exploration = c * math.sqrt(math.log(node.visits) / child.visits)
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
        print("Expansion start")
        max_children = MAX_CHILDREN  # 限制子节点数量
        if node.untried_actions:
            # 如果未尝试动作列表长度超过 max_children，只保留前 max_children 个动作
            if len(node.untried_actions) > max_children:
                node.untried_actions = node.untried_actions[:max_children]
            # 从未尝试的动作中选择一个动作进行扩展
            action = node.untried_actions.pop(0)  # 选择优先级最高的动作

            # 在模拟的状态中执行动作
            piece = state.get_piece_at(action[0])
            move_successful = state.move_piece(piece, action[1][0], action[1][1])
            if not move_successful:
                # 如果移动不成功，跳过此动作
                return node, state

            # 创建新节点
            child_node = MCTS_Node(state=deepcopy(state), parent=node, action=action)
            node.children.append(child_node)
            node = child_node

            if self.debug:
                print(f"Expanded new node with action: {action}")
        print("Expansion done!")
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
        piece_values = {
            'che': 9,
            'ma': 4.5,
            'xiang': 2,
            'shi': 2,
            'jiang': 10000,
            'pao': 4.5,
            'bing': 1
        }
        my_score = 0
        opponent_score = 0
        for piece in state.pieces.values():
            value = piece_values.get(piece.type, 0)
            # 考虑棋子的位置价值，例如：
            x, y = piece.position

            # 增加攻击性奖励
            attack_bonus = 0
            possible_moves = state.get_all_possible_moves(piece)
            for move in possible_moves:
                target_piece = state.get_piece_at(move)
                if target_piece and target_piece.color != piece.color:
                    # 奖励攻击对方棋子
                    target_value = piece_values.get(target_piece.type, 0)
                    attack_bonus += target_value * 0.1  # 可调整系数
            # 根据棋子颜色累加得分
            if piece.color == self.color:
                my_score += value + attack_bonus
            else:
                opponent_score += value + attack_bonus

            # position_value = self.get_position_value(piece.type, x, y)
            # total_value = value + position_value
            # if piece.color == self.color:
            #     my_score += total_value
            # else:
            #     opponent_score += total_value
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