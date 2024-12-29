'''
for every part of this program:
"player" is a bool. if it is false, it is the player's turn, else the opponents's
the "board" is a list of 14 ints going in the following order (with the player being the bottom holes and the game bein played clockwise)
  07 08 09 10 11 12
06                 13
  05 04 03 02 01 00

TODO:
in recursive step: return cost, if no moves are availible
'''
from math import inf

def make_move(board:list[int], move:int) -> tuple[list[int], bool] | None:
    board_ret = board.copy()
    #if not (0 <= move <= 5): return None
    if board[move] <= 0: return None
    amount = board[move]
    board_ret[move] = 0
    i = 0
    enemies_safe = 6 if move < 6 else 13
    while amount > 0:
        i += 1
        if ((move + i) % 14) == enemies_safe: i += 1
        board_ret[(move + i) % 14] += 1
        amount -= 1
    move_again = ((move + i) % 14) == (enemies_safe - 7) % 14
    final_hole = (move + i) % 14
    if enemies_safe == 6:
        if final_hole < 6 and board_ret[final_hole] == 1:
            hole_mirrored = 13 - final_hole
            board_ret[13] += 1 + board_ret[hole_mirrored]
            board_ret[final_hole] = 0
            board_ret[hole_mirrored] = 0
    else:
        if final_hole > 6 and board_ret[final_hole] == 1:
            hole_mirrored = 13 - final_hole
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
        majority_score = sum(board[:6]) - sum(board[7:13])
        score += majority_score / 2
    score -= board_local[6]
    score += board_local[13]
    
    if board_local[6] > 18: score -= inf
    if board_local[13] > 18: score += inf
    return score

def get_availible_moves(board:list[int], player:bool) -> list[int]:
    '''
    returns a list of indices that may be moved / a list of moves
    '''
    if player:
        return [i for i in range(6) if board[i] > 0]
    else:
        return [i for i in range(7, 13) if board[i] > 0]

def recursive_step(board:list[int], moves:list[int], player:bool, depth:int, depth_max:int) -> float:
    '''
    RENAME;
    '''
    #print(f"current_depth: \t{depth}")
    if depth == depth_max: return eval_board(board=board.copy())
    
    moves_availible = get_availible_moves(board=board, player=player)
    if moves_availible == []: return eval_board(board.copy())
    minimax = max if player else min

    costs_next_branch: list[float] = []
    for move_next in moves_availible:
        _make_move_output = make_move(board=board.copy(), move=move_next)
        if _make_move_output == None: continue
        board_new, move_again = _make_move_output
        moves_new = moves + [move_next]
        player_new = player if move_again else not player
        cost_new = recursive_step(board=board_new, moves=moves_new, player=player_new, depth=depth+1, depth_max=depth_max)
        if player and (cost_new == inf): return inf
        elif not player and (cost_new == -inf): return -inf
        costs_next_branch.append(cost_new)
    return minimax(costs_next_branch)

def find_moves(board:list[int], search_depth:int, player:bool) -> dict[int, float]:
    moves_availible = get_availible_moves(board=board.copy(), player=player)
    output: dict[int, float] = {}
    for move_availible in moves_availible:
        output[move_availible] = recursive_step(board=board.copy(), moves=[move_availible], player=player, depth=0, depth_max=search_depth)
    return output

if __name__ == "__main__":
    board = [3 if not (i % 7) == 6 else 0 for i in range(14)]
    search_depth = 8
    player = True

    moves = find_moves(board=board.copy(), search_depth=search_depth, player=player)

    print(f"SOLUTIONS:")
    for move in moves:
        print(f"{move}:\t{moves[move]}")
