from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, PASS, \
                       MAXSIZE, coord_to_point
import random

class PatternUtil():

    @staticmethod
    def play_game(board, color, **kwargs):
        """
        Run a simluation game according to give parameters
        """
        random_simulation = kwargs.pop('random_simulation', True)
        # use_pattern = kwargs.pop('use_pattern', False)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        while(True):
            if random_simulation:
                move = GoBoardUtil.generate_random_move_gomoku(board)   
            else:
                move = PatternUtil.generate_policy_move_gomoku(board)

            if move == PASS:
                return None
            
            board.play_move_gomoku(move, board.current_player)
            has_winner, winner = board.check_game_end_gomoku()
            if has_winner == True:
                return winner

    
    @staticmethod
    def generate_policy_move_gomoku(board):
        if len(GoBoardUtil.generate_legal_moves_gomoku(board)) == 0:
            return PASS
        
        _, moves = PatternUtil.generate_policy_moves(board)
        return random.choice(moves)


    @staticmethod
    def check_win_policy(board, color, point):
        board.play_move_gomoku(point, color)
        has_winner, winner = board.check_game_end_gomoku()
        board.undo_move_gomoku(point)
        if has_winner and winner == color:
            return True
        else:
            return False

    @staticmethod
    def check_block_win_policy(board, color, point):
        opp_color = GoBoardUtil.opponent(color)
        board.play_move_gomoku(point, opp_color)
        has_winner, winner = board.check_game_end_gomoku()
        board.undo_move_gomoku(point)
        if has_winner and winner == opp_color:
            return True
        else:
            return False

    @staticmethod
    def check_open_four_policy(board, color, point):
        board.play_move_gomoku(point, color)
        is_exist = board.check_game_open_four_by_color(color)
        board.undo_move_gomoku(point)
        return is_exist

    @staticmethod
    def check_block_open_four_policy(board, color, point):
        opp_color = GoBoardUtil.opponent(color)

        # check three inline first
        if board.check_game_three_inline_by_color(opp_color) == False:
            return False

        board.play_move_gomoku(point, color)
        is_exist = True
        rest_points = GoBoardUtil.generate_legal_moves_gomoku(board)
        for p in rest_points:
            board.play_move_gomoku(p, opp_color)
            if board.check_game_open_four_by_color(opp_color) == True:
                is_exist = False
                board.undo_move_gomoku(p)
                break
            board.undo_move_gomoku(p)
        board.undo_move_gomoku(point)
        return is_exist

    @staticmethod
    def get_block_open_four_points(board, color):
        opp_color = GoBoardUtil.opponent(color)

        is_exist, points = board.get_points_open_block_four_by_color(opp_color)
        if is_exist:
            return points
        else:
            return None

    @staticmethod
    def generate_policy_moves(board):
        """
        Generate move by rules
        """
        color = board.current_player
        rule_result_dict = {
            "Win": [],
            "BlockWin": [],
            "OpenFour": [],
            "BlockOpenFour": [],
        }
        # get the legal moves
        moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        rules_dict = {
            "Win": PatternUtil.check_win_policy, 
            "BlockWin": PatternUtil.check_block_win_policy, 
            "OpenFour": PatternUtil.check_open_four_policy,
            "BlockOpenFour": PatternUtil.check_block_open_four_policy
        }

        divide_line = 5
        for move in moves:
            # check win
            if PatternUtil.check_win_policy(board, color, move):
                rule_result_dict["Win"].append(move)
                divide_line = 1
                continue

            # check blockwin
            if divide_line < 2:
                continue
            if PatternUtil.check_block_win_policy(board, color, move):
                rule_result_dict["BlockWin"].append(move)
                divide_line = 2
                continue

            # check OpenFour
            if divide_line < 3:
                continue
            if PatternUtil.check_open_four_policy(board, color, move):
                rule_result_dict["OpenFour"].append(move)
                divide_line = 3
                continue

            # # check BlockOpneFour
            # if divide_line < 4:
            #     continue
            # if PatternUtil.check_block_open_four_policy(board, color, move):
            #     rule_result_dict["BlockOpenFour"].append(move)
            #     divide_line = 4
            #     continue
            
        if len(rule_result_dict["Win"]) > 0:
            return "Win", rule_result_dict["Win"]
        if len(rule_result_dict["BlockWin"]) > 0:
            return "BlockWin", rule_result_dict["BlockWin"]
        if len(rule_result_dict["OpenFour"]) > 0:
            return "OpenFour", rule_result_dict["OpenFour"]

        # check BlockOpenFour
        block_open_four_points = PatternUtil.get_block_open_four_points(board, color)
        if block_open_four_points:
            rule_result_dict["BlockOpenFour"] = block_open_four_points
        
        if len(rule_result_dict["BlockOpenFour"]) > 0:
            return "BlockOpenFour", rule_result_dict["BlockOpenFour"]
        else:
            move = GoBoardUtil.generate_legal_moves_gomoku(board)
            return "Random", move  

            
                       

