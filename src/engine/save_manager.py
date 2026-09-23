"""
Save Manager for persistent meta-progression, talent tree, and lifetime statistics.
Saves data to save_data.json in the user's game directory.
"""

import json
import os

SAVE_FILE = "save_data.json"

DEFAULT_SAVE = {
    "total_gold": 0,
    "talents": {
        "vitality": 0,      # Max HP (+10 per level)
        "strength": 0,      # Base Damage (+10% per level)
        "agility": 0,       # Move Speed (+5% per level, -10% dash cd)
        "greed": 0,         # Magnet radius & +15% gold per level
        "lethality": 0,     # Crit chance (+5% per level)
        "phoenix": 0        # Free revive once per run
    },
    "highest_floor": 1,
    "total_runs": 0,
    "boss_kills": 0
}

TALENT_CONFIG = {
    "vitality": {
        "max_lvl": 5,
        "base_cost": 25,
        "cost_mult": 1.6,
        "icon": "potion_hp"
    },
    "strength": {
        "max_lvl": 5,
        "base_cost": 30,
        "cost_mult": 1.7,
        "icon": "sword"
    },
    "agility": {
        "max_lvl": 5,
        "base_cost": 30,
        "cost_mult": 1.6,
        "icon": "sword"
    },
    "greed": {
        "max_lvl": 5,
        "base_cost": 20,
        "cost_mult": 1.5,
        "icon": "coin"
    },
    "lethality": {
        "max_lvl": 5,
        "base_cost": 40,
        "cost_mult": 1.8,
        "icon": "staff"
    },
    "phoenix": {
        "max_lvl": 1,
        "base_cost": 150,
        "cost_mult": 1.0,
        "icon": "potion_mana"
    }
}


class SaveManager:
    def __init__(self, filepath=SAVE_FILE):
        self.filepath = filepath
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge with default to ensure no missing keys
                    merged = dict(DEFAULT_SAVE)
                    merged.update(loaded)
                    if "talents" in loaded:
                        merged["talents"] = dict(DEFAULT_SAVE["talents"])
                        merged["talents"].update(loaded["talents"])
                    return merged
            except Exception as e:
                print(f"[SaveManager] Error loading save ({e}). Using defaults.")
        return dict(DEFAULT_SAVE)

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[SaveManager] Error saving data: {e}")

    def add_gold(self, amount):
        self.data["total_gold"] = max(0, self.data.get("total_gold", 0) + amount)
        self.save()

    def get_gold(self):
        return self.data.get("total_gold", 0)

    def get_talent_level(self, talent_id):
        return self.data.get("talents", {}).get(talent_id, 0)

    def get_talent_cost(self, talent_id):
        cfg = TALENT_CONFIG.get(talent_id)
        if not cfg:
            return 999999
        cur_lvl = self.get_talent_level(talent_id)
        if cur_lvl >= cfg["max_lvl"]:
            return -1  # Maxed out
        cost = int(cfg["base_cost"] * (cfg["cost_mult"] ** cur_lvl))
        return cost

    def upgrade_talent(self, talent_id):
        cost = self.get_talent_cost(talent_id)
        if cost > 0 and self.get_gold() >= cost:
            self.data["total_gold"] -= cost
            self.data["talents"][talent_id] = self.get_talent_level(talent_id) + 1
            self.save()
            return True
        return False
