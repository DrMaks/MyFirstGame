"""
Procedural Multi-Floor Dungeon Generator.
Generates rooms, corridors, chests (wood/gold), columns, banners, stairs, and boss arena.
"""

import random

TILE_EMPTY = 0
TILE_FLOOR = 1
TILE_WALL_TOP = 2
TILE_WALL_FRONT = 3
TILE_DOOR = 4


class Room:
    def __init__(self, x, y, w, h, room_type="combat"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.room_type = room_type  # start, combat, treasure, shop, boss, exit
        self.center_x = x + w // 2
        self.center_y = y + h // 2
        self.cleared = (room_type in ("start", "shop", "treasure"))
        self.visited = False

    def intersects(self, other, margin=2):
        return (
            self.x - margin <= other.x + other.w and
            self.x + self.w + margin >= other.x and
            self.y - margin <= other.y + other.h and
            self.y + self.h + margin >= other.y
        )


class DungeonGenerator:
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        self.tiles = [[TILE_EMPTY for _ in range(height)] for _ in range(width)]
        self.rooms = []
        self.torches = []
        self.chests = []     # List of (x, y, tier)
        self.columns = []    # List of (x, y)
        self.banners = []    # List of (x, y)
        self.start_pos = (0, 0)
        self.boss_pos = (0, 0)
        self.stairs_pos = None

    def generate(self, floor=1, max_floors=4):
        # Scale dungeon size with floor
        self.width = min(68, 50 + (floor - 1) * 6)
        self.height = min(68, 50 + (floor - 1) * 6)
        max_rooms = min(14, 8 + floor * 2)

        self.tiles = [[TILE_EMPTY for _ in range(self.height)] for _ in range(self.width)]
        self.rooms = []
        self.torches = []
        self.chests = []
        self.columns = []
        self.banners = []
        self.stairs_pos = None

        # 1. Attempt room placement
        attempts = 0
        min_size = 7
        max_size = 13 if floor < max_floors else 15

        while len(self.rooms) < max_rooms and attempts < 160:
            attempts += 1
            w = random.randint(min_size, max_size)
            h = random.randint(min_size, max_size)
            x = random.randint(3, self.width - w - 4)
            y = random.randint(3, self.height - h - 4)

            new_room = Room(x, y, w, h)
            overlap = any(new_room.intersects(other) for other in self.rooms)
            if not overlap:
                self.rooms.append(new_room)

        if not self.rooms:
            self.rooms.append(Room(10, 10, 12, 12, "start"))

        # 2. Assign room types
        self.rooms[0].room_type = "start"
        self.rooms[0].cleared = True

        if floor < max_floors:
            # End room has exit stairs to next floor
            self.rooms[-1].room_type = "exit"
            self.stairs_pos = (self.rooms[-1].center_x, self.rooms[-1].center_y)
            self.boss_pos = (0, 0)
        else:
            # Final Floor: Boss Arena!
            self.rooms[-1].room_type = "boss"
            self.boss_pos = (self.rooms[-1].center_x, self.rooms[-1].center_y)
            self.stairs_pos = None

        if len(self.rooms) >= 4:
            self.rooms[1].room_type = "treasure"
            self.rooms[2].room_type = "shop"

        # 3. Carve rooms into floor tiles
        for room in self.rooms:
            for rx in range(room.x, room.x + room.w):
                for ry in range(room.y, room.y + room.h):
                    self.tiles[rx][ry] = TILE_FLOOR

        # 4. Connect rooms with corridors
        for i in range(len(self.rooms) - 1):
            r1 = self.rooms[i]
            r2 = self.rooms[i + 1]
            self._carve_corridor(r1.center_x, r1.center_y, r2.center_x, r2.center_y)

        # 5. Build walls
        self._build_walls()

        # 6. Place torches, columns, banners & chests
        self._decorate_dungeon(floor)

        start_room = self.rooms[0]
        self.start_pos = (start_room.center_x, start_room.center_y)
        return self

    def _carve_corridor(self, x1, y1, x2, y2):
        x, y = x1, y1
        while x != x2:
            self.tiles[x][y] = TILE_FLOOR
            self.tiles[x][y + 1] = TILE_FLOOR
            x += 1 if x2 > x else -1

        while y != y2:
            self.tiles[x][y] = TILE_FLOOR
            self.tiles[x + 1][y] = TILE_FLOOR
            y += 1 if y2 > y else -1

    def _build_walls(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y] == TILE_EMPTY:
                    if self._is_adjacent_to_floor(x, y):
                        if y + 1 < self.height and self.tiles[x][y + 1] == TILE_FLOOR:
                            self.tiles[x][y] = TILE_WALL_FRONT
                        else:
                            self.tiles[x][y] = TILE_WALL_TOP

    def _is_adjacent_to_floor(self, x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.tiles[nx][ny] == TILE_FLOOR:
                        return True
        return False

    def _decorate_dungeon(self, floor):
        for room in self.rooms:
            # Torches on walls
            y_wall = room.y - 1
            if y_wall >= 0:
                torch_x1 = room.x + 2
                torch_x2 = room.x + room.w - 3
                if torch_x1 < self.width and self.tiles[torch_x1][y_wall] == TILE_WALL_FRONT:
                    self.torches.append((torch_x1, y_wall))
                if torch_x2 < self.width and torch_x2 != torch_x1 and self.tiles[torch_x2][y_wall] == TILE_WALL_FRONT:
                    self.torches.append((torch_x2, y_wall))

                # Wall Banners in large rooms
                if room.w >= 10:
                    bx = room.x + room.w // 2
                    if bx < self.width and self.tiles[bx][y_wall] == TILE_WALL_FRONT:
                        self.banners.append((bx, y_wall))

            # Stone Columns in rooms >= 10x10
            if room.w >= 10 and room.h >= 10:
                self.columns.append((room.x + 2, room.y + 2))
                self.columns.append((room.x + room.w - 3, room.y + 2))
                self.columns.append((room.x + 2, room.y + room.h - 3))
                self.columns.append((room.x + room.w - 3, room.y + room.h - 3))

            # Chests
            if room.room_type == "treasure":
                tier = "gold" if (floor >= 2 or random.random() < 0.5) else "wood"
                self.chests.append((room.center_x, room.center_y, tier))
            elif room.room_type == "combat" and random.random() < 0.40:
                tier = "gold" if (floor >= 3 and random.random() < 0.5) else "wood"
                offset_x = random.choice([-2, 2])
                offset_y = random.choice([-2, 2])
                self.chests.append((room.center_x + offset_x, room.center_y + offset_y, tier))
