#!/usr/bin/python3
'''
for every part of this program:
"player" is a bool. if it is false, it is the player's turn, else the opponents's
the "board" is a list of 14 ints going in the following order (with the player being the bottom holes and the game bein played clockwise)
  07 08 09 10 11 12
06                 13
  05 04 03 02 01 00

TODO:
add move-ordering so alpha beta pruning is more optimal
'''
from math import inf
from random import choice
from time import time

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
    if board[move] <= 0: return None
    amount = board[move]
    board_ret[move] = 0
    i = 0
    index = 0
    enemies_safe = 6 if move < 6 else 13
    while amount > 0:
        i += 1
        if ((move + i) % 14) == enemies_safe: i += 1
        index = (move + i) % 14
        board_ret[index] += 1
        amount -= 1
    move_again = (index) == (enemies_safe - 7) % 14
    final_hole = (index) % 14
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
    return board_ret, move_again

def eval_board(board:list[int]) -> float:
    board_local = board.copy()
    score = 0
    if sum(board_local[0:6]) == 0:
        board_local[6] = sum(board_local[7:13])
        for i in range(7, 13):
            board_local[i] = 0
    elif sum(board_local[7:13]) == 0:
        board_local[13] = sum(board_local[0:6])
        for i in range(6):
            board_local[i] = 0
    else:
        majority_score = sum(board_local[:6]) - sum(board_local[7:13])
        score += majority_score / 2
    score -= board_local[6]
    score += board_local[13]
    
    if board_local[6 ] > 18: score -= inf
    if board_local[13] > 18: score += inf
    return score

def get_available_moves(board:list[int], player:bool) -> list[int]:
    '''
    returns a list of indices that may be moved / a list of moves
    '''
    if player:
        return [i for i in range(6) if board[i] > 0]
    else:
        return [i for i in range(7, 13) if board[i] > 0]

def recursive_step(board:list[int], player:bool, depth:int, depth_max:int, alpha:float, beta:float) -> float:
    '''
    RENAME;
    '''
    #print(f"current_depth: \t{depth}")
    if depth >= depth_max: return eval_board(board=board.copy())
    
    moves_available = get_available_moves(board=board, player=player)
    if moves_available == []: return eval_board(board.copy())
    value = -inf if player else inf

    for move_next in moves_available:
        _make_move_output = make_move(board=board.copy(), move=move_next)
        if _make_move_output == None: continue
        board_new, move_again = _make_move_output
        player_new = player if move_again else not player
        cost_new = recursive_step(board=board_new, player=player_new, depth=depth+1, depth_max=depth_max, alpha=alpha, beta=beta)
        if player:
            value = max(value, cost_new)
            alpha = max(alpha, value)
        else:
            value = min(value, cost_new)
            beta  = min(beta, value)
        if beta <= alpha: break
        if player and (cost_new == inf): return inf
        elif not player and (cost_new == -inf): return -inf
    return value

def eval_moves(board:list[int], depth_max:int, player:bool) -> dict[int, float]:
    player_passed_to_function = player
    if not player:
        board = flip_board(board=board)
        player = True
    moves_available = get_available_moves(board=board.copy(), player=player)
    output: dict[int, float] = {}
    for move_chosen in moves_available:
        _make_move_output = make_move(board=board.copy(), move=move_chosen)
        if _make_move_output == None: raise ValueError("fuck off, this is not a thing")
        board_instance, move_again = _make_move_output
        player_instance = player if move_again else not player
        output[(7 * int(not player_passed_to_function)) + move_chosen] = recursive_step(board=board_instance.copy(), player=player_instance, depth=1, depth_max=depth_max, alpha=-inf, beta=+inf)
    return output

def get_player_move(available_moves:list[int]) -> int:
    while True:
        user_input = input(f"What piece do you want to play? {available_moves}: ")
        if not user_input.isdecimal(): continue
        chosen_move = int(user_input)
        if not chosen_move in available_moves: continue

        return chosen_move

def game() -> None:
    board = [3 if not (i % 7) == 6 else 0 for i in range(14)]
    depth_max = 4

    player: bool|None = None
    while True:
        user_input = input("Who goes first? ([P]layer|[C]omputer): ").lower()
        if user_input == "p":
            player = True
            break
        elif user_input == "c":
            player = False
            break
        else:
            print("invalid input.")
            continue
    
    while True:
        print_board(board=board)
        if player:
            move = get_player_move(get_available_moves(board=board.copy(), player=True))
        else:
            move_list = eval_moves(board=board.copy(), depth_max=depth_max, player=False)
            best_cost = max([move_list[i] for i in move_list])
            best_moves = [i for i in move_list if move_list[i] == best_cost]
            move = choice(best_moves)
            print(f"pc chooses to play {move} from {move_list=}")
        _make_move_output = make_move(board=board, move=move)
        if _make_move_output == None: raise ValueError(f"idk, this feels like it should not happen. not like i haven't put a million checks into this code already")
        board, move_again = _make_move_output
        if not move_again: player = not player


if __name__ == "__main__":
    #'''
    board = INITIAL_BOARD
    #board = [1,0,3,6,1,6,0,
    #         2,0,7,0,5,5,0]
    search_depth = 8
    player = True
    
    start = time()
    moves = eval_moves(board=board.copy(), depth_max=search_depth, player=player)
    stop = time()
    
    print(f"executed in {stop - start}")

    print(f"SOLUTIONS:")
    for move in moves:
        print(f"{move}:\t{moves[move]}")
    '''
    game()
    ''#'
    #board = [1,1,0,1,0,0,17,6,3,0,0,1,0,16]
    board = [2,1,0,1,0,0,17,0,4,1,1,2,1,16]
    search_depth = 1
    player = True
    moves = eval_moves(board=board, depth_max=search_depth, player=player)
    print(f"SOLUTIONS:")
    for move in moves:
        print(f"{move}:\t{moves[move]}")
    '''
