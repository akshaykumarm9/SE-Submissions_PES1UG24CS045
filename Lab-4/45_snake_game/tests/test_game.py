"""Headless tests for the Snake game.  Run from the project root:

    python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402
from game import game_engine as ge  # noqa: E402
from game.game_engine import GameEngine, STATE_PLAYING, STATE_GAME_OVER, STATE_MENU  # noqa: E402
from game.snake import Snake, UP, DOWN, LEFT, RIGHT  # noqa: E402
from game.food import Food  # noqa: E402
from game.sound import SoundManager, SOUNDS_DIR  # noqa: E402

pygame.init()
SCREEN = pygame.display.set_mode((600, 600))

KEYS = {
    "UP": (UP, [pygame.K_UP, pygame.K_w]),
    "DOWN": (DOWN, [pygame.K_DOWN, pygame.K_s]),
    "LEFT": (LEFT, [pygame.K_LEFT, pygame.K_a]),
    "RIGHT": (RIGHT, [pygame.K_RIGHT, pygame.K_d]),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}


class RecordingSound:
    def __init__(self):
        self.played = []

    def play(self, name):
        self.played.append(name)
        return True


def make_engine():
    e = GameEngine(600, 600, sound=RecordingSound())
    return e


def heading(engine, name):
    """Place a 3-long snake mid-board, laid out consistently with `name`."""
    dx, dy = KEYS[name][0]
    hx, hy = 15, 15
    engine.snake.body = [(hx - i * dx, hy - i * dy) for i in range(3)]
    engine.snake.direction = (dx, dy)
    engine.snake.pending_directions.clear()
    engine.food.x, engine.food.y = -1, -1
    return engine


def tick(e, n=1):
    for _ in range(n):
        e.step()


class MovementTests(unittest.TestCase):
    def test_all_four_directions_both_key_sets(self):
        for name, (vec, keys) in KEYS.items():
            for key in keys:
                e = make_engine()
                # Start RIGHT; get to a state where `name` is a legal turn.
                if name == "LEFT":
                    e.handle_keydown(pygame.K_UP); tick(e)
                    start = e.snake.body[0]
                    e.handle_keydown(key); tick(e)
                else:
                    start = e.snake.body[0]
                    e.handle_keydown(key); tick(e)
                self.assertEqual(e.snake.direction, vec, f"{name} via key {key}")
                nx, ny = e.snake.body[0]
                self.assertEqual((nx - start[0], ny - start[1]), vec)
                self.assertEqual(e.state, STATE_PLAYING)

    def test_snake_moves_one_cell_per_step_and_keeps_length(self):
        e = make_engine()
        before = list(e.snake.body)
        e.step()
        self.assertEqual(len(e.snake.body), len(before))
        self.assertEqual(e.snake.body[0], (before[0][0] + 1, before[0][1]))


class ReversalTests(unittest.TestCase):
    def test_all_180_reversals_rejected_every_key_combination(self):
        for name, (vec, keys) in KEYS.items():
            opp_name = OPPOSITE[name]
            for k_new in KEYS[opp_name][1]:
                e = make_engine()
                heading(e, name)
                body_before = list(e.snake.body)
                e.handle_keydown(k_new)
                e.step()
                self.assertEqual(e.snake.direction, vec, f"{name} then {opp_name}")
                self.assertEqual(e.state, STATE_PLAYING, f"{name} then {opp_name} died")
                self.assertEqual(e.snake.body[0],
                                 (body_before[0][0] + vec[0], body_before[0][1] + vec[1]))

    def test_first_move_reversal_right_then_left(self):
        # Snake is shortest right after spawn - the classic instant death.
        e = make_engine()
        e.handle_keydown(pygame.K_LEFT)
        tick(e, 5)
        self.assertEqual(e.state, STATE_PLAYING)
        self.assertEqual(e.snake.direction, RIGHT)


class ValidTurnTests(unittest.TestCase):
    def test_all_eight_valid_turns(self):
        pairs = [("RIGHT", "UP"), ("RIGHT", "DOWN"), ("LEFT", "UP"), ("LEFT", "DOWN"),
                 ("UP", "LEFT"), ("UP", "RIGHT"), ("DOWN", "LEFT"), ("DOWN", "RIGHT")]
        for cur, new in pairs:
            for k in KEYS[new][1]:
                e = make_engine()
                heading(e, cur)
                start = e.snake.body[0]
                e.handle_keydown(k)
                e.step()
                self.assertEqual(e.snake.direction, KEYS[new][0], f"{cur}->{new}")
                nx, ny = e.snake.body[0]
                v = KEYS[new][0]
                self.assertEqual((nx - start[0], ny - start[1]), v)
                self.assertEqual(e.state, STATE_PLAYING)


class RapidInputTests(unittest.TestCase):
    def test_left_then_up_while_moving_right(self):
        e = make_engine()
        e.handle_keydown(pygame.K_LEFT)   # invalid: ignored
        e.handle_keydown(pygame.K_UP)     # valid: must still work
        e.step()
        self.assertEqual(e.snake.direction, UP)
        self.assertEqual(e.state, STATE_PLAYING)
        tick(e, 3)
        self.assertEqual(e.state, STATE_PLAYING)

    def test_up_then_left_in_one_tick_no_reversal_death(self):
        # The exact bug in the supplied code: UP then LEFT before a tick.
        e = make_engine()
        e.handle_keydown(pygame.K_UP)
        e.handle_keydown(pygame.K_LEFT)
        tick(e, 6)
        self.assertEqual(e.state, STATE_PLAYING)
        self.assertEqual(e.snake.direction, LEFT)  # legit UP-then-LEFT path

    def test_up_then_down_then_left_burst(self):
        e = make_engine()
        for k in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT):
            e.handle_keydown(k)
        tick(e, 10)
        self.assertEqual(e.state, STATE_PLAYING)

    def test_random_key_mashing_never_dies_from_reversal(self):
        import random
        rng = random.Random(1234)
        pool = [k for _, ks in KEYS.values() for k in ks]
        for trial in range(300):
            e = make_engine()
            e.food.x, e.food.y = -1, -1  # keep food out of the way
            for _ in range(40):
                for _ in range(rng.randint(0, 4)):
                    e.handle_keydown(rng.choice(pool))
                prev_body = list(e.snake.body)
                e.step()
                if e.state != STATE_PLAYING:
                    # Any death must be a genuine wall/self collision,
                    # never a neck hit (head == segment 1 before the move).
                    head = e.snake.body[0]
                    self.assertNotEqual(head, prev_body[1], "reversal collision")
                    break

    def test_turn_queue_is_bounded(self):
        s = Snake(10, 10, 20)
        accepted = [s.set_direction(*d) for d in (UP, LEFT, DOWN, RIGHT, UP, LEFT)]
        self.assertLessEqual(len(s.pending_directions), Snake.MAX_QUEUED_TURNS)
        self.assertEqual(accepted[:3], [True, True, True])
        self.assertFalse(any(accepted[3:]))


class FoodTests(unittest.TestCase):
    def test_eat_grows_scores_respawns(self):
        e = make_engine()
        hx, hy = e.snake.body[0]
        e.food.x, e.food.y = hx + 1, hy
        length = len(e.snake.body)
        e.step()
        self.assertEqual(e.score, 1)
        self.assertIn("eat", e.sound.played)
        self.assertNotIn(e.food.position(), e.snake.body)
        tick(e, 1)
        self.assertEqual(len(e.snake.body), length + 1)

    def test_food_never_on_snake_at_start_or_after_respawn(self):
        for _ in range(3000):
            e = make_engine()
            self.assertNotIn(e.food.position(), e.snake.body)
            self.assertTrue(0 <= e.food.x < e.grid_width and 0 <= e.food.y < e.grid_height)

    def test_food_respawn_many_times_never_on_snake_and_in_bounds(self):
        e = make_engine()
        e.snake.body = [(x, 5) for x in range(25, 0, -1)]
        for _ in range(2000):
            self.assertTrue(e.food.respawn(e.snake.body))
            self.assertNotIn(e.food.position(), e.snake.body)
            self.assertTrue(0 <= e.food.x < e.grid_width and 0 <= e.food.y < e.grid_height)

    def test_food_full_board_does_not_hang(self):
        f = Food(3, 3, 20)
        cells = [(x, y) for x in range(3) for y in range(3)]
        self.assertFalse(f.respawn(cells))
        # one free cell -> must pick exactly it
        self.assertTrue(f.respawn(cells[1:]))
        self.assertEqual(f.position(), cells[0])

    def test_score_multiple_foods(self):
        e = make_engine()
        for i in range(1, 6):
            hx, hy = e.snake.body[0]
            e.food.x, e.food.y = hx + 1, hy
            e.step()
            self.assertEqual(e.score, i)


class CollisionTests(unittest.TestCase):
    def test_wall_collision_all_four_walls(self):
        setups = {
            "RIGHT": (28, 10), "LEFT": (1, 10), "UP": (10, 1), "DOWN": (10, 28),
        }
        for name, (x, y) in setups.items():
            e = make_engine()
            dx, dy = KEYS[name][0]
            e.snake.body = [(x, y), (x - dx, y - dy), (x - 2 * dx, y - 2 * dy)]
            e.snake.direction = KEYS[name][0]
            e.food.x, e.food.y = -1, -1
            e.step()
            self.assertEqual(e.state, STATE_PLAYING, f"{name}: last in-bounds cell is legal")
            e.step()
            self.assertEqual(e.state, STATE_GAME_OVER, f"{name} wall")

    def test_no_false_wall_collision_on_edge_cells(self):
        e = make_engine()
        e.snake.body = [(29, 29), (28, 29), (27, 29)]
        e.snake.direction = RIGHT
        e.snake.pending_directions.clear()
        e.food.x, e.food.y = 0, 0
        self.assertFalse(e.snake.collides_with_wall(30, 30))
        e.snake.body = [(0, 0), (1, 0), (2, 0)]
        self.assertFalse(e.snake.collides_with_wall(30, 30))

    def test_self_collision(self):
        e = make_engine()
        e.food.x, e.food.y = -1, -1
        # Long snake, spiral into itself: RIGHT, DOWN, LEFT, UP
        e.snake.body = [(15, 10), (14, 10), (13, 10), (12, 10), (11, 10), (10, 10)]
        e.snake.direction = RIGHT
        e.handle_keydown(pygame.K_DOWN); e.step()
        e.handle_keydown(pygame.K_LEFT); e.step()
        self.assertEqual(e.state, STATE_PLAYING)
        e.handle_keydown(pygame.K_UP); e.step()
        self.assertEqual(e.state, STATE_GAME_OVER)

    def test_moving_into_vacating_tail_is_legal(self):
        # 2x2 loop: head chases its own tail. The tail cell is freed by
        # move() before the collision check, so this is NOT a collision.
        e = make_engine()
        e.food.x, e.food.y = -1, -1
        e.snake.body = [(5, 5), (5, 6), (6, 6), (6, 5)]   # tail at (6,5)
        e.snake.direction = UP
        e.snake.set_direction(*RIGHT)                       # head -> (6,5)
        e.step()
        self.assertEqual(e.snake.body[0], (6, 5))
        self.assertEqual(e.state, STATE_PLAYING)

    def test_moving_into_tail_while_growing_is_collision(self):
        e = make_engine()
        e.food.x, e.food.y = -1, -1
        e.snake.body = [(5, 5), (5, 6), (6, 6), (6, 5)]
        e.snake.direction = UP
        e.snake.set_direction(*RIGHT)
        e.snake.grow()
        e.step()
        self.assertEqual(e.state, STATE_GAME_OVER)

    def test_early_short_snake_no_false_self_collision(self):
        e = make_engine()
        e.food.x, e.food.y = -1, -1
        for k in (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN):
            e.handle_keydown(k); e.step()
            self.assertEqual(e.state, STATE_PLAYING)


class GameOverTests(unittest.TestCase):
    def crash(self, e):
        e.food.x, e.food.y = -1, -1
        for _ in range(60):
            e.step()
            if e.state != STATE_PLAYING:
                return
        self.fail("never crashed")

    def test_game_over_shows_score_and_waits(self):
        e = make_engine()
        e.score = 7
        self.crash(e)
        self.assertEqual(e.state, STATE_GAME_OVER)
        self.assertEqual(e.final_score, 7)
        self.assertEqual(e.sound.played.count("game_over"), 1)
        for _ in range(300):               # ~5 s of frames: must stay put
            e.update(16.7)
            e.render(SCREEN)
        self.assertEqual(e.state, STATE_GAME_OVER)
        self.assertFalse(e.quit_requested)

    def test_direction_keys_do_not_skip_game_over_screen(self):
        e = make_engine()
        self.crash(e)
        for k in (pygame.K_UP, pygame.K_LEFT, pygame.K_w, pygame.K_1, pygame.K_2, pygame.K_ESCAPE):
            e.handle_keydown(k)
        self.assertEqual(e.state, STATE_GAME_OVER)

    def test_enter_and_space_go_to_menu(self):
        for k in (pygame.K_RETURN, pygame.K_SPACE):
            e = make_engine()
            self.crash(e)
            e.handle_keydown(k)
            self.assertEqual(e.state, STATE_MENU)

    def test_game_over_sound_played_only_once(self):
        e = make_engine()
        self.crash(e)
        for _ in range(50):
            e.update(100)
        self.assertEqual(e.sound.played.count("game_over"), 1)


class ReplayTests(unittest.TestCase):
    def to_menu(self, e):
        e.food.x, e.food.y = -1, -1
        while e.state == STATE_PLAYING:
            e.step()
        e.handle_keydown(pygame.K_RETURN)
        self.assertEqual(e.state, STATE_MENU)

    def test_each_difficulty_starts_fresh_game_with_right_speed(self):
        expected = {pygame.K_1: ("Easy", 5), pygame.K_2: ("Medium", 8), pygame.K_3: ("Hard", 12)}
        for key, (name, speed) in expected.items():
            e = make_engine()
            e.score = 9
            self.to_menu(e)
            e.handle_keydown(key)
            self.assertEqual(e.state, STATE_PLAYING)
            self.assertEqual(e.difficulty_name, name)
            self.assertEqual(e.moves_per_second, speed)
            self.assertEqual(e.score, 0)
            self.assertEqual(e.snake.body, [(15, 15), (14, 15), (13, 15)])
            self.assertEqual(e.snake.direction, RIGHT)
            self.assertEqual(len(e.snake.pending_directions), 0)
            self.assertFalse(e.snake.grow_pending)
            self.assertNotIn(e.food.position(), e.snake.body)
            self.assertTrue(0 <= e.food.x < 30 and 0 <= e.food.y < 30)
            self.assertFalse(e.game_over)

    def test_keyboard_navigation_and_enter(self):
        e = make_engine()
        self.to_menu(e)
        e.handle_keydown(pygame.K_UP)    # Medium -> Easy
        e.handle_keydown(pygame.K_RETURN)
        self.assertEqual(e.state, STATE_PLAYING)
        self.assertEqual(e.difficulty_name, "Easy")
        e2 = make_engine()
        self.to_menu(e2)
        e2.handle_keydown(pygame.K_DOWN); e2.handle_keydown(pygame.K_s)   # -> Exit
        self.assertEqual(e2.menu_index, 3)
        e2.handle_keydown(pygame.K_RETURN)
        self.assertTrue(e2.quit_requested)

    def test_menu_wraps(self):
        e = make_engine(); self.to_menu(e)
        e.menu_index = 0
        e.handle_keydown(pygame.K_UP)
        self.assertEqual(e.menu_index, 3)
        e.handle_keydown(pygame.K_DOWN)
        self.assertEqual(e.menu_index, 0)

    def test_exit_option_and_escape(self):
        e = make_engine(); self.to_menu(e)
        e.handle_keydown(pygame.K_4)
        self.assertTrue(e.quit_requested)
        e = make_engine(); self.to_menu(e)
        e.handle_keydown(pygame.K_ESCAPE)
        self.assertTrue(e.quit_requested)

    def test_irrelevant_menu_keys_ignored(self):
        e = make_engine(); self.to_menu(e)
        for k in (pygame.K_x, pygame.K_5, pygame.K_LEFT, pygame.K_RIGHT):
            e.handle_keydown(k)
        self.assertEqual(e.state, STATE_MENU)
        self.assertFalse(e.quit_requested)

    def test_menu_render_and_game_over_render_do_not_crash(self):
        e = make_engine()
        e.food.x, e.food.y = -1, -1
        while e.state == STATE_PLAYING:
            e.step()
        e.render(SCREEN)
        e.handle_keydown(pygame.K_RETURN)
        e.render(SCREEN)

    def test_replay_many_times_no_stale_state(self):
        e = make_engine()
        for cycle in range(6):
            diff = cycle % 3
            # play: eat one food, then crash into wall
            hx, hy = e.snake.body[0]
            e.food.x, e.food.y = hx + 1, hy
            e.step()
            self.assertEqual(e.score, 1)
            e.handle_keydown(pygame.K_UP)   # leave stale queued input on purpose
            e.handle_keydown(pygame.K_LEFT)
            e.food.x, e.food.y = -1, -1
            while e.state == STATE_PLAYING:
                e.step()
            self.assertEqual(e.state, STATE_GAME_OVER)
            self.assertEqual(e.final_score, 1)
            e.handle_keydown(pygame.K_RETURN)
            e.handle_keydown((pygame.K_1, pygame.K_2, pygame.K_3)[diff])
            self.assertEqual(e.state, STATE_PLAYING)
            self.assertEqual(e.score, 0)
            self.assertEqual(len(e.snake.body), 3)
            self.assertEqual(e.snake.direction, RIGHT)
            self.assertEqual(len(e.snake.pending_directions), 0)
            self.assertEqual(e.moves_per_second, ge.DIFFICULTIES[diff][1])
        self.assertEqual(e.sound.played.count("game_over"), 6)
        self.assertEqual(e.sound.played.count("eat"), 6)


class DifficultySpeedTests(unittest.TestCase):
    def moves_in(self, difficulty_index, seconds=10.0):
        e = make_engine()
        e.reset_game(difficulty_index)
        e.food.x, e.food.y = -1, -1
        # keep the snake alive: it just counts step() calls
        count = 0
        def counting():
            nonlocal count
            count += 1
            e.snake.body = [(15, 15), (14, 15), (13, 15)]  # stay in the middle
        e.step = counting
        for _ in range(int(seconds * 60)):
            e.update(1000 / 60)
        return count

    def test_easy_slower_than_medium_slower_than_hard(self):
        easy, med, hard = (self.moves_in(i) for i in range(3))
        print(f"\n   moves in 10s @60fps -> Easy={easy} Medium={med} Hard={hard}")
        self.assertLess(easy, med)
        self.assertLess(med, hard)
        self.assertAlmostEqual(easy, 50, delta=3)
        self.assertAlmostEqual(med, 80, delta=3)
        self.assertAlmostEqual(hard, 120, delta=4)

    def test_speeds_are_sensible(self):
        for _, mps in ge.DIFFICULTIES:
            self.assertTrue(3 <= mps <= 15)


class SoundTests(unittest.TestCase):
    def test_wav_files_exist_and_load_via_relative_path(self):
        self.assertTrue(os.path.isfile(os.path.join(SOUNDS_DIR, "eat.wav")))
        self.assertTrue(os.path.isfile(os.path.join(SOUNDS_DIR, "game_over.wav")))
        self.assertFalse(SOUNDS_DIR.startswith("/Users"))
        sm = SoundManager()
        self.assertTrue(sm.enabled)
        self.assertIn("eat", sm.sounds)
        self.assertIn("game_over", sm.sounds)
        self.assertTrue(sm.play("eat"))
        self.assertTrue(sm.play("game_over"))

    def test_real_sound_manager_plays_at_right_moments(self):
        e = GameEngine(600, 600)  # real SoundManager
        plays = []
        real_play = e.sound.play
        e.sound.play = lambda n: (plays.append(n), real_play(n))[1]
        hx, hy = e.snake.body[0]
        e.food.x, e.food.y = hx + 1, hy
        e.step()
        self.assertEqual(plays, ["eat"])
        e.food.x, e.food.y = -1, -1
        while e.state == STATE_PLAYING:
            e.step()
        self.assertEqual(plays, ["eat", "game_over"])

    def test_missing_files_do_not_crash(self):
        sm = SoundManager(sounds_dir="/nonexistent/dir")
        self.assertFalse(sm.enabled)
        self.assertFalse(sm.play("eat"))
        e = GameEngine(600, 600, sound=sm)
        e.step()

    def test_mixer_init_failure_does_not_crash(self):
        real_init, real_get = pygame.mixer.init, pygame.mixer.get_init
        try:
            pygame.mixer.get_init = lambda: None
            def boom(*a, **k):
                raise pygame.error("no audio device")
            pygame.mixer.init = boom
            sm = SoundManager()
            self.assertFalse(sm.enabled)
            self.assertFalse(sm.play("eat"))
            e = GameEngine(600, 600, sound=sm)
            hx, hy = e.snake.body[0]
            e.food.x, e.food.y = hx + 1, hy
            e.step()
            e.food.x, e.food.y = -1, -1
            while e.state == STATE_PLAYING:
                e.step()
        finally:
            pygame.mixer.init, pygame.mixer.get_init = real_init, real_get


class WinTests(unittest.TestCase):
    def test_engine_ends_game_when_no_free_cell_for_food(self):
        e = GameEngine(600, 600, sound=RecordingSound())
        hx, hy = e.snake.body[0]
        e.food.x, e.food.y = hx + 1, hy
        e.food.respawn = lambda occupied: False   # board is completely full
        e.step()
        self.assertEqual(e.score, 1)
        self.assertEqual(e.state, STATE_GAME_OVER)
        self.assertTrue(e.won)
        self.assertEqual(e.final_score, 1)
        e.render(SCREEN)

    def test_respawn_on_full_board_returns_false(self):
        f = Food(30, 30, 20)
        self.assertFalse(f.respawn([(x, y) for x in range(30) for y in range(30)]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
