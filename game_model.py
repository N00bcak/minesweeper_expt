from constants_and_imports import *

class Model:
    # An abstract object that handles all the data and controls of the game.

    def create_grid(self):
        temp_grid = [[0] * self.grid_width for _ in range(self.grid_height)]
        grid_coords = [[(x, y) for y in range(self.grid_height)] for x in range(self.grid_width)]
        return temp_grid, grid_coords

    def populate_adjacent_tiles(self):
        # Computes how many mines are adjacent to each blank tile.

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.grid[y][x] != MINE_SYMBOL:
                    tile_mine_count=0
                    for adj_x, adj_y in product([-1, 0, 1], [-1, 0, 1]):
                        # Technically we don't have to consider (0,0) but this is a lot cleaner IMO.
                        curr_x = x + adj_x
                        curr_y = y + adj_y
                        if (0 <= curr_x <= self.grid_width - 1 
                            and 0 <= curr_y <= self.grid_height - 1 
                            and self.grid[curr_y][curr_x] == MINE_SYMBOL):
                            tile_mine_count += 1
                    self.grid[y][x] = tile_mine_count

    def switch_mines(self, x, y, new_x, new_y):

        # Look. This only ever switches mines and blank tiles.

        self.grid[y][x] = self.grid[new_y][new_x]
        self.grid[new_y][new_x] = MINE_SYMBOL

    def gol_iter(self):
        for i in range(30):
            for x, y in product(range(self.grid_width), range(self.grid_height)):
                neighbor_count = 0
                for adj_x, adj_y in product([-1, 0, 1], [-1, 0, 1]):
                    curr_x = x + adj_x
                    curr_y = y + adj_y
                    if (0 <= curr_x <= self.grid_width - 1 
                        and 0 <= curr_y <= self.grid_height - 1 
                        and self.grid[curr_y][curr_x] == MINE_SYMBOL):
                        neighbor_count += 1

                if self.grid[y][x] == MINE_SYMBOL and neighbor_count > 4:
                    self.grid[y][x] = 0
                    self.curr_mines -= 1
                elif neighbor_count < 4 and self.grid[y][x] != MINE_SYMBOL:
                    self.grid[y][x] = MINE_SYMBOL
                    self.curr_mines += 1
        
        while(self.mines - self.curr_mines > 0):
            i = random.randrange(0, self.grid_height * self.grid_width)
            if(self.grid[i // self.grid_height][i % self.grid_height] == 0): 
                self.grid[i // self.grid_height][i % self.grid_height] = MINE_SYMBOL
                self.curr_mines += 1

        while(self.curr_mines - self.mines > 0):
            i = random.randrange(0, self.grid_height * self.grid_width)
            if(self.grid[i // self.grid_height][i % self.grid_height] == MINE_SYMBOL): 
                self.grid[i // self.grid_height][i % self.grid_height] = 0
                self.curr_mines -= 1

    def populate_grid(self):
        # Populates the grid with mines.

        for rand in random.sample([i for i in range(self.grid_height * self.grid_width)], self.mines):
            self.grid[rand // self.grid_height][rand % self.grid_height] = MINE_SYMBOL # This tile contains a mine.
        
        if self.algorithm:
            self.gol_iter()

    def get_cell(self, x, y):
        if x < 0 or y < 0 or x >= self.grid_width or y >= self.grid_height:
            raise Exception("You are referencing an invalid cell!")
        else:
            return self.grid[y][x]

    def __init__(self, grid_height, grid_width, mines, algorithm):
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.mines = mines
        self.curr_mines = mines
        self.algorithm = algorithm
        self.grid, self.coords = self.create_grid()
        self.populate_grid()
        self.tiles_revealed = set()
        self.tiles_flagged = set()
        self.blank_tiles = set()
        self.state = None