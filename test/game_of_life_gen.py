# An interesting idea popped up in my head to try a game-of-life esque algorithm to weed out the lower and higher numbers in minesweeper.
# My intuition is that this encourages the generation of more difficult boards since in a vacuum the numbers 4 and 5 precede the riskiest sequence of guesses.

from itertools import product
from math import floor
from random import randint, randrange, sample
import argparse
from multiprocessing import Pool
import numpy as np

class MinesweeperGrid:

    def get_adj(self):
        return product([-1, 0, 1], [-1, 0, 1])

    def get_difficulty(self):
        self.populate_numbers()
        difficulty = 0
        for x, y in product(range(self.width), range(self.height)):
            if self.grid[y][x] >= 0:
                # difficulty += 81 - abs(9 - (2*self.grid[y][x]))**2
                # We will change the difficulty metric out for something that more clearly reflects near our desired targets (4 and 5 mines adjacent).
                difficulty += (4 - abs(4 - self.grid[y][x]))**2
        return difficulty // 2

    def setup_mines(self):
        for i in sample([i for i in range(self.height * self.width)], self.mines):
            self.grid[i // self.height][i % self.height] = -1

    def populate_numbers(self):
        for x, y in product(range(self.width), range(self.height)):
            if self.grid[y][x] >= 0:
                tile_mine_count = 0
                for adj_x, adj_y in self.get_adj():
                    curr_x = x + adj_x
                    curr_y = y + adj_y
                    if (0 <= curr_x <= self.width - 1 
                        and 0 <= curr_y <= self.height - 1 
                        and self.grid[curr_y][curr_x] == -1):
                        tile_mine_count += 1
                self.grid[y][x] = tile_mine_count

    def __repr__(self):
        self.populate_numbers()
        return f"The grid: \n\n" + "\n".join([ " ".join([str(self.grid[y][x]) for x in range(self.width)]) for y in range(self.height)]) + f"\n\nDifficulty ranking: {self.get_difficulty()}"
    
    def __init__(self, grid_height = 5, grid_width = 5, num_mines = 3):        
        self.height = grid_height
        self.width = grid_width
        self.mines = num_mines
        self.grid = [[0 for i in range(self.width)] for j in range(self.height)]
        self.curr_mines = num_mines

class MinesweeperGridGameOfLife(MinesweeperGrid):

    def gol_iter(self):
        for i in range(self.iter):
            for x, y in product(range(self.width), range(self.height)):
                neighbor_count = 0
                for adj_x, adj_y in self.get_adj():
                    curr_x = x + adj_x
                    curr_y = y + adj_y
                    if (0 <= curr_x <= self.width - 1 
                        and 0 <= curr_y <= self.height - 1 
                        and self.grid[curr_y][curr_x] == -1):
                        neighbor_count += 1

                if self.grid[y][x] == -1 and neighbor_count > 4:
                    self.grid[y][x] = 0
                    self.curr_mines -= 1
                elif neighbor_count < 4 and self.grid[y][x] != -1:
                    self.grid[y][x] = -1
                    self.curr_mines += 1
        
        while(self.mines - self.curr_mines > 0):
            i = randrange(0, self.height * self.width)
            if(self.grid[i // self.height][i % self.height] == 0): 
                self.grid[i // self.height][i % self.height] = -1
                self.curr_mines += 1

        while(self.curr_mines - self.mines > 0):
            i = randrange(0, self.height * self.width)
            if(self.grid[i // self.height][i % self.height] == -1): 
                self.grid[i // self.height][i % self.height] = 0
                self.curr_mines -= 1

    # Bigger grid numbers offer better representations of the algorithm, although I will have to tailor the actual number of iterations to taste.
    def __init__(self, grid_height = 5, grid_width = 5, num_mines = 3, num_iterations = 3):
        super().__init__(grid_height, grid_width, num_mines)
        self.iter = num_iterations
        self.setup_mines()
        self.gol_iter()


class MinesweeperGridCluster(MinesweeperGrid):
    
    def weight_metric(self, seed_x, seed_y, x, y):
        # A simple Manhattan distance-based metric that lends greater weight to mines that are closer to the seed mine.
        return 1/max(abs(seed_x - x), abs(seed_y - y)) 

    def setup_mines(self):
        for i in sample([i for i in range(self.height * self.width)], floor(self.mines * self.seed_density)):
            self.grid[i // self.height][i % self.height] = -1
            self.mine_locations.append((i % self.height, i // self.height))

    def clustering(self):

        # The idea of this algorithm is to stochastically place mines in the neighborhood of a "seed" mine.
        # Of course, the clustering of mines is favored. 
        mines_left = self.curr_mines

        while mines_left:
            potential_neighbors = []

            while not len(potential_neighbors):
                (mine_x, mine_y) = sample(self.mine_locations, 1)[0]
                potential_neighbors = [(mine_x + x, mine_y + y) for x, y in product(list(range(-2, 3)), list(range(-2, 3))) 
                                                            if ((mine_x + x, mine_y + y) not in self.mine_locations)
                                                            and 0 <= mine_x + x <= self.width - 1
                                                            and 0 <= mine_y + y <= self.height - 1]
                potential_neighbor_p = [self.weight_metric(mine_x, mine_y, x, y) for x, y in potential_neighbors]
                potential_neighbor_p = [i/sum(potential_neighbor_p) for i in potential_neighbor_p]

            mines_to_place = randint(1, min(floor(1/self.seed_density), len(potential_neighbors)))
            for sample_idx in np.random.choice(range(len(potential_neighbors)), mines_to_place, replace = False, p = potential_neighbor_p):
                # print(potential_neighbors[sample_idx])
                neighbor_x, neighbor_y = potential_neighbors[sample_idx]
                self.grid[neighbor_y][neighbor_x] = -1
                self.mine_locations.append((neighbor_x, neighbor_y))
                mines_left -= 1

        

    def __init__(self, grid_height = 5, grid_width = 5, num_mines = 3, seed_density = 0.25):
        super().__init__(grid_height, grid_width, num_mines)
        self.seed_density = seed_density
        self.curr_mines = num_mines - floor(self.mines * self.seed_density)
        self.mine_locations = []
        self.setup_mines()
        self.clustering()


def expt(argp, num_iter, seed_den):
    if argp.gol:
        mine = MinesweeperGridGameOfLife(grid_height = argp.height, grid_width = argp.width, num_mines = floor(argp.mine_density * (argp.height * argp.width)), num_iterations = num_iter)
    elif argp.cluster:
        mine = MinesweeperGridCluster(grid_height = argp.height, grid_width = argp.width, num_mines = floor(argp.mine_density * (argp.height * argp.width)), seed_density = seed_den)

    return mine.get_difficulty()
    print(mine)

    

if __name__ == "__main__":

    argp = argparse.ArgumentParser(description = "idk")
    argp.add_argument("-height", type = int, help = "Grid Height.", default = 5)
    argp.add_argument("-width", type = int, help = "Grid Width.", default = 5)
    argp.add_argument("-mine_density", type = float, help = "Density of mines.", default = 5)
    argp.add_argument("-gol", type = int, help = "Whether or not to use Game of Life iteration.", default = 0)
    argp.add_argument("-gol_iter", type = int, help = "The number of iterations of Game of Life to go through.", default = 3)
    argp.add_argument("-cluster", type = int, help = "Whether to use the clustering algorithm.", default = 0)
    argp.add_argument("-seed_den", type = float, help = "Proportion of mines to be used as seeds.", default = 0.25)
    argp.add_argument("-sample_n", type = int, help = "The number of grids to generate.", default = 5)

    argp = argp.parse_args()
    
    avg = 0
    with Pool(4) as p:
        if argp.gol:
            avg = sum(p.starmap(expt, [(argp, argp.gol_iter, 0) for i in range(argp.sample_n)])) // argp.sample_n
        elif argp.cluster:
            avg = sum(p.starmap(expt, [(argp, 0, argp.seed_den) for i in range(argp.sample_n)])) // argp.sample_n

    print(f"Grid Height: {argp.height}, Grid Width: {argp.width}, Mine density: {argp.mine_density}, Sample: {argp.sample_n}")
    print(f"Game of Life Iterations: {argp.gol_iter}" if argp.gol else (f"Cluster Seed Density: {argp.seed_den}" if argp.cluster else "NA"))
    print(f"Average Difficulty Ranking per mine: {avg/floor(argp.mine_density * (argp.height * argp.width))}")

    # for i in range(argp.sample_n):
        
    #     mine_half_gol = MinesweeperGridGameOfLife(grid_height = argp.height, grid_width = argp.width, num_mines = argp.mines, num_iterations = argp.gol_iter // 2)
    #     mine_dbl_gol = MinesweeperGridGameOfLife(grid_height = argp.height, grid_width = argp.width, num_mines = argp.mines, num_iterations = argp.gol_iter * 2)
    #     mine_no_gol = MinesweeperGridGameOfLife(grid_height = argp.height, grid_width = argp.width, num_mines = argp.mines, num_iterations = 0)

    #     avg_gol += mine_gol.get_difficulty()
    #     avg_half_gol += mine_half_gol.get_difficulty()
    #     avg_dbl_gol += mine_dbl_gol.get_difficulty()
    #     avg_no_gol += mine_no_gol.get_difficulty()

    #     # if i == argp.sample_n - 1:
    #     #     print(f"{mine_gol}\n\n\n {mine_no_gol}")
    
    # avg_gol /= argp.sample_n
    # avg_half_gol /= argp.sample_n
    # avg_dbl_gol /= argp.sample_n
    # avg_no_gol /= argp.sample_n