"""
Projectiles for player weapons and enemy attacks.
"""

import math
import pygame
from src.config import COLOR_CYAN, COLOR_YELLOW, COLOR_RED, COLOR_PURPLE, COLOR_WHITE, TILE_SIZE


class Projectile:
    def __init__(self, x, y, angle, speed, damage, is_player=True, color=COLOR_CYAN, size=3, bounces=0):
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.is_player = is_player
        self.color = color
        self.size = size
        self.bounces = bounces
        self.lifetime = 2.5
        self.radius = size

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), int(self.radius * 2), int(self.radius * 2))

    def update(self, dt, tilemap, particles):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

        # Spawn subtle trail particle
        if self.lifetime > 0:
            tx = self.x - self.vx * dt * 0.5
            ty = self.y - self.vy * dt * 0.5
            particles.spawn_spark(tx, ty, count=1, color=self.color)

        # Check collision with wall
        if tilemap.collides_with_wall(self.rect):
            if self.bounces > 0:
                self.bounces -= 1
                # Invert velocity
                self.vx = -self.vx * 0.9
                self.vy = -self.vy * 0.9
                particles.spawn_spark(self.x, self.y, count=3, color=COLOR_YELLOW)
            else:
                particles.spawn_spark(self.x, self.y, count=5, color=self.color)
                return False  # Dead

        return self.lifetime > 0

    def draw(self, surface, camera):
        screen_x, screen_y = camera.apply_pos(self.x, self.y)
        # Glowing inner and outer circle
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(surface, COLOR_WHITE, (screen_x, screen_y), max(1, self.size - 1))
