"""
Enemy AI, Behaviors, and Boss Encounter with Multi-Floor Difficulty Scaling.
Includes Slime, Skeleton Archer, Dark Mage, Goblin Bombardier, Wraith, Stone Golem, and the Dungeon Overlord.
"""

import math
import random
import pygame
from src.config import (
    COLOR_RED, COLOR_PURPLE, COLOR_YELLOW, COLOR_WHITE, COLOR_ORANGE, COLOR_CYAN, TILE_SIZE
)
from src.entities.projectile import Projectile
from src.entities.drops import Coin, PotionDrop, GemDrop


class BaseEnemy:
    def __init__(self, x, y, hp, speed, enemy_type, floor=1):
        self.x = float(x)
        self.y = float(y)
        floor_mult = 1.0 + (floor - 1) * 0.30
        scaled_hp = int(hp * floor_mult)
        self.max_hp = scaled_hp
        self.hp = scaled_hp
        self.speed = speed
        self.enemy_type = enemy_type
        self.facing_left = False
        self.anim_timer = 0.0
        self.current_frame = 0
        self.hitbox_radius = 7
        self.contact_damage = int(10 * floor_mult)
        self.xp_value = int(15 * floor_mult)
        self.is_boss = False
        self.armor_ratio = 1.0  # 1.0 = normal, 0.65 = armored

    @property
    def rect(self):
        r = self.hitbox_radius
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def take_damage(self, damage, audio, particles, is_crit=False):
        effective_dmg = max(1, int(damage * self.armor_ratio))
        self.hp -= effective_dmg
        audio.play("hit")
        particles.spawn_blood(self.x, self.y, count=5)
        particles.add_damage_text(self.x, self.y, effective_dmg, is_crit=is_crit)
        return self.hp <= 0

    def on_death(self, drops, audio, particles, steam):
        audio.play("enemy_die")
        particles.spawn_blood(self.x, self.y, count=12)
        steam.unlock_achievement("ACH_FIRST_BLOOD")

        # Drop coins
        for _ in range(random.randint(1, 3)):
            drops.append(Coin(self.x + random.uniform(-6, 6), self.y + random.uniform(-6, 6), value=1))

        # Chance for health potion or gems
        roll = random.random()
        if roll < 0.15:
            drops.append(PotionDrop(self.x, self.y, "hp"))
        elif roll < 0.25:
            drops.append(GemDrop(self.x, self.y, "ruby"))


class Slime(BaseEnemy):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, hp=45, speed=55.0, enemy_type="slime", floor=floor)
        self.contact_damage = int(12 * (1.0 + (floor - 1) * 0.25))
        self.xp_value = 18
        self.hop_timer = random.uniform(0.0, 1.0)
        self.is_hopping = False

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 6.0
        self.current_frame = int(self.anim_timer) % 2

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 220.0 and dist > 0.1:
            self.facing_left = (dx < 0)
            self.hop_timer += dt
            if self.hop_timer > 1.2:
                self.is_hopping = True
                if self.hop_timer > 1.6:
                    self.hop_timer = 0.0
                    self.is_hopping = False

            speed = self.speed * (2.0 if self.is_hopping else 0.4)
            mx = (dx / dist) * speed * dt
            my = (dy / dist) * speed * dt

            self.x += mx
            if tilemap.collides_with_wall(self.rect):
                self.x -= mx
            self.y += my
            if tilemap.collides_with_wall(self.rect):
                self.y -= my

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite = art.get_sprite(f"slime_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))


class SkeletonArcher(BaseEnemy):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, hp=50, speed=40.0, enemy_type="skeleton", floor=floor)
        self.contact_damage = int(8 * (1.0 + (floor - 1) * 0.25))
        self.xp_value = 22
        self.shoot_cooldown = random.uniform(1.0, 2.2)

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 4.0
        self.current_frame = int(self.anim_timer) % 2

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 250.0 and dist > 0.1:
            self.facing_left = (dx < 0)
            ideal_dist = 110.0

            if dist < ideal_dist - 20:
                mx = -(dx / dist) * self.speed * dt
                my = -(dy / dist) * self.speed * dt
            elif dist > ideal_dist + 20:
                mx = (dx / dist) * self.speed * dt
                my = (dy / dist) * self.speed * dt
            else:
                mx, my = 0, 0

            self.x += mx
            if tilemap.collides_with_wall(self.rect):
                self.x -= mx
            self.y += my
            if tilemap.collides_with_wall(self.rect):
                self.y -= my

            self.shoot_cooldown -= dt
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = 2.0
                angle = math.atan2(dy, dx)
                projectiles.append(Projectile(
                    self.x, self.y, angle, speed=180.0, damage=14,
                    is_player=False, color=COLOR_YELLOW, size=3
                ))
                audio.play("shoot")

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite = art.get_sprite(f"skeleton_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))


class DarkMage(BaseEnemy):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, hp=60, speed=30.0, enemy_type="mage", floor=floor)
        self.contact_damage = 10
        self.xp_value = 30
        self.cast_cooldown = random.uniform(1.5, 3.0)

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 3.0
        self.current_frame = int(self.anim_timer) % 2

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 280.0 and dist > 0.1:
            self.facing_left = (dx < 0)
            self.cast_cooldown -= dt
            if self.cast_cooldown <= 0:
                self.cast_cooldown = 2.8
                base_angle = math.atan2(dy, dx)
                for offset in (-0.2, 0.2):
                    projectiles.append(Projectile(
                        self.x, self.y, base_angle + offset, speed=150.0, damage=18,
                        is_player=False, color=COLOR_PURPLE, size=4
                    ))
                audio.play("shoot")

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite = art.get_sprite(f"mage_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))


class GoblinBombardier(BaseEnemy):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, hp=65, speed=46.0, enemy_type="goblin", floor=floor)
        self.contact_damage = 14
        self.xp_value = 28
        self.bomb_cooldown = random.uniform(2.0, 3.5)

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 5.0
        self.current_frame = int(self.anim_timer) % 2

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 260.0 and dist > 0.1:
            self.facing_left = (dx < 0)
            # Maintain skirmish distance
            if dist < 80.0:
                mx = -(dx / dist) * self.speed * dt
                my = -(dy / dist) * self.speed * dt
            else:
                mx = (dx / dist) * (self.speed * 0.7) * dt
                my = (dy / dist) * (self.speed * 0.7) * dt

            self.x += mx
            if tilemap.collides_with_wall(self.rect):
                self.x -= mx
            self.y += my
            if tilemap.collides_with_wall(self.rect):
                self.y -= my

            self.bomb_cooldown -= dt
            if self.bomb_cooldown <= 0:
                self.bomb_cooldown = 3.0
                angle = math.atan2(dy, dx)
                # Throw glowing bomb projectile
                projectiles.append(Projectile(
                    self.x, self.y, angle, speed=130.0, damage=22,
                    is_player=False, color=COLOR_ORANGE, size=5
                ))
                audio.play("shoot")

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite = art.get_sprite(f"goblin_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))


class Wraith(BaseEnemy):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, hp=75, speed=50.0, enemy_type="wraith", floor=floor)
        self.contact_damage = 18
        self.xp_value = 35
        self.frost_cooldown = random.uniform(1.8, 3.0)

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 3.0
        self.current_frame = int(self.anim_timer) % 2

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 300.0 and dist > 0.1:
            self.facing_left = (dx < 0)
            # Wraith floats directly through walls!
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

            self.frost_cooldown -= dt
            if self.frost_cooldown <= 0:
                self.frost_cooldown = 2.5
                angle = math.atan2(dy, dx)
                projectiles.append(Projectile(
                    self.x, self.y, angle, speed=140.0, damage=16,
                    is_player=False, color=COLOR_CYAN, size=4
                ))
                audio.play("shoot")

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite = art.get_sprite(f"wraith_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))


class StoneGolem(BaseEnemy):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, hp=220, speed=26.0, enemy_type="golem", floor=floor)
        self.hitbox_radius = 11
        self.armor_ratio = 0.65  # Takes 35% reduced damage
        self.contact_damage = 25
        self.xp_value = 50
        self.slam_timer = 2.5

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 2.5
        self.current_frame = int(self.anim_timer) % 2

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0.1:
            self.facing_left = (dx < 0)
            mx = (dx / dist) * self.speed * dt
            my = (dy / dist) * self.speed * dt
            self.x += mx
            if tilemap.collides_with_wall(self.rect):
                self.x -= mx
            self.y += my
            if tilemap.collides_with_wall(self.rect):
                self.y -= my

        # Ground shockwave slam
        self.slam_timer -= dt
        if self.slam_timer <= 0 and dist < 120.0:
            self.slam_timer = 3.2
            audio.play("explosion")
            # 4 cross-shockwaves
            for ang in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
                projectiles.append(Projectile(
                    self.x, self.y, ang, speed=110.0, damage=18,
                    is_player=False, color=COLOR_YELLOW, size=5
                ))

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 12, self.y - 12)
        sprite = art.get_sprite(f"golem_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))


class DungeonOverlord(BaseEnemy):
    def __init__(self, x, y, floor=3):
        super().__init__(x, y, hp=680, speed=46.0, enemy_type="boss", floor=floor)
        self.hitbox_radius = 14
        self.contact_damage = 28
        self.xp_value = 200
        self.is_boss = True
        self.attack_timer = 2.0
        self.enraged = False
        self.attack_pattern = 0

    def update(self, player, tilemap, dt, projectiles, audio):
        self.anim_timer += dt * 4.0
        self.current_frame = int(self.anim_timer) % 2

        if not self.enraged and self.hp < self.max_hp * 0.5:
            self.enraged = True
            self.speed = 68.0
            audio.play("explosion")

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0.1:
            self.facing_left = (dx < 0)
            mx = (dx / dist) * self.speed * dt
            my = (dy / dist) * self.speed * dt
            self.x += mx
            if tilemap.collides_with_wall(self.rect):
                self.x -= mx
            self.y += my
            if tilemap.collides_with_wall(self.rect):
                self.y -= my

        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.attack_pattern = (self.attack_pattern + 1) % (3 if self.enraged else 2)
            base_angle = math.atan2(dy, dx)

            if self.attack_pattern == 0:
                self.attack_timer = 1.7 if not self.enraged else 1.1
                for offset in (-0.25, 0.0, 0.25):
                    projectiles.append(Projectile(
                        self.x, self.y, base_angle + offset, speed=190.0, damage=20,
                        is_player=False, color=COLOR_RED, size=5
                    ))
                audio.play("shoot")

            elif self.attack_pattern == 1:
                self.attack_timer = 2.0 if not self.enraged else 1.4
                for offset in (-0.4, -0.2, 0.0, 0.2, 0.4):
                    projectiles.append(Projectile(
                        self.x, self.y, base_angle + offset, speed=160.0, damage=18,
                        is_player=False, color=COLOR_ORANGE, size=4
                    ))
                audio.play("shoot")

            elif self.attack_pattern == 2 and self.enraged:
                self.attack_timer = 1.9
                for i in range(8):
                    ang = i * (math.pi / 4.0)
                    projectiles.append(Projectile(
                        self.x, self.y, ang, speed=145.0, damage=16,
                        is_player=False, color=COLOR_PURPLE, size=4
                    ))
                audio.play("explosion")

    def on_death(self, drops, audio, particles, steam):
        super().on_death(drops, audio, particles, steam)
        steam.unlock_achievement("ACH_BOSS_SLAYER")
        for _ in range(16):
            drops.append(Coin(self.x + random.uniform(-20, 20), self.y + random.uniform(-20, 20), value=random.randint(4, 9)))
        drops.append(PotionDrop(self.x, self.y, "hp"))
        drops.append(GemDrop(self.x + 10, self.y + 10, "sapphire"))

    def draw(self, surface, camera, art):
        screen_x, screen_y = camera.apply_pos(self.x - 16, self.y - 16)
        sprite = art.get_sprite(f"boss_{self.current_frame}")
        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (screen_x, screen_y))
