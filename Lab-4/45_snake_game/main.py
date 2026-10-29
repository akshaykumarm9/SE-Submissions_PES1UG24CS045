import pygame
from game.game_engine import GameEngine

# Screen dimensions
WIDTH, HEIGHT = 600, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 60


def main():
    # Initialize pygame/Start application
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - Pygame Version")
    clock = pygame.time.Clock()

    # Game loop
    engine = GameEngine(WIDTH, HEIGHT)

    running = True
    dt_ms = 0
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                engine.handle_keydown(event.key)

        if engine.quit_requested:
            running = False

        engine.handle_input()
        engine.update(dt_ms)
        engine.render(screen)

        pygame.display.flip()
        dt_ms = clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
