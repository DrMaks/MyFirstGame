"""
Player Entity with responsive movement, dodge roll, shooting, talents integration, and relics.
"""

import math
import random
import pygame
from src.config import (
    PLAYER_BASE_HP, PLAYER_BASE_SPEED, PLAYER_DASH_SPEED,
    PLAYER_DASH_DURATION, PLAYER_DASH_COOLDOWN, PLAYER_INVULN_AFTER_HIT,
    COLOR_CYAN, COLOR_YELLOW, COLOR_RED, COLOR_WHITE, COLOR_ORANGE, COLOR_GOLD, TILE_SIZE
)
from src.entities.projectile import Projectile


class Player:
    def __init__(self, x, y, save_manager=None):
        self.x = float(x)
        self.y = float(y)
        self.max_hp = PLAYER_BASE_HP
        self.hp = PLAYER_BASE_HP

        # Leveling & XP
        self.level = 1
        self.xp = 0
        self.xp_to_next = 50
        self.gold = 0
        self.pending_upgrades = 0

        # Movement
        self.base_speed = PLAYER_BASE_SPEED
        self.speed_mult = 1.0
        self.facing_left = False
        self.is_moving = False

        # Dash / Dodge roll
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown_base = PLAYER_DASH_COOLDOWN
        self.dash_cooldown_timer = 0.0
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0

        # Invulnerability frames
        self.invuln_timer = 0.0

        # Combat & Attacks
        self.attack_cooldown_timer = 0.0
        self.base_fire_rate = 0.28
        self.attack_speed_mult = 1.0
        self.bullet_damage = 25
        self.damage_mult = 1.0
        self.multi_shot = 1
        self.ricochet_bounces = 0
        self.has_vampirism = False
        self.fire_aura = False
        self.fire_aura_timer = 0.0

        # Talents & Relics
        self.magnet_radius = 45.0
        self.gold_mult = 1.0
        self.crit_chance = 0.15
        self.shield_charges = 0
        self.phoenix_charges = 0
        self.has_meteor_scroll = False
        self.active_magnet_timer = 0.0

        # Apply persistent talents
        if save_manager:
            vit_lvl = save_manager.get_talent_level("vitality")
            str_lvl = save_manager.get_talent_level("strength")
            agi_lvl = save_manager.get_talent_level("agility")
            grd_lvl = save_manager.get_talent_level("greed")
            let_lvl = save_manager.get_talent_level("lethality")
            phx_lvl = save_manager.get_talent_level("phoenix")

            self.max_hp += vit_lvl * 12
            self.hp = self.max_hp
            self.damage_mult += str_lvl * 0.10
            self.speed_mult += agi_lvl * 0.05
            self.dash_cooldown_base = max(0.40, PLAYER_DASH_COOLDOWN - agi_lvl * 0.06)
            self.magnet_radius = 45.0 + grd_lvl * 18.0
            self.gold_mult = 1.0 + grd_lvl * 0.15
            self.crit_chance = 0.15 + let_lvl * 0.05
            self.phoenix_charges = 1 if phx_lvl >= 1 else 0

        # Animation
        self.anim_timer = 0.0
        self.current_frame = 0

        # Hitbox
        self.hitbox_w = 10
        self.hitbox_h = 10

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.hitbox_w / 2),
            int(self.y - self.hitbox_h / 2 + 2),
            self.hitbox_w,
            self.hitbox_h
        )

    def add_gold(self, amount):
        boosted = int(amount * self.gold_mult)
        self.gold += max(1, boosted)

    def add_xp(self, amount, audio=None, particles=None, steam=None):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            self.pending_upgrades += 1
            if audio:
                audio.play("level_up")
            if particles:
                particles.spawn_level_up(self.x, self.y)
            if steam and self.level >= 5:
                steam.unlock_achievement("ACH_LEVEL_5")

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, damage, audio, particles, camera):
        if self.is_dashing or self.invuln_timer > 0:
            return False

        # Shield absorbs damage
        if self.shield_charges > 0:
            self.shield_charges -= 1
            audio.play("hit")
            particles.spawn_spark(self.x, self.y, count=14, color=COLOR_CYAN)
            camera.trigger_shake(intensity=3.0, duration=0.15)
            self.invuln_timer = PLAYER_INVULN_AFTER_HIT
            return False

        self.hp -= damage
        self.invuln_timer = PLAYER_INVULN_AFTER_HIT
        audio.play("player_hurt")
        particles.spawn_blood(self.x, self.y, count=10)
        particles.add_damage_text(self.x, self.y, damage, is_player=True)
        camera.trigger_shake(intensity=5.0, duration=0.22)

        # Phoenix Revive check
        if self.hp <= 0 and self.phoenix_charges > 0:
            self.phoenix_charges -= 1
            self.hp = int(self.max_hp * 0.60)
            audio.play("level_up")
            particles.spawn_level_up(self.x, self.y, count=35)
            camera.trigger_shake(intensity=6.0, duration=0.30)
            return False

        return True

    def start_dash(self, move_x, move_y, audio, particles):
        if self.dash_cooldown_timer <= 0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_cooldown_timer = self.dash_cooldown_base

            if move_x != 0 or move_y != 0:
                self.dash_dir_x = move_x
                self.dash_dir_y = move_y
            else:
                self.dash_dir_x = -1.0 if self.facing_left else 1.0
                self.dash_dir_y = 0.0

            audio.play("dash")
            particles.spawn_dust(self.x, self.y, count=6)

    def update(self, input_mgr, tilemap, dt, audio, particles, camera):
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        # Super magnet timer from relic
        if self.active_magnet_timer > 0:
            self.active_magnet_timer -= dt
            self.magnet_radius = 260.0  # Room wide
        else:
            self.magnet_radius = 45.0 + getattr(self, "base_magnet_bonus", 0)

        # Handle Dash
        if input_mgr.just_dashed:
            self.start_dash(input_mgr.move_x, input_mgr.move_y, audio, particles)

        if self.is_dashing:
            self.dash_timer -= dt
            move_speed = PLAYER_DASH_SPEED
            dx = self.dash_dir_x * move_speed * dt
            dy = self.dash_dir_y * move_speed * dt
            particles.spawn_dust(self.x, self.y, count=1)
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            speed = self.base_speed * self.speed_mult
            dx = input_mgr.move_x * speed * dt
            dy = input_mgr.move_y * speed * dt

        self.is_moving = (abs(dx) > 0.01 or abs(dy) > 0.01)

        if input_mgr.move_x < -0.1:
            self.facing_left = True
        elif input_mgr.move_x > 0.1:
            self.facing_left = False

        self.x += dx
        if tilemap.collides_with_wall(self.rect):
            self.x -= dx

        self.y += dy
        if tilemap.collides_with_wall(self.rect):
            self.y -= dy

        if self.is_moving:
            self.anim_timer += dt * 8.0
            self.current_frame = int(self.anim_timer) % 2 + 2
        else:
            self.anim_timer += dt * 3.0
            self.current_frame = int(self.anim_timer) % 2

        if self.fire_aura:
            self.fire_aura_timer += dt
            if self.fire_aura_timer >= 0.5:
                self.fire_aura_timer = 0.0
                particles.spawn_spark(self.x, self.y, count=4, color=COLOR_ORANGE)

    def shoot(self, aim_angle, projectiles, audio, particles):
        if self.attack_cooldown_timer > 0:
            return

        effective_cd = self.base_fire_rate / self.attack_speed_mult
        self.attack_cooldown_timer = effective_cd
        audio.play("shoot")

        bullet_speed = 280.0
        dmg = int(self.bullet_damage * self.damage_mult)

        if self.multi_shot == 1:
            projectiles.append(Projectile(
                self.x, self.y, aim_angle, bullet_speed, dmg,
                is_player=True, color=COLOR_CYAN, bounces=self.ricochet_bounces
            ))
        elif self.multi_shot == 2:
            for offset in (-0.12, 0.12):
                projectiles.append(Projectile(
                    self.x, self.y, aim_angle + offset, bullet_speed, dmg,
                    is_player=True, color=COLOR_CYAN, bounces=self.ricochet_bounces
                ))
        elif self.multi_shot >= 3:
            for offset in (-0.22, 0.0, 0.22):
                projectiles.append(Projectile(
                    self.x, self.y, aim_angle + offset, bullet_speed, dmg,
                    is_player=True, color=COLOR_CYAN, bounces=self.ricochet_bounces
                ))

        particles.spawn_spark(self.x, self.y, count=3, color=COLOR_CYAN)

    def draw(self, surface, camera, art):
        if self.invuln_timer > 0 and (int(self.invuln_timer * 20) % 2 == 0):
            return

        screen_x, screen_y = camera.apply_pos(self.x - 8, self.y - 8)
        sprite_name = f"player_{'walk' if self.current_frame >= 2 else 'idle'}_{self.current_frame % 2}"
        sprite = art.get_sprite(sprite_name)

        if self.facing_left:
            sprite = pygame.transform.flip(sprite, True, False)

        if self.is_dashing:
            shadow_x, shadow_y = camera.apply_pos(self.x - 8 - self.dash_dir_x * 8, self.y - 8 - self.dash_dir_y * 8)
            surf_ghost = sprite.copy()
            surf_ghost.set_alpha(100)
            surface.blit(surf_ghost, (shadow_x, shadow_y))

        surface.blit(sprite, (screen_x, screen_y))

        # Shield energy aura
        if self.shield_charges > 0:
            center_x, center_y = camera.apply_pos(self.x, self.y)
            pygame.draw.circle(surface, COLOR_CYAN, (center_x, center_y), 11, 1)
