"""
Pixel Rogue: Mobile Edition (Google Play Market).
Dedicated entry point for Android mobile devices and desktop touch simulator.
Initializes touch controls, virtual joystick, and Google Play Games Services.
"""

import sys
import os
import pygame

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import GAME_TITLE
from src.engine.game import Game


def main():
    print("=" * 60)
    print("Pixel Rogue: Dungeon of the Ancients [Google Play / Mobile Edition]")
    print("Touch Controls & Virtual Gamepad Enabled")
    print("=" * 60)

    # Initialize in mobile mode
    game = Game(is_mobile=True)

    # On Android devices, start fullscreen in landscape
    is_android = "android" in sys.platform or hasattr(sys, "getandroidapilevel")
    if is_android:
        try:
            game.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            info = pygame.display.Info()
            game.window_w = info.current_w
            game.window_h = info.current_h
        except Exception as e:
            print(f"Could not switch to Android Fullscreen: {e}")

    # Start main game loop
    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
