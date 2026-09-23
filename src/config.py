"""
Game configuration constants, color palettes, and settings.
"""

# Window and Display
GAME_TITLE = "Pixel Rogue: Dungeon of the Ancients"
VIRTUAL_WIDTH = 480
VIRTUAL_HEIGHT = 270
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720
FPS = 60
TILE_SIZE = 16

# Retro Color Palette (inspired by DawnBringer 32 & Pico-8)
COLOR_BLACK = (20, 18, 29)
COLOR_DARK_BLUE = (34, 32, 52)
COLOR_PURPLE = (63, 63, 116)
COLOR_RED = (217, 87, 99)
COLOR_ORANGE = (215, 123, 63)
COLOR_YELLOW = (251, 242, 54)
COLOR_GREEN = (106, 190, 48)
COLOR_TEAL = (91, 110, 225)
COLOR_CYAN = (99, 155, 255)
COLOR_LIGHT_GRAY = (155, 173, 183)
COLOR_WHITE = (245, 245, 255)
COLOR_BROWN = (102, 57, 49)
COLOR_DARK_GRAY = (69, 40, 60)
COLOR_GOLD = (238, 195, 44)
COLOR_SHADOW = (10, 8, 15, 120)

# Gameplay Balance
PLAYER_BASE_HP = 100
PLAYER_BASE_SPEED = 120.0
PLAYER_DASH_SPEED = 300.0
PLAYER_DASH_DURATION = 0.20  # seconds
PLAYER_DASH_COOLDOWN = 0.80  # seconds
PLAYER_INVULN_AFTER_HIT = 0.60

# Audio settings
DEFAULT_MASTER_VOLUME = 0.8
DEFAULT_MUSIC_VOLUME = 0.6
DEFAULT_SFX_VOLUME = 0.85

# Steam Info
STEAM_APP_ID = 480  # Default Spacewar AppID for testing

import pygame

def get_font(size, bold=True):
    for name in ('consolas', 'tahoma', 'segoeui', 'arial'):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)
