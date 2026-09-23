"""
CRT / Scanline Post-Processing Shader & Overlay.
Applies authentic retro television / arcade CRT scanlines and subtle vignette to the scaled display.
"""

import pygame


class CRTFilter:
    def __init__(self, width, height, enabled=True):
        self.width = width
        self.height = height
        self.enabled = enabled
        self.overlay = None
        self._build_overlay()

    def resize(self, width, height):
        self.width = width
        self.height = height
        self._build_overlay()

    def _build_overlay(self):
        if self.width <= 0 or self.height <= 0:
            return

        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # 1. Scanlines (dark horizontal line every 2-3 pixels)
        scanline_color = (0, 0, 0, 45)
        for y in range(0, self.height, 3):
            pygame.draw.line(self.overlay, scanline_color, (0, y), (self.width, y))

        # 2. Subtle Vignette border
        vignette_depth = min(40, int(min(self.width, self.height) * 0.08))
        for i in range(vignette_depth):
            alpha = int(70 * (1.0 - i / vignette_depth))
            color = (0, 0, 0, alpha)
            pygame.draw.rect(self.overlay, color, (i, i, self.width - 2 * i, self.height - 2 * i), 1)

    def apply(self, target_surface):
        if self.enabled and self.overlay:
            target_surface.blit(self.overlay, (0, 0))
