'''
TODO:
make search account for being allowed to move again
do not generate gametree, instead do search recursively
'''

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
    
    score -= board_local[6]
    score += board_local[13]
    
    if board_local[6] >= 18: score -= 100
    if board_local[13] > 18: score += 100
    return score

def _move_sequence_to_index(move_costs:list[tuple[list[int], float]], move_sequence:list[int], only_next:bool=False) -> list[int]:
    indices = []
    for i in range(len(move_costs)):
        ms, _ = move_costs[i]
        if len(ms) <= len(move_sequence): continue
        if only_next and (len(ms) + 1 != len(move_sequence)): continue
        if ms[:len(move_sequence)] == move_sequence:
            indices.append(i)
    #print(f"{move_costs=}")
    print(f"{move_sequence=}")
    print(f"{indices=}")
    return indices

def aggregate_cost(move_costs:list[tuple[list[int], float]], move_sequence:list[int], is_maximizing:bool) -> float:
    for moves_made, move_cost in move_costs:
        if moves_made == move_sequence:
            return move_cost
    minimax = max if is_maximizing else min
    costs_this_level = []
    for i in _move_sequence_to_index(move_costs, move_sequence, True):
        costs_this_level.append(aggregate_cost(move_costs, move_costs[i][0], not is_maximizing))
    return minimax(costs_this_level)

def find_move(initial_board:list[int], search_depth:int) -> dict[int, float]:
    queue: list[tuple[list[int], list[int], float]] = [([i], board:=make_move(initial_board, i)[0], eval_board(board)) for i in range(6) if initial_board[i] > 0]
    for depth_level in range(1, search_depth):
        print(f"creating gametree with {depth_level=}\tand {len(queue)=}")
        queue_new = []
        for element in queue:
            moves, board, cost_current = element
            move_range = range(6) if depth_level % 2 == 0 else range(7, 12)
            moves_new = [moves + [i] for i in move_range if board[i] > 0]
            for move_sequence_new in moves_new:
                board_new = make_move(board, move_sequence_new[-1])[0]
                cost_new = eval_board(board_new)
                queue_new.append((move_sequence_new, board_new, cost_new))
        queue = queue_new.copy()
    print("aggregating costs")
    move_costs: list[tuple[list[int], float]] = [(moves, cost) for moves, _, cost in queue]
    output = {i: aggregate_cost(move_costs, [i], True) for i in range(6) if board[i] > 0}
    return output

if __name__ == "__main__":
    board = [3 if i % 7 != 6 else 0 for i in range(14)]
    search_depth = 8
    
    evaluations = find_move(board, search_depth)
    
    print(evaluations)
