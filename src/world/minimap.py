"""
Retro Dungeon Minimap with Fog of War.
Displays discovered rooms and player position in the corner of the HUD.
"""

import pygame
from src.config import (
    COLOR_DARK_BLUE, COLOR_PURPLE, COLOR_GREEN, COLOR_RED,
    COLOR_GOLD, COLOR_WHITE, COLOR_SHADOW, TILE_SIZE
)


class Minimap:
    def __init__(self, dungeon, scale=1.5):
        self.dungeon = dungeon
        self.scale = scale
        self.size = 56
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.blink_timer = 0.0

    def update(self, player_x, player_y, dt):
        self.blink_timer = (self.blink_timer + dt * 4.0) % 2.0
        # Check player's current room to mark as visited
        tx = int(player_x // TILE_SIZE)
        ty = int(player_y // TILE_SIZE)
        for room in self.dungeon.rooms:
            if room.x <= tx < room.x + room.w and room.y <= ty < room.y + room.h:
                room.visited = True

    def draw(self, target_surface, player_x, player_y, top_right_pos):
        self.surface.fill((0, 0, 0, 0))

        # Background frame
        pygame.draw.rect(self.surface, (20, 16, 28, 200), (0, 0, self.size, self.size))
        pygame.draw.rect(self.surface, COLOR_PURPLE, (0, 0, self.size, self.size), 1)

        # Center minimap around player
        ptx = player_x / TILE_SIZE
        pty = player_y / TILE_SIZE
        center_screen = self.size // 2

        # Draw discovered rooms
        for room in self.dungeon.rooms:
            if not room.visited:
                continue

            rx = center_screen + (room.x - ptx) * self.scale
            ry = center_screen + (room.y - pty) * self.scale
            rw = room.w * self.scale
            rh = room.h * self.scale

            # Clip to minimap inner rect
            room_rect = pygame.Rect(rx, ry, rw, rh)

            room_color = (60, 50, 80)
            if room.room_type == "boss":
                room_color = COLOR_RED
            elif room.room_type == "treasure":
                room_color = COLOR_GOLD
            elif room.room_type == "shop":
                room_color = COLOR_PURPLE

            pygame.draw.rect(self.surface, room_color, room_rect)
            pygame.draw.rect(self.surface, (90, 80, 120), room_rect, 1)

        # Draw player blip (blinking green)
        if int(self.blink_timer) == 0:
            pygame.draw.circle(self.surface, COLOR_GREEN, (center_screen, center_screen), 2)

        # Blit minimap to target HUD surface
        target_surface.blit(self.surface, top_right_pos)
