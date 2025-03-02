#!/usr/bin/python3

'''
TODO:
make it so that it is apearant, what player' turn it is
'''

import engine
from algorithms import v1 as kalaha_cpu
import tkinter as tk
from tkinter.font import Font
from typing import Literal
from random import choice

class GUI():
    def __init__(self, platform:Literal["phone", "pc"] | None=None, debug:bool=False) -> None:
        self.platform: Literal["phone", "pc"] = platform if platform != None else ("phone" if f"{__file__}".startswith("/storage/emulated/") else "pc")
        self.gui_created: bool = False
        self.is_running = True
        self.ui_exists = False
        self.debug = debug

        self.FOREGROUND = "#ffffff"
        self.BACKGROUND = "#000000"
        self.FOREGROUND_DISABLED = "#808080" # color disabled

        self.player = True
        
        self.turn: int = 0

        self.override_player = False
        self.game_setup_state: Literal["game", "add", "subtract"] = "game"
        self.game_setup_states: list[Literal["game", "add", "subtract"]] = ["game", "add", "subtract"]

        self.board: list[int] = engine.INITIAL_BOARD.copy()
        self.create_gui()

    def create_gui(self) -> None:
        self.mw = tk.Tk()
        self.mw.title(f"Kalaha game")
        #self.mw.geometry("1000x800")
        self.mw.columnconfigure(index=1, minsize=0, weight=1)
        self.mw.rowconfigure(index=1, minsize=0, weight=1)
        self.mw.configure(background=self.BACKGROUND)

        if self.platform == "pc":
            font_settings = Font(size=20)
            font_game = Font(size=40)
        elif self.platform == "phone":
            font_settings = ("Arial", 8)
            font_game = ("Arial", 14)
        else:
            raise NotImplementedError(f"platform '{self.platform}' not implemented")

        self.ui_frame_settings = tk.Frame(master=self.mw, background=self.BACKGROUND)
        self.ui_frame_settings.grid(row=0, column=0, padx=5, pady=5)
        self.ui_frame_settings_buttons1 = tk.Frame(master=self.ui_frame_settings, background=self.BACKGROUND)
        self.ui_frame_settings_buttons1.grid(row=0, column=0)
        self.ui_frame_settings_buttons2 = tk.Frame(master=self.ui_frame_settings, background=self.BACKGROUND)
        self.ui_frame_settings_buttons2.grid(row=1, column=0)
        self.ui_frame_settings_buttons3 = tk.Frame(master=self.ui_frame_settings, background=self.BACKGROUND)
        self.ui_frame_settings_buttons3.grid(row=2, column=0)
        self.ui_frame_settings_other = tk.Frame(master=self.ui_frame_settings, background=self.BACKGROUND)
        self.ui_frame_settings_other.grid(row=3, column=0)

        self.ui_frame_game = tk.Frame(master=self.mw, background=self.BACKGROUND)
        self.ui_frame_game.grid(row=1, column=0, padx=5, pady=5)

        # create system buttons
        self.ui_reset_board = tk.Button(self.ui_frame_settings_buttons1, text="reset board", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.reset_board)
        self.ui_reset_board.grid(row=0, column=0)
        self.ui_button_change_setup = tk.Button(self.ui_frame_settings_buttons1, text=self.game_setup_state, font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.change_setup_state)
        self.ui_button_change_setup.grid(row=0, column=1)
        self.ui_search_depth_tvar = tk.Variable(master=self.mw, value="8")
        self.ui_suggest_move = tk.Button(master=self.ui_frame_settings_buttons1, text="suggest", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.suggest_move)
        self.ui_suggest_move.grid(row=0, column=2)

        self.ui_make_move = tk.Button(master=self.ui_frame_settings_buttons2, text="make move", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.make_move_pc)
        self.ui_make_move.grid(row=0, column=0)

        self.ui_button_override_player = tk.Button(master=self.ui_frame_settings_buttons3, text=f"override={self.override_player}", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.handle_button_override_player)
        self.ui_button_override_player.grid(row=0, column=0)
        self.ui_button_change_player = tk.Button(master=self.ui_frame_settings_buttons3, text="change player", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.handle_button_change_player)
        self.ui_button_change_player.grid(row=0, column=1)

        self.ui_search_depth_entry = tk.Entry(master=self.ui_frame_settings_other, font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, textvariable=self.ui_search_depth_tvar)
        self.ui_search_depth_entry.grid(row=0, column=0)
        self.ui_label_whos_turn = tk.Label(master=self.ui_frame_settings_other, text="Player 1's turn", font=font_settings, background=self.BACKGROUND, foreground=self.FOREGROUND)
        self.ui_label_whos_turn.grid(row=1, column=0)

        if self.debug:
            self.ui_label_sum = tk.Label(master=self.ui_frame_settings, text=f"{sum(self.board)}", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND)
            self.ui_label_sum.grid(row=4, column=0)
            self.ui_label_turn = tk.Label(master=self.ui_frame_settings, text=f"turn: {self.turn}", font=font_settings, foreground=self.FOREGROUND, background=self.BACKGROUND)
            self.ui_label_turn.grid(row=5, column=0)

        # create and position game buttons
        self.ui_game_buttons: list[tk.Button] = []
        for i in range(6):
            button = tk.Button(master=self.ui_frame_game, text=f"3", font=font_game, foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda i=i: self.handle_button(i)))
            if self.platform == "pc":
                row = 2
                column = 6 - i
            elif self.platform == "phone":
                row = 6 - i
                column = 0
            else: raise NotImplementedError(f"Platform '{self.platform}' not implemented")
            button.grid(row=row, column=column)
            self.ui_game_buttons.append(button)
        button = tk.Button(master=self.ui_frame_game, text="0", font=font_game, foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda: self.handle_button(6)))
        button.config(state="disabled")
        if   self.platform == "pc"   : button.grid(row=1, column=0)
        elif self.platform == "phone": button.grid(row=0, column=1)
        else: raise NotImplementedError(f"Platform '{self.platform}' not implemented")
        self.ui_game_buttons.append(button)
        for i in range(7, 13):
            button = tk.Button(master=self.ui_frame_game, text=f"3", font=font_game, foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda i=i: self.handle_button(i)))
            if self.platform == "pc":
                row = 0
                column = i - 6
            elif self.platform == "phone":
                row = i - 6
                column = 2
            else: raise NotImplementedError(f"Platform '{self.platform}' not implemented")
            button.grid(row=row, column=column)
            self.ui_game_buttons.append(button)        
        button = tk.Button(master=self.ui_frame_game, text="0", font=font_game, foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda: self.handle_button(13)))
        button.config(state="disabled")
        if self.platform == "pc":
            button.grid(row=1, column=7)
        elif self.platform == "phone":
            button.grid(row=7, column=1)
        else: raise NotImplementedError(f"Platform '{self.platform}' not implemented")
        self.ui_game_buttons.append(button)

        self.ui_exists = True
        self.reset_board()
        self.update_ui()
    
    def handle_button(self, button_index:int) -> None:
        self.reset_highlights()
        if self.game_setup_state == "game":
            self._handle_button_game(button_index=button_index)
        elif self.game_setup_state in ["add", "subtract"]:
            self._handle_button_change_amount(button_index=button_index)
        else: raise NotImplementedError(f"gamestate '{self.game_setup_state}' not implemented")
    
    def _handle_button_game(self, button_index:int) -> None:
        moves_available = engine.get_available_moves(board=self.board, player=(button_index < 7))
        if not (button_index in moves_available): return

        make_move_output = engine.make_move(board=self.board, move=button_index)
        if make_move_output == None: raise ValueError("Another error that can never occur")
        self.board, move_again = make_move_output
        self.player = self.player if move_again else not self.player
        self.turn += 1
        self.update_ui()
    
    def _handle_button_change_amount(self, button_index:int) -> None:
        amount = self.board[button_index] - 1 if self.game_setup_state == "subtract" else self.board[button_index] + 1
        self.board[button_index] = max(0, amount)
        self.update_ui()
    
    def handle_button_change_player(self) -> None:
        self.player = not self.player
        self.update_ui()
    
    def update_ui(self) -> None:
        if not self.ui_exists: return
        is_game_over = engine.is_game_over(board=self.board)
        for i in range(14):
            self.ui_game_buttons[i].config(text=f"{self.board[i]}")
            if self.game_setup_state == "game":
                    enabled = (not (i in [6, 13]) and not is_game_over and self.board[i] > 0 and ((i in [[7,8,9,10,11,12],[0,1,2,3,4,5]][int(self.player)]) or self.override_player))
            else:
                enabled = True
            self.ui_game_buttons[i].config(state=("normal" if enabled else "disabled"))
        
        if not is_game_over:
            self.ui_label_whos_turn.config(text=f"Player {'1' if self.player else '2'}s turn")
        else:
            if   self.board[6] == self.board[13]: msg = "game over: tie"
            elif self.board[6] >  self.board[13]: msg = "game over: Player 2 won"
            elif self.board[6] <  self.board[13]: msg = "game over: Player 1 won"
            else:                                 msg = "game over: result unknown"
            self.ui_label_whos_turn.config(text=msg)
        
        self.ui_button_override_player.config(text=f"override={self.override_player}")

        if self.debug:
            self.ui_label_sum.config(text=f"{sum(self.board)}")
            self.ui_label_turn.config(text=f"turn: {self.turn}")
    
    def reset_board(self) -> None:
        self.board = engine.INITIAL_BOARD.copy()
        self.turn = 0
        self.player = True
        self.reset_highlights()
        self.update_ui()

    def change_setup_state(self) -> None:
        self.game_setup_state = self.game_setup_states[(self.game_setup_states.index(self.game_setup_state) + 1) % len(self.game_setup_states)]
        self.ui_button_change_setup.config(text=self.game_setup_state)
        self.update_ui()
    
    def suggest_move(self) -> None:
        depth_max_input = str(self.ui_search_depth_tvar.get()) # type: ignore
        if not depth_max_input.isdecimal(): return
        depth_max = int(depth_max_input)
        if depth_max <= 0: return
        move_list = kalaha_cpu.eval_moves(board=self.board.copy(), depth_max=depth_max, player=self.player)
        '''
        best_cost = max([move_list[i] for i in move_list])
        best_moves = [i for i in move_list if move_list[i] == best_cost]
        move = choice(best_moves)
        
        _make_move_output = engine.make_move(board=self.board.copy(), move=move)
        if _make_move_output == None: return
        self.board, move_again = _make_move_output
        self.player = self.player if move_again else not self.player
        self.turn += 1
        '''
        self.pc_highlight_moves(moves=move_list)
        self.update_ui()
    
    def make_move_pc(self) -> None:
        depth_max_input = str(self.ui_search_depth_tvar.get()) # type: ignore
        if not depth_max_input.isdecimal(): return
        depth_max = int(depth_max_input)
        if depth_max <= 0: return
        move_list = kalaha_cpu.eval_moves(board=self.board.copy(), depth_max=depth_max, player=self.player)
        best_cost = max([move_list[i] for i in move_list])
        best_moves = [i for i in move_list if move_list[i] == best_cost]
        move = choice(best_moves)
        
        _make_move_output = engine.make_move(board=self.board.copy(), move=move)
        if _make_move_output == None: return
        self.board, move_again = _make_move_output
        self.player = self.player if move_again else not self.player
        self.turn += 1
        self.update_ui()
    
    def reset_highlights(self) -> None:
        for i in range(14):
            self.ui_game_buttons[i].config(background=self.BACKGROUND)

    def pc_highlight_moves(self, moves:dict[int, float]) -> None:
        # dict that containts the colors for highlighting in ascending order
        colors = {
            1: ["#008000"],
            2: ["#800000", "#008000"],
            3: ["#800000", "#404000", "#008000"],
            4: ["#800000", "#602000", "#206000", "#008000"],
            5: ["#800000", "#602000", "#404000", "#206000", "#008000"],
            6: ["#800000", "#602000", "#503000", "#305000", "#206000", "#008000"]
            }
        
        moves_list = [i for i in moves]
        moves_packed: dict[float, list[int]] = {}
        for i in moves_list:
            if not moves[i] in moves_packed:
                moves_packed[moves[i]] = []
            moves_packed[moves[i]].append(i)
        costs_sorted = sorted([i for i in moves_packed])
        colors_count = len(costs_sorted)

        for cost_index in range(colors_count):
            button_index_list = moves_packed[costs_sorted[cost_index]]
            for button_index_list_index in range(len(button_index_list)):
                button_index = button_index_list[button_index_list_index]
                self.ui_game_buttons[button_index].config(background=colors[colors_count][cost_index])

    def handle_button_override_player(self) -> None:
        self.override_player = not self.override_player
        self.update_ui()


if __name__ == "__main__":
    gui = GUI()
    #gui.create_gui()
    gui.mw.mainloop()
