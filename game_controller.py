from constants_and_imports import *
from game_model import *
from game_view import *

class Controller:
    
    # This class manipulates the game objects via user interaction.

    def reset_game(self):
        self.ui.reset_grid()
        self.model = Model(self.grid_height, self.grid_width, self.mines, self.algorithm)
        self.ui = UserInterface(self.root, self, self.grid_height, self.grid_width, self.mines)
        self.ui.mainloop()
    
    def select_difficulty(self):

        # This is an ad-hoc algorithm that only works for this particular setup.
        # The essential idea is that the concealed buttons aren't deleted, and in doing so we can preserve the main difficulty controlling buttons of the game.
        # So you can endlessly change your game difficulty without having to rerun the file every time.

        prev_children = self.root.winfo_children()
        self.difficulty_label = tk.Label(self.root, text = "Select a difficulty")
        self.difficulty_label.grid()
        for child in prev_children:
            if not isinstance(child, tk.Button):
                child.destroy()
            elif child.winfo_viewable():
                child.destroy()
            else:
                child.grid()

    def reveal_tile(self, x, y, value):
        if (x, y) in self.model.tiles_flagged:
            return None
        else:
            self.model.tiles_revealed.add((x, y))
            self.ui.reveal_tile(x, y, value)
    
    def reveal_adjacent_numbered(self, x, y, num):

        # Essentially we wish to count the number of flagged tiles adjacent to this numbered tile.
        
        adj_mines_flagged = 0
        tiles_to_reveal = []
        
        for adj_x, adj_y in product([-1, 0, 1], [-1, 0, 1]):

            adj_tile_x = x + adj_x
            adj_tile_y = y + adj_y

            if (0 <= adj_tile_x <= self.grid_width - 1
                and 0 <= adj_tile_y <= self.grid_height - 1):

                if (adj_tile_x, adj_tile_y) in self.model.tiles_flagged:
                    adj_mines_flagged += 1
                elif (adj_tile_x, adj_tile_y) not in self.model.tiles_revealed:
                    tiles_to_reveal.append((adj_tile_x, adj_tile_y))

        # print(f"Flagged mines: {adj_mines_flagged}")
        if adj_mines_flagged == num:
            for reveal_x, reveal_y in tiles_to_reveal:
                self.reveal_decision(reveal_x, reveal_y)


    def reveal_all_blanks(self, x, y):
        
        # Conducts a BFS to reveal all adjacent tiles until a numbered tile is reached.
        # print(f"I was called to explore the tile at {(x, y)} {self.model.get_cell(x, y)}!")
        tiles_to_visit = [(x, y)]
        while len(tiles_to_visit) > 0:

            # Get the value of this current tile.
            curr_tile_x, curr_tile_y = tiles_to_visit.pop(0)
            curr_tile_value = self.model.get_cell(curr_tile_x, curr_tile_y)

            if curr_tile_value == 0:
                for adj_x, adj_y in product([-1, 0, 1], [-1, 0, 1]):
                    adj_tile_x = curr_tile_x + adj_x
                    adj_tile_y = curr_tile_y + adj_y

                    if (0 <= adj_tile_x <= self.grid_width - 1
                        and 0 <= adj_tile_y <= self.grid_height - 1):
                        adj_tile_value = self.model.get_cell(adj_tile_x, adj_tile_y)
                        self.reveal_tile(adj_tile_x, adj_tile_y, adj_tile_value)

                        if (adj_tile_value == 0
                            and (adj_tile_x, adj_tile_y) not in self.model.blank_tiles):
                            self.model.blank_tiles.add((adj_tile_x, adj_tile_y))
                            tiles_to_visit.append((adj_tile_x, adj_tile_y))
            # print(f"Next we are visiting tiles {tiles_to_visit} {len(tiles_to_visit)}")

    def check_win(self):
        unrevealed_tiles = self.grid_height * self.grid_width - len(self.model.tiles_revealed)
        if unrevealed_tiles == self.mines and len(self.model.tiles_flagged) == self.mines and self.model.state is None:
            # If we haven't lost yet, and we flagged every single tile there is, then we must have found all the mines.
            self.win()

    def reveal_decision(self, x, y):
        tile_value = self.model.get_cell(x, y)
        tile_state = self.ui.get_tile_state(x, y)
        
        if (x, y) in self.model.tiles_flagged:
            return None
        
        if not len(self.model.tiles_revealed):

            print(f"Hi! {(x,y)} {tile_value} {tile_state}")
            if tile_value == MINE_SYMBOL:
                # If no tiles were revealed, then our first click can never be a mine. Because that's just bullshit.
                
                swap_mine_x, swap_mine_y = x, y
                while(self.model.grid[swap_mine_y][swap_mine_x] == MINE_SYMBOL):
                    swap_mine_x, swap_mine_y = random.randrange(0, self.grid_width), random.randrange(0, self.grid_height)
                
                self.model.switch_mines(x, y, swap_mine_x, swap_mine_y)

            self.model.populate_adjacent_tiles()
            tile_value = self.model.get_cell(x, y)
            tile_state = self.ui.get_tile_state(x, y)
            print(f"{(x, y)} {tile_value} {tile_state}")


        if ((x, y) in self.model.tiles_revealed) and tile_state in list(range(1,9)):
            self.reveal_adjacent_numbered(x, y, tile_state)
        elif tile_value in range(1, 9):
            # We stepped on a numbered tile.
            self.reveal_tile(x, y, tile_value)
        elif tile_value == MINE_SYMBOL and self.model.state is None:
                # We stepped on a mine, so we lose.
                self.lose()
        else:
            # We stepped on a blank tile.
            self.reveal_all_blanks(x, y)

        self.check_win()

    def update_mines(self):
        mines_left = self.mines - len(self.model.tiles_flagged)

        if mines_left >= 0:
            self.ui.update_mines_panel(mines_left)
            self.check_win()

    def update_flagged_tile(self, x, y):
        if (x, y) not in self.model.tiles_revealed and (x, y) not in self.model.tiles_flagged:
            self.model.tiles_flagged.add((x, y))
            self.ui.flag_tile(x, y)
        elif (x, y) in self.model.tiles_flagged and (x, y) not in self.model.tiles_revealed:
            self.model.tiles_flagged.remove((x, y))
            self.ui.unflag_tile(x, y)
        self.update_mines()

    def win(self):
        self.model.state = "You win!"
        self.ui.display_win()
    
    def lose(self):
        self.model.state = "You lose!"
        self.ui.display_loss()

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                tile_value = self.model.get_cell(x, y)
                self.ui.reveal_tile(x, y, tile_value)

    def __init__(self, height, width, mines, algorithm, root):
        self.grid_height = height
        self.grid_width = width
        self.root = root
        self.mines = mines
        self.algorithm = algorithm
        self.model = Model(self.grid_height, self.grid_width, self.mines, self.algorithm)
        self.ui = UserInterface(self.root, self, self.grid_height, self.grid_width, self.mines)
        self.ui.mainloop()