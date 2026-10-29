# Snake Game

A grid-based Snake game built with **Python + Pygame**.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ and Pygame (see `requirements.txt`). No other dependencies.

## Controls

| Where            | Keys                                                        |
| ---------------- | ----------------------------------------------------------- |
| Playing          | Arrow keys or `W` `A` `S` `D`                               |
| Game Over screen | `ENTER` (or `SPACE`) to continue to the replay menu         |
| Replay menu      | `1` Easy, `2` Medium, `3` Hard, `4` Exit — or `UP`/`DOWN` + `ENTER`; `ESC` exits |

## Features

- Smooth grid movement, growing snake, food, score
- Fair direction handling: no instant 180-degree reversals, and fast key
  sequences (e.g. `LEFT` then `UP` while moving right) are handled safely
- Proper **Game Over** screen showing the final score; it stays until you press a key
- **Replay menu** with difficulty selection (repeatable any number of times)
  - Easy = 5 moves/second, Medium = 8 moves/second, Hard = 12 moves/second
- **Sound effects** for eating food and for Game Over (the game runs silently if
  audio is unavailable)

## Project structure

```
45_snake_final/
├── main.py                 # window + main loop
├── requirements.txt
├── README.md
├── game/
│   ├── __init__.py
│   ├── game_engine.py      # states (playing / game over / menu), update, rendering
│   ├── snake.py            # snake body, direction queue, collision checks
│   ├── food.py             # food spawning on free cells only
│   └── sound.py            # safe sound loading/playback
├── assets/
│   └── sounds/
│       ├── eat.wav
│       └── game_over.wav
└── tests/
    └── test_game.py        # headless unit tests
```

## Tests (optional)

```bash
python -m unittest discover -s tests -v
```

The tests run headless (they use SDL's dummy video/audio drivers).

## How the key fixes work

- **Direction queue** (`snake.py`): key presses are validated against the direction
  the snake *will* be moving after earlier queued turns, then applied one per tick.
  A reversal can therefore never be applied, even when several keys arrive
  between two ticks.
- **Collision order**: the snake moves first (the tail cell is vacated), then wall and
  self collisions are checked, so moving into the cell the tail just left is legal
  but hitting any other body segment is not.
- **Food** (`food.py`): chosen from the list of free cells, so it never lands on the
  snake and can never loop forever.
