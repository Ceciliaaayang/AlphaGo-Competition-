ONE = 10
TWO = 100
THREE = 1000
FOUR = 100000
FIVE = 10000000

BLOCKED_ONE = 1
BLOCKED_TWO = 10
BLOCKED_THREE = 100
BLOCKED_FOUR = 10000

WEST_EAST = 0
NORTH_SOUTH = 1
NORTHWEST_SOUTHEAST = 2
NORTHEAST_SOUTHWEST = 3

def count_to_score(count, block, empty): 
    
    # print(count, block, empty)
    if empty is None: 
        empty = 0
    
    # no empty point 
    if empty <= 0: 
        if count >= 5: 
            return FIVE
        if block == 0: 
            if count == 1: 
                return ONE
            elif count == 2: 
                return TWO
            elif count == 3: 
                return THREE
            elif count == 4: 
                return FOUR

        if block == 1: 
            if count == 1: 
                return BLOCKED_ONE
            elif count == 2: 
                return BLOCKED_TWO
            elif count == 3: 
                return BLOCKED_THREE
            elif count == 4: 
                return BLOCKED_FOUR
    # first position is empty 
    elif empty == 1 or empty == count - 1: 
        if count >= 6: 
            return FIVE
        if block == 0: 
            if count == 2: 
                return TWO // 2
            elif count == 3: 
                return THREE
            elif count == 4: 
                return BLOCKED_FOUR
            elif count == 5: 
                return FOUR
        if block == 1: 
            if count == 2: 
                return BLOCKED_TWO
            elif count == 3: 
                return BLOCKED_THREE
            elif count == 4 or count == 5: 
                return BLOCKED_FOUR

    elif empty == 2 or empty == count - 2: 
        if count >= 7: 
            return FIVE
        if block == 0: 
            if count == 3: 
                return THREE
            elif count == 4 or count == 5: 
                return BLOCKED_FOUR
            elif count == 6: 
                return FOUR

        if block == 1: 
            if count == 3: 
                return BLOCKED_THREE
            elif count == 4: 
                return BLOCKED_FOUR
            elif count == 5: 
                return BLOCKED_FOUR
            elif count == 6: 
                return FOUR

        if block == 2: 
            if count == 4 or count == 5 or count == 6: 
                return BLOCKED_FOUR

    elif empty == 3 or empty == count - 3: 
        if count >= 8: 
            return FIVE
        if block == 0: 
            if count == 4 or count == 5: 
                return THREE
            elif count == 6: 
                return BLOCKED_FOUR
            elif count == 7: 
                return FOUR 

        if block == 1: 
            if count == 4 or count == 5 or count == 6: 
                return BLOCKED_FOUR
            elif count == 7: 
                return FOUR

        if block == 2: 
            if count == 4 or count == 5 or count == 6 or count == 7: 
                return BLOCKED_FOUR

    elif empty == 4 or empty == count - 4: 
        if count >= 9: 
            return FIVE
        if block == 0: 
            if count == 5 or count == 6 or count == 7 or count == 8: 
                return FOUR

            if block == 1: 
                if count == 4 or count == 5 or count == 6 or count == 7: 
                    return BLOCKED_FOUR
                elif count == 8: 
                    return FOUR

            if block == 2: 
                if count == 5 or count == 6 or count == 7 or count == 8: 
                    return BLOCKED_FOUR

    elif empty == 5 or empty == count - 5: 
        return FIVE
    
    return 0

