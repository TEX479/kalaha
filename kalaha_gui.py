#!/usr/bin/python3
import kalaha
import tkinter as tk
from typing import Literal

class GUI():
    def __init__(self, phone:bool=False) -> None:
        self.platform: Literal["phone", "pc"] = "phone" if phone else "pc"
        self.reset_board()
        self.gui_created: bool = False

        self.FOREGROUND = "#ffffff"
        self.BACKGROUND = "#000000"
        self.FOREGROUND_DISABLED = "#808080" # color disabled

        self.player = True

        self.create_gui()

    def create_gui(self) -> None:
        if self.platform == "pc":
            self._create_gui_pc()
        elif self.platform == "phone":
            self._create_gui_phone()
        else:
            raise NotImplementedError(f"No implementation for {self.platform=}")
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
        self.ui_frame_game.grid(row=0, column=1, padx=5, pady=5)

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
        self.mw.mainloop()
    
    def handle_button(self, button_index:int) -> None:
        moves_available = kalaha.get_available_moves(board=self.board, player=(button_index < 7))
        if not (button_index in moves_available): return

        make_move_output = kalaha.make_move(board=self.board, move=button_index)
        if make_move_output == None: raise ValueError("Another error that can never occur")
        self.board, move_again = make_move_output
        self.player = self.player if move_again else not self.player
        self.ui_update_board()
    
    def ui_update_board(self) -> None:
        for i in range(14):
            self.ui_game_buttons[i].config(text=f"{self.board[i]}")
            enabled = (not (i in [6, 13]) and not kalaha.is_game_over(board=self.board))
            self.ui_game_buttons[i].config(state="normal" if enabled else "disabled")
    
    def reset_board(self) -> None:
        self.board = kalaha.INITIAL_BOARD.copy()


if __name__ == "__main__":
    gui = GUI(phone=False)
    #gui.create_gui()
