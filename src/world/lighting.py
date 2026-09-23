"""
Dynamic Ambient Lighting and Torch Halos in the style of Loop Hero and dark fantasy RPGs.
Pre-renders soft radial light falloff textures and composites them onto the dark canvas.
"""

import math
import random
import pygame
from src.config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT


class LightingEngine:
    def __init__(self):
        self.darkness = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self.base_ambient_darkness = 85  # Much brighter, vibrant dungeon feel
        self.brightness_mult = 1.0       # 0.8 to 1.4 adjustable via Settings
        self.ambient_darkness = 85
        self.flicker_time = 0.0

        # Pre-cache larger, warmer radial light masks
        self.torch_mask_radius = 70
        self.player_mask_radius = 92
        self.torch_mask = self._create_radial_mask(self.torch_mask_radius, (255, 205, 110))
        self.player_mask = self._create_radial_mask(self.player_mask_radius, (250, 235, 180))
        self.crystal_mask = self._create_radial_mask(48, (130, 205, 255))

    def set_brightness(self, mult):
        self.brightness_mult = max(0.5, min(2.0, float(mult)))
        self.ambient_darkness = max(15, min(220, int(self.base_ambient_darkness / self.brightness_mult)))

    def _create_radial_mask(self, radius, color):
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        cr, cg, cb = color
        for r in range(radius, 0, -2):
            ratio = r / radius
            alpha = int(255 * ((1.0 - ratio) ** 1.8))
            # Colored light ring
            col = (min(255, int(cr * (0.8 + 0.2 * (1 - ratio)))),
                   min(255, int(cg * (0.8 + 0.2 * (1 - ratio)))),
                   min(255, int(cb * (0.8 + 0.2 * (1 - ratio)))),
                   alpha)
            pygame.draw.circle(surf, col, (radius, radius), r)
        return surf

    def update(self, dt):
        self.flicker_time += dt * 8.0

    def apply_lighting(self, target_surface, camera, player, torches, special_lights=None):
        # 1. Fill base dark dungeon shadow
        self.darkness.fill((14, 10, 20, self.ambient_darkness))

        # 2. Carve player light aura
        px, py = camera.apply_pos(player.x, player.y)
        p_offset = self.player_mask_radius
        self.darkness.blit(
            self.player_mask,
            (px - p_offset, py - p_offset),
            special_flags=pygame.BLEND_RGBA_SUB
        )

        # 3. Carve torch lights with dynamic organic flicker
        for i, (tx, ty) in enumerate(torches):
            world_x = tx * 16 + 8
            world_y = ty * 16 + 6
            screen_x, screen_y = camera.apply_pos(world_x, world_y)

            # Skip torches off-screen
            if -60 <= screen_x <= VIRTUAL_WIDTH + 60 and -60 <= screen_y <= VIRTUAL_HEIGHT + 60:
                flicker = math.sin(self.flicker_time + i * 1.7) * 3.0
                flicker_radius = max(20, int(self.torch_mask_radius + flicker))

                # Quick scale or blit
                mask = self.torch_mask
                if abs(flicker) > 1.5:
                    mask = pygame.transform.scale(self.torch_mask, (flicker_radius * 2, flicker_radius * 2))

                offset = mask.get_width() // 2
                self.darkness.blit(
                    mask,
                    (screen_x - offset, screen_y - offset),
                    special_flags=pygame.BLEND_RGBA_SUB
                )

        # 4. Special lights (e.g. magic portals / projectiles)
        if special_lights:
            for (lx, ly, ltype) in special_lights:
                sx, sy = camera.apply_pos(lx, ly)
                if -40 <= sx <= VIRTUAL_WIDTH + 40 and -40 <= sy <= VIRTUAL_HEIGHT + 40:
                    offset = self.crystal_mask.get_width() // 2
                    self.darkness.blit(
                        self.crystal_mask,
                        (sx - offset, sy - offset),
                        special_flags=pygame.BLEND_RGBA_SUB
                    )

        # 5. Composite shadows onto the main scene
        target_surface.blit(self.darkness, (0, 0))
