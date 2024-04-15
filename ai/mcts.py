import numpy as np
import random

class MCTSNode:
    def __init__(self, state, player_color, parent=None, move=None, board=None):
        self.state = state
        self.player_color = player_color  # Track which player's move it is
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        if board:
            self.untried_moves = board.get_legal_moves(state, player_color)
        else:
            self.untried_moves = []
        self.board = board

    def expand(self):
        move = self.untried_moves.pop()
        next_state = self.board.simulate_move(self.state, move)
        # Assuming the color alternates, adjust accordingly if not.
        next_player_color = 'black' if self.player_color == 'red' else 'red'
        child_node = MCTSNode(next_state, next_player_color, parent=self, move=move, board=self.board)
        self.children.append(child_node)
        return child_node

    def update(self, result):
        self.visits += 1
        self.wins += result

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c.wins / c.visits) + c_param * np.sqrt((2 * np.log(self.visits) / c.visits))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return random.choice(possible_moves)

    def rollout(self):
        current_rollout_state = self.state
        current_player_color = self.player_color
        while not self.board.is_terminal(current_rollout_state):
            possible_moves = self.board.get_legal_moves(current_rollout_state, current_player_color)
            action = self.rollout_policy(possible_moves)
            current_rollout_state = self.board.simulate_move(current_rollout_state, action)
            current_player_color = 'black' if current_player_color == 'red' else 'red'
        return self.board.get_result(current_rollout_state, self.player_color)

def do_mcts(root_state, player_color, board, iterations):
    root_node = MCTSNode(state=root_state, player_color=player_color, board=board)
    for _ in range(iterations):
        node = root_node
        while node.is_fully_expanded():
            node = node.best_child()
        if not node.is_fully_expanded():
            node = node.expand()
        result = node.rollout()
        while node is not None:
            node.update(result)
            node = node.parent
    return root_node.best_child().move
