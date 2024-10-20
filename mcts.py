import random
import math
import copy

from gomoku.gomoku.palette import COLOR_BLACK, COLOR_WHITE

'''
define node class that will be used to represent game states and the overall structure of the search tree 
different from depth first search because this one balances exploration and exploitation
'''


class Node:
    # each node represents a state of the game
    def __init__(self, game, stone, play_order, parent=None, move=None):
        self.game = game
        self.stone = stone
        self.play_order = play_order
        self.parent = parent
        self.visits = 0
        self.reward = 0.0
        self.children = []
        self.move = move

    def fully_expanded(self):
        return len(self.children) == len(self.legal_moves())

    def legal_moves(self):  # list of all the possible moves that are available, empty places
        available_moves = [(x, y) for x in range(45, self.game.w_h, 45) for y in range(45, self.game.w_h, 45) if
                           (x, y) not in self.stone["white"] and (x, y) not in self.stone["black"]]
        return available_moves

    def best(self, exploration_weight=1.41):  # 1.41 is used because sqrt(2) is the conventional value
        # applying uct algorithm
        weights = [
            (child.reward / child.visits) + exploration_weight * math.sqrt(2 * math.log(self.visits) / child.visits) for
            child in self.children

        ]
        return self.children[weights.index(max(weights))]  # returns the sim best value

    def expand(self):  # self or just self, node
        unexplored = self.legal_moves()
        new_mv = random.choice(unexplored)
        new_stone = copy.deepcopy(self.stone)
        new_game = copy.deepcopy(self.game)
        new_play_order = self.play_order
        color = "black" if self.play_order else "white"
        color_draw = COLOR_BLACK if color == "black" else COLOR_WHITE

        # draw the stones
        new_stone, new_play_order = new_game.play_draw_stone(new_stone, new_play_order, color, color_draw, *new_mv)
        child_node = Node(new_game, new_stone, new_play_order, self.parent, new_mv)
        self.children.append(child_node)
        return child_node

    def backpropagation(self, result):
        self.visits += 1
        self.reward += result
        if self.parent:
            self.parent.backpropagation(result)


def simulate(game, stone, play_order):
    current_game = copy.deepcopy(game)
    current_stone = copy.deepcopy(stone)
    current_play_order = play_order

    while len(current_stone["white"]) + len(current_stone["black"]) < 225:  # while there are still blank spaces
        available_moves = [(x, y) for x in range(45, current_game.w_h, 45) for y in range(45, current_game.w_h, 45) if
                           (x, y) not in current_stone["white"] and (x, y) not in current_stone["black"]]
        if not available_moves:
            return 0

        move = random.choice(available_moves)
        color = "black" if current_play_order else "white"
        color_draw = COLOR_BLACK if color == "black" else COLOR_WHITE
        current_stone, current_play_order = current_game.play_draw_stone(current_stone, current_play_order, color,
                                                                         color_draw, *move)

        # check if the player wins
        score = current_game.score(current_stone, color, 0, current_play_order)[0]
        if score > 0:
            return 1 if color == "black" else 0

    return 0  # no one wins


def mcts_search(game, stone, play_order, num_simulations=100):
    root = Node(game, stone, play_order)

    for i in range(num_simulations):
        node = root
        # selects the branches and nodes represented by the game state
        while node.fully_expanded() and node.children:
            node = node.best()

        # expand tree to explore based on the exploration weight
        if not node.fully_expanded():
            node = node.expand()

        # simulate random possibilities
        result = simulate(node.game, node.stone, node.play_order)

        # back propagation
        node.backpropagation(result)
    best_child_node = root.best(exploration_weight=0)
    return best_child_node.move


def mcts_ai_make_move(game, stone, play_order, num_simulations=100):
    best_move = mcts_search(game, stone, play_order, num_simulations)
    return best_move  # the coordinates of the optimal move