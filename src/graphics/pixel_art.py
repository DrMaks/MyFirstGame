"""
Procedural Pixel Art Generator in the aesthetic of Loop Hero and Travellers Rest.
Rich dark fantasy palette, atmospheric dungeon tiles, new enemies, expanded loot, and custom cursors.
"""

import math
import pygame
from src.config import (
    COLOR_BLACK, COLOR_DARK_BLUE, COLOR_PURPLE, COLOR_RED,
    COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN, COLOR_TEAL,
    COLOR_CYAN, COLOR_LIGHT_GRAY, COLOR_WHITE, COLOR_BROWN,
    COLOR_DARK_GRAY, COLOR_GOLD, TILE_SIZE
)


class PixelArtGenerator:
    def __init__(self):
        self.cache = {}

    def get_sprite(self, name):
        if name in self.cache:
            return self.cache[name]
        sprite = self._generate(name)
        self.cache[name] = sprite
        return sprite

    def _generate(self, name):
        # Player frames
        if name == "player_idle_0":
            return self._make_player(frame=0)
        elif name == "player_idle_1":
            return self._make_player(frame=1)
        elif name == "player_walk_0":
            return self._make_player(frame=2)
        elif name == "player_walk_1":
            return self._make_player(frame=3)

        # Enemies
        elif name.startswith("slime_"):
            frame = int(name.split("_")[-1])
            return self._make_slime(frame)
        elif name.startswith("skeleton_"):
            frame = int(name.split("_")[-1])
            return self._make_skeleton(frame)
        elif name.startswith("mage_"):
            frame = int(name.split("_")[-1])
            return self._make_mage(frame)
        elif name.startswith("goblin_"):
            frame = int(name.split("_")[-1])
            return self._make_goblin(frame)
        elif name.startswith("wraith_"):
            frame = int(name.split("_")[-1])
            return self._make_wraith(frame)
        elif name.startswith("golem_"):
            frame = int(name.split("_")[-1])
            return self._make_golem(frame)
        elif name.startswith("boss_"):
            frame = int(name.split("_")[-1])
            return self._make_boss(frame)

        # World tiles (Loop Hero & Travellers Rest detailed style)
        elif name == "tile_floor_0":
            return self._make_floor(variant=0)
        elif name == "tile_floor_1":
            return self._make_floor(variant=1)  # Mossy
        elif name == "tile_floor_cracked":
            return self._make_floor(variant=2)
        elif name == "tile_floor_wood":
            return self._make_wood_floor()
        elif name == "tile_wall_top":
            return self._make_wall(part="top")
        elif name == "tile_wall_front":
            return self._make_wall(part="front")
        elif name == "tile_column":
            return self._make_column()
        elif name == "tile_banner":
            return self._make_banner()
        elif name == "tile_stairs":
            return self._make_stairs()
        elif name == "tile_torch_0":
            return self._make_torch(frame=0)
        elif name == "tile_torch_1":
            return self._make_torch(frame=1)

        # Items and weapons
        elif name == "sword":
            return self._make_sword()
        elif name == "staff":
            return self._make_staff()
        elif name == "bow":
            return self._make_bow()
        elif name == "chest_closed":
            return self._make_chest(open_state=False, tier="wood")
        elif name == "chest_open":
            return self._make_chest(open_state=True, tier="wood")
        elif name == "chest_gold_closed":
            return self._make_chest(open_state=False, tier="gold")
        elif name == "chest_gold_open":
            return self._make_chest(open_state=True, tier="gold")
        elif name == "coin":
            return self._make_coin()
        elif name == "potion_hp":
            return self._make_potion(COLOR_RED)
        elif name == "potion_mana":
            return self._make_potion(COLOR_CYAN)

        # New Loot: Relics, scrolls, gems
        elif name == "scroll_meteor":
            return self._make_scroll()
        elif name == "relic_shield":
            return self._make_shield()
        elif name == "relic_magnet":
            return self._make_magnet()
        elif name == "gem_ruby":
            return self._make_gem(COLOR_RED)
        elif name == "gem_sapphire":
            return self._make_gem(COLOR_CYAN)

        # Custom Cursors
        elif name == "cursor_normal":
            return self._make_cursor(interact=False)
        elif name == "cursor_interact":
            return self._make_cursor(interact=True)

        # Fallback surface
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        surf.fill(COLOR_RED)
        return surf

    def _make_cursor(self, interact=False):
        surf = pygame.Surface((14, 14), pygame.SRCALPHA)
        center = 7
        color = COLOR_GOLD if interact else COLOR_CYAN

        # Center dot
        surf.set_at((center, center), COLOR_WHITE)
        # Crosshair notches
        surf.set_at((center - 4, center), color)
        surf.set_at((center + 4, center), color)
        surf.set_at((center, center - 4), color)
        surf.set_at((center, center + 4), color)

        if interact:
            # Diamond corners when hovering over button/chest
            surf.set_at((center - 3, center - 3), COLOR_GOLD)
            surf.set_at((center + 3, center - 3), COLOR_GOLD)
            surf.set_at((center - 3, center + 3), COLOR_GOLD)
            surf.set_at((center + 3, center + 3), COLOR_GOLD)
        return surf

    def _make_player(self, frame=0):
        # 16x16 Loop Hero styled cloaked adventurer
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        bob = 1 if frame in (1, 3) else 0

        # Shadow
        pygame.draw.ellipse(surf, (10, 8, 15, 110), (3, 13, 10, 3))

        # Flowing cloak (Dark teal / deep slate)
        pygame.draw.polygon(surf, (36, 48, 76), [(4, 8 + bob), (11, 8 + bob), (13, 14), (2, 14)])
        # Inner tunic
        pygame.draw.rect(surf, (55, 80, 125), (5, 7 + bob, 6, 6))

        # Belt and golden buckle
        pygame.draw.line(surf, COLOR_BROWN, (5, 11 + bob), (10, 11 + bob))
        surf.set_at((7, 11 + bob), COLOR_GOLD)

        # Hood / Helmet (Gothic hood with shadowed face)
        pygame.draw.rect(surf, (28, 38, 62), (5, 2 + bob, 6, 5))
        pygame.draw.rect(surf, (15, 12, 24), (6, 4 + bob, 4, 3))  # Shadowed eye cavity
        # Piercing glowing cyan eyes
        surf.set_at((6, 4 + bob), COLOR_CYAN)
        surf.set_at((8, 4 + bob), COLOR_CYAN)

        # Plume / helm feather
        surf.set_at((7, 1 + bob), COLOR_RED)

        # Boots
        if frame == 2:
            surf.set_at((5, 14), (80, 48, 40))
            surf.set_at((9, 13), (80, 48, 40))
        elif frame == 3:
            surf.set_at((5, 13), (80, 48, 40))
            surf.set_at((9, 14), (80, 48, 40))
        else:
            surf.set_at((5, 14), (80, 48, 40))
            surf.set_at((9, 14), (80, 48, 40))
        return surf

    def _make_slime(self, frame=0):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (10, 8, 15, 90), (3, 13, 10, 3))
        if frame == 0:
            pygame.draw.ellipse(surf, (60, 150, 40), (3, 5, 10, 9))
            pygame.draw.ellipse(surf, (110, 210, 70), (4, 6, 8, 7))
            surf.set_at((5, 8), COLOR_WHITE)
            surf.set_at((6, 8), COLOR_BLACK)
            surf.set_at((9, 8), COLOR_WHITE)
            surf.set_at((10, 8), COLOR_BLACK)
        else:
            pygame.draw.ellipse(surf, (60, 150, 40), (2, 7, 12, 7))
            pygame.draw.ellipse(surf, (110, 210, 70), (3, 8, 10, 5))
            pygame.draw.line(surf, COLOR_BLACK, (5, 9), (6, 9))
            pygame.draw.line(surf, COLOR_BLACK, (9, 9), (10, 9))
        return surf

    def _make_skeleton(self, frame=0):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        bob = 1 if frame == 1 else 0
        pygame.draw.ellipse(surf, (10, 8, 15, 80), (4, 13, 8, 3))

        # Weathered bone skull
        pygame.draw.rect(surf, (190, 195, 185), (5, 2 + bob, 6, 5))
        surf.set_at((6, 4 + bob), (30, 20, 30))
        surf.set_at((9, 4 + bob), COLOR_RED)  # Red evil gleam

        # Ribs & spine
        pygame.draw.line(surf, (170, 175, 165), (7, 7 + bob), (7, 11 + bob))
        pygame.draw.line(surf, (210, 215, 205), (5, 8 + bob), (9, 8 + bob))
        pygame.draw.line(surf, (210, 215, 205), (6, 10 + bob), (8, 10 + bob))

        # Legs
        surf.set_at((5, 12 + bob), (170, 175, 165))
        surf.set_at((5, 13 + bob), (170, 175, 165))
        surf.set_at((9, 12 + bob), (170, 175, 165))
        surf.set_at((9, 13 + bob), (170, 175, 165))

        # Bow
        pygame.draw.line(surf, COLOR_BROWN, (12, 4 + bob), (14, 8 + bob))
        pygame.draw.line(surf, COLOR_BROWN, (14, 8 + bob), (12, 12 + bob))
        return surf

    def _make_mage(self, frame=0):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        bob = 1 if frame == 1 else 0
        pygame.draw.ellipse(surf, (10, 8, 15, 90), (3, 13, 10, 3))
        # Robe
        pygame.draw.polygon(surf, (55, 40, 85), [(7, 4 + bob), (3, 13), (12, 13)])
        # Hood
        pygame.draw.rect(surf, (35, 25, 55), (5, 2 + bob, 6, 5))
        surf.set_at((6, 4 + bob), COLOR_YELLOW)
        surf.set_at((9, 4 + bob), COLOR_YELLOW)
        # Crystal Staff
        pygame.draw.line(surf, COLOR_BROWN, (12, 4), (12, 13))
        surf.set_at((12, 3), COLOR_CYAN)
        surf.set_at((11, 2), COLOR_WHITE)
        return surf

    def _make_goblin(self, frame=0):
        # 16x16 Goblin Bombardier
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        bob = 1 if frame == 1 else 0
        pygame.draw.ellipse(surf, (10, 8, 15, 90), (3, 13, 10, 3))

        # Green head & pointed ears
        pygame.draw.rect(surf, (75, 140, 50), (5, 4 + bob, 6, 5))
        surf.set_at((4, 5 + bob), (75, 140, 50))  # Left ear
        surf.set_at((11, 5 + bob), (75, 140, 50))  # Right ear
        # Red goggle eyes
        surf.set_at((6, 5 + bob), COLOR_RED)
        surf.set_at((9, 5 + bob), COLOR_RED)

        # Leather tunic & bomb bag
        pygame.draw.rect(surf, COLOR_BROWN, (5, 9 + bob, 6, 4))
        # Ticking bomb in hand
        pygame.draw.circle(surf, (40, 35, 45), (12, 9 + bob), 3)
        surf.set_at((12, 6 + bob), COLOR_ORANGE)  # Sparking fuse
        return surf

    def _make_wraith(self, frame=0):
        # 16x16 Ghostly Wraith
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        wave = int(math.sin(frame * 3.14) * 2)

        # Ethereal floating shroud
        pygame.draw.polygon(surf, (90, 110, 160, 200), [(7, 2), (2, 12 + wave), (13, 12 - wave)])
        pygame.draw.polygon(surf, (140, 180, 230, 160), [(7, 4), (4, 11), (11, 11)])
        # Ghostly eyes
        surf.set_at((6, 5), COLOR_CYAN)
        surf.set_at((9, 5), COLOR_CYAN)
        return surf

    def _make_golem(self, frame=0):
        # 24x24 Armored Stone Golem
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        bob = 1 if frame == 1 else 0
        pygame.draw.ellipse(surf, (10, 8, 15, 120), (3, 19, 18, 5))

        # Stone body
        pygame.draw.rect(surf, (90, 95, 105), (5, 6 + bob, 14, 13))
        pygame.draw.rect(surf, (65, 70, 80), (6, 7 + bob, 12, 11))
        # Rune core
        pygame.draw.rect(surf, COLOR_CYAN, (10, 10 + bob, 4, 4))
        surf.set_at((11, 11 + bob), COLOR_WHITE)

        # Stone head
        pygame.draw.rect(surf, (110, 115, 125), (7, 2 + bob, 10, 5))
        surf.set_at((9, 4 + bob), COLOR_CYAN)
        surf.set_at((13, 4 + bob), COLOR_CYAN)

        # Moss patches on stone
        surf.set_at((6, 8 + bob), (60, 130, 50))
        surf.set_at((7, 8 + bob), (60, 130, 50))
        surf.set_at((15, 14 + bob), (60, 130, 50))
        return surf

    def _make_boss(self, frame=0):
        # 32x32 Demon Overlord
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        bob = 1 if frame == 1 else 0

        pygame.draw.ellipse(surf, (10, 8, 15, 120), (4, 26, 24, 6))

        # Wings
        wing_color = (32, 28, 50)
        pygame.draw.polygon(surf, wing_color, [(16, 10 + bob), (2, 4 + bob), (6, 16 + bob)])
        pygame.draw.polygon(surf, wing_color, [(16, 10 + bob), (30, 4 + bob), (26, 16 + bob)])

        # Body Armor & Molten Core
        pygame.draw.rect(surf, (45, 35, 55), (10, 12 + bob, 12, 14))
        pygame.draw.rect(surf, COLOR_RED, (12, 14 + bob, 8, 10))
        pygame.draw.rect(surf, COLOR_ORANGE, (13, 16 + bob, 6, 6))

        # Horned Helm
        pygame.draw.rect(surf, (20, 15, 26), (11, 4 + bob, 10, 9))
        pygame.draw.line(surf, COLOR_GOLD, (11, 5 + bob), (8, 1 + bob), 2)
        pygame.draw.line(surf, COLOR_GOLD, (20, 5 + bob), (23, 1 + bob), 2)

        # Eyes
        pygame.draw.rect(surf, COLOR_YELLOW, (13, 7 + bob, 2, 2))
        pygame.draw.rect(surf, COLOR_YELLOW, (17, 7 + bob, 2, 2))
        surf.set_at((13, 7 + bob), COLOR_RED)
        surf.set_at((17, 7 + bob), COLOR_RED)

        # Greatsword
        pygame.draw.line(surf, (200, 205, 215), (25, 4 + bob), (25, 26 + bob), 2)
        pygame.draw.line(surf, COLOR_GOLD, (22, 20 + bob), (28, 20 + bob), 2)
        return surf

    def _make_floor(self, variant=0):
        # 16x16 Loop Hero & Travellers Rest stone slate
        surf = pygame.Surface((16, 16))
        # Deep gothic slate
        surf.fill((42, 36, 52))
        pygame.draw.rect(surf, (30, 26, 40), (0, 0, 16, 16), 1)

        # Subtle stone tile grain
        surf.set_at((4, 4), (52, 46, 64))
        surf.set_at((12, 9), (52, 46, 64))
        surf.set_at((8, 12), (34, 30, 44))

        if variant == 1:
            # Mossy flagstone
            pygame.draw.rect(surf, (48, 85, 45), (3, 3, 3, 2))
            surf.set_at((4, 4), (80, 145, 65))
            surf.set_at((10, 11), (50, 95, 45))
        elif variant == 2:
            # Cracked slate
            pygame.draw.line(surf, (22, 18, 30), (3, 4), (8, 9))
            pygame.draw.line(surf, (22, 18, 30), (8, 9), (12, 8))
        return surf

    def _make_wood_floor(self):
        # Travellers Rest tavern wood plank
        surf = pygame.Surface((16, 16))
        surf.fill((110, 68, 48))
        # Planks separation
        pygame.draw.line(surf, (78, 45, 32), (0, 7), (15, 7))
        pygame.draw.line(surf, (78, 45, 32), (0, 15), (15, 15))
        # Nail studs
        surf.set_at((2, 3), (50, 30, 20))
        surf.set_at((13, 11), (50, 30, 20))
        return surf

    def _make_wall(self, part="top"):
        surf = pygame.Surface((16, 16))
        if part == "top":
            # Wall cap with stone trim
            surf.fill((28, 22, 38))
            pygame.draw.line(surf, (52, 42, 68), (0, 0), (15, 0))
            pygame.draw.line(surf, (18, 14, 26), (0, 15), (15, 15))
        elif part == "front":
            # Weathered gothic bricks with deep mortar
            surf.fill((38, 30, 50))
            pygame.draw.line(surf, (20, 15, 28), (0, 7), (15, 7))
            pygame.draw.line(surf, (20, 15, 28), (0, 15), (15, 15))
            pygame.draw.line(surf, (20, 15, 28), (7, 0), (7, 7))
            pygame.draw.line(surf, (20, 15, 28), (12, 8), (12, 15))
            pygame.draw.line(surf, (20, 15, 28), (3, 8), (3, 15))
            # Highlight on brick edges
            surf.set_at((8, 1), (55, 45, 70))
            surf.set_at((1, 8), (55, 45, 70))
        return surf

    def _make_column(self):
        # Decorative stone pillar
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Base & capital
        pygame.draw.rect(surf, (80, 85, 95), (2, 1, 12, 3))
        pygame.draw.rect(surf, (80, 85, 95), (2, 12, 12, 3))
        # Shaft
        pygame.draw.rect(surf, (60, 65, 75), (4, 4, 8, 8))
        pygame.draw.line(surf, (95, 100, 115), (5, 4), (5, 11))
        return surf

    def _make_banner(self):
        # Hanging medieval wall banner
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.line(surf, COLOR_GOLD, (2, 2), (13, 2), 2)
        # Red fabric with gold trim
        pygame.draw.polygon(surf, COLOR_RED, [(3, 3), (12, 3), (12, 12), (7, 15), (3, 12)])
        surf.set_at((7, 7), COLOR_GOLD)
        surf.set_at((7, 8), COLOR_GOLD)
        return surf

    def _make_stairs(self):
        # Descending stone stairs with glowing portal
        surf = pygame.Surface((16, 16))
        surf.fill((20, 16, 30))
        # Step contours
        pygame.draw.rect(surf, (45, 38, 55), (1, 1, 14, 4))
        pygame.draw.rect(surf, (35, 28, 45), (2, 5, 12, 4))
        pygame.draw.rect(surf, (25, 20, 35), (3, 9, 10, 4))
        pygame.draw.rect(surf, (10, 8, 18), (4, 13, 8, 3))
        # Glowing cyan runes on the top step
        surf.set_at((5, 2), COLOR_CYAN)
        surf.set_at((10, 2), COLOR_CYAN)
        return surf

    def _make_torch(self, frame=0):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.line(surf, COLOR_DARK_GRAY, (7, 8), (7, 13), 2)
        if frame == 0:
            pygame.draw.circle(surf, COLOR_ORANGE, (8, 6), 3)
            surf.set_at((8, 5), COLOR_YELLOW)
            surf.set_at((8, 4), COLOR_WHITE)
        else:
            pygame.draw.circle(surf, COLOR_ORANGE, (8, 6), 3)
            surf.set_at((7, 5), COLOR_YELLOW)
            surf.set_at((8, 3), COLOR_YELLOW)
            surf.set_at((8, 4), COLOR_WHITE)
        return surf

    def _make_chest(self, open_state=False, tier="wood"):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (10, 8, 15, 100), (1, 12, 14, 4))

        body_col = (115, 68, 50) if tier == "wood" else (175, 135, 35)
        trim_col = COLOR_GOLD if tier == "wood" else COLOR_WHITE

        pygame.draw.rect(surf, body_col, (2, 6, 12, 8))
        pygame.draw.rect(surf, trim_col, (1, 5, 14, 9), 1)

        if not open_state:
            lid_col = (135, 80, 60) if tier == "wood" else (210, 165, 45)
            pygame.draw.rect(surf, lid_col, (2, 4, 12, 4))
            surf.set_at((8, 8), COLOR_CYAN if tier == "gold" else COLOR_GOLD)
        else:
            lid_col = (135, 80, 60) if tier == "wood" else (210, 165, 45)
            pygame.draw.rect(surf, lid_col, (2, 1, 12, 4))
            pygame.draw.rect(surf, COLOR_GOLD, (4, 6, 8, 4))
            surf.set_at((7, 7), COLOR_WHITE)
        return surf

    def _make_coin(self):
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(surf, COLOR_GOLD, (4, 4), 3)
        pygame.draw.circle(surf, COLOR_YELLOW, (4, 4), 2)
        surf.set_at((3, 3), COLOR_WHITE)
        return surf

    def _make_potion(self, color):
        surf = pygame.Surface((10, 12), pygame.SRCALPHA)
        pygame.draw.rect(surf, COLOR_BROWN, (4, 1, 2, 2))
        pygame.draw.rect(surf, COLOR_LIGHT_GRAY, (4, 3, 2, 2))
        pygame.draw.circle(surf, color, (5, 8), 4)
        surf.set_at((4, 7), COLOR_WHITE)
        return surf

    def _make_scroll(self):
        # Magic Scroll of Meteor
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.rect(surf, (230, 220, 180), (2, 2, 8, 8))
        pygame.draw.rect(surf, COLOR_RED, (4, 2, 4, 8))  # Ribbon
        surf.set_at((5, 5), COLOR_GOLD)
        return surf

    def _make_shield(self):
        # Aegis Shield Relic
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.polygon(surf, COLOR_GOLD, [(6, 1), (11, 4), (10, 10), (6, 12), (2, 10), (1, 4)])
        pygame.draw.circle(surf, COLOR_CYAN, (6, 6), 2)
        return surf

    def _make_magnet(self):
        # Golden Magnet Relic
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.arc(surf, COLOR_GOLD, (1, 1, 10, 10), 0.5, 3.5, 3)
        surf.set_at((2, 8), COLOR_CYAN)
        surf.set_at((9, 8), COLOR_CYAN)
        return surf

    def _make_gem(self, color):
        # Gemstone (Ruby/Sapphire)
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(surf, color, [(5, 1), (9, 4), (5, 9), (1, 4)])
        surf.set_at((4, 3), COLOR_WHITE)
        return surf

    def _make_sword(self):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.line(surf, COLOR_WHITE, (4, 11), (12, 3), 2)
        surf.set_at((13, 2), COLOR_CYAN)
        pygame.draw.line(surf, COLOR_GOLD, (3, 9), (7, 13), 2)
        surf.set_at((2, 13), COLOR_BROWN)
        surf.set_at((1, 14), COLOR_GOLD)
        return surf

    def _make_staff(self):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.line(surf, COLOR_BROWN, (3, 12), (11, 4), 2)
        pygame.draw.circle(surf, COLOR_CYAN, (12, 3), 2)
        surf.set_at((12, 3), COLOR_WHITE)
        return surf

    def _make_bow(self):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.arc(surf, COLOR_BROWN, (2, 2, 12, 12), 0.5, 3.5, 2)
        pygame.draw.line(surf, COLOR_LIGHT_GRAY, (4, 4), (4, 12))
        return surf
