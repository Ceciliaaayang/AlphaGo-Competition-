#!/usr/bin/python3
#/usr/local/bin/python3
from board_util import GoBoardUtil
from gtp_connection import GtpConnection
from simple_board import SimpleGoBoard
from pattern_util import PatternUtil
import numpy as np
import random

def select_best_move(board, moves, moveWins):
    """
    Move select after the search.
    """
    max_child = np.argmax(moveWins)
    return moves[max_child]

class Gomoku3():
    
    def __init__(self, sim=10, sim_rule="random"):
        """
        Gomoku Player that selects moves by simulation.
        """
        self.name = "Gomoku3"
        self.version = 1.0
        self.sim = sim
        self.random_simulation = True if sim_rule == "random" else False
        # self.use_pattern = not self.random_simulation

    def name(self):
        return "{} Player ({} sim.)".format(self.name, self.sim)

    def simulate(self, board, move, to_play):
        """
        Run a simulate game for a given move.
        """
        cboard = board.copy()
        cboard.play_move_gomoku(move, to_play)
        opp = GoBoardUtil.opponent(to_play)
        return PatternUtil.play_game(cboard,
                                    opp,
                                    random_simulation = self.random_simulation)

    def simulate_move(self, board, move, to_play):
        """
        Run simulations for a given move.
        """
        wins = 0
        for i in range(self.sim):
            result = self.simulate(board, move, to_play)
            if result == to_play:
                wins += 1
        return wins

    def select_move(self, board, color, moves):
        """
            select moves by simulations
        """
        color = board.current_player
        cboard = board.copy()
        
        move_wins = []
        for move in moves:
            wins = self.simulate_move(cboard, move, color)
            move_wins.append(wins)
        
        return select_best_move(board, moves, move_wins)

    def get_move(self, board, color):
        """
        Run one-player MC simulations to get a move to play
        """
        color = board.current_player
        cboard = board.copy()
        if self.random_simulation:
            moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        else:
            _, moves = PatternUtil.generate_policy_moves(board)

        #move_wins = []
        #for move in moves:
        #    wins = self.simulate_move(cboard, move, color)
        #    move_wins.append(wins)
        
        #return select_best_move(board, moves, move_wins)
        return random.choice(moves)

def run():
    """
    start the gtp connection and wait for commands
    """
    board = SimpleGoBoard(7)
    con = GtpConnection(Gomoku3(sim=10, sim_rule="rule_based"), board)
    con.start_connection()

if __name__=='__main__':
    run()


        

