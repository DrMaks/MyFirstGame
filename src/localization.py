"""
Localization Manager for Pixel Rogue.
Supports dynamic switching between Russian and English for all menus, HUD, settings, perks, and talents.
"""

STRINGS = {
    "ru": {
        # General & App
        "game_title": "Pixel Rogue: Dungeon of the Ancients",
        "game_subtitle": "RETRO PIXEL ROGUELIKE * STEAM EDITION",
        "lang_name": "РУССКИЙ",
        "on": "ВКЛ",
        "off": "ВЫКЛ",
        "open": "ОТКРЫТЬ",

        # Main Menu
        "start_game": "НАЧАТЬ ПРИКЛЮЧЕНИЕ",
        "skill_tree": "АЛТАРЬ ПРОКАЧКИ",
        "settings": "НАСТРОЙКИ",
        "quit": "ВЫХОД",
        "menu_hint": "[W / S / Стрелки] Выбор   [Enter / Пробел] Подтвердить",

        # Settings
        "settings_title": "НАСТРОЙКИ ЗВУКА И ВИДЕО",
        "master_vol": "ОБЩАЯ ГРОМКОСТЬ",
        "music_vol": "ГРОМКОСТЬ МУЗЫКИ",
        "sfx_vol": "ГРОМКОСТЬ ЭФФЕКТОВ",
        "crt_scanlines": "CRT СКАНЛАЙНЫ",
        "brightness": "ЯРКОСТЬ ПОДЗЕМЕЛЬЯ",
        "fullscreen": "ПОЛНЫЙ ЭКРАН",
        "language": "ЯЗЫК / LANGUAGE",
        "controls_btn": "УПРАВЛЕНИЕ (КЛАВИШИ / ГЕЙМПАД)",
        "back": "НАЗАД",
        "settings_hint": "[Влево/Вправо] Изменить  [Пробел/Enter] Выбрать  [Esc] Назад",

        # Skill Tree
        "skill_tree_title": "АЛТАРЬ ВЕЧНЫХ УЛУЧШЕНИЙ",
        "skill_tree_hint": "[Клик ЛКМ / Стрелки] Улучшить   [Esc] Назад",
        "maxed": "МАКСИМУМ",
        "talent_vitality": "Живучесть",
        "talent_strength": "Сила Клинка",
        "talent_agility": "Проворство",
        "talent_greed": "Золотоискатель",
        "talent_lethality": "Смертоносность",
        "talent_phoenix": "Перо Феникса",

        # Controls Guide
        "controls_title": "УПРАВЛЕНИЕ: КЛАВИАТУРА И ГЕЙМПАД",
        "kb_title": "КЛАВИАТУРА + МЫШЬ",
        "pad_title": "ГЕЙМПАД (XBOX / PS)",
        "controls_back_hint": "[Esc / Пробел / Enter] Назад в настройки",

        "act_move": "Ходьба:",
        "act_aim": "Прицел:",
        "act_attack": "Атака:",
        "act_dash": "Кувырок:",
        "act_chest": "Сундук:",
        "act_pause": "Пауза:",
        "act_screen": "Экран:",
        "act_vibration": "Вибрация:",

        "bind_kb_move": "W, A, S, D / Стрелки",
        "bind_kb_aim": "Курсор мыши",
        "bind_kb_attack": "ЛКМ (Левая кнопка)",
        "bind_kb_dash": "Пробел или ПКМ",
        "bind_kb_chest": "Клавиша [E] или [F]",
        "bind_kb_pause": "Клавиша [Esc] или [P]",
        "bind_kb_screen": "Клавиша [F11]",

        "bind_pad_move": "Левый стик (L-Stick)",
        "bind_pad_aim": "Правый стик (R-Stick)",
        "bind_pad_attack": "Кнопка [X] / Курок [RT]",
        "bind_pad_dash": "Кнопка [A] (✕ на PS)",
        "bind_pad_chest": "Кнопка [Y] (△ на PS)",
        "bind_pad_pause": "Кнопка [Start / Menu]",
        "bind_pad_vibe": "Авто-реакция",

        # HUD & World
        "hp": "HP",
        "lvl": "УР.",
        "floor": "ЭТАЖ",
        "dash_ready": "ДЭШ: ГОТОВ",
        "dash_wait": "ДЭШ: ...",
        "shield": "ЩИТ",
        "boss_title": "ВЛАДЫКА ПОДЗЕМЕЛЬЯ",
        "chest_prompt": "[E/Y] ОТКРЫТЬ",
        "stairs_prompt": "[E/Y] СПУСТИТЬСЯ НА СЛЕДУЮЩИЙ ЭТАЖ",
        "hud_controls_bar": "[WASD] Ходьба  [ЛКМ] Огонь  [Пробел/ПКМ] Дэш  [E] Сундук  [Esc] Пауза",

        # Notifications
        "meteor_msg": "СВИТОК МЕТЕОРА СТИРАЕТ ВРАГОВ В ПЫЛЬ!",
        "shield_msg": "ЭНЕРГЕТИЧЕСКИЙ ЩИТ АКТИВИРОВАН!",
        "magnet_msg": "МАГНИТ ПРИТЯГИВАЕТ ВСЕ ЗОЛОТО!",
        "phoenix_msg": "ПЕРО ФЕНИКСА ВОСКРЕШАЕТ ВАС!",

        # Pause Menu
        "paused_title": "ИГРА НА ПАУЗЕ",
        "resume": "ПРОДОЛЖИТЬ",
        "quit_title": "В ГЛАВНОЕ МЕНЮ",

        # Upgrade Modal
        "level_up_title": "ВЫБЕРИТЕ УЛУЧШЕНИЕ (LEVEL UP)",
        "level_up_hint": "[Клик ЛКМ / Стрелки] Выбор   [Пробел / Enter] Подтвердить",

        # Game Over
        "game_over_title": "ВЫ ПОГИБЛИ В ПОДЗЕМЕЛЬЕ",
        "stat_level": "Достигнутый уровень:",
        "stat_gold": "Собрано золота:",
        "stat_kills": "Побеждено монстров:",
        "retry": "ПОПРОБОВАТЬ СНОВА",

        # Victory
        "victory_title": "ПОДЗЕМЕЛЬЕ ПОКОРЕНО!",
        "victory_subtitle": "Владыка Подземелья повержен, мир спасен!",
        "stat_fin_level": "Итоговый уровень:",
        "stat_fin_gold": "Золота в карманах:",
        "stat_fin_kills": "Всего уничтожено врагов:",
        "play_again": "ИГРАТЬ СНОВА"
    },
    "en": {
        # General & App
        "game_title": "Pixel Rogue: Dungeon of the Ancients",
        "game_subtitle": "RETRO PIXEL ROGUELIKE * STEAM EDITION",
        "lang_name": "ENGLISH",
        "on": "ON",
        "off": "OFF",
        "open": "VIEW",

        # Main Menu
        "start_game": "START ADVENTURE",
        "skill_tree": "SKILL TREE",
        "settings": "SETTINGS",
        "quit": "QUIT GAME",
        "menu_hint": "[W / S / Arrows] Navigate   [Enter / Space] Confirm",

        # Settings
        "settings_title": "AUDIO & VIDEO SETTINGS",
        "master_vol": "MASTER VOLUME",
        "music_vol": "MUSIC VOLUME",
        "sfx_vol": "SFX VOLUME",
        "crt_scanlines": "CRT SCANLINES",
        "brightness": "DUNGEON BRIGHTNESS",
        "fullscreen": "FULLSCREEN",
        "language": "LANGUAGE / ЯЗЫК",
        "controls_btn": "CONTROLS (KEYBOARD / GAMEPAD)",
        "back": "BACK",
        "settings_hint": "[Left/Right] Adjust  [Space/Enter] Toggle  [Esc] Back",

        # Skill Tree
        "skill_tree_title": "ALTAR OF PERSISTENT TALENTS",
        "skill_tree_hint": "[LMB Click / Arrows] Upgrade   [Esc] Back",
        "maxed": "MAX LEVEL",
        "talent_vitality": "Vitality",
        "talent_strength": "Strength",
        "talent_agility": "Agility",
        "talent_greed": "Greed Magnet",
        "talent_lethality": "Lethality",
        "talent_phoenix": "Phoenix Feather",

        # Controls Guide
        "controls_title": "CONTROLS: KEYBOARD & GAMEPAD",
        "kb_title": "KEYBOARD + MOUSE",
        "pad_title": "GAMEPAD (XBOX / PS)",
        "controls_back_hint": "[Esc / Space / Enter] Back to Settings",

        "act_move": "Move:",
        "act_aim": "Aim:",
        "act_attack": "Attack:",
        "act_dash": "Dash:",
        "act_chest": "Chest:",
        "act_pause": "Pause:",
        "act_screen": "Screen:",
        "act_vibration": "Vibration:",

        "bind_kb_move": "W, A, S, D / Arrows",
        "bind_kb_aim": "Mouse Cursor",
        "bind_kb_attack": "LMB (Left Click)",
        "bind_kb_dash": "Space or RMB",
        "bind_kb_chest": "Key [E] or [F]",
        "bind_kb_pause": "Key [Esc] or [P]",
        "bind_kb_screen": "Key [F11]",

        "bind_pad_move": "Left Stick (L-Stick)",
        "bind_pad_aim": "Right Stick (R-Stick)",
        "bind_pad_attack": "Button [X] / Trigger [RT]",
        "bind_pad_dash": "Button [A] (✕ on PS)",
        "bind_pad_chest": "Button [Y] (△ on PS)",
        "bind_pad_pause": "Button [Start / Menu]",
        "bind_pad_vibe": "Auto-feedback",

        # HUD & World
        "hp": "HP",
        "lvl": "LVL",
        "floor": "FLOOR",
        "dash_ready": "DASH: READY",
        "dash_wait": "DASH: ...",
        "shield": "SHIELD",
        "boss_title": "THE DUNGEON OVERLORD",
        "chest_prompt": "[E/Y] OPEN",
        "stairs_prompt": "[E/Y] DESCEND TO NEXT FLOOR",
        "hud_controls_bar": "[WASD] Move  [LMB] Shoot  [Space/RMB] Dash  [E] Chest  [Esc] Pause",

        # Notifications
        "meteor_msg": "METEOR SCROLL PURGES THE ROOM!",
        "shield_msg": "ENERGY SHIELD ACTIVATED!",
        "magnet_msg": "MAGNET DRAWS ALL GOLD TO YOU!",
        "phoenix_msg": "PHOENIX FEATHER REVIVES YOU!",

        # Pause Menu
        "paused_title": "GAME PAUSED",
        "resume": "RESUME",
        "quit_title": "QUIT TO TITLE",

        # Upgrade Modal
        "level_up_title": "CHOOSE AN UPGRADE (LEVEL UP)",
        "level_up_hint": "[LMB Click / Arrows] Select   [Space / Enter] Confirm",

        # Game Over
        "game_over_title": "YOU HAVE FALLEN IN BATTLE",
        "stat_level": "Level Reached:",
        "stat_gold": "Gold Collected:",
        "stat_kills": "Enemies Slain:",
        "retry": "TRY AGAIN",

        # Victory
        "victory_title": "DUNGEON CONQUERED!",
        "victory_subtitle": "The Dungeon Overlord has been defeated!",
        "stat_fin_level": "Final Level:",
        "stat_fin_gold": "Gold Hoarded:",
        "stat_fin_kills": "Total Kills:",
        "play_again": "PLAY AGAIN"
    }
}

UPGRADES_DATA = {
    "multishot": {
        "ru": {"name": "Двойной Выстрел", "desc": "Веер дополнительных магических снарядов."},
        "en": {"name": "Twin Spark", "desc": "Fires additional projectiles in a spread."}
    },
    "damage": {
        "ru": {"name": "Руна Мощи", "desc": "+25% к урону от всех ваших атак."},
        "en": {"name": "Power Rune", "desc": "+25% to damage of all attacks."}
    },
    "attack_speed": {
        "ru": {"name": "Чародейская Скорость", "desc": "+30% к скорости перезарядки и стрельбы."},
        "en": {"name": "Arcane Haste", "desc": "+30% faster fire rate and reload."}
    },
    "swift_boots": {
        "ru": {"name": "Сапоги Гермеса", "desc": "+20% к скорости бега героя."},
        "en": {"name": "Hermes Boots", "desc": "+20% movement speed increase."}
    },
    "ricochet": {
        "ru": {"name": "Прыгающие Искры", "desc": "Снаряды рикошетят от каменных стен."},
        "en": {"name": "Bouncing Sparks", "desc": "Shots bounce off dungeon walls."}
    },
    "vampirism": {
        "ru": {"name": "Вампиризм", "desc": "Шанс исцелить здоровье при убийстве врага."},
        "en": {"name": "Vampiric Drain", "desc": "Chance to heal health on enemy kill."}
    },
    "fire_aura": {
        "ru": {"name": "Огненный Плащ", "desc": "Постоянно поджигает ближайших монстров."},
        "en": {"name": "Flame Cloak", "desc": "Constantly burns surrounding enemies."}
    },
    "max_hp": {
        "ru": {"name": "Сердце Титана", "desc": "+35 к макс. здоровью и мгновенное лечение."},
        "en": {"name": "Titan Heart", "desc": "+35 Max Health and instant heal."}
    }
}


class Localization:
    def __init__(self, lang="ru"):
        self.lang = lang

    def set_language(self, lang):
        if lang in ("ru", "en"):
            self.lang = lang

    def toggle_lang(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        return self.lang

    def get(self, key):
        return STRINGS.get(self.lang, STRINGS["ru"]).get(key, key)

    def get_upgrade(self, upg_id):
        data = UPGRADES_DATA.get(upg_id, {})
        return data.get(self.lang, data.get("ru", {"name": upg_id, "desc": ""}))


# Global localization instance
loc = Localization("ru")
