from simple_board import SimpleGoBoard
import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
    PASS, is_black_white, coord_to_point, where1d, \
    MAXSIZE, NULLPOINT
import gtp_connection
from evaluate import gen_possible_moves, evaluate_board, update_board, debug, point_estimation
import score

best_move = PASS

def print_board(board):
    size = board.size
    str = ''
    for row in range(size-1, -1, -1):
        start = board.row_start(row + 1)
        for i in range(size):
            point = board.board[start + i]
            if point == BLACK:
                str += 'X'
            elif point == WHITE:
                str += 'O'
            elif point == EMPTY:
                str += '.'
            else:
                assert False
        str += '\n'
    print(str)

def print_moves(moves,boardsize): 
    for m in moves: 
        print('(', gtp_connection.format_point(gtp_connection.point_to_coord(m[0],boardsize)),m[1], m[2], end=' ), ')
    print()




def boolean_negamax(board: SimpleGoBoard, last_move: int, current_color: int) -> ('result', 'move'):
    if debug: 
        print_board(board)
    if last_move is None: 
        evaluate_board(board)

    if last_move is not None and check_winning_condition(board, last_move, board.board[last_move]):
        # print('game ends')
        return -1, None

    opponent_color = GoBoardUtil.opponent(current_color)
    moves = gen_possible_moves(board, current_color)
    if len(moves) == 0:
        return 0, None

    best_result = -1
    best_move = moves[0][0]
    if debug:
        print_moves(moves, board.size)

    for m in moves:
        move = m[0]
        board.board[move] = current_color
        update_board(board, move)
        # print('play', gtp_connection.point_to_str(move, board.size))
        result, _ = boolean_negamax(board, move, opponent_color)
        result = -result
        board.board[move] = EMPTY
        update_board(board, move)
        if result > 0:
            # print("win")
            return 1, move
        if result > best_result:
            best_result = result
            best_move = move

    return best_result, best_move


def alphabeta_search(
    board: SimpleGoBoard, 
    last_move: int, 
    current_color: int, 
    depth: int, 
    alpha: int, beta: int) -> int:
    # if last_move is None:
    #     evaluate_board(board)
    # last_move is not None
    if check_winning_condition(board, last_move, board.board[last_move]):
        return -10 * score.FIVE

    if depth <= 0:
        return point_estimation(board, current_color)
    opponent_color = GoBoardUtil.opponent(current_color)
    moves = gen_possible_moves(board, current_color)
    if len(moves) == 0:
        return 0
    depth -= min(10, len(moves))

    if debug:
        print_moves(moves, board.size)

    for m in moves:
        move = m[0]
        board.board[move] = current_color
        update_board(board, move)
        result = -alphabeta_search(board, move, opponent_color, depth, -beta, -alpha)
        board.board[move] = EMPTY
        update_board(board, move)
        if result > alpha:
            alpha = result
        if result >= beta:
            return beta
        
    return alpha


def solve_alphabeta(board: SimpleGoBoard, color: int, board_is_evaluated=False):
    result, winner = board.check_game_end_gomoku()
    if result: 
        if winner == color:
            return 10*score.FIVE, None
        else: 
            return -10*score.FIVE, None
    # print('ok')
    alpha, beta = -10*score.FIVE, 10*score.FIVE
    if not board_is_evaluated:
        evaluate_board(board)
    moves = gen_possible_moves(board, color)
    print(list(map(lambda t: (t[0], gtp_connection.format_point(
        gtp_connection.point_to_coord(t[0], board.size)), t[1], t[2]), moves)))
    if len(moves) == 0: 
        return 0, None
    if (gtp_connection.total_steps == 0 or gtp_connection.total_steps == 1) and board.board[36] == EMPTY: 
        return 1, 36

    # best_move = None
    global best_move
    best_move = PASS
    for m in moves:
        move = m[0]

        # move_coord = gtp_connection.point_to_coord(move, board.size)
        # move_as_string = gtp_connection.format_point(move_coord)
        
        board.board[move] = color
        update_board(board, move)
        result = -alphabeta_search(board, move, GoBoardUtil.opponent(color), 40, -beta, -alpha)
        # print("trying move:", move_as_string, "score:", result)

        board.board[move] = EMPTY
        update_board(board, move)
        if result > alpha: 
            alpha = result
            best_move = move
        if result >= beta: 
            return beta, move
    return alpha, best_move




def check_winning_condition(_board: SimpleGoBoard, point: int, color: int) -> bool:
    """
    checks the winning condition of color, centered on point
    """

    consecutive_occurrence = 0
    # check horizontal: west to east
    for i in range(0, 9):
        if _constrained_index(_board, point - 4 + i) == color:
            consecutive_occurrence += 1
            if consecutive_occurrence >= 5:
                return True
        else:
            consecutive_occurrence = 0


    consecutive_occurrence = 0
    # check vertical: south to north
    for i in range(0, 9):
        if _constrained_index(_board, point + (-4 + i) * _board.NS) == color:
            consecutive_occurrence += 1
            if consecutive_occurrence >= 5:
                return True
        else:
            consecutive_occurrence = 0


    consecutive_occurrence = 0
    # check diagonal: southwest to northeast
    for i in range(0, 9):
        if _constrained_index(_board, point + (-4 + i) * _board.NS - 4 + i) == color:
            consecutive_occurrence += 1
            if consecutive_occurrence >= 5:
                return True
        else:
            consecutive_occurrence = 0


    consecutive_occurrence = 0
    # check diagonal: southeast to northwest
    for i in range(0, 9):
        if _constrained_index(_board, point + (-4 + i) * _board.NS + 4 - i) == color:
            consecutive_occurrence += 1
            if consecutive_occurrence >= 5:
                return True
        else:
            consecutive_occurrence = 0

    return False


def _constrained_index(_board: SimpleGoBoard, point: int) -> int:
    """
    if point lies on the board, return the corresponding color, otherwise return BORDER
    """
    return BORDER if (point < 0 or point >= _board.maxpoint) else _board.board[point]
