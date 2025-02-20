from math import inf
from ..engine import get_available_moves, make_move, flip_board


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


