import pygame
from collections import deque

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
VALID_DIRECTIONS = (UP, DOWN, LEFT, RIGHT)


class Snake:
    # How many not-yet-applied turns we remember. Lets fast players chain
    # e.g. UP then LEFT between two game ticks without losing either input.
    MAX_QUEUED_TURNS = 3

    def __init__(self, x, y, cell_size):
        self.cell_size = cell_size
        # body is a list of (x, y) grid-cell positions, head is body[0]
        self.body = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = RIGHT  # direction used by the most recent move
        self.pending_directions = deque()  # turns waiting for upcoming ticks
        self.grow_pending = False

    # ------------------------------------------------------------------
    # Direction handling
    # ------------------------------------------------------------------
    def _reference_direction(self):
        # A new key press must be judged against the direction the snake
        # WILL be travelling once earlier queued turns are applied - not
        # against the direction of the last completed move. Otherwise
        # RIGHT -> UP -> LEFT typed inside one tick would slip through and
        # drive the head straight into its own neck.
        if self.pending_directions:
            return self.pending_directions[-1]
        return self.direction

    def set_direction(self, dx, dy):
        """Queue a turn. Returns True if accepted, False if rejected.

        Rejected: unknown vectors, repeats of the current heading, direct
        180-degree reversals, and overflow of the small turn queue.
        """
        new_dir = (dx, dy)
        if new_dir not in VALID_DIRECTIONS:
            return False

        ref_x, ref_y = self._reference_direction()
        if new_dir == (ref_x, ref_y):
            return False  # already heading that way
        if new_dir == (-ref_x, -ref_y):
            return False  # 180-degree reversal is never allowed
        if len(self.pending_directions) >= self.MAX_QUEUED_TURNS:
            return False

        self.pending_directions.append(new_dir)
        return True

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------
    def move(self):
        # Apply at most one queued turn per tick.
        if self.pending_directions:
            self.direction = self.pending_directions.popleft()

        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)
        if self.grow_pending:
            self.grow_pending = False  # keep the tail: snake gets longer
        else:
            self.body.pop()  # tail leaves its cell BEFORE collision is checked

    def grow(self):
        self.grow_pending = True

    # ------------------------------------------------------------------
    # Geometry / collisions (checked after move())
    # ------------------------------------------------------------------
    def head_rect(self):
        x, y = self.body[0]
        return pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

    def segment_rects(self):
        return [
            pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            for (x, y) in self.body
        ]

    def collides_with_self(self):
        # move() has already removed the vacated tail cell, so stepping into
        # the cell the tail just left is (correctly) not a collision, while
        # stepping into any other body cell is.
        return self.body[0] in self.body[1:]

    def collides_with_wall(self, grid_width, grid_height):
        x, y = self.body[0]
        return x < 0 or y < 0 or x >= grid_width or y >= grid_height
