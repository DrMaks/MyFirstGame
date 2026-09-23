"""
Interactive Skill Tree / Altar of Upgrades for persistent meta-progression.
Fully interactive via both Mouse click/hover and Keyboard/Gamepad navigation.
"""

import pygame
from src.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_BLACK, COLOR_DARK_BLUE,
    COLOR_PURPLE, COLOR_GOLD, COLOR_WHITE, COLOR_LIGHT_GRAY,
    COLOR_CYAN, COLOR_GREEN, COLOR_RED, get_font
)
from src.engine.save_manager import TALENT_CONFIG
from src.localization import loc

TALENT_ORDER = ["vitality", "strength", "agility", "greed", "lethality", "phoenix"]


class SkillTreeMenu:
    def __init__(self, save_manager, pixel_art, sound_synth):
        self.save_mgr = save_manager
        self.art = pixel_art
        self.sound = sound_synth

        self.selected_idx = 0
        self.hovered_idx = -1

        self.title_font = get_font(15, bold=True)
        self.header_font = get_font(12, bold=True)
        self.text_font = get_font(10, bold=True)
        self.small_font = get_font(9, bold=True)

    def _render_shadow_text(self, surface, font, text, pos, color, shadow_color=(10, 8, 15)):
        x, y = pos
        sh_surf = font.render(text, True, shadow_color)
        surface.blit(sh_surf, (x + 1, y + 1))
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (x, y))

    def handle_input(self, action, virtual_mouse_x=None, virtual_mouse_y=None, mouse_clicked=False):
        # 1. Mouse hover & click detection on talent cards
        card_w = 136
        card_h = 74
        start_x = 28
        start_y = 52
        gap_x = 14
        gap_y = 10

        if virtual_mouse_x is not None and virtual_mouse_y is not None:
            self.hovered_idx = -1
            for i, tid in enumerate(TALENT_ORDER):
                row = i // 3
                col = i % 3
                cx = start_x + col * (card_w + gap_x)
                cy = start_y + row * (card_h + gap_y)

                if cx <= virtual_mouse_x <= cx + card_w and cy <= virtual_mouse_y <= cy + card_h:
                    self.hovered_idx = i
                    self.selected_idx = i
                    if mouse_clicked:
                        return self.try_upgrade_selected()

        # 2. Keyboard / Gamepad actions
        if action == "up":
            self.selected_idx = (self.selected_idx - 3) % len(TALENT_ORDER)
            self.sound.play("swing")
        elif action == "down":
            self.selected_idx = (self.selected_idx + 3) % len(TALENT_ORDER)
            self.sound.play("swing")
        elif action == "left":
            self.selected_idx = (self.selected_idx - 1) % len(TALENT_ORDER)
            self.sound.play("swing")
        elif action == "right":
            self.selected_idx = (self.selected_idx + 1) % len(TALENT_ORDER)
            self.sound.play("swing")
        elif action == "select":
            return self.try_upgrade_selected()
        elif action == "back":
            return "back"

        return None

    def try_upgrade_selected(self):
        tid = TALENT_ORDER[self.selected_idx]
        success = self.save_mgr.upgrade_talent(tid)
        if success:
            self.sound.play("level_up")
            return "upgraded"
        else:
            self.sound.play("player_hurt")
            return "failed"

    def draw(self, surface):
        surface.fill(COLOR_BLACK)

        # Title
        title = loc.get("skill_tree_title")
        self._render_shadow_text(
            surface, self.title_font, title,
            ((VIRTUAL_WIDTH - self.title_font.size(title)[0]) // 2, 12),
            COLOR_GOLD
        )

        # Total Gold Counter
        gold_txt = f"{loc.get('stat_gold')} {self.save_mgr.get_gold()}"
        gold_w = self.header_font.size(gold_txt)[0]
        coin_surf = self.art.get_sprite("coin")
        surface.blit(coin_surf, ((VIRTUAL_WIDTH - gold_w) // 2 - 16, 31))
        self._render_shadow_text(
            surface, self.header_font, gold_txt,
            ((VIRTUAL_WIDTH - gold_w) // 2, 30),
            COLOR_GOLD
        )

        card_w = 136
        card_h = 74
        start_x = 28
        start_y = 52
        gap_x = 14
        gap_y = 10

        for i, tid in enumerate(TALENT_ORDER):
            row = i // 3
            col = i % 3
            cx = start_x + col * (card_w + gap_x)
            cy = start_y + row * (card_h + gap_y)

            is_sel = (i == self.selected_idx or i == self.hovered_idx)
            cfg = TALENT_CONFIG[tid]
            cur_lvl = self.save_mgr.get_talent_level(tid)
            max_lvl = cfg["max_lvl"]
            cost = self.save_mgr.get_talent_cost(tid)
            can_afford = (cost > 0 and self.save_mgr.get_gold() >= cost)

            # Card background
            card_bg = (42, 32, 60) if is_sel else (25, 20, 36)
            pygame.draw.rect(surface, card_bg, (cx, cy, card_w, card_h))
            border_col = COLOR_GOLD if is_sel else (COLOR_CYAN if can_afford else COLOR_PURPLE)
            pygame.draw.rect(surface, border_col, (cx, cy, card_w, card_h), 2 if is_sel else 1)

            # Icon
            icon = self.art.get_sprite(cfg["icon"])
            surface.blit(icon, (cx + 8, cy + 8))

            # Talent Name
            t_name = loc.get(f"talent_{tid}")
            self._render_shadow_text(surface, self.text_font, t_name, (cx + 28, cy + 9), COLOR_WHITE if is_sel else COLOR_LIGHT_GRAY)

            # Level Pips / Text
            lvl_str = f"LVL {cur_lvl}/{max_lvl}"
            self._render_shadow_text(surface, self.small_font, lvl_str, (cx + 28, cy + 24), COLOR_CYAN if cur_lvl > 0 else (130, 130, 150))

            # Level progress bar pips
            pip_x = cx + 8
            pip_y = cy + 40
            for p in range(max_lvl):
                p_color = COLOR_GOLD if p < cur_lvl else (60, 50, 75)
                pygame.draw.rect(surface, p_color, (pip_x + p * 12, pip_y, 9, 4))
                pygame.draw.rect(surface, (10, 8, 15), (pip_x + p * 12, pip_y, 9, 4), 1)

            # Cost / Max Status
            if cost > 0:
                cost_str = f"{cost} G"
                col = COLOR_GOLD if can_afford else COLOR_RED
                self._render_shadow_text(surface, self.text_font, cost_str, (cx + card_w - self.text_font.size(cost_str)[0] - 8, cy + 50), col)
            else:
                max_str = loc.get("maxed")
                self._render_shadow_text(surface, self.text_font, max_str, (cx + card_w - self.text_font.size(max_str)[0] - 8, cy + 50), COLOR_GREEN)

        # Bottom tip
        tip = loc.get("skill_tree_hint")
        self._render_shadow_text(
            surface, self.small_font, tip,
            ((VIRTUAL_WIDTH - self.small_font.size(tip)[0]) // 2, VIRTUAL_HEIGHT - 18),
            (140, 135, 165)
        )
