"""
Pixel-perfect Camera with Screen Shake and Bounds Clamping.
"""

import random
import pygame


class Camera:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

        # Screen shake
        self.shake_duration = 0.0
        self.shake_intensity = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

        # World bounds
        self.bounds = None

    def set_bounds(self, min_x, min_y, max_x, max_y):
        self.bounds = (min_x, min_y, max_x, max_y)

    def trigger_shake(self, intensity=4.0, duration=0.2):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)

    def update(self, target_x, target_y, dt):
        # Smooth camera following (lerp)
        self.target_x = target_x - self.width / 2
        self.target_y = target_y - self.height / 2

        smooth_speed = 10.0
        self.x += (self.target_x - self.x) * min(1.0, smooth_speed * dt)
        self.y += (self.target_y - self.y) * min(1.0, smooth_speed * dt)

        # Shake update
        if self.shake_duration > 0:
            self.shake_duration -= dt
            decay = max(0.0, self.shake_duration)
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity) * (decay + 0.2)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity) * (decay + 0.2)
            if self.shake_duration <= 0:
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
                self.shake_intensity = 0.0
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

        # Clamp to bounds if present
        if self.bounds:
            min_x, min_y, max_x, max_y = self.bounds
            self.x = max(min_x, min(max_x - self.width, self.x))
            self.y = max(min_y, min(max_y - self.height, self.y))

    def apply_pos(self, x, y):
        """Returns int-rounded screen coordinates for crisp pixel rendering."""
        return (
            int(x - self.x + self.shake_offset_x),
            int(y - self.y + self.shake_offset_y)
        )

    def apply_rect(self, rect):
        screen_x = int(rect.x - self.x + self.shake_offset_x)
        screen_y = int(rect.y - self.y + self.shake_offset_y)
        return pygame.Rect(screen_x, screen_y, rect.width, rect.height)

    def screen_to_world(self, screen_x, screen_y):
        return (
            screen_x + self.x - self.shake_offset_x,
            screen_y + self.y - self.shake_offset_y
        )
