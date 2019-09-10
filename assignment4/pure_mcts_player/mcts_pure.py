import copy
import numpy as np
from operator import itemgetter
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
                       PASS, is_black_white, coord_to_point, where1d, \
                       MAXSIZE, NULLPOINT, TIE

def rollout_policy_fn(board):
    moves = GoBoardUtil.generate_legal_moves_gomoku(board)
    move_probs = np.random.rand(len(moves))
    return zip(moves, move_probs)


def policy_value_fn(board):
    moves = GoBoardUtil.generate_legal_moves_gomoku(board)
    move_probs = np.ones(len(moves)) / len(moves)
    return zip(moves, move_probs), 0

class TreeNode():
    """A node in the MCTS tree. Each node keeps track of its own value Q,
    prior probability P, and its visit-count-adjusted prior score u.
    """

    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {}  # a map from action to TreeNode
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, move_priors):
        """Expand tree by creating new children.
        move_priors: a list of tuples of moves and their prior probability
            according to the policy function.
        """
        for move, prob in move_priors:
            if move not in self._children:
                self._children[move] = TreeNode(self, prob)

    def select(self, c_puct):
        """Select move among children that gives maximum move value Q
        plus bonus u(P).
        Return: A tuple of (move, next_node)
        """
        return max(self._children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.
        leaf_value: the value of subtree evaluation from the current player's
            perspective.
        """
        # Count visit.
        self._n_visits += 1
        # Update Q, a running average of values for all visits.
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits

    def update_recursive(self, leaf_value):
        """Like a call to update(), but applied recursively for all ancestors.
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, u.
        c_puct: a number in (0, inf) controlling the relative impact of
            value Q, and prior probability P, on this node's score.
        """
        self._u = (c_puct * self._P *
                   np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded).
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None


class MCTS(object):
    """A simple implementation of Monte Carlo Tree Search."""

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """
        policy_value_fn: a function that takes in a board state and outputs
            a list of (action, probability) tuples and also a score in [-1, 1]
            (i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct: a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, board):
        """Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self._root
        while(1):
            if node.is_leaf():
                break
            # Greedily select next move.
            move, node = node.select(self._c_puct)
            # state.do_move(action)
            board.play_move_gomoku(move, board.current_player)

        move_probs, _ = self._policy(board)
        # Check for end of game
        end, winner = board.check_game_end_gomoku()
        if not end:
            node.expand(move_probs)
        
        # Evaluate the leaf node by random rollout
        leaf_value = self._evaluate_rollout(board)
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)
        # print("-----")

    def _evaluate_rollout(self, board, limit=1000):
        """Use the rollout policy to play until the end of the game,
        returning +1 if the current player wins, -1 if the opponent wins,
        and 0 if it is a tie.
        """
        current_player = board.current_player
        for i in range(limit):
            end, winner = board.check_game_end_gomoku()
            if end:
                break
            # use random move in this case
            move_probs = rollout_policy_fn(board)
            max_move = max(move_probs, key=itemgetter(1))[0]
            board.play_move_gomoku(max_move, current_player)
        else:
            # If no break from the loop, issue a warning.
            print("WARNING: rollout reached move limit")
        if winner == TIE:  # tie
            return 0
        else:
            return 1 if winner == current_player else -1

    def get_move(self, board):
        """Runs all playouts sequentially and returns the most visited action.
        board: the current game state

        Return: the selected action
        """
        # print("n_playout= ", self._n_playout)
        for n in range(self._n_playout):
            # print(n)
            # board_copy = copy.deepcopy(board)
            board_copy = board.copy()
            self._playout(board_copy)

            if n == int(self._n_playout // 2):
                self.best_move = max(self._root._children.items(),
                        key=lambda act_node: act_node[1]._n_visits)[0]
        
        return max(self._root._children.items(),
                   key=lambda act_node: act_node[1]._n_visits)[0]

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)


    def get_best_move_so_far(self):
        print("timeout--------")
        return max(self._root._children.items(),
                   key=lambda act_node: act_node[1]._n_visits)[0]

    def __str__(self):
        return "MCTS"


# class MCTSPlayer(object):
#     """AI player based on MCTS"""
#     def __init__(self, c_puct=5, n_playout=2000):
#         self.mcts = MCTS(policy_value_fn, c_puct, n_playout)

#     def set_player_ind(self, p):
#         self.player = p

#     def reset_player(self):
#         self.mcts.update_with_move(-1)

#     def get_action(self, board):
#         sensible_moves = GoBoardUtil.generate_legal_moves_gomoku(board)
#         if len(sensible_moves) > 0:
#             move = self.mcts.get_move(board)
#             self.mcts.update_with_move(-1)
#             return move
#         else:
#             print("WARNING: the board is full")

#     def __str__(self):
#         return "MCTS {}".format(self.player)