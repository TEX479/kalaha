import random
from engine import get_available_moves

def get_move(board:list[int], player:bool, depth_max:int) -> int:
    return random.choice(get_available_moves(board=board.copy(), player=player))