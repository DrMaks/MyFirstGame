"""
Pixel Rogue: Dungeon of the Ancients
Root executable entry point.
"""

import sys
import os

# Ensure the project root is in Python sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.engine.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
