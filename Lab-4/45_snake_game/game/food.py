import pygame
import random


class Food:
    def __init__(self, grid_width, grid_height, cell_size, occupied_cells=()):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.x = -1
        self.y = -1
        self.respawn(occupied_cells)

    def respawn(self, occupied_cells):
        """Place food on a random free cell.

        Picks from the list of genuinely free cells, so it can never land on
        the snake and can never loop forever. Returns False (and leaves the
        food off-board) only if there is no free cell at all.
        """
        occupied = set(occupied_cells)
        free = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in occupied
        ]
        if not free:
            self.x, self.y = -1, -1
            return False
        self.x, self.y = random.choice(free)
        return True

    def position(self):
        return (self.x, self.y)

    def rect(self):
        return pygame.Rect(self.x * self.cell_size, self.y * self.cell_size, self.cell_size, self.cell_size)
