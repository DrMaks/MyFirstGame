"""
Game UI Screens: Main Menu, Upgrade Picker (Level-up modal), Pause, Game Over, and Victory.
Fully localized with dynamic RU/EN switching, crisp drop-shadowed fonts, and precise card boundaries.
"""

import random
import pygame
from src.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_BLACK, COLOR_DARK_BLUE,
    COLOR_PURPLE, COLOR_RED, COLOR_CYAN, COLOR_GOLD, COLOR_WHITE,
    COLOR_LIGHT_GRAY, COLOR_GREEN, get_font
)
from src.localization import loc

ALL_UPGRADES_BASE = [
    {"id": "multishot", "icon": "sword"},
    {"id": "damage", "icon": "staff"},
    {"id": "attack_speed", "icon": "bow"},
    {"id": "swift_boots", "icon": "sword"},
    {"id": "ricochet", "icon": "staff"},
    {"id": "vampirism", "icon": "potion_hp"},
    {"id": "fire_aura", "icon": "potion_mana"},
    {"id": "max_hp", "icon": "potion_hp"}
]


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines


class MenuRenderer:
    def __init__(self, pixel_art):
        self.art = pixel_art
        self.title_font = get_font(18, bold=True)
        self.header_font = get_font(13, bold=True)
        self.text_font = get_font(11, bold=True)
        self.small_font = get_font(10, bold=True)

    def _render_shadow_text(self, surface, font, text, pos, color, shadow_color=(10, 8, 15)):
        x, y = pos
        # 1px drop shadow
        sh_surf = font.render(text, True, shadow_color)
        surface.blit(sh_surf, (x + 1, y + 1))
        # Main text
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (x, y))

    def draw_main_menu(self, surface, selected_idx, timer):
        surface.fill(COLOR_BLACK)

        # Title
        title_text = loc.get("game_title")
        title_surf = self.title_font.render(title_text, True, COLOR_GOLD)
        surface.blit(title_surf, ((VIRTUAL_WIDTH - title_surf.get_width()) // 2, 42))

        sub_surf = self.small_font.render(loc.get("game_subtitle"), True, COLOR_CYAN)
        surface.blit(sub_surf, ((VIRTUAL_WIDTH - sub_surf.get_width()) // 2, 68))

        options = [
            loc.get("start_game"),
            loc.get("skill_tree"),
            loc.get("settings"),
            loc.get("quit")
        ]
        for i, opt in enumerate(options):
            is_sel = (i == selected_idx)
            color = COLOR_WHITE if is_sel else COLOR_LIGHT_GRAY
            prefix = "> " if is_sel else "  "
            y_pos = 100 + i * 26
            self._render_shadow_text(
                surface, self.header_font, f"{prefix}{opt}",
                ((VIRTUAL_WIDTH - self.header_font.size(f"{prefix}{opt}")[0]) // 2, y_pos),
                color
            )

        controls_tip = self.small_font.render(loc.get("menu_hint"), True, (130, 120, 150))
        surface.blit(controls_tip, ((VIRTUAL_WIDTH - controls_tip.get_width()) // 2, VIRTUAL_HEIGHT - 24))

    def draw_pause_menu(self, surface, selected_idx):
        dim = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim.fill((10, 8, 15, 195))
        surface.blit(dim, (0, 0))

        box_w, box_h = 240, 160
        bx = (VIRTUAL_WIDTH - box_w) // 2
        by = (VIRTUAL_HEIGHT - box_h) // 2

        pygame.draw.rect(surface, (28, 24, 40), (bx, by, box_w, box_h))
        pygame.draw.rect(surface, COLOR_PURPLE, (bx, by, box_w, box_h), 2)

        p_title = loc.get("paused_title")
        self._render_shadow_text(
            surface, self.header_font, p_title,
            (bx + (box_w - self.header_font.size(p_title)[0]) // 2, by + 12),
            COLOR_GOLD
        )

        opts = [
            loc.get("resume"),
            loc.get("skill_tree"),
            loc.get("settings"),
            loc.get("quit_title")
        ]
        for i, opt in enumerate(opts):
            is_sel = (i == selected_idx)
            color = COLOR_WHITE if is_sel else COLOR_LIGHT_GRAY
            label = f"{'> ' if is_sel else '  '}{opt}"
            self._render_shadow_text(
                surface, self.text_font, label,
                (bx + 24, by + 42 + i * 26),
                color
            )

    def get_main_menu_option_at_pos(self, virtual_x, virtual_y):
        for i in range(4):
            y_pos = 100 + i * 26
            if y_pos - 4 <= virtual_y <= y_pos + 22:
                if 60 <= virtual_x <= VIRTUAL_WIDTH - 60:
                    return i
        return -1

    def get_pause_menu_option_at_pos(self, virtual_x, virtual_y):
        box_w, box_h = 240, 160
        bx = (VIRTUAL_WIDTH - box_w) // 2
        by = (VIRTUAL_HEIGHT - box_h) // 2
        for i in range(4):
            y_pos = by + 42 + i * 26
            if y_pos - 4 <= virtual_y <= y_pos + 22:
                if bx <= virtual_x <= bx + box_w:
                    return i
        return -1

    def get_upgrade_card_at_pos(self, virtual_x, virtual_y, num_options):
        card_w, card_h = 138, 155
        spacing = 14
        total_w = num_options * card_w + (num_options - 1) * spacing
        start_x = (VIRTUAL_WIDTH - total_w) // 2
        card_y = 50

        for i in range(num_options):
            cx = start_x + i * (card_w + spacing)
            if cx <= virtual_x <= cx + card_w and card_y <= virtual_y <= card_y + card_h:
                return i
        return -1

    def draw_upgrade_picker(self, surface, upgrade_options, selected_idx):
        dim = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim.fill((10, 8, 15, 210))
        surface.blit(dim, (0, 0))

        title = loc.get("level_up_title")
        self._render_shadow_text(
            surface, self.header_font, title,
            ((VIRTUAL_WIDTH - self.header_font.size(title)[0]) // 2, 20),
            COLOR_GOLD
        )

        card_w, card_h = 138, 155
        spacing = 14
        total_w = len(upgrade_options) * card_w + (len(upgrade_options) - 1) * spacing
        start_x = (VIRTUAL_WIDTH - total_w) // 2
        card_y = 50

        max_text_width = card_w - 16

        for i, upg_base in enumerate(upgrade_options):
            upg_info = loc.get_upgrade(upg_base["id"])
            cx = start_x + i * (card_w + spacing)
            is_sel = (i == selected_idx)

            # Card background
            card_bg = (38, 30, 56) if is_sel else (24, 18, 34)
            pygame.draw.rect(surface, card_bg, (cx, card_y, card_w, card_h))
            border_col = COLOR_GOLD if is_sel else COLOR_PURPLE
            pygame.draw.rect(surface, border_col, (cx, card_y, card_w, card_h), 2 if is_sel else 1)

            # Icon
            icon_surf = self.art.get_sprite(upg_base["icon"])
            surface.blit(icon_surf, (cx + (card_w - 16) // 2, card_y + 12))

            # Upgrade Title (centered, drop shadow)
            title_str = upg_info["name"]
            title_x = cx + (card_w - self.text_font.size(title_str)[0]) // 2
            self._render_shadow_text(
                surface, self.text_font, title_str,
                (title_x, card_y + 36),
                COLOR_WHITE if is_sel else (200, 195, 215)
            )

            # Description (word-wrapped strictly inside max_text_width)
            desc_lines = wrap_text(upg_info["desc"], self.small_font, max_text_width)
            for li, line_str in enumerate(desc_lines[:5]):
                line_x = cx + (card_w - self.small_font.size(line_str)[0]) // 2
                self._render_shadow_text(
                    surface, self.small_font, line_str,
                    (line_x, card_y + 60 + li * 15),
                    (235, 235, 245) if is_sel else COLOR_LIGHT_GRAY
                )

        hint = loc.get("level_up_hint")
        self._render_shadow_text(
            surface, self.small_font, hint,
            ((VIRTUAL_WIDTH - self.small_font.size(hint)[0]) // 2, VIRTUAL_HEIGHT - 22),
            COLOR_GOLD
        )

    def draw_game_over(self, surface, stats, selected_idx):
        surface.fill((20, 10, 15))

        title = loc.get("game_over_title")
        self._render_shadow_text(
            surface, self.title_font, title,
            ((VIRTUAL_WIDTH - self.title_font.size(title)[0]) // 2, 40),
            COLOR_RED
        )

        lines = [
            f"{loc.get('stat_level')} {stats.get('level', 1)}",
            f"{loc.get('stat_gold')} {stats.get('gold', 0)}",
            f"{loc.get('stat_kills')} {stats.get('kills', 0)}"
        ]
        for i, l in enumerate(lines):
            self._render_shadow_text(
                surface, self.text_font, l,
                ((VIRTUAL_WIDTH - self.text_font.size(l)[0]) // 2, 90 + i * 20),
                COLOR_WHITE
            )

        opts = [loc.get("retry"), loc.get("quit_title")]
        for i, opt in enumerate(opts):
            is_sel = (i == selected_idx)
            color = COLOR_GOLD if is_sel else COLOR_LIGHT_GRAY
            prefix = "> " if is_sel else "  "
            label = f"{prefix}{opt}"
            self._render_shadow_text(
                surface, self.header_font, label,
                ((VIRTUAL_WIDTH - self.header_font.size(label)[0]) // 2, 175 + i * 26),
                color
            )

    def draw_victory(self, surface, stats, selected_idx):
        surface.fill((15, 25, 20))

        title = loc.get("victory_title")
        self._render_shadow_text(
            surface, self.title_font, title,
            ((VIRTUAL_WIDTH - self.title_font.size(title)[0]) // 2, 38),
            COLOR_GOLD
        )

        sub = loc.get("victory_subtitle")
        self._render_shadow_text(
            surface, self.text_font, sub,
            ((VIRTUAL_WIDTH - self.text_font.size(sub)[0]) // 2, 66),
            COLOR_CYAN
        )

        lines = [
            f"{loc.get('stat_fin_level')} {stats.get('level', 1)}",
            f"{loc.get('stat_fin_gold')} {stats.get('gold', 0)}",
            f"{loc.get('stat_fin_kills')} {stats.get('kills', 0)}"
        ]
        for i, l in enumerate(lines):
            self._render_shadow_text(
                surface, self.text_font, l,
                ((VIRTUAL_WIDTH - self.text_font.size(l)[0]) // 2, 102 + i * 20),
                COLOR_WHITE
            )

        opts = [loc.get("play_again"), loc.get("quit_title")]
        for i, opt in enumerate(opts):
            is_sel = (i == selected_idx)
            color = COLOR_GOLD if is_sel else COLOR_LIGHT_GRAY
            prefix = "> " if is_sel else "  "
            label = f"{prefix}{opt}"
            self._render_shadow_text(
                surface, self.header_font, label,
                ((VIRTUAL_WIDTH - self.header_font.size(label)[0]) // 2, 180 + i * 26),
                color
            )
