"""
Loot Drops: Coins, Potions, Chests, Relics, Scrolls, Gems, and Stairs Portal.
"""

import math
import random
import pygame
from src.config import TILE_SIZE, COLOR_GOLD, COLOR_WHITE, COLOR_CYAN, COLOR_RED, COLOR_ORANGE


class Coin:
    def __init__(self, x, y, value=1):
        self.x = float(x)
        self.y = float(y)
        self.value = value
        self.radius = 4
        self.float_offset = 0.0
        self.timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, player, dt):
        self.timer += dt * 5.0
        self.float_offset = math.sin(self.timer) * 1.5

        # Magnet effect towards player (boosted by greed talent)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        pickup_radius = getattr(player, "magnet_radius", 45.0)

        if dist < pickup_radius and dist > 0.01:
            speed = 160.0 * (1.0 - dist / pickup_radius) + 70.0
            self.x += (dx / dist) * speed * dt
            self.y += (dy / dist) * speed * dt

        # Collect check
        if dist < 12.0:
            player.add_gold(self.value)
            return False
        return True

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x, self.y + self.float_offset)
        coin_surf = art.get_sprite("coin")
        surface.blit(coin_surf, (screen_x - 4, screen_y - 4))


class GemDrop:
    def __init__(self, x, y, gem_type="ruby"):
        self.x = float(x)
        self.y = float(y)
        self.gem_type = gem_type
        self.value = 15 if gem_type == "ruby" else 30
        self.timer = random.uniform(0, 3)

    def update(self, player, dt):
        self.timer += dt * 4.0
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        pickup_radius = getattr(player, "magnet_radius", 45.0) * 1.2
        if dist < pickup_radius and dist > 0.01:
            speed = 170.0 * (1.0 - dist / pickup_radius) + 80.0
            self.x += (dx / dist) * speed * dt
            self.y += (dy / dist) * speed * dt

        if dist < 14.0:
            player.add_gold(self.value)
            return False
        return True

    def draw(self, surface, camera, art):
        bob = math.sin(self.timer) * 2.0
        screen_x, screen_y = camera.apply_pos(self.x, self.y + bob)
        sprite = art.get_sprite(f"gem_{self.gem_type}")
        surface.blit(sprite, (screen_x - 5, screen_y - 5))


class PotionDrop:
    def __init__(self, x, y, potion_type="hp"):
        self.x = float(x)
        self.y = float(y)
        self.potion_type = potion_type
        self.timer = 0.0

    def update(self, player, dt):
        self.timer += dt * 4.0
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 14.0:
            if self.potion_type == "hp":
                if player.hp < player.max_hp:
                    player.heal(35)
                    return False
            else:
                player.add_xp(25)
                return False
        return True

    def draw(self, surface, camera, art):
        bob = math.sin(self.timer) * 1.5
        screen_x, screen_y = camera.apply_pos(self.x, self.y + bob)
        sprite = art.get_sprite(f"potion_{self.potion_type}")
        surface.blit(sprite, (screen_x - 5, screen_y - 6))


class ScrollDrop:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.timer = 0.0

    def update(self, player, dt):
        self.timer += dt * 4.0
        dx = player.x - self.x
        dy = player.y - self.y
        if math.hypot(dx, dy) < 14.0:
            # Grant meteor trigger on player
            player.has_meteor_scroll = True
            return False
        return True

    def draw(self, surface, camera, art):
        bob = math.sin(self.timer) * 2.0
        screen_x, screen_y = camera.apply_pos(self.x, self.y + bob)
        sprite = art.get_sprite("scroll_meteor")
        surface.blit(sprite, (screen_x - 6, screen_y - 6))


class ShieldDrop:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.timer = 0.0

    def update(self, player, dt):
        self.timer += dt * 4.0
        dx = player.x - self.x
        dy = player.y - self.y
        if math.hypot(dx, dy) < 14.0:
            player.shield_charges = getattr(player, "shield_charges", 0) + 1
            return False
        return True

    def draw(self, surface, camera, art):
        bob = math.sin(self.timer) * 2.0
        screen_x, screen_y = camera.apply_pos(self.x, self.y + bob)
        sprite = art.get_sprite("relic_shield")
        surface.blit(sprite, (screen_x - 6, screen_y - 6))


class MagnetDrop:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.timer = 0.0

    def update(self, player, dt):
        self.timer += dt * 4.0
        dx = player.x - self.x
        dy = player.y - self.y
        if math.hypot(dx, dy) < 14.0:
            player.active_magnet_timer = 8.0  # Room-wide super magnet for 8s
            return False
        return True

    def draw(self, surface, camera, art):
        bob = math.sin(self.timer) * 2.0
        screen_x, screen_y = camera.apply_pos(self.x, self.y + bob)
        sprite = art.get_sprite("relic_magnet")
        surface.blit(sprite, (screen_x - 6, screen_y - 6))


class Chest:
    def __init__(self, tile_x, tile_y, tier="wood"):
        self.x = tile_x * TILE_SIZE + TILE_SIZE // 2
        self.y = tile_y * TILE_SIZE + TILE_SIZE // 2
        self.tier = tier  # "wood" or "gold"
        self.opened = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 8), int(self.y - 8), 16, 16)

    def can_interact(self, player):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        return not self.opened and dist < 26.0

    def open(self, player, drops_list, audio, particles, steam):
        if self.opened:
            return
        self.opened = True
        audio.play("chest")
        particles.spawn_spark(self.x, self.y, count=20, color=COLOR_GOLD)

        if self.tier == "gold":
            # Royal Chest: Tons of coins, gems, scrolls or relics
            for _ in range(random.randint(6, 12)):
                cx = self.x + random.uniform(-14, 14)
                cy = self.y + random.uniform(-14, 14)
                drops_list.append(Coin(cx, cy, value=random.randint(3, 7)))

            drops_list.append(GemDrop(self.x - 8, self.y + 8, random.choice(["ruby", "sapphire"])))
            loot_choice = random.choice(["scroll", "shield", "magnet", "hp"])
            if loot_choice == "scroll":
                drops_list.append(ScrollDrop(self.x + 8, self.y + 8))
            elif loot_choice == "shield":
                drops_list.append(ShieldDrop(self.x + 8, self.y + 8))
            elif loot_choice == "magnet":
                drops_list.append(MagnetDrop(self.x + 8, self.y + 8))
            else:
                drops_list.append(PotionDrop(self.x + 8, self.y + 8, "hp"))
        else:
            # Wooden Chest
            for _ in range(random.randint(3, 6)):
                cx = self.x + random.uniform(-10, 10)
                cy = self.y + random.uniform(-10, 10)
                drops_list.append(Coin(cx, cy, value=random.randint(1, 4)))

            roll = random.random()
            if roll < 0.4:
                drops_list.append(PotionDrop(self.x, self.y + 10, "hp"))
            elif roll < 0.7:
                drops_list.append(ShieldDrop(self.x, self.y + 10))
            elif roll < 0.85:
                drops_list.append(ScrollDrop(self.x, self.y + 10))
            else:
                drops_list.append(GemDrop(self.x, self.y + 10, "ruby"))

        steam.unlock_achievement("ACH_CHEST_HUNTER")

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        prefix = "chest_gold" if self.tier == "gold" else "chest"
        sprite = art.get_sprite(f"{prefix}_open" if self.opened else f"{prefix}_closed")
        surface.blit(sprite, (screen_x, screen_y))


class StairsPortal:
    def __init__(self, tile_x, tile_y, target_floor=2):
        self.x = tile_x * TILE_SIZE + TILE_SIZE // 2
        self.y = tile_y * TILE_SIZE + TILE_SIZE // 2
        self.target_floor = target_floor
        self.timer = 0.0

    def can_interact(self, player):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        return dist < 28.0

    def update(self, dt):
        self.timer += dt * 4.0

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite = art.get_sprite("tile_stairs")
        surface.blit(sprite, (screen_x, screen_y))
        # Pulsing rune glow
        glow_radius = int(3 + math.sin(self.timer) * 1.5)
        pygame.draw.circle(surface, COLOR_CYAN, (screen_x + 8, screen_y + 8), glow_radius, 1)
