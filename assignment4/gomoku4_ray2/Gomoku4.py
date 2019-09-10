#!/Users/mac/anaconda/bin/python3
#/home/tongtong/anaconda2/envs/py36/bin/python
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, EMPTY
from simple_board import SimpleGoBoard

import random
import numpy as np
import math

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

class GomokuSimulationPlayer(object):
    """
    For each move do `n_simualtions_per_move` playouts,
    then select the one with best win-rate.
    playout could be either random or rule_based (i.e., uses pre-defined patterns) 
    """
    def __init__(self, n_simualtions_per_move=10, playout_policy='random', board_size=7):
        assert(playout_policy in ['random', 'rule_based'])
        self.n_simualtions_per_move=n_simualtions_per_move
        self.board_size=board_size
        self.playout_policy=playout_policy

        #NOTE: pattern has preference, later pattern is ignored if an earlier pattern is found
        self.pattern_list=['Win', 'BlockWin', 'OpenFour', 'BlockOpenFour', 'Random']

        self.name="Gomoku3"
        self.version = 3.0
        self.best_move=None
        self.POS = self._POS()


    def _POS(self):
        POS = []
        for i in range(7):
            row = []
            for j in range(7):
                row.append( 3 - max(abs(i - 3), abs(j - 3)) )
            # row = [ (3 - max(abs(i - 3), abs(j - 3))) for j in range(7) ]
            POS.append(tuple(row))
        return POS
    
    def set_playout_policy(self, playout_policy='random'):
        assert(playout_policy in ['random', 'rule_based'])
        self.playout_policy=playout_policy

    def _random_moves(self, board, color_to_play):
        return GoBoardUtil.generate_legal_moves_gomoku(board)
    
    def policy_moves(self, board, color_to_play):
        if(self.playout_policy=='random'):
            return "Random", self._random_moves(board, color_to_play)
        else:
            assert(self.playout_policy=='rule_based')
            assert(isinstance(board, SimpleGoBoard))
            ret=board.get_pattern_moves()
            if ret is None:
                return "Random", self._random_moves(board, color_to_play)
            movetype_id, moves=ret
            return self.pattern_list[movetype_id], moves
    
    def _do_playout(self, board, color_to_play):
        res=game_result(board)
        simulation_moves=[]
        while(res is None):
            _ , candidate_moves = self.policy_moves(board, board.current_player)
            playout_move=random.choice(candidate_moves)
            play_move(board, playout_move, board.current_player)
            simulation_moves.append(playout_move)
            res=game_result(board)
        for m in simulation_moves[::-1]:
            undo(board, m)
        if res == color_to_play:
            return 1.0
        elif res == 'draw':
            return 0.0
        else:
            assert(res == GoBoardUtil.opponent(color_to_play))
            return -1.0

    def convert_moves(self, moves, board):
        result = []
        POSES = self.POS
        # from point to 2D
        for move in moves:
            i, j = board._point_to_2d_coord(move)
            # print(POSES)
            score = POSES[i][j]
            result.append((score, i, j))
        return result

    def get_move(self, board, color_to_play):
        """
        The genmove function called by gtp_connection
        """
        ret = board.get_pattern_moves()
        # print(color_to_play)
        # print(ret)
        if ret is None:
            _, row, col = board.board_searcher.search(
                board=board.twoDBoard,
                turn=color_to_play, 
                pattern_moves=[], 
                depth=board.maxdepth)
        else:
            _, moves = ret
            # print("moves,", moves)
            # print("test----------")
            moves = self.convert_moves(moves, board)
            # print(moves, 'aa')
            _, row, col = board.board_searcher.search(
                board=board.twoDBoard,
                turn=color_to_play, 
                pattern_moves=moves, 
                depth=board.maxdepth)
             
        # print("generated row = {}, col = {}".format(row, col))
        return board.twoD_coord_to_point(row, col)

    def get_pattern_move_by_signal(self, board, color_to_play):
        ## RAY's before Apr.6, 2019 ######
        # ret = board.get_pattern_moves()
        # if ret is None:
        #     return GoBoardUtil.generate_random_move_gomoku(board)
        # movetype_id, moves = ret
        # move = random.choice(moves)
        # return move
        ##################################

        ## RAY's after Apr.6 2019 ########
        ret = board.get_pattern_moves()
        if ret is None:
            moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        else:
            movetype_id, moves = ret

        best_move = moves[0]
        best_score = -math.inf
        # print(moves)

        for move in moves:
            board.play_move_gomoku(move, color_to_play)
            score = board.board_searcher.evaluator.evaluate(board.twoDBoard, color_to_play)

            if score > best_score:
                best_score = score
                best_move = move

            board.undo_move_gomoku()
        return best_move
        ###################################


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(GomokuSimulationPlayer(), board)
    con.start_connection()

if __name__=='__main__':
    run()
