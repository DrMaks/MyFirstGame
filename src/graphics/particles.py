"""
Particle System and Floating Damage Numbers.
Adds juicy retro game feel with dust, sparks, blood splatters, and floating combat text.
"""

import math
import random
import pygame
from src.config import COLOR_RED, COLOR_YELLOW, COLOR_WHITE, COLOR_ORANGE, COLOR_CYAN, COLOR_GOLD, get_font


class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=2, fade=True):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.fade = fade

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (0.95 ** (dt * 60))
        self.vy *= (0.95 ** (dt * 60))
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface, camera):
        alpha_ratio = max(0.0, self.lifetime / self.max_lifetime)
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        cur_size = max(1, int(self.size * (alpha_ratio if self.fade else 1.0)))

        # Fast direct rect draw
        rect = pygame.Rect(int(screen_x - cur_size / 2), int(screen_y - cur_size / 2), cur_size, cur_size)
        surface.fill(self.color, rect)


class DamageText:
    def __init__(self, x, y, text, color=COLOR_WHITE, size=10, is_crit=False):
        self.x = float(x)
        self.y = float(y)
        self.text = str(text)
        self.color = color
        self.lifetime = 0.65
        self.max_lifetime = 0.65
        self.vy = -35.0  # Float upwards
        self.vx = random.uniform(-10, 10)
        self.is_crit = is_crit
        # Use crisp monospaced font
        self.font = get_font(12 if not is_crit else 14, bold=True)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 25.0 * dt  # Gentle gravity deceleration
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface, camera):
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        txt_surf = self.font.render(self.text, False, self.color)
        # Drop shadow for readability
        shadow_surf = self.font.render(self.text, False, (10, 10, 10))
        surface.blit(shadow_surf, (int(screen_x) + 1, int(screen_y) + 1))
        surface.blit(txt_surf, (int(screen_x), int(screen_y)))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.texts = []

    def spawn_spark(self, x, y, count=6, color=COLOR_YELLOW):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            dur = random.uniform(0.15, 0.35)
            self.particles.append(Particle(x, y, vx, vy, color, dur, size=2))

    def spawn_blood(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            dur = random.uniform(0.2, 0.45)
            color = random.choice([COLOR_RED, (160, 40, 50), (230, 90, 100)])
            self.particles.append(Particle(x, y, vx, vy, color, dur, size=random.choice([2, 3])))

    def spawn_dust(self, x, y, count=5):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(15, 45)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            dur = random.uniform(0.2, 0.35)
            self.particles.append(Particle(x, y, vx, vy, (140, 140, 150), dur, size=2))

    def spawn_level_up(self, x, y, count=25):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 100)
            vx = math.cos(angle) * speed
            vy = -random.uniform(50, 140)  # Ascend
            dur = random.uniform(0.4, 0.8)
            color = random.choice([COLOR_CYAN, COLOR_GOLD, COLOR_WHITE])
            self.particles.append(Particle(x, y, vx, vy, color, dur, size=random.choice([2, 3])))

    def add_damage_text(self, x, y, damage, is_crit=False, is_player=False):
        color = COLOR_GOLD if is_crit else (COLOR_RED if is_player else COLOR_WHITE)
        self.texts.append(DamageText(x, y - 6, f"-{damage}" if is_player else str(damage), color, is_crit=is_crit))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.texts = [t for t in self.texts if t.update(dt)]

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)
        for t in self.texts:
            t.draw(surface, camera)

    def clear(self):
        self.particles.clear( )
        self.texts.clear()
