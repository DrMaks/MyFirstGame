"""
Retro In-Game HUD: Health Bar, XP Bar, Dash Indicator, Boss HP, Floor Display, and Controls Hint.
Fully localized with crisp drop-shadowed typography.
"""

import math
import pygame
from src.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_BLACK, COLOR_DARK_BLUE,
    COLOR_RED, COLOR_ORANGE, COLOR_CYAN, COLOR_GOLD, COLOR_WHITE, COLOR_LIGHT_GRAY,
    COLOR_PURPLE, COLOR_GREEN, get_font
)
from src.localization import loc


class HUD:
    def __init__(self, pixel_art):
        self.art = pixel_art
        self.font = get_font(11, bold=True)
        self.small_font = get_font(9, bold=True)
        self.boss_font = get_font(12, bold=True)

    def _render_shadow_text(self, surface, font, text, pos, color, shadow_color=(10, 8, 15)):
        x, y = pos
        sh_surf = font.render(text, True, shadow_color)
        surface.blit(sh_surf, (x + 1, y + 1))
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (x, y))

    def draw(self, surface, player, boss=None, minimap=None, floor=1):
        # 1. Health Bar (top left)
        bar_x, bar_y = 10, 10
        bar_w, bar_h = 75, 7
        hp_ratio = max(0.0, min(1.0, player.hp / player.max_hp))

        pygame.draw.rect(surface, (25, 20, 30), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(surface, (70, 20, 30), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * hp_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_RED, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surface, COLOR_WHITE, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)

        hp_txt = f"{loc.get('hp')} {int(player.hp)}/{player.max_hp}"
        self._render_shadow_text(surface, self.font, hp_txt, (bar_x + bar_w + 6, bar_y - 2), COLOR_WHITE)

        # 2. XP Bar (directly beneath HP)
        xp_y = bar_y + 11
        xp_w, xp_h = 75, 5
        xp_ratio = max(0.0, min(1.0, player.xp / player.xp_to_next))

        pygame.draw.rect(surface, (20, 25, 35), (bar_x - 1, xp_y - 1, xp_w + 2, xp_h + 2))
        fill_xp = int(xp_w * xp_ratio)
        if fill_xp > 0:
            pygame.draw.rect(surface, COLOR_CYAN, (bar_x, xp_y, fill_xp, xp_h))
        pygame.draw.rect(surface, COLOR_LIGHT_GRAY, (bar_x - 1, xp_y - 1, xp_w + 2, xp_h + 2), 1)

        lvl_txt = f"{loc.get('lvl')} {player.level}"
        self._render_shadow_text(surface, self.font, lvl_txt, (bar_x + xp_w + 6, xp_y - 3), COLOR_CYAN)

        # 3. Dash Cooldown & Shield indicator
        dash_y = xp_y + 9
        dash_ready = (player.dash_cooldown_timer <= 0)
        dash_color = COLOR_GREEN if dash_ready else COLOR_LIGHT_GRAY
        dash_txt = loc.get("dash_ready") if dash_ready else loc.get("dash_wait")
        self._render_shadow_text(surface, self.small_font, dash_txt, (bar_x, dash_y), dash_color)

        if getattr(player, "shield_charges", 0) > 0:
            shield_txt = f"[{loc.get('shield')}: {player.shield_charges}]"
            self._render_shadow_text(surface, self.small_font, shield_txt, (bar_x + 65, dash_y), COLOR_CYAN)

        # 4. Gold counter & Meteor relic
        coin_surf = self.art.get_sprite("coin")
        coin_x = 10
        coin_y = dash_y + 13
        surface.blit(coin_surf, (coin_x, coin_y))
        gold_txt = f"{player.gold}"
        self._render_shadow_text(surface, self.font, gold_txt, (coin_x + 12, coin_y - 1), COLOR_GOLD)

        if getattr(player, "has_meteor_scroll", False):
            scroll_icon = self.art.get_sprite("scroll_meteor")
            surface.blit(scroll_icon, (coin_x + 50, coin_y - 1))

        # 5. Minimap & Floor depth (top right)
        if minimap:
            minimap.draw(surface, player.x, player.y, (VIRTUAL_WIDTH - 66, 8))

        floor_str = f"{loc.get('floor')} {floor}"
        self._render_shadow_text(
            surface, self.font, floor_str,
            (VIRTUAL_WIDTH - 66, 68),
            COLOR_GOLD
        )

        # 6. Bottom screen persistent controls hint bar
        tip_text = loc.get("hud_controls_bar")
        tip_w, tip_h = self.small_font.size(tip_text)
        pill_w = tip_w + 12
        pill_h = tip_h + 4
        pill_x = (VIRTUAL_WIDTH - pill_w) // 2
        pill_y = VIRTUAL_HEIGHT - pill_h - 2

        pill_bg = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pill_bg.fill((15, 12, 22, 170))
        surface.blit(pill_bg, (pill_x, pill_y))
        self._render_shadow_text(surface, self.small_font, tip_text, (pill_x + 6, pill_y + 2), (180, 175, 200))

        # 7. Boss Health Bar
        boss_dist = math.hypot(player.x - boss.x, player.y - boss.y) if boss else 9999
        if boss and boss.hp > 0 and (boss.hp < boss.max_hp or boss_dist < 200.0):
            boss_bar_w = 200
            boss_bar_h = 8
            boss_x = (VIRTUAL_WIDTH - boss_bar_w) // 2
            boss_y = VIRTUAL_HEIGHT - 32

            boss_title = loc.get("boss_title")
            self._render_shadow_text(
                surface, self.boss_font, boss_title,
                (boss_x + (boss_bar_w - self.boss_font.size(boss_title)[0]) // 2, boss_y - 13),
                COLOR_RED
            )

            b_ratio = max(0.0, min(1.0, boss.hp / boss.max_hp))
            pygame.draw.rect(surface, (25, 10, 15), (boss_x - 1, boss_y - 1, boss_bar_w + 2, boss_bar_h + 2))
            pygame.draw.rect(surface, (80, 20, 25), (boss_x, boss_y, boss_bar_w, boss_bar_h))
            b_fill = int(boss_bar_w * b_ratio)
            if b_fill > 0:
                fill_color = COLOR_ORANGE if boss.enraged else COLOR_RED
                pygame.draw.rect(surface, fill_color, (boss_x, boss_y, b_fill, boss_bar_h))
            pygame.draw.rect(surface, COLOR_GOLD, (boss_x - 1, boss_y - 1, boss_bar_w + 2, boss_bar_h + 2), 1)
