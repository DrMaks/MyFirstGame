"""
Mobile Touch Controls & Virtual Gamepad for Android / Google Play Edition.
Includes a virtual floating analog stick, tactile action buttons (Attack, Dash, Interact, Magic),
multi-touch gesture tracking, and tactile press animation.
"""

import math
import pygame
from src.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
    COLOR_WHITE, COLOR_GOLD, COLOR_CYAN, COLOR_RED, COLOR_DARK_BLUE
)


class TouchControls:
    def __init__(self, pixel_art=None):
        self.art = pixel_art
        self.enabled = False  # Enabled in mobile edition or when touch is detected

        # Joystick configuration
        self.stick_base_x = 56
        self.stick_base_y = VIRTUAL_HEIGHT - 56
        self.stick_base_radius = 36
        self.stick_knob_radius = 16
        self.stick_touch_id = None
        self.stick_pos = [float(self.stick_base_x), float(self.stick_base_y)]
        self.stick_dir = [0.0, 0.0]  # Normalized -1.0 to 1.0
        self.is_stick_active = False

        # Action Buttons configuration
        # Attack Button (Main)
        self.btn_attack = {
            "x": VIRTUAL_WIDTH - 42,
            "y": VIRTUAL_HEIGHT - 44,
            "radius": 20,
            "label": "ATK",
            "pressed": False,
            "touch_id": None
        }

        # Dash Button
        self.btn_dash = {
            "x": VIRTUAL_WIDTH - 82,
            "y": VIRTUAL_HEIGHT - 32,
            "radius": 16,
            "label": "DASH",
            "pressed": False,
            "touch_id": None
        }

        # Interact / Chest Button
        self.btn_interact = {
            "x": VIRTUAL_WIDTH - 42,
            "y": VIRTUAL_HEIGHT - 88,
            "radius": 15,
            "label": "USE",
            "pressed": False,
            "touch_id": None,
            "visible": True
        }

        # Scroll / Magic Button
        self.btn_scroll = {
            "x": VIRTUAL_WIDTH - 82,
            "y": VIRTUAL_HEIGHT - 74,
            "radius": 15,
            "label": "SPELL",
            "pressed": False,
            "touch_id": None,
            "visible": False
        }

        # Pause Button (Top-Right)
        self.btn_pause = {
            "x": VIRTUAL_WIDTH - 22,
            "y": 18,
            "radius": 12,
            "label": "||",
            "pressed": False,
            "touch_id": None
        }

        # Outputs polled by input manager
        self.move_x = 0.0
        self.move_y = 0.0
        self.just_attacked = False
        self.is_attacking = False
        self.just_dashed = False
        self.just_interacted = False
        self.just_used_scroll = False
        self.just_paused = False

        # Pre-render button surfaces with transparency
        self._overlay_surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)

    def reset_frame_triggers(self):
        """Called each frame to clear single-frame impulses."""
        self.just_attacked = False
        self.just_dashed = False
        self.just_interacted = False
        self.just_used_scroll = False
        self.just_paused = False

    def screen_to_virtual(self, screen_x, screen_y, screen_w, screen_h):
        scale = min(screen_w / VIRTUAL_WIDTH, screen_h / VIRTUAL_HEIGHT)
        offset_x = (screen_w - VIRTUAL_WIDTH * scale) / 2
        offset_y = (screen_h - VIRTUAL_HEIGHT * scale) / 2
        vx = (screen_x - offset_x) / scale
        vy = (screen_y - offset_y) / scale
        return vx, vy

    def handle_touch_down(self, touch_id, vx, vy):
        self.enabled = True  # Auto-enable on touch

        # 1. Check Pause button
        p = self.btn_pause
        if math.hypot(vx - p["x"], vy - p["y"]) <= p["radius"] + 8:
            p["pressed"] = True
            p["touch_id"] = touch_id
            self.just_paused = True
            return

        # 2. Check Action Buttons
        for b, flag_attr in [
            (self.btn_attack, "just_attacked"),
            (self.btn_dash, "just_dash"),
            (self.btn_interact, "just_interacted"),
            (self.btn_scroll, "just_used_scroll")
        ]:
            if not b.get("visible", True):
                continue
            dist = math.hypot(vx - b["x"], vy - b["y"])
            if dist <= b["radius"] + 8:
                b["pressed"] = True
                b["touch_id"] = touch_id
                if flag_attr == "just_dash":
                    self.just_dashed = True
                elif flag_attr == "just_attacked":
                    self.just_attacked = True
                    self.is_attacking = True
                elif flag_attr == "just_interacted":
                    self.just_interacted = True
                elif flag_attr == "just_used_scroll":
                    self.just_used_scroll = True
                return

        # 3. Left side of screen = Virtual Joystick
        if vx < VIRTUAL_WIDTH * 0.5:
            self.stick_touch_id = touch_id
            self.is_stick_active = True
            # Optional floating joystick: center on finger touch if near bottom
            if vy > VIRTUAL_HEIGHT * 0.4:
                self.stick_base_x = vx
                self.stick_base_y = vy
            self._update_stick(vx, vy)

    def handle_touch_motion(self, touch_id, vx, vy):
        # Update joystick if matches touch ID
        if touch_id == self.stick_touch_id and self.is_stick_active:
            self._update_stick(vx, vy)

    def handle_touch_up(self, touch_id):
        # 1. Release joystick
        if touch_id == self.stick_touch_id:
            self.is_stick_active = False
            self.stick_touch_id = None
            self.stick_pos = [float(self.stick_base_x), float(self.stick_base_y)]
            self.move_x = 0.0
            self.move_y = 0.0

        # 2. Release buttons
        for b in (self.btn_attack, self.btn_dash, self.btn_interact, self.btn_scroll, self.btn_pause):
            if b["touch_id"] == touch_id:
                b["pressed"] = False
                b["touch_id"] = None
                if b == self.btn_attack:
                    self.is_attacking = False

    def _update_stick(self, vx, vy):
        dx = vx - self.stick_base_x
        dy = vy - self.stick_base_y
        dist = math.hypot(dx, dy)
        max_dist = float(self.stick_base_radius)

        if dist < 4.0:
            self.stick_pos = [self.stick_base_x, self.stick_base_y]
            self.move_x = 0.0
            self.move_y = 0.0
            return

        clamped_dist = min(dist, max_dist)
        norm_x = dx / dist
        norm_y = dy / dist

        self.stick_pos = [
            self.stick_base_x + norm_x * clamped_dist,
            self.stick_base_y + norm_y * clamped_dist
        ]

        # Normalized movement output
        ratio = clamped_dist / max_dist
        self.move_x = norm_x * ratio
        self.move_y = norm_y * ratio

    def update_context(self, can_interact_chest, has_scroll, dash_cooldown_ratio=0.0):
        """Update button visibilities and states based on player game context."""
        self.btn_interact["visible"] = can_interact_chest
        self.btn_scroll["visible"] = has_scroll
        self.dash_cd_ratio = dash_cooldown_ratio

    def draw(self, surface):
        if not self.enabled:
            return

        self._overlay_surf.fill((0, 0, 0, 0))

        # 1. Draw Virtual Joystick
        bx, by = int(self.stick_base_x), int(self.stick_base_y)
        kx, ky = int(self.stick_pos[0]), int(self.stick_pos[1])

        # Outer base ring
        pygame.draw.circle(self._overlay_surf, (20, 25, 45, 120), (bx, by), self.stick_base_radius)
        pygame.draw.circle(self._overlay_surf, (80, 110, 160, 180), (bx, by), self.stick_base_radius, 2)
        # Inner guide cross
        pygame.draw.line(self._overlay_surf, (80, 110, 160, 100), (bx - 10, by), (bx + 10, by), 1)
        pygame.draw.line(self._overlay_surf, (80, 110, 160, 100), (bx, by - 10), (bx, by + 10), 1)

        # Thumb Knob
        knob_color = (255, 215, 0, 220) if self.is_stick_active else (160, 190, 240, 180)
        pygame.draw.circle(self._overlay_surf, (30, 40, 65, 200), (kx, ky), self.stick_knob_radius)
        pygame.draw.circle(self._overlay_surf, knob_color, (kx, ky), self.stick_knob_radius, 2)
        pygame.draw.circle(self._overlay_surf, knob_color, (kx, ky), 4)

        # 2. Draw Action Buttons
        # Helper button drawer
        def draw_btn(btn, primary_col, border_col):
            x, y, r = int(btn["x"]), int(btn["y"]), int(btn["radius"])
            is_down = btn["pressed"]
            draw_r = r - 2 if is_down else r
            bg_col = (primary_col[0], primary_col[1], primary_col[2], 180 if is_down else 110)
            pygame.draw.circle(self._overlay_surf, bg_col, (x, y), draw_r)
            pygame.draw.circle(self._overlay_surf, border_col, (x, y), draw_r, 2)

            # Icon or text
            if btn["label"] == "||":
                pygame.draw.rect(self._overlay_surf, COLOR_WHITE, (x - 4, y - 5, 3, 10))
                pygame.draw.rect(self._overlay_surf, COLOR_WHITE, (x + 1, y - 5, 3, 10))
            elif btn["label"] == "ATK":
                # Sword cross icon
                pygame.draw.line(self._overlay_surf, COLOR_WHITE, (x - 6, y + 6), (x + 6, y - 6), 2)
                pygame.draw.line(self._overlay_surf, COLOR_WHITE, (x - 2, y + 1), (x - 6, y + 5), 2)
                pygame.draw.circle(self._overlay_surf, COLOR_RED, (x + 4, y - 4), 2)
            elif btn["label"] == "DASH":
                # Double chevron dash icon
                pygame.draw.line(self._overlay_surf, COLOR_CYAN, (x - 4, y - 5), (x + 2, y), 2)
                pygame.draw.line(self._overlay_surf, COLOR_CYAN, (x + 2, y), (x - 4, y + 5), 2)
            elif btn["label"] == "USE":
                # Chest / Key icon
                pygame.draw.rect(self._overlay_surf, COLOR_GOLD, (x - 6, y - 4, 12, 8), 1)
                pygame.draw.circle(self._overlay_surf, COLOR_GOLD, (x, y), 2)
            elif btn["label"] == "SPELL":
                # Meteor spark icon
                pygame.draw.circle(self._overlay_surf, COLOR_GOLD, (x, y), 5)
                pygame.draw.circle(self._overlay_surf, COLOR_RED, (x, y), 2)

        # Attack Button
        draw_btn(self.btn_attack, (140, 20, 20), (255, 100, 100, 220))

        # Dash Button with Cooldown Arc
        draw_btn(self.btn_dash, (20, 80, 140), (100, 200, 255, 220))
        if getattr(self, "dash_cd_ratio", 0.0) > 0.0:
            # Draw cooldown darkening mask
            cd_r = self.btn_dash["radius"]
            pygame.draw.circle(self._overlay_surf, (0, 0, 0, 130), (self.btn_dash["x"], self.btn_dash["y"]), cd_r)

        # Interact Button (only if near chest/portal)
        if self.btn_interact.get("visible", False):
            draw_btn(self.btn_interact, (160, 130, 20), (255, 230, 100, 240))

        # Spell Button (only if player has scroll)
        if self.btn_scroll.get("visible", False):
            draw_btn(self.btn_scroll, (120, 30, 120), (240, 140, 255, 240))

        # Pause Button
        draw_btn(self.btn_pause, (30, 30, 45), (160, 160, 180, 200))

        surface.blit(self._overlay_surf, (0, 0))
