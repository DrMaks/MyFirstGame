"""
Main Game Loop, Engine, and State Machine.
Coordinates multi-floor progression, dynamic lighting, custom cursor, skill tree, and Steamworks.
"""

import sys
import os
import math
import random
import pygame
from src.config import (
    GAME_TITLE, VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, FPS,
    COLOR_BLACK, COLOR_WHITE, COLOR_GOLD, COLOR_RED, COLOR_CYAN, TILE_SIZE
)
from src.graphics.pixel_art import PixelArtGenerator
from src.graphics.particles import ParticleSystem
from src.graphics.crt_filter import CRTFilter
from src.audio.sound_synth import SoundSynth
from src.audio.chiptune_engine import ChiptuneEngine
from src.engine.camera import Camera
from src.engine.input_manager import InputManager
from src.engine.steam_manager import SteamManager
from src.services.google_play_manager import GooglePlayManager
from src.engine.save_manager import SaveManager
from src.world.dungeon_gen import DungeonGenerator
from src.world.tilemap import TileMap
from src.world.minimap import Minimap
from src.world.lighting import LightingEngine
from src.entities.player import Player
from src.entities.enemy import (
    Slime, SkeletonArcher, DarkMage, GoblinBombardier, Wraith, StoneGolem, DungeonOverlord
)
from src.entities.drops import Chest, Coin, PotionDrop, StairsPortal, GemDrop, ScrollDrop, ShieldDrop
from src.ui.hud import HUD
from src.ui.menus import MenuRenderer, ALL_UPGRADES_BASE
from src.ui.settings import SettingsMenu
from src.ui.skill_tree import SkillTreeMenu
from src.localization import loc

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_UPGRADE = 2
STATE_PAUSED = 3
STATE_SETTINGS = 4
STATE_GAMEOVER = 5
STATE_VICTORY = 6
STATE_SKILL_TREE = 7


class Game:
    def __init__(self, is_mobile=False):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)

        self.is_mobile = is_mobile
        self.window_w = DEFAULT_WINDOW_WIDTH
        self.window_h = DEFAULT_WINDOW_HEIGHT
        self.fullscreen = False
        self.window = pygame.display.set_mode((self.window_w, self.window_h), pygame.RESIZABLE)
        self.virtual_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Systems
        self.art = PixelArtGenerator()
        self.particles = ParticleSystem()
        self.crt = CRTFilter(self.window_w, self.window_h, enabled=(not is_mobile))
        self.sound = SoundSynth()
        self.chiptune = ChiptuneEngine()
        self.camera = Camera(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.input = InputManager(enable_touch=is_mobile)
        self.steam = SteamManager()
        self.google_play = GooglePlayManager() if is_mobile else None
        if self.google_play:
            self.steam.companion_service = self.google_play
        self.save_mgr = SaveManager()
        self.lighting = LightingEngine()

        # UI & Menus
        self.hud = HUD(self.art)
        self.menu_renderer = MenuRenderer(self.art)
        self.settings_menu = SettingsMenu(self.sound, self.chiptune, self.crt, self.lighting)
        self.skill_tree_menu = SkillTreeMenu(self.save_mgr, self.art, self.sound)

        # State machine
        self.state = STATE_MENU
        self.prev_state = STATE_MENU
        self.menu_selected = 0
        self.pause_selected = 0
        self.game_over_selected = 0
        self.victory_selected = 0
        self.upgrade_selected = 0
        self.current_upgrade_choices = []

        # Multi-Floor Run Progression
        self.current_floor = 1
        self.max_floors = 4
        self.stats = {"kills": 0, "gold": 0, "level": 1}

        # Gameplay entities
        self.tilemap = None
        self.minimap = None
        self.player = None
        self.boss = None
        self.stairs = None
        self.enemies = []
        self.projectiles = []
        self.drops = []
        self.chests = []

        # Start menu music
        self.chiptune.play_track("menu")

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((self.window_w, self.window_h), pygame.RESIZABLE)
        info = pygame.display.Info()
        self.crt.resize(info.current_w, info.current_h)

    def start_new_game(self):
        self.current_floor = 1
        self.stats = {"kills": 0, "gold": 0, "level": 1}
        self.enter_floor(floor=1, is_new_run=True)

    def enter_floor(self, floor=1, is_new_run=False):
        self.current_floor = floor
        self.particles.clear()
        self.projectiles.clear()
        self.drops.clear()
        self.chests.clear()
        self.enemies.clear()
        self.boss = None
        self.stairs = None

        # 1. Generate Dungeon for current floor
        gen = DungeonGenerator()
        dungeon_data = gen.generate(floor=self.current_floor, max_floors=self.max_floors)
        self.tilemap = TileMap(dungeon_data, self.art)
        self.minimap = Minimap(dungeon_data)
        self.camera.set_bounds(0, 0, dungeon_data.width * TILE_SIZE, dungeon_data.height * TILE_SIZE)

        # 2. Player setup
        sx, sy = dungeon_data.start_pos
        spawn_px = sx * TILE_SIZE + 8
        spawn_py = sy * TILE_SIZE + 8

        if is_new_run or self.player is None:
            self.player = Player(spawn_px, spawn_py, save_manager=self.save_mgr)
        else:
            self.player.x = spawn_px
            self.player.y = spawn_py

        # 3. Chests
        for (cx, cy, tier) in dungeon_data.chests:
            self.chests.append(Chest(cx, cy, tier=tier))

        # 4. Exit Stairs (if not final boss floor)
        if dungeon_data.stairs_pos:
            st_x, st_y = dungeon_data.stairs_pos
            self.stairs = StairsPortal(st_x, st_y, target_floor=self.current_floor + 1)

        # 5. Boss (on final floor)
        if self.current_floor == self.max_floors and dungeon_data.boss_pos != (0, 0):
            bx, by = dungeon_data.boss_pos
            self.boss = DungeonOverlord(bx * TILE_SIZE + 8, by * TILE_SIZE + 8, floor=self.current_floor)
            self.enemies.append(self.boss)

        # 6. Enemies spawning based on floor depth
        for room in dungeon_data.rooms:
            if room.room_type == "combat":
                num_enemies = random.randint(3 + self.current_floor, 6 + self.current_floor)
                for _ in range(num_enemies):
                    ex = random.randint(room.x + 1, room.x + room.w - 2) * TILE_SIZE + 8
                    ey = random.randint(room.y + 1, room.y + room.h - 2) * TILE_SIZE + 8

                    # Floor specific enemy roster
                    if self.current_floor == 1:
                        etype = random.choice(["slime", "skeleton"])
                    elif self.current_floor == 2:
                        etype = random.choice(["slime", "skeleton", "goblin"])
                    elif self.current_floor == 3:
                        etype = random.choice(["goblin", "mage", "wraith", "golem"])
                    else:
                        etype = random.choice(["wraith", "golem", "mage", "goblin"])

                    if etype == "slime":
                        self.enemies.append(Slime(ex, ey, floor=self.current_floor))
                    elif etype == "skeleton":
                        self.enemies.append(SkeletonArcher(ex, ey, floor=self.current_floor))
                    elif etype == "mage":
                        self.enemies.append(DarkMage(ex, ey, floor=self.current_floor))
                    elif etype == "goblin":
                        self.enemies.append(GoblinBombardier(ex, ey, floor=self.current_floor))
                    elif etype == "wraith":
                        self.enemies.append(Wraith(ex, ey, floor=self.current_floor))
                    elif etype == "golem":
                        self.enemies.append(StoneGolem(ex, ey, floor=self.current_floor))

        # Music
        if self.current_floor == self.max_floors:
            self.chiptune.play_track("boss")
        else:
            self.chiptune.play_track("dungeon")

        self.state = STATE_PLAYING

    def prompt_level_up(self):
        choices = random.sample(ALL_UPGRADES_BASE, min(3, len(ALL_UPGRADES_BASE)))
        self.current_upgrade_choices = choices
        self.upgrade_selected = 0
        self.state = STATE_UPGRADE

    def apply_upgrade(self, upg_id):
        if upg_id == "multishot":
            self.player.multi_shot += 1
        elif upg_id == "damage":
            self.player.damage_mult += 0.25
        elif upg_id == "attack_speed":
            self.player.attack_speed_mult += 0.30
        elif upg_id == "swift_boots":
            self.player.speed_mult += 0.20
        elif upg_id == "ricochet":
            self.player.ricochet_bounces += 1
        elif upg_id == "vampirism":
            self.player.has_vampirism = True
        elif upg_id == "fire_aura":
            self.player.fire_aura = True
        elif upg_id == "max_hp":
            self.player.max_hp += 35
            self.player.heal(35)

        self.player.pending_upgrades -= 1
        if self.player.pending_upgrades > 0:
            self.prompt_level_up()
        else:
            self.state = STATE_PLAYING

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit(0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                if not self.fullscreen:
                    self.window_w = event.w
                    self.window_h = event.h
                    self.crt.resize(event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

                # Navigation based on current state
                if self.state == STATE_MENU:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.menu_selected = (self.menu_selected - 1) % 4
                        self.sound.play("swing")
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.menu_selected = (self.menu_selected + 1) % 4
                        self.sound.play("swing")
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menu_selected == 0:
                            self.start_new_game()
                        elif self.menu_selected == 1:
                            self.prev_state = STATE_MENU
                            self.state = STATE_SKILL_TREE
                        elif self.menu_selected == 2:
                            self.prev_state = STATE_MENU
                            self.state = STATE_SETTINGS
                        elif self.menu_selected == 3:
                            self.running = False

                elif self.state == STATE_SKILL_TREE:
                    action = None
                    if event.key in (pygame.K_w, pygame.K_UP):
                        action = "up"
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        action = "down"
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        action = "left"
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        action = "right"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        action = "select"
                    elif event.key == pygame.K_ESCAPE:
                        action = "back"

                    if action:
                        res = self.skill_tree_menu.handle_input(action)
                        if res == "back":
                            self.state = self.prev_state

                elif self.state == STATE_SETTINGS:
                    action = None
                    if event.key in (pygame.K_w, pygame.K_UP):
                        action = "up"
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        action = "down"
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        action = "left"
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        action = "right"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        action = "select"
                    elif event.key == pygame.K_ESCAPE:
                        action = "back"

                    if action:
                        res = self.settings_menu.handle_input(action)
                        if res == "toggle_fullscreen":
                            self.toggle_fullscreen()
                        elif res == "back":
                            self.state = self.prev_state

                elif self.state == STATE_PAUSED:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.pause_selected = (self.pause_selected - 1) % 4
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.pause_selected = (self.pause_selected + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.pause_selected == 0:
                            self.state = STATE_PLAYING
                        elif self.pause_selected == 1:
                            self.prev_state = STATE_PAUSED
                            self.state = STATE_SKILL_TREE
                        elif self.pause_selected == 2:
                            self.prev_state = STATE_PAUSED
                            self.state = STATE_SETTINGS
                        elif self.pause_selected == 3:
                            self.save_mgr.add_gold(self.player.gold)
                            self.state = STATE_MENU
                            self.chiptune.play_track("menu")
                    elif event.key == pygame.K_ESCAPE:
                        self.state = STATE_PLAYING

                elif self.state == STATE_UPGRADE:
                    if event.key in (pygame.K_a, pygame.K_LEFT):
                        self.upgrade_selected = (self.upgrade_selected - 1) % len(self.current_upgrade_choices)
                        self.sound.play("swing")
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.upgrade_selected = (self.upgrade_selected + 1) % len(self.current_upgrade_choices)
                        self.sound.play("swing")
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        chosen = self.current_upgrade_choices[self.upgrade_selected]
                        self.sound.play("coin")
                        self.apply_upgrade(chosen["id"])

                elif self.state == STATE_GAMEOVER:
                    if event.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN):
                        self.game_over_selected = (self.game_over_selected + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.game_over_selected == 0:
                            self.start_new_game()
                        else:
                            self.state = STATE_MENU
                            self.chiptune.play_track("menu")

                elif self.state == STATE_VICTORY:
                    if event.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN):
                        self.victory_selected = (self.victory_selected + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.victory_selected == 0:
                            self.start_new_game()
                        else:
                            self.state = STATE_MENU
                            self.chiptune.play_track("menu")

            self.input.handle_event(event, self.window_w, self.window_h)

    def update(self, dt):
        if self.steam:
            self.steam.update()
        if getattr(self, "google_play", None):
            self.google_play.update()

        info = pygame.display.Info()
        scale_x = info.current_w / VIRTUAL_WIDTH
        scale_y = info.current_h / VIRTUAL_HEIGHT
        self.input.update(
            self.camera,
            self.player.x if self.player else 0,
            self.player.y if self.player else 0,
            window_scale=(scale_x, scale_y)
        )

        # Reset interactive hover state
        self.input.is_hovering_interactive = False

        if self.state == STATE_MENU:
            opt = self.menu_renderer.get_main_menu_option_at_pos(self.input.virtual_mouse_x, self.input.virtual_mouse_y)
            if opt != -1:
                self.menu_selected = opt
                self.input.is_hovering_interactive = True
                if self.input.mouse_clicked:
                    self.sound.play("swing")
                    if opt == 0:
                        self.start_new_game()
                    elif opt == 1:
                        self.prev_state = STATE_MENU
                        self.state = STATE_SKILL_TREE
                    elif opt == 2:
                        self.prev_state = STATE_MENU
                        self.state = STATE_SETTINGS
                    elif opt == 3:
                        self.running = False
            return

        if self.state == STATE_PAUSED:
            if self.input.just_paused:
                self.state = STATE_PLAYING
                return
            opt = self.menu_renderer.get_pause_menu_option_at_pos(self.input.virtual_mouse_x, self.input.virtual_mouse_y)
            if opt != -1:
                self.pause_selected = opt
                self.input.is_hovering_interactive = True
                if self.input.mouse_clicked:
                    self.sound.play("swing")
                    if opt == 0:
                        self.state = STATE_PLAYING
                    elif opt == 1:
                        self.prev_state = STATE_PAUSED
                        self.state = STATE_SKILL_TREE
                    elif opt == 2:
                        self.prev_state = STATE_PAUSED
                        self.state = STATE_SETTINGS
                    elif opt == 3:
                        self.state = STATE_MENU
                        self.chiptune.play_track("menu")
            return

        if self.state == STATE_SKILL_TREE:
            res = self.skill_tree_menu.handle_input(
                None,
                virtual_mouse_x=self.input.virtual_mouse_x,
                virtual_mouse_y=self.input.virtual_mouse_y,
                mouse_clicked=self.input.mouse_clicked
            )
            if self.skill_tree_menu.hovered_idx != -1:
                self.input.is_hovering_interactive = True
            if res == "back":
                self.state = self.prev_state
            return

        if self.state == STATE_UPGRADE:
            # Mouse / touch card picking
            hovered = self.menu_renderer.get_upgrade_card_at_pos(
                self.input.virtual_mouse_x, self.input.virtual_mouse_y, len(self.current_upgrade_choices)
            )
            if hovered != -1:
                self.upgrade_selected = hovered
                self.input.is_hovering_interactive = True
                if self.input.mouse_clicked:
                    chosen = self.current_upgrade_choices[self.upgrade_selected]
                    self.sound.play("coin")
                    self.apply_upgrade(chosen["id"])
            return

        if self.state == STATE_PLAYING:
            if self.input.just_paused:
                self.state = STATE_PAUSED
                return

            # Update mobile touch controls context
            if self.input.touch_controls.enabled and self.player:
                can_chest = any(c.can_interact(self.player) for c in getattr(self, "chests", [])) or (self.stairs and self.stairs.can_interact(self.player))
                has_scroll = getattr(self.player, "has_meteor_scroll", False)
                dash_cd = getattr(self.player, "dash_cooldown", 0.0) / max(0.01, getattr(self.player, "dash_max_cooldown", 1.0))
                self.input.touch_controls.update_context(can_chest, has_scroll, dash_cd)

            self.camera.update(self.player.x, self.player.y, dt)
            self.tilemap.update(dt)
            self.lighting.update(dt)

            if self.stairs:
                self.stairs.update(dt)

            self.player.update(self.input, self.tilemap, dt, self.sound, self.particles, self.camera)

            # Shooting
            if self.input.action_attack:
                self.player.shoot(self.input.aim_angle, self.projectiles, self.sound, self.particles)

            # Level up check
            if self.player.pending_upgrades > 0:
                self.prompt_level_up()
                return

            # Meteor Scroll Room Purge activation
            if getattr(self.player, "has_meteor_scroll", False) and (
                self.input.touch_controls.just_used_scroll or
                pygame.key.get_pressed()[pygame.K_q]
            ):
                self.player.has_meteor_scroll = False
                self.sound.play("explosion")
                self.camera.trigger_shake(intensity=8.0, duration=0.45)
                # Purge all living enemies on screen
                for enemy in self.enemies:
                    killed = enemy.take_damage(95, self.sound, self.particles, is_crit=True)
                    if killed:
                        self.stats["kills"] += 1
                        self.player.add_xp(enemy.xp_value, self.sound, self.particles, self.steam)
                        enemy.on_death(self.drops, self.sound, self.particles, self.steam)

            # Chest interaction
            for chest in self.chests:
                if chest.can_interact(self.player):
                    self.input.is_hovering_interactive = True
                    if self.input.just_interacted or (self.input.mouse_clicked and math.hypot(self.input.aim_world_x - chest.x, self.input.aim_world_y - chest.y) < 20):
                        chest.open(self.player, self.drops, self.sound, self.particles, self.steam)

            # Stairs interaction to next floor
            if self.stairs and self.stairs.can_interact(self.player):
                self.input.is_hovering_interactive = True
                if self.input.just_interacted or (self.input.mouse_clicked and math.hypot(self.input.aim_world_x - self.stairs.x, self.input.aim_world_y - self.stairs.y) < 20):
                    self.sound.play("level_up")
                    self.save_mgr.add_gold(self.player.gold)
                    self.enter_floor(self.current_floor + 1)
                    return

            # Drops update
            self.drops = [d for d in self.drops if d.update(self.player, dt)]

            if self.player.gold >= 100:
                self.steam.unlock_achievement("ACH_RICH")

            # Projectiles
            living_projectiles = []
            for p in self.projectiles:
                alive = p.update(dt, self.tilemap, self.particles)
                if not alive:
                    continue

                if p.is_player:
                    hit_enemy = False
                    for enemy in self.enemies:
                        if p.rect.colliderect(enemy.rect):
                            is_crit = (random.random() < getattr(self.player, "crit_chance", 0.15))
                            dmg = int(p.damage * (1.80 if is_crit else 1.0))
                            killed = enemy.take_damage(dmg, self.sound, self.particles, is_crit=is_crit)
                            hit_enemy = True

                            if killed:
                                self.stats["kills"] += 1
                                self.player.add_xp(enemy.xp_value, self.sound, self.particles, self.steam)
                                enemy.on_death(self.drops, self.sound, self.particles, self.steam)
                                if self.player.has_vampirism and random.random() < 0.35:
                                    self.player.heal(6)
                                    self.particles.spawn_spark(self.player.x, self.player.y, count=5, color=COLOR_GOLD)
                            break
                    if not hit_enemy:
                        living_projectiles.append(p)
                else:
                    if p.rect.colliderect(self.player.rect):
                        self.player.take_damage(p.damage, self.sound, self.particles, self.camera)
                    else:
                        living_projectiles.append(p)

            self.projectiles = living_projectiles

            # Fire Aura
            if self.player.fire_aura and self.player.fire_aura_timer == 0.0:
                for enemy in self.enemies:
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    if math.hypot(dx, dy) < 45.0:
                        killed = enemy.take_damage(14, self.sound, self.particles)
                        if killed:
                            self.stats["kills"] += 1
                            self.player.add_xp(enemy.xp_value, self.sound, self.particles, self.steam)
                            enemy.on_death(self.drops, self.sound, self.particles, self.steam)

            # Enemies update
            living_enemies = []
            for enemy in self.enemies:
                if enemy.hp > 0:
                    enemy.update(self.player, self.tilemap, dt, self.projectiles, self.sound)
                    if enemy.rect.colliderect(self.player.rect):
                        self.player.take_damage(enemy.contact_damage, self.sound, self.particles, self.camera)
                    living_enemies.append(enemy)

            self.enemies = living_enemies

            # Check Boss proximity
            if self.boss and self.boss.hp > 0:
                boss_dist = math.hypot(self.player.x - self.boss.x, self.player.y - self.boss.y)
                if boss_dist < 180.0:
                    self.chiptune.play_track("boss")
                else:
                    self.chiptune.play_track("dungeon")

            # Check Victory
            if self.current_floor == self.max_floors and self.boss and self.boss.hp <= 0:
                self.save_mgr.add_gold(self.player.gold)
                self.stats["gold"] = self.player.gold
                self.stats["level"] = self.player.level
                self.state = STATE_VICTORY
                return

            # Check Player Death
            if self.player.hp <= 0:
                self.sound.play("player_hurt")
                self.save_mgr.add_gold(self.player.gold)
                self.stats["gold"] = self.player.gold
                self.stats["level"] = self.player.level
                self.state = STATE_GAMEOVER
                return

            self.minimap.update(self.player.x, self.player.y, dt)
            self.particles.update(dt)

    def render(self):
        self.virtual_surf.fill(COLOR_BLACK)

        if self.state == STATE_MENU:
            self.menu_renderer.draw_main_menu(self.virtual_surf, self.menu_selected, pygame.time.get_ticks() / 1000.0)

        elif self.state == STATE_SKILL_TREE:
            self.skill_tree_menu.draw(self.virtual_surf)

        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_UPGRADE):
            # 1. World & Tiles
            self.tilemap.draw(self.virtual_surf, self.camera)

            # 2. Stairs to next floor
            if self.stairs:
                self.stairs.draw(self.virtual_surf, self.camera, self.art)
                if self.stairs.can_interact(self.player):
                    sx, sy = self.camera.apply_pos(self.stairs.x - 36, self.stairs.y - 18)
                    tip = self.settings_menu.small_font.render(loc.get("stairs_prompt"), True, COLOR_CYAN)
                    self.virtual_surf.blit(tip, (sx, sy))

            # 3. Chests & Drops
            for chest in self.chests:
                chest.draw(self.virtual_surf, self.camera, self.art)
                if chest.can_interact(self.player):
                    cx, cy = self.camera.apply_pos(chest.x - 14, chest.y - 18)
                    tip = self.settings_menu.small_font.render(loc.get("chest_prompt"), True, COLOR_GOLD)
                    self.virtual_surf.blit(tip, (cx, cy))

            for drop in self.drops:
                drop.draw(self.virtual_surf, self.camera, self.art)

            # 4. Enemies
            for enemy in self.enemies:
                enemy.draw(self.virtual_surf, self.camera, self.art)

            # 5. Player
            self.player.draw(self.virtual_surf, self.camera, self.art)

            # 6. Projectiles
            for p in self.projectiles:
                p.draw(self.virtual_surf, self.camera)

            # 7. Dynamic Torch & Ambient Lighting Pass (Loop Hero style)
            self.lighting.apply_lighting(
                self.virtual_surf, self.camera, self.player, self.tilemap.dungeon.torches
            )

            # 8. Particles
            self.particles.draw(self.virtual_surf, self.camera)

            # 9. HUD with current floor
            self.hud.draw(self.virtual_surf, self.player, self.boss, self.minimap, floor=self.current_floor)

            # Overlays
            if self.state == STATE_PAUSED:
                self.menu_renderer.draw_pause_menu(self.virtual_surf, self.pause_selected)
            elif self.state == STATE_UPGRADE:
                self.menu_renderer.draw_upgrade_picker(self.virtual_surf, self.current_upgrade_choices, self.upgrade_selected)

        elif self.state == STATE_SETTINGS:
            self.settings_menu.draw(self.virtual_surf)

        elif self.state == STATE_GAMEOVER:
            self.menu_renderer.draw_game_over(self.virtual_surf, self.stats, self.game_over_selected)

        elif self.state == STATE_VICTORY:
            self.menu_renderer.draw_victory(self.virtual_surf, self.stats, self.victory_selected)

        # Draw custom retro crosshair / cursor on top
        self.input.draw_cursor(self.virtual_surf, self.art)

        # Scale to window using nearest-neighbor
        info = pygame.display.Info()
        win_w, win_h = info.current_w, info.current_h
        scaled_surf = pygame.transform.scale(self.virtual_surf, (win_w, win_h))

        self.window.blit(scaled_surf, (0, 0))
        self.crt.apply(self.window)
        pygame.display.flip()
