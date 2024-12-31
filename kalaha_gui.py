#!/usr/bin/python3

'''
TODO:
make it so that it is apearant, what player' turn it is
'''

import kalaha
import tkinter as tk
from typing import Literal
from random import choice

class GUI():
    def __init__(self, phone:bool=False) -> None:
        self.platform: Literal["phone", "pc"] = "phone" if phone else "pc"
        self.gui_created: bool = False
        self.is_running = True
        self.ui_exists = False

        self.FOREGROUND = "#ffffff"
        self.BACKGROUND = "#000000"
        self.FOREGROUND_DISABLED = "#808080" # color disabled

        self.player = True

        self.game_setup_state: Literal["game", "add", "subtract"] = "game"
        self.game_setup_states: list[Literal["game", "add", "subtract"]] = ["game", "add", "subtract"]

        self.board: list[int] = kalaha.INITIAL_BOARD.copy()
        self.create_gui()

    def create_gui(self) -> None:
        if self.platform == "pc":
            self._create_gui_pc()
        elif self.platform == "phone":
            self._create_gui_phone()
        else:
            raise NotImplementedError(f"No implementation for {self.platform=}")
        self.ui_exists = True
        self.reset_board()
        self.ui_update_board()
    
    def _create_gui_phone(self) -> None:
        ...
    
    def _create_gui_pc(self) -> None:
        self.mw = tk.Tk()
        self.mw.title(f"Kalaha game")
        #self.mw.geometry("1000x800")
        self.mw.columnconfigure(index=1, minsize=0, weight=1)
        self.mw.rowconfigure(index=1, minsize=0, weight=1)
        self.mw.configure(background=self.BACKGROUND)

        self.ui_frame_settings = tk.Frame(master=self.mw, background=self.BACKGROUND)
        self.ui_frame_settings.grid(row=0, column=0, padx=5, pady=5)

        self.ui_frame_game = tk.Frame(master=self.mw, background=self.BACKGROUND)
        self.ui_frame_game.grid(row=1, column=0, padx=5, pady=5)

        # create system buttons
        self.ui_reset_board = tk.Button(self.ui_frame_settings, text="reset board", foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.reset_board)
        self.ui_reset_board.grid(row=0, column=0)
        self.ui_button_change_setup = tk.Button(self.ui_frame_settings, text=self.game_setup_state, foreground=self.FOREGROUND, background=self.BACKGROUND, command=self.change_setup_state)
        self.ui_button_change_setup.grid(row=0, column=1)
        self.ui_search_depth_tvar = tk.Variable(master=self.mw, value="8")
        self.ui_search_depth_entry = tk.Entry(master=self.ui_frame_settings, foreground=self.FOREGROUND, background=self.BACKGROUND, textvariable=self.ui_search_depth_tvar)
        self.ui_search_depth_entry.grid(row=0, column=2)
        self.ui_move_p1 = tk.Button(master=self.ui_frame_settings, text="p1", foreground=self.FOREGROUND, background=self.BACKGROUND, command=lambda: self.make_move_pc(1))
        self.ui_move_p2 = tk.Button(master=self.ui_frame_settings, text="p2", foreground=self.FOREGROUND, background=self.BACKGROUND, command=lambda: self.make_move_pc(2))
        self.ui_move_p1.grid(row=0, column=3)
        self.ui_move_p2.grid(row=0, column=4)

        # create and position game buttons
        self.ui_game_buttons: list[tk.Button] = []
        for i in range(6):
            button = tk.Button(master=self.ui_frame_game, text=f"3", foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda i=i: self.handle_button(i)))
            row = 2
            column = 6 - i
            button.grid(row=row, column=column)
            self.ui_game_buttons.append(button)
        button = tk.Button(master=self.ui_frame_game, text="0", foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda: self.handle_button(6)))
        button.config(state="disabled")
        button.grid(row=1, column=0)
        self.ui_game_buttons.append(button)
        for i in range(7, 13):
            button = tk.Button(master=self.ui_frame_game, text=f"3", foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda i=i: self.handle_button(i)))
            row = 0
            column = i - 6
            button.grid(row=row, column=column)
            self.ui_game_buttons.append(button)        
        button = tk.Button(master=self.ui_frame_game, text="0", foreground=self.FOREGROUND, background=self.BACKGROUND, command=(lambda: self.handle_button(13)))
        button.config(state="disabled")
        button.grid(row=1, column=7)
        self.ui_game_buttons.append(button)
    
    def handle_button(self, button_index:int) -> None:
        if self.game_setup_state == "game":
            self._handle_button_game(button_index=button_index)
    
    def _handle_button_game(self, button_index:int) -> None:
        moves_available = kalaha.get_available_moves(board=self.board, player=(button_index < 7))
        if not (button_index in moves_available): return

        make_move_output = kalaha.make_move(board=self.board, move=button_index)
        if make_move_output == None: raise ValueError("Another error that can never occur")
        self.board, move_again = make_move_output
        self.player = self.player if move_again else not self.player
        self.ui_update_board()
    
    def _handle_button_change_amount(self, button_index:int) -> None:
        amount = self.board[button_index] - 1 if self.game_setup_state == "subtract" else self.board[button_index] + 1
        self.board[button_index] = max(0, amount)
        self.ui_update_board()
    
    def ui_update_board(self) -> None:
        if not self.ui_exists: return
        for i in range(14):
            self.ui_game_buttons[i].config(text=f"{self.board[i]}")
            if self.game_setup_state == "game":
                enabled = (not (i in [6, 13]) and not kalaha.is_game_over(board=self.board) and self.board[i] > 0)
            else:
                enabled = True
            self.ui_game_buttons[i].config(state="normal" if enabled else "disabled")
    
    def reset_board(self) -> None:
        self.board = kalaha.INITIAL_BOARD.copy()
        self.ui_update_board()

    def change_setup_state(self) -> None:
        self.game_setup_state = self.game_setup_states[(self.game_setup_states.index(self.game_setup_state) + 1) % len(self.game_setup_states)]
        self.ui_button_change_setup.config(text=self.game_setup_state)
    
    def make_move_pc(self, player:Literal[1, 2]) -> None:
        depth_max_input = str(self.ui_search_depth_tvar.get()) # type: ignore
        if not depth_max_input.isdecimal(): return
        depth_max = int(depth_max_input)
        if depth_max <= 0: return
        move_list = kalaha.eval_moves(board=self.board.copy(), depth_max=depth_max, player=(player==1))
        best_cost = max([move_list[i] for i in move_list])
        best_moves = [i for i in move_list if move_list[i] == best_cost]
        move = choice(best_moves)
        
        _make_move_output = kalaha.make_move(board=self.board.copy(), move=move)
        if _make_move_output == None: return
        self.board, _move_again = _make_move_output
        self.ui_update_board()


if __name__ == "__main__":
    gui = GUI(phone=False)
    #gui.create_gui()
    gui.mw.mainloop()
