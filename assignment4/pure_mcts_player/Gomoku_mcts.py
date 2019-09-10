#!/Users/mac/anaconda/bin/python
#/usr/bin/env python
#/usr/local/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, EMPTY
from simple_board import SimpleGoBoard
from mcts_pure import MCTS, rollout_policy_fn, policy_value_fn
from timeit import default_timer as timer

import random
import numpy as np

def undo(board,move):
    board.board[move]=EMPTY
    board.current_player=GoBoardUtil.opponent(board.current_player)

def play_move(board, move, color):
    board.play_move_gomoku(move, color)

def game_result(board):
    game_end, winner = board.check_game_end_gomoku()
    moves = board.get_empty_points()
    board_full = (len(moves) == 0)
    if game_end:
        #return 1 if winner == board.current_player else -1
        return winner
    if board_full:
        return 'draw'
    return None


class GomokuMCTSPlayer():
    """
    For each move do `n_simualtions_per_move` playouts,
    then select the one with best win-rate.
    playout could be either random or rule_based (i.e., uses pre-defined patterns) 
    """
    def __init__(self, c_puct=5, n_playout=2000):
        self.name = "Gomoku3"
        self.version = 3.0
        self.best_move = None
        self.mcts = MCTS(policy_value_fn, c_puct, n_playout)

    def get_move(self, board, color_to_play):
        """
        The genmove function called by gtp_connection
        """
        
        sensible_moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        if len(sensible_moves) > 0:
            start = timer()
            move = self.mcts.get_move(board)
            end = timer()
            self.mcts.update_with_move(-1)
            print("time = ", end-start)
            return move
        else:
            print("WARNING: the board is full")

    def get_best_move_so_far(self):
        return self.mcts.get_best_move_so_far()
        

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(GomokuMCTSPlayer(n_playout=4000), board)
    con.start_connection()

if __name__=='__main__':
    run()
