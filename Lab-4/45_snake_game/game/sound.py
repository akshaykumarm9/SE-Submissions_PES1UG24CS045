import os
import pygame

# Project-relative path: <project>/assets/sounds, independent of the
# current working directory and of any machine-specific location.
SOUNDS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sounds")
)

SOUND_FILES = {
    "eat": "eat.wav",
    "game_over": "game_over.wav",
}


class SoundManager:
    """Loads and plays sound effects. Never raises: if audio is unavailable
    (no device, missing file, mixer failure) the game simply runs silently."""

    def __init__(self, sounds_dir=SOUNDS_DIR):
        self.enabled = False
        self.sounds = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except (pygame.error, NotImplementedError, OSError) as exc:
            print(f"[sound] audio disabled: {exc}")
            return

        for name, filename in SOUND_FILES.items():
            path = os.path.join(sounds_dir, filename)
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except (pygame.error, FileNotFoundError, OSError) as exc:
                print(f"[sound] could not load {path}: {exc}")

        self.enabled = bool(self.sounds)

    def play(self, name):
        sound = self.sounds.get(name)
        if sound is None:
            return False
        try:
            sound.play()
            return True
        except pygame.error:
            return False
