"""
Settings Menu with dynamic Language selection (Russian / English),
CRT filter toggle, volume controls, and controls guide.
"""

import pygame
from src.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_BLACK, COLOR_DARK_BLUE,
    COLOR_PURPLE, COLOR_GOLD, COLOR_WHITE, COLOR_LIGHT_GRAY,
    COLOR_CYAN, COLOR_GREEN, get_font
)
from src.localization import loc


class SettingsMenu:
    def __init__(self, audio_synth, chiptune_engine, crt_filter, lighting_engine=None):
        self.audio_synth = audio_synth
        self.chiptune = chiptune_engine
        self.crt = crt_filter
        self.lighting = lighting_engine

        self.master_vol = 80
        self.music_vol = 70
        self.sfx_vol = 85
        self.brightness = 100  # 60% to 160%
        self.crt_enabled = True
        self.fullscreen = False

        self.selected_idx = 0
        self.in_controls_view = False

        self.options_keys = [
            "master_vol",
            "music_vol",
            "sfx_vol",
            "brightness",
            "crt_scanlines",
            "fullscreen",
            "language",
            "controls_btn",
            "back"
        ]

        self.title_font = get_font(15, bold=True)
        self.header_font = get_font(12, bold=True)
        self.text_font = get_font(11, bold=True)
        self.small_font = get_font(10, bold=True)

    def _render_shadow_text(self, surface, font, text, pos, color, shadow_color=(10, 8, 15)):
        x, y = pos
        sh_surf = font.render(text, True, shadow_color)
        surface.blit(sh_surf, (x + 1, y + 1))
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (x, y))

    def handle_input(self, action):
        if self.in_controls_view:
            if action in ("select", "back"):
                self.in_controls_view = False
            return None

        num_opts = len(self.options_keys)
        if action == "up":
            self.selected_idx = (self.selected_idx - 1) % num_opts
        elif action == "down":
            self.selected_idx = (self.selected_idx + 1) % num_opts
        elif action in ("left", "right"):
            delta = -10 if action == "left" else 10
            if self.selected_idx == 0:
                self.master_vol = max(0, min(100, self.master_vol + delta))
                self.chiptune.set_volume(master_vol=self.master_vol / 100.0)
            elif self.selected_idx == 1:
                self.music_vol = max(0, min(100, self.music_vol + delta))
                self.chiptune.set_volume(music_vol=self.music_vol / 100.0)
            elif self.selected_idx == 2:
                self.sfx_vol = max(0, min(100, self.sfx_vol + delta))
            elif self.selected_idx == 3:
                self.brightness = max(60, min(160, self.brightness + delta))
                if self.lighting:
                    self.lighting.set_brightness(self.brightness / 100.0)
            elif self.selected_idx == 4:
                self.crt_enabled = not self.crt_enabled
                self.crt.enabled = self.crt_enabled
            elif self.selected_idx == 5:
                self.fullscreen = not self.fullscreen
                return "toggle_fullscreen"
            elif self.selected_idx == 6:
                loc.toggle_lang()
        elif action == "select":
            if self.selected_idx == 4:
                self.crt_enabled = not self.crt_enabled
                self.crt.enabled = self.crt_enabled
            elif self.selected_idx == 5:
                self.fullscreen = not self.fullscreen
                return "toggle_fullscreen"
            elif self.selected_idx == 6:
                loc.toggle_lang()
            elif self.selected_idx == 7:
                self.in_controls_view = True
            elif self.selected_idx == 8:
                return "back"
        elif action == "back":
            return "back"

        return None

    def draw(self, surface):
        surface.fill(COLOR_BLACK)

        if self.in_controls_view:
            self._draw_controls(surface)
            return

        # Main Settings View
        title = loc.get("settings_title")
        self._render_shadow_text(
            surface, self.title_font, title,
            ((VIRTUAL_WIDTH - self.title_font.size(title)[0]) // 2, 14),
            COLOR_GOLD
        )

        for i, opt_key in enumerate(self.options_keys):
            is_sel = (i == self.selected_idx)
            col = COLOR_WHITE if is_sel else COLOR_LIGHT_GRAY
            prefix = "> " if is_sel else "  "

            val_str = ""
            if opt_key == "master_vol":
                val_str = f"<{self.master_vol}%>"
            elif opt_key == "music_vol":
                val_str = f"<{self.music_vol}%>"
            elif opt_key == "sfx_vol":
                val_str = f"<{self.sfx_vol}%>"
            elif opt_key == "brightness":
                val_str = f"<{self.brightness}%>"
            elif opt_key == "crt_scanlines":
                val_str = f"<{loc.get('on') if self.crt_enabled else loc.get('off')}>"
            elif opt_key == "fullscreen":
                val_str = f"<{loc.get('on') if self.fullscreen else loc.get('off')}>"
            elif opt_key == "language":
                val_str = f"<{loc.get('lang_name')}>"
            elif opt_key == "controls_btn":
                val_str = f"[{loc.get('open')}]"

            label = f"{prefix}{loc.get(opt_key)}"
            y = 38 + i * 21

            self._render_shadow_text(surface, self.text_font, label, (24, y), col)
            if val_str:
                val_w = self.text_font.size(val_str)[0]
                self._render_shadow_text(
                    surface, self.text_font, val_str,
                    (VIRTUAL_WIDTH - val_w - 28, y),
                    COLOR_GOLD if is_sel else COLOR_CYAN
                )

        tip = loc.get("settings_hint")
        self._render_shadow_text(
            surface, self.small_font, tip,
            ((VIRTUAL_WIDTH - self.small_font.size(tip)[0]) // 2, VIRTUAL_HEIGHT - 18),
            (140, 135, 165)
        )

    def _draw_controls(self, surface):
        title = loc.get("controls_title")
        self._render_shadow_text(
            surface, self.title_font, title,
            ((VIRTUAL_WIDTH - self.title_font.size(title)[0]) // 2, 14),
            COLOR_GOLD
        )

        col_w = 214
        col_h = 192
        c1_x = 20
        c2_x = 246
        y_top = 38

        # Column 1: Keyboard & Mouse
        pygame.draw.rect(surface, (28, 22, 40), (c1_x, y_top, col_w, col_h))
        pygame.draw.rect(surface, COLOR_PURPLE, (c1_x, y_top, col_w, col_h), 1)

        t_kb = loc.get("kb_title")
        self._render_shadow_text(
            surface, self.header_font, t_kb,
            (c1_x + (col_w - self.header_font.size(t_kb)[0]) // 2, y_top + 8),
            COLOR_CYAN
        )

        kb_items = [
            (loc.get("act_move"), loc.get("bind_kb_move")),
            (loc.get("act_aim"), loc.get("bind_kb_aim")),
            (loc.get("act_attack"), loc.get("bind_kb_attack")),
            (loc.get("act_dash"), loc.get("bind_kb_dash")),
            (loc.get("act_chest"), loc.get("bind_kb_chest")),
            (loc.get("act_pause"), loc.get("bind_kb_pause")),
            (loc.get("act_screen"), loc.get("bind_kb_screen"))
        ]

        for i, (action_name, bind_name) in enumerate(kb_items):
            row_y = y_top + 32 + i * 21
            self._render_shadow_text(surface, self.small_font, action_name, (c1_x + 8, row_y), COLOR_LIGHT_GRAY)
            self._render_shadow_text(surface, self.small_font, bind_name, (c1_x + 64, row_y), COLOR_WHITE)

        # Column 2: Gamepad
        pygame.draw.rect(surface, (28, 22, 40), (c2_x, y_top, col_w, col_h))
        pygame.draw.rect(surface, COLOR_PURPLE, (c2_x, y_top, col_w, col_h), 1)

        t_pad = loc.get("pad_title")
        self._render_shadow_text(
            surface, self.header_font, t_pad,
            (c2_x + (col_w - self.header_font.size(t_pad)[0]) // 2, y_top + 8),
            COLOR_GREEN
        )

        pad_items = [
            (loc.get("act_move"), loc.get("bind_pad_move")),
            (loc.get("act_aim"), loc.get("bind_pad_aim")),
            (loc.get("act_attack"), loc.get("bind_pad_attack")),
            (loc.get("act_dash"), loc.get("bind_pad_dash")),
            (loc.get("act_chest"), loc.get("bind_pad_chest")),
            (loc.get("act_pause"), loc.get("bind_pad_pause")),
            (loc.get("act_vibration"), loc.get("bind_pad_vibe"))
        ]

        for i, (action_name, bind_name) in enumerate(pad_items):
            row_y = y_top + 32 + i * 21
            self._render_shadow_text(surface, self.small_font, action_name, (c2_x + 8, row_y), COLOR_LIGHT_GRAY)
            self._render_shadow_text(surface, self.small_font, bind_name, (c2_x + 64, row_y), COLOR_WHITE)

        back_tip = loc.get("controls_back_hint")
        self._render_shadow_text(
            surface, self.small_font, back_tip,
            ((VIRTUAL_WIDTH - self.small_font.size(back_tip)[0]) // 2, VIRTUAL_HEIGHT - 18),
            COLOR_GOLD
        )
