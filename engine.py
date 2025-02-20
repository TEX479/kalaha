INITIAL_BOARD: list[int] = [3 if not (i % 7) == 6 else 0 for i in range(14)]

def is_game_over(board:list[int]) -> bool:
    return (board[6] > 18 or board[13] > 18 or board[6] == board[13] == 18)

def flip_board(board:list[int]) -> list[int]:
    return board[7:14] + board[0:7]

def print_board(board:list[int]) -> None:
    message = "  " + " ".join([f"{board[i]:02}" for i in range(7, 13)])
    message += "\n"
    message += f"{board[6]:02}                 {board[13]:02}"
    message += "\n"
    message += "  " + " ".join([f"{board[i]:02}" for i in range(5, -1, -1)])
    print(message)

def make_move(board:list[int], move:int) -> tuple[list[int], bool] | None:
    board_ret = board.copy()
    if board_ret[move] <= 0: return None
    amount = board_ret[move]
    board_ret[move] = 0
    i = 0
    board_index = 0
    enemies_safe = 6 if move < 6 else 13
    while amount > 0:
        i += 1
        if ((move + i) % 14) == enemies_safe: i += 1
        board_index = (move + i) % 14
        board_ret[board_index] += 1
        amount -= 1
    move_again = (board_index) == (enemies_safe - 7) % 14
    final_hole = (board_index) % 14
    if enemies_safe == 6:
        if final_hole < 6 and board_ret[final_hole] == 1:
            hole_mirrored = 12 - final_hole
            if board_ret[hole_mirrored] > 0:
                board_ret[13] += 1 + board_ret[hole_mirrored]
                board_ret[final_hole] = 0
                board_ret[hole_mirrored] = 0
    else:
        if final_hole > 6 and board_ret[final_hole] == 1:
            hole_mirrored = 12 - final_hole
            if board_ret[hole_mirrored] > 0:
                board_ret[6] += 1 + board_ret[hole_mirrored]
                board_ret[final_hole] = 0
                board_ret[hole_mirrored] = 0
    
    if sum(board_ret[:6]) == 0:
        board_ret[6] += sum(board_ret[7:13])
        board_ret = [board_ret[i] if i in [6, 13] else 0 for i in range(14)]
    elif sum(board_ret[7:13]) == 0:
        board_ret[13] += sum(board_ret[:6])
        board_ret = [board_ret[i] if i in [6, 13] else 0 for i in range(14)]

    return board_ret, move_again

def get_available_moves(board:list[int], player:bool) -> list[int]:
    '''
    returns a list of indices that may be moved / a list of moves
    '''
    if player:
        return [i for i in range(6) if board[i] > 0]
    else:
        return [i for i in range(7, 13) if board[i] > 0]

