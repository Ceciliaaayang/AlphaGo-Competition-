from simple_board import SimpleGoBoard
import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
    PASS, is_black_white, coord_to_point, where1d, \
    MAXSIZE, NULLPOINT
import gtp_connection
import score

debug = False

def point_to_coord(point, boardsize):
    """
    Transform point given as board array index
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)

# this table is very important!!! 
score_cache = None
score_color = None

def init_score_cache(board: SimpleGoBoard): 
    global score_cache
    # score_cache[color][direction][row][col]
    # this is to store the scores calculated before sometimes we don't compute some directions
    # and score_cache is to store those scores 
    score_cache = {\
        BLACK: (\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)],\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)],\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)],\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)]), 
        
        WHITE: (\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)],\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)],\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)],\
            [[0 for _ in range(board.size + 1)] for _ in range(board.size + 1)])\
        }

    global score_color
    score_color = {BLACK: [[0 for _ in range(board.size+1)] for _ in range(board.size+1)], WHITE: [[0 for _ in range(board.size+1)] for _ in range(board.size+1)]}



def _constrained_index_2d(board, row, col): 
    if row <= 0 or row > board.size or col <= 0 or col > board.size: 
        return BORDER
    p = coord_to_point(row, col, board.size)
    return board.board[p]

def evaluate_point_dir(board: SimpleGoBoard, row, col, color, direction):
    # if debug: 
    #     print(123)
    result = 0
    empty = 0
    count = 0
    block = 0
    second_count = 0

    board_size = board.size

    if direction is None or direction == score.WEST_EAST: 
        count = 1
        block = 0
        empty = -1
        second_count = 0

        i = col
        while 1: 
            i += 1
            if i > board_size: 
                block += 1
                break 
            p = _constrained_index_2d(board, row, i)
            if p == EMPTY: 
                if empty == -1 and i < board_size and _constrained_index_2d(board, row, i+1) == color: 
                    empty = count
                    continue
                else: 
                    break 
            if p == color: 
                count += 1
                continue
            else: 
                block += 1
                break

        i = col
        while 1: 
            i -= 1
            if i <= 0: 
                block += 1
                break
            p = _constrained_index_2d(board, row, i)
            if p == EMPTY: 
                if empty == -1 and i > 1 and _constrained_index_2d(board, row, i-1) == color: 
                    empty = 0
                    continue
                else: 
                    break
            if p == color: 
                second_count += 1
                if empty != -1: 
                    empty += 1
                continue
            else: 
                block += 1
                break


        count += second_count
        score_cache[color][score.WEST_EAST][row][col] = score.count_to_score(count, block, empty)

    # this is very important! remember to add the previously evaluated score!!! 
    result += score_cache[color][score.WEST_EAST][row][col]

    if direction is None or direction == score.NORTH_SOUTH: 
        count = 1
        block = 0
        empty = -1
        second_count = 0

        i = row
        while 1: 
            i += 1
            if i > board_size: 
                block += 1
                break
            p = _constrained_index_2d(board, i, col)
            if p == EMPTY: 
                if empty == -1 and i < board_size and _constrained_index_2d(board, i+1, col) == color: 
                    empty = count
                    continue
                else: 
                    break
            if p == color: 
                count += 1
                continue
            else: 
                block += 1
                break

        i = row
        while 1: 
            i -= 1
            if i <= 0: 
                block += 1
                break
            p = _constrained_index_2d(board, i, col)
            if p == EMPTY: 
                if empty == -1 and i > 1 and _constrained_index_2d(board, i-1, col) == color: 
                    empty = 0
                    continue
                else: 
                    break
            if p == color: 
                second_count += 1
                if empty != -1: 
                    empty += 1
                continue
            else: 
                block += 1
                break 

        count += second_count
        score_cache[color][score.NORTH_SOUTH][row][col] = score.count_to_score(count, block, empty)
    result += score_cache[color][score.NORTH_SOUTH][row][col]

    if direction is None or direction == score.NORTHWEST_SOUTHEAST: 
        # print('NWSE')
        count = 1
        block = 0
        empty = -1
        second_count = 0
        i = 0
        while 1: 
            i += 1
            x = row + i
            y = col + i
            if x > board_size or y > board_size: 
                block += 1
                break
            p = _constrained_index_2d(board, x, y)
            if p == EMPTY: 
                if empty == -1 and (x < board_size and y < board_size) and _constrained_index_2d(board, x+1, y+1) == color: 
                    empty = count 
                    continue
                else: 
                    break
            if p == color: 
                count += 1
                continue
            else: 
                block += 1
                break

        i = 0
        while 1: 
            i += 1
            x = row - i
            y = col - i
            if x <= 0 or y <= 0: 
                block += 1
                break
            p = _constrained_index_2d(board, x, y)
            if p == EMPTY: 
                if empty == -1 and (x > 1 and y > 1) and _constrained_index_2d(board, x-1, y-1) == color: 
                    empty = 0 
                    continue
                else: 
                    break
            if p == color: 
                second_count += 1
                if empty != -1: 
                    empty += 1
                continue
            else: 
                block += 1
                break

        count += second_count
        score_cache[color][score.NORTHWEST_SOUTHEAST][row][col] = score.count_to_score(count, block, empty)
    result += score_cache[color][score.NORTHWEST_SOUTHEAST][row][col]

    if direction is None or direction == score.NORTHEAST_SOUTHWEST: 
        # print('NESW')
        count = 1
        block = 0
        empty = -1
        second_count = 0

        i = 0
        while 1: 
            i += 1
            x = row + i
            y = col - i
            if x <= 0 or y <= 0 or x > board_size or y > board_size: 
                block += 1
                break
            p = _constrained_index_2d(board, x, y)
            if p == EMPTY: 
                if empty == -1 and (x < board_size and y > 1) and _constrained_index_2d(board, x+1, y-1) == color: 
                    empty = count
                    continue
                else: 
                    break
            if p == color: 
                count += 1
                continue
            else: 
                block += 1
                break

        i = 0
        while 1: 
            i += 1
            x = row - i
            y = col + i
            if x <= 0 or y <= 0 or x > board_size or y > board_size: 
                block += 1
                break
            p = _constrained_index_2d(board, x, y)
            if p == EMPTY: 
                if empty == -1 and (x > 1 and y < board_size) and _constrained_index_2d(board, x-1, y+1) == color: 
                    empty = 0
                    continue
                else: 
                    break
            if p == color: 
                second_count += 1
                if empty != -1: 
                    empty += 1
                continue
            else: 
                block += 1
                break
        count += second_count
        score_cache[color][score.NORTHEAST_SOUTHWEST][row][col] = score.count_to_score(count, block, empty)
    result += score_cache[color][score.NORTHEAST_SOUTHWEST][row][col]

    # if debug: 
    #     print(score_cache[color][score.WEST_EAST][row][col],score_cache[color][score.NORTH_SOUTH][row][col],score_cache[color][score.NORTHEAST_SOUTHWEST][row][col],score_cache[color][score.NORTHWEST_SOUTHEAST][row][col])

    return result





def evaluate_board(board: SimpleGoBoard): 
    init_score_cache(board)
    # current_player = board.current_player
    # opponent_player = GoBoardUtil.opponent(current_player)
    for row in range(1, board.size+1): 
        for col in range(1, board.size+1): 
            p = _constrained_index_2d(board, row, col)
            m = coord_to_point(row, col, board.size)
            if p == EMPTY: 
                board.board[m] = WHITE
                score_color[WHITE][row][col] = evaluate_point_dir(board, row, col, WHITE, None)
                board.board[m] = BLACK
                score_color[BLACK][row][col] = evaluate_point_dir(board, row, col, BLACK, None)
                board.board[m] = EMPTY
            elif p == WHITE: 
                score_color[WHITE][row][col] = evaluate_point_dir(board, row, col, WHITE, None)
                score_color[BLACK][row][col] = 0
            elif p == BLACK: 
                score_color[WHITE][row][col] = 0
                score_color[BLACK][row][col] = evaluate_point_dir(board, row, col, BLACK, None)
    return 


def update_dir(board: SimpleGoBoard, row, col, direction): 
    current = _constrained_index_2d(board, row, col)
    m = coord_to_point(row, col, board.size)
    if current == EMPTY: 
        board.board[m] = WHITE
        score_color[WHITE][row][col] = evaluate_point_dir(board, row, col, WHITE, direction)
        board.board[m] = BLACK
        score_color[BLACK][row][col] = evaluate_point_dir(board, row, col, BLACK, direction)
        board.board[m] = EMPTY
    elif current == BLACK or current == WHITE: 
        oppponent = GoBoardUtil.opponent(current)
        score_color[current][row][col] = evaluate_point_dir(board, row, col, current, direction)
        score_color[oppponent][row][col] = 0
    return 
    


def update_board(board: SimpleGoBoard, move): 
    # only update those points that are affected 
    boardsize = board.size
    r = 4
    if move == PASS: 
        return 
    row, col = point_to_coord(move, boardsize)
    for i in range(-r, r+1): 
        x = row
        y = col + i
        if y <= 0: 
            continue
        if y > boardsize: 
            break 
        update_dir(board, x, y, score.WEST_EAST)

    for i in range(-r, r+1): 
        x = row + i
        y = col
        if x <= 0: 
            continue
        if x > boardsize: 
            break 
        update_dir(board, x, y, score.NORTH_SOUTH)

    for i in range(-r, r+1): 
        x = row + i
        y = col + i
        if x <= 0 or y <= 0: 
            continue
        if x > boardsize or y > boardsize: 
            break
        update_dir(board, x, y, score.NORTHWEST_SOUTHEAST)

    for i in range(-r, r+1): 
        x = row + i
        y = col - i
        if x <= 0 or y <= 0: 
            continue
        if x > boardsize or y > boardsize: 
            continue
        update_dir(board, x, y, score.NORTHEAST_SOUTHWEST)

    return 


def gen_possible_moves(board: SimpleGoBoard, color): 
    fives = []
    fours = {BLACK:[], WHITE:[]}
    blocked_fours = {BLACK:[], WHITE:[]}
    two_threes = {BLACK:[], WHITE:[]}
    threes = {BLACK:[], WHITE:[]}
    twos = {BLACK:[], WHITE:[]}
    others = []

    current = color
    opponent = GoBoardUtil.opponent(current)

    empty_points = board.get_empty_points()
    for point in empty_points: 
        row, col = point_to_coord(point, board.size)
        current_score = score_color[current][row][col]
        opponent_score = score_color[opponent][row][col]

        move = coord_to_point(row, col, board.size)

        # always consider current side, then the opposite side 
        if current_score >= score.FIVE: 
            fives.append((move, current_score, opponent_score))
        elif opponent_score >= score.FIVE: 
            fives.append((move, current_score, opponent_score))
        elif current_score >= score.FOUR: 
            fours[current].append((move, current_score, opponent_score))
        elif opponent_score >= score.FOUR: 
            fours[opponent].append((move, current_score, opponent_score))
        elif current_score >= score.BLOCKED_FOUR: 
            blocked_fours[current].append((move, current_score, opponent_score))
        elif opponent_score >= score.BLOCKED_FOUR: 
            blocked_fours[opponent].append((move, current_score, opponent_score))
        elif current_score >= 2 * score.THREE: 
            two_threes[current].append((move, current_score, opponent_score))
        elif opponent_score >= 2 * score.THREE: 
            two_threes[opponent].append((move, current_score, opponent_score))
        elif current_score >= score.THREE: 
            threes[current].append((move, current_score, opponent_score))
        elif opponent_score >= score.THREE: 
            threes[opponent].append((move, current_score, opponent_score))
        elif current_score >= score.TWO: 
            twos[current] = [(move, current_score, opponent_score)] + twos[current]
        elif opponent_score >= score.TWO: 
            twos[opponent] = [(move, current_score, opponent_score)] + twos[opponent]
        else: 
            others.append((move, current_score, opponent_score))



    # if debug: 
    #     print('fives:', fives)
    #     print('current fours:', fours[current])
    #     print('current blocked fours:', blocked_fours[current])
    #     print('current two threes:', two_threes[current])
    #     print('current threes:', threes[current])
                
    if len(fives) > 0: 
        # form our fives or block other's fives 
        return fives 
    
    if len(fours[current]) > 0:
        # form our fours  
        return fours[current]

    if len(fours[opponent]) > 0 and len(blocked_fours[current]) <= 0: 
        # other has fours, but we don't even have blocked four
        return fours[opponent]

    # others have fours, but we have blocked fours, then we can take those blocked fours
    total_fours = fours[current] + fours[opponent]
    total_blocked_fours = blocked_fours[current] + blocked_fours[opponent]
    if len(total_fours) > 0: 
        return total_fours + total_blocked_fours

    # two threes, either block or form
    result = two_threes[current] + two_threes[opponent] + blocked_fours[current] + blocked_fours[opponent] + threes[current] + threes[opponent]
    if len(two_threes[current]) > 0 or len(two_threes[opponent]) > 0:
        return result

    # twos, not very useful...
    total_twos = twos[current] + twos[opponent]
    # total_twos.sort(key=lambda t: max(t[1],t[2]), reverse=True)
    total_twos.sort(reverse=True)
    if len(total_twos) > 0: 
        result += total_twos
    else: 
        result += others
    # remember to add other points

    return result[:20]


def adjust_score(s: int) -> int: 
    """
    adjust the score between blocked four and open three, 
    because they are not that significant if appear alone
    """
    # blocked four < blocked four + three < blocked four * 2 < four
    if (score.BLOCKED_FOUR <= s and s < score.FOUR): 
        if (s < score.BLOCKED_FOUR + score.THREE): 
            # single blocked four
            return score.THREE
        elif (s < score.BLOCKED_FOUR * 2): 
            # blocked four + open three, we win
            return score.FOUR
        else: 
            # double blocked four, we win, but it's more significant 
            return score.FOUR * 2
    return s


def point_estimation(board: SimpleGoBoard, color: int) -> int: 
    """
    a point estimation at search limit
    """
    current_score = 0
    opponent_score = 0
    opponent_color = GoBoardUtil.opponent(color)
    for row in range(1, board.size+1): 
        for col in range(1, board.size+1): 
            c = _constrained_index_2d(board, row, col)
            if c == color: 
                current_score += adjust_score(score_color[color][row][col])
            elif c == opponent_color: 
                opponent_score += adjust_score(score_color[opponent_color][row][col])
    return current_score - opponent_score
    
                
                
                


    
                


        


        

            
