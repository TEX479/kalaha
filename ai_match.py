"""
TODO
- make algorithms time-dependent
- Move-selection: random or deterministic?
- fix `print_results()`
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import os
from typing import Callable, Literal

from engine import INITIAL_BOARD, get_available_moves, make_move, is_game_over

algorithms: dict[str, tuple[Callable[[list[int], bool, int], int]]] = {}
algorithms_names: list[str] = []
def import_algorithms() -> None:
    global algorithms, algorithms_names
    files = os.listdir("algorithms")
    python_files = sorted([file for file in files if file.endswith(".py")])
    import_specs = [importlib.util.spec_from_file_location(file[:-3], f"algorithms/{file}") for file in python_files]
    import_specs = [spec for spec in import_specs if spec != None]
    for spec in import_specs:
        importlib.util.module_from_spec(spec)
        module = importlib.util.module_from_spec(spec)
        if spec.loader == None: continue
        spec.loader.exec_module(module=module)
        if not (hasattr(module, "get_move")): continue
        if not isinstance(module.get_move, Callable): continue
        
        algorithms[spec.name] = (module.get_move, ) # type: ignore
        algorithms_names.append(spec.name)
import_algorithms()


Name = str
SearchDepth = int
class Game:
    def __init__(self,
                 alg1:str, search_depth1:int,
                 alg2:str, search_depth2:int,
                 initial_board:list[int]|None=None, initial_player:Literal["1", "2", True, False]="1") -> None:
        self.alg1 = alg1
        self.alg2 = alg2
        if (algs_missing:=((int(not alg1 in algorithms) << 1) + int(not alg2 in algorithms))) > 0:
            if algs_missing == 0b10:
                raise ValueError(f"Algorithm \"{alg1}\" not present in global \"algorithms\"-dictionary.")
            elif algs_missing == 0b01:
                raise ValueError(f"Algorithms \"{alg2}\" not present in global \"algorithms\"-dictionary.")
            elif algs_missing == 0b11:
                raise ValueError(f"Algorthims \"{alg1}\" and \"{alg2}\" not present in global \"algorithms\"-dictionary.")
        if search_depth1 < 0 or search_depth2 < 0:
            raise ValueError("Search-depths may not be negative.")
        self.search_depth1 = search_depth1
        self.search_depth2 = search_depth2

        self.board: list[int] = INITIAL_BOARD.copy()
        if initial_board != None: self.board = initial_board
        self.player = initial_player in ["1", True]
        self.initial_player = self.player
    
    def run(self) -> Literal[1, 0, -1]:
        while True:
            if is_game_over(self.board): break

            # get algorithm that has to make a move
            alg = self.alg1 if self.player else self.alg2
            search_depth = self.search_depth1 if self.player else self.search_depth2

            selected_move = algorithms[alg][0](self.board.copy(), self.player, search_depth)
            make_move_output = make_move(board=self.board.copy(), move=selected_move)
            if make_move_output == None:
                raise ValueError("Something went wrong while making a move.")
            new_board, move_again = make_move_output
            self.board = new_board.copy()
            self.player = self.player if move_again else not self.player
        
        if self.board[13] > 18:
            return 1
        if self.board[6] > 18:
            return -1
        return 0

def print_results(results: list[list[list[Literal[1, 0, -1]]]]) -> None:
    results_strings: list[list[str]] = []
    results_strings_lengths: list[list[int]] = []
    color_reset = "\033[49m"
    for i1 in range(len(results)):
        results_strings.append([])
        results_strings_lengths.append([])
        for i2 in range(len(results)):
            base_string = f"{results[i1][i2].count(1)}:{results[i1][i2].count(0)}:{results[i1][i2].count(-1)}"
            relative_victories = (results[i1][i2].count(1) - results[i1][i2].count(-1)) / max(1, len(results[i1][i2]))
            relative_victories_int = int(relative_victories * 255)
            if relative_victories_int > 0:
                r = 255 - relative_victories_int
                g = 255
            else:
                r = 255
                g = 255 + relative_victories_int
            b = 0
            color_code = f"\033[48;2;{r};{g};{b}m"
            results_strings[i1].append(f"{color_code}{base_string}{color_reset}")
            results_strings_lengths[i1].append(len(base_string))
    column_lengths: list[int] = []
    for column in range(len(algorithms_names)):
        col_length = max(
            max([results_strings_lengths[row][column] for row in range(len(algorithms_names))]),
            len(algorithms_names[column])
        )
        column_lengths.append(col_length)
    column0_length = max([len(name) for name in algorithms_names])
    print(" " * column0_length + " " + " ".join([f"{algorithms_names[i]: ^{column_lengths[i]}}" for i in range(len(algorithms_names))]))
    for row in range(len(algorithms_names)):
        row_elements = [f"{results_strings[row][column]: ^{column_lengths[column]}}" for column in range(len(algorithms_names))]
        print(f"{algorithms_names[row]: <{column0_length}} " + " ".join(row_elements))

def create_initial_boards(n_boards:int=100) -> list[tuple[list[int], Literal["1", "2", True, False]]]:
    queue: list[tuple[list[int], bool]] = [(INITIAL_BOARD, True)]
    boards: list[tuple[list[int], Literal[True, False, "1", "2"]]] = []
    while True:
        if len(boards) >= n_boards: break
        if len(queue) == 0: break
        board, player = queue.pop(0)
        for move in get_available_moves(board, player):
            make_move_output = make_move(INITIAL_BOARD.copy(), move)
            if make_move_output == None: continue
            board_new, move_again = make_move_output
            player_new = player if move_again else not player
            queue.append((board_new, player_new))
            boards.append((board_new, player_new))
    if len(boards) > n_boards:
        boards = boards[:n_boards]
    return boards

def run_all_matches(depth:int=4, games_ammount:int=100):
    games: list[Game] = []
    #initial_boards: list[tuple[list[int], Literal["1", "2", True, False]]] = [(INITIAL_BOARD, "1")]
    initial_boards = create_initial_boards(games_ammount)
    results: list[list[list[Literal[1, 0, -1]]]] = []
    for i1 in range(len(algorithms)):
        results.append([])
        for i2 in range(len(algorithms)):
            results[i1].append([])
            if i1 == i2: continue
            alg1, alg2 = algorithms_names[i1], algorithms_names[i2]
            for initial_board in initial_boards:
                games.append((Game(alg1, depth, alg2, depth, initial_board[0], initial_board[1])))
    if games == []: return results
    games_done: list[None] = []
    print(f"{len(games_done):0{len(str(len(games)))}}/{len(games)}")
    with ThreadPoolExecutor(4) as executor:
        future_to_game = {executor.submit(game.run): game for game in games}
        for future in as_completed(future_to_game):
            game = future_to_game[future]
            result = future.result()
            results[algorithms_names.index(game.alg1)][algorithms_names.index(game.alg2)].append(result)
            games_done.append(None)
            print(f"{len(games_done):0{len(str(len(games)))}}/{len(games)}")
    
    return results


if __name__ == "__main__":
    results = run_all_matches(depth=8, games_ammount=100)
    """
    results: list[list[list[Literal[1, 0, -1]]]] = [
        [[1], [1,0]],
        [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1,0]]
    ]
    algorithms_names = ["v1", "v2"]
    """
    print_results(results)
