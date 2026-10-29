import pygame
from .snake import Snake, UP, DOWN, LEFT, RIGHT
from .food import Food
from .sound import SoundManager

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
GRAY = (170, 170, 170)

# Game states
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_MENU = "menu"

# (label, snake moves per second). Medium keeps the original speed of 8.
DIFFICULTIES = [
    ("Easy", 5),
    ("Medium", 8),
    ("Hard", 12),
]
MENU_OPTIONS = [name for name, _ in DIFFICULTIES] + ["Exit"]
EXIT_INDEX = len(DIFFICULTIES)
DEFAULT_DIFFICULTY_INDEX = 1  # Medium

CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
NUMBER_KEYS = (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)
KEYPAD_NUMBER_KEYS = (pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4)

# Longest frame time we will credit to the move timer (guards against a
# huge jump after the window is dragged/paused).
MAX_FRAME_MS = 100


class GameEngine:
    def __init__(self, width, height, sound=None):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.menu_font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.sound = sound if sound is not None else SoundManager()

        self.difficulty_index = DEFAULT_DIFFICULTY_INDEX
        self.menu_index = DEFAULT_DIFFICULTY_INDEX
        self.quit_requested = False
        self.final_score = 0

        self.reset_game(self.difficulty_index)

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------
    @property
    def moves_per_second(self):
        return DIFFICULTIES[self.difficulty_index][1]

    @property
    def difficulty_name(self):
        return DIFFICULTIES[self.difficulty_index][0]

    @property
    def game_over(self):
        # True on both the Game Over screen and the replay menu.
        return self.state != STATE_PLAYING

    def reset_game(self, difficulty_index=None):
        """Start a completely fresh game. Rebuilds every piece of state."""
        if difficulty_index is not None:
            self.difficulty_index = difficulty_index
        self.menu_index = self.difficulty_index

        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size, self.snake.body)

        self.score = 0
        self.final_score = 0
        self.won = False
        self._move_timer_ms = 0.0
        self.state = STATE_PLAYING

    def _end_game(self, won=False):
        self.state = STATE_GAME_OVER
        self.won = won
        self.final_score = self.score
        self.snake.pending_directions.clear()
        self.sound.play("game_over")

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_keydown(self, key):
        if self.state == STATE_PLAYING:
            self._handle_playing_key(key)
        elif self.state == STATE_GAME_OVER:
            # Only an explicit confirm key leaves the Game Over screen, so a
            # direction key still held from gameplay cannot skip past it.
            if key in CONFIRM_KEYS:
                self.state = STATE_MENU
                self.menu_index = self.difficulty_index
        elif self.state == STATE_MENU:
            self._handle_menu_key(key)

    def _handle_playing_key(self, key):
        # Turns are queued and applied on the next tick (see Snake).
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(*UP)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(*DOWN)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(*LEFT)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(*RIGHT)

    def _handle_menu_key(self, key):
        if key in NUMBER_KEYS:
            self._activate_menu_option(NUMBER_KEYS.index(key))
        elif key in KEYPAD_NUMBER_KEYS:
            self._activate_menu_option(KEYPAD_NUMBER_KEYS.index(key))
        elif key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(MENU_OPTIONS)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(MENU_OPTIONS)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._activate_menu_option(self.menu_index)
        elif key == pygame.K_ESCAPE:
            self.quit_requested = True

    def _activate_menu_option(self, index):
        if index == EXIT_INDEX:
            self.quit_requested = True
        else:
            self.reset_game(index)

    def handle_input(self):
        # Reserved for continuously-held-key input (not used for a
        # grid-based snake, but kept here to mirror the engine's shape).
        pass

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt_ms=1000 / 60):
        """Advance the game by dt_ms milliseconds of real time."""
        if self.state != STATE_PLAYING:
            return

        self._move_timer_ms += min(dt_ms, MAX_FRAME_MS)
        interval_ms = 1000.0 / self.moves_per_second
        if self._move_timer_ms < interval_ms:
            return
        self._move_timer_ms = min(self._move_timer_ms - interval_ms, interval_ms)

        self.step()

    def step(self):
        """One grid move: input -> direction -> move -> collisions -> food."""
        self.snake.move()

        if self.snake.collides_with_wall(self.grid_width, self.grid_height):
            self._end_game()
            return

        if self.snake.collides_with_self():
            self._end_game()
            return

        if self.snake.body[0] == self.food.position():
            self.snake.grow()
            self.score += 1
            self.sound.play("eat")
            if not self.food.respawn(self.snake.body):
                # Board completely filled: nothing left to eat.
                self._end_game(won=True)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, screen):
        if self.state == STATE_MENU:
            self._render_menu(screen)
            return

        self._render_board(screen)
        if self.state == STATE_GAME_OVER:
            self._render_game_over(screen)

    def _render_board(self, screen):
        # Draw food
        if self.food.x >= 0:
            pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

    def _blit_centered(self, screen, surface, y):
        rect = surface.get_rect(center=(self.width // 2, y))
        screen.blit(surface, rect)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = "YOU WIN!" if self.won else "GAME OVER"
        title_color = GREEN if self.won else RED
        cy = self.height // 2
        self._blit_centered(screen, self.title_font.render(title, True, title_color), cy - 70)
        self._blit_centered(
            screen, self.menu_font.render(f"Final Score: {self.final_score}", True, WHITE), cy + 5
        )
        self._blit_centered(
            screen, self.small_font.render("Press ENTER to continue", True, GRAY), cy + 75
        )

    def _render_menu(self, screen):
        cy = self.height // 2
        self._blit_centered(screen, self.title_font.render("PLAY AGAIN?", True, GREEN), cy - 190)
        self._blit_centered(
            screen, self.small_font.render(f"Last score: {self.final_score}", True, WHITE), cy - 130
        )
        self._blit_centered(
            screen, self.small_font.render("Choose a difficulty:", True, GRAY), cy - 90
        )

        left_x = self.width // 2 - 90
        for i, name in enumerate(MENU_OPTIONS):
            selected = i == self.menu_index
            color = GREEN if selected else WHITE
            y = cy - 30 + i * 52
            if selected:
                marker = self.menu_font.render(">", True, color)
                screen.blit(marker, marker.get_rect(midleft=(left_x - 40, y)))
            line = self.menu_font.render(f"{i + 1}. {name}", True, color)
            screen.blit(line, line.get_rect(midleft=(left_x, y)))

        self._blit_centered(
            screen,
            self.small_font.render("Press 1-4, or UP/DOWN + ENTER", True, GRAY),
            cy + 210,
        )
