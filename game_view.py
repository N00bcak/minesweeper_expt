from constants_and_imports import *
from game_model import *

class UserInterface(tk.Frame):

    # The code that handles the GUI of the game. Mostly to interact with Tkinter and extract data from Model.

    def reset_grid(self):
        for child in self.master.winfo_children():
            if not isinstance(child, tk.Button) or child.winfo_viewable():
                child.destroy()

    def get_tile_state(self, x, y):
        return self.tiles[y][x]['text']

    def reveal_tile(self, x, y, value):
        self.tiles[y][x].configure(text = value, bg = DEFAULT_CONFIG["colors"][value])

    def flag_tile(self, x, y):
        self.tiles[y][x].configure(text = FLAG_SYMBOL, bg = "grey")

    def unflag_tile(self, x, y):
        self.tiles[y][x].configure(text = "", bg = "grey")

    def update_mines_panel(self, mines):
        self.menu.curr_mines.set(str(mines))

    def setup_tile_controls(self):
        for x in range(self.grid_width):
            for y in range(self.grid_height):

                def on_click(f, *arguments):
                    def g(_):
                        f(*arguments)
                    return g

                self.tiles[y][x].bind("<Button-1>", on_click(self.controller.reveal_decision, x, y))
                self.tiles[y][x].bind("<Button-3>", on_click(self.controller.update_flagged_tile, x, y))
        self.menu.reset_button.bind("<Button>", on_click(self.controller.reset_game))
        self.menu.diff_button.bind("<Button>", on_click(self.controller.select_difficulty))

    def create_tiles(self):
        # Creates buttons for each grid tile so our Controller can interact with our view.

        def Button(x, y):
            button = tk.Button(self.master, width = 5, text = "", bg = "grey")
            button.grid(row = y + 5, column = x + 1)
            return button
        
        return [
                    [  
                        Button(x, y)
                        for x in range(self.grid_width)
                    ] 
                    for y in range(self.grid_height)
                ]

    def display_loss(self):
        self.menu.loss_label.grid(row = 0, columnspan = self.grid_width)
    
    def display_win(self):
        self.menu.win_label.grid(row = 0, columnspan = self.grid_width)

    def __init__(self, master: tk.Tk, controller, grid_height, grid_width, mines):
        self.master = master
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.mines = mines
        self.controller = controller
        self.master.title("Minesweeper Clone")

    def mainloop(self):
        self.menu = Menu(self.master, self.grid_height, self.grid_width, self.mines)
        self.tiles = self.create_tiles()
        self.menu.mines_left.grid(row = 0, columnspan = self.grid_width)
        self.setup_tile_controls()
        self.master.mainloop()

class Menu(tk.Frame):
    def __init__(self, master: tk.Tk, height, width, mines):
        tk.Frame.__init__(self,master)
        self.master = master
        self.mines = mines
        self.grid()

        self.reset_button = tk.Button(self.master, width = 15, text = "Reset")
        self.reset_button.grid(row = 0)

        self.diff_button = tk.Button(self.master, width = 15, text = "Select Difficulty")
        self.diff_button.grid(row = 1)

        self.curr_mines = tk.StringVar()
        self.curr_mines.set(str(self.mines))
        self.mines_left = tk.Label(self.master, textvariable = self.curr_mines)

        self.loss_label = tk.Label(self.master, text = "Kaboom!", bg = "red")
        self.win_label = tk.Label(self.master, text = "You Win!", bg = "green")