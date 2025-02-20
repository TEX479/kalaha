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
from random import choice
from time import time
from engine import print_board, get_available_moves, make_move, INITIAL_BOARD
from algorithms.v1 import eval_moves


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
