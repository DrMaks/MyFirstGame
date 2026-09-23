"""
Tilemap Manager for rendering visible dungeon tiles, columns, banners, and handling collisions.
"""

import pygame
from src.config import TILE_SIZE, COLOR_BLACK
from src.world.dungeon_gen import (
    TILE_EMPTY, TILE_FLOOR, TILE_WALL_TOP, TILE_WALL_FRONT, TILE_DOOR
)


class TileMap:
    def __init__(self, dungeon_data, pixel_art):
        self.dungeon = dungeon_data
        self.art = pixel_art
        self.width = dungeon_data.width
        self.height = dungeon_data.height
        self.tiles = dungeon_data.tiles
        self.torch_anim_timer = 0.0

        # Pre-cache static surfaces
        self.floor_surf_0 = self.art.get_sprite("tile_floor_0")
        self.floor_surf_1 = self.art.get_sprite("tile_floor_1")
        self.floor_surf_cracked = self.art.get_sprite("tile_floor_cracked")
        self.wall_top_surf = self.art.get_sprite("tile_wall_top")
        self.wall_front_surf = self.art.get_sprite("tile_wall_front")
        self.column_surf = self.art.get_sprite("tile_column")
        self.banner_surf = self.art.get_sprite("tile_banner")

        self.columns_set = set(self.dungeon.columns)

        # Static floor variant mapping for visual variety
        self.floor_variants = {}
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y] == TILE_FLOOR:
                    val = (x * 37 + y * 53) % 10
                    if val == 0:
                        self.floor_variants[(x, y)] = self.floor_surf_cracked
                    elif val > 6:
                        self.floor_variants[(x, y)] = self.floor_surf_1
                    else:
                        self.floor_variants[(x, y)] = self.floor_surf_0

    def is_solid(self, tile_x, tile_y):
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True
        if (tile_x, tile_y) in self.columns_set:
            return True
        t = self.tiles[tile_x][tile_y]
        return t in (TILE_EMPTY, TILE_WALL_TOP, TILE_WALL_FRONT)

    def collides_with_wall(self, rect):
        min_tx = max(0, int(rect.left // TILE_SIZE))
        max_tx = min(self.width - 1, int(rect.right // TILE_SIZE))
        min_ty = max(0, int(rect.top // TILE_SIZE))
        max_ty = min(self.height - 1, int(rect.bottom // TILE_SIZE))

        for tx in range(min_tx, max_tx + 1):
            for ty in range(min_ty, max_ty + 1):
                if self.is_solid(tx, ty):
                    tile_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(tile_rect):
                        return True
        return False

    def update(self, dt):
        self.torch_anim_timer = (self.torch_anim_timer + dt * 4.0) % 2.0

    def draw(self, surface, camera):
        start_tx = max(0, int(camera.x // TILE_SIZE))
        end_tx = min(self.width - 1, int((camera.x + camera.width) // TILE_SIZE) + 1)
        start_ty = max(0, int(camera.y // TILE_SIZE))
        end_ty = min(self.height - 1, int((camera.y + camera.height) // TILE_SIZE) + 1)

        # 1. Floor & Walls
        for tx in range(start_tx, end_tx + 1):
            for ty in range(start_ty, end_ty + 1):
                t_type = self.tiles[tx][ty]
                world_x = tx * TILE_SIZE
                world_y = ty * TILE_SIZE
                screen_x, screen_y = camera.apply_pos(world_x, world_y)

                if t_type == TILE_FLOOR:
                    surf = self.floor_variants.get((tx, ty), self.floor_surf_0)
                    surface.blit(surf, (screen_x, screen_y))
                elif t_type == TILE_WALL_FRONT:
                    surface.blit(self.wall_front_surf, (screen_x, screen_y))
                elif t_type == TILE_WALL_TOP:
                    surface.blit(self.wall_top_surf, (screen_x, screen_y))

        # 2. Banners
        for (bx, by) in self.dungeon.banners:
            if start_tx <= bx <= end_tx and start_ty <= by <= end_ty:
                screen_x, screen_y = camera.apply_pos(bx * TILE_SIZE, by * TILE_SIZE)
                surface.blit(self.banner_surf, (screen_x, screen_y))

        # 3. Stone Columns
        for (cx, cy) in self.dungeon.columns:
            if start_tx <= cx <= end_tx and start_ty <= cy <= end_ty:
                screen_x, screen_y = camera.apply_pos(cx * TILE_SIZE, cy * TILE_SIZE)
                surface.blit(self.column_surf, (screen_x, screen_y))

        # 4. Torches
        torch_frame = int(self.torch_anim_timer)
        torch_surf = self.art.get_sprite(f"tile_torch_{torch_frame}")
        for (tx, ty) in self.dungeon.torches:
            if start_tx <= tx <= end_tx and start_ty <= ty <= end_ty:
                world_x = tx * TILE_SIZE
                world_y = ty * TILE_SIZE
                screen_x, screen_y = camera.apply_pos(world_x, world_y)
                surface.blit(torch_surf, (screen_x, screen_y))

    def get_world_bounds(self):
        return (0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
