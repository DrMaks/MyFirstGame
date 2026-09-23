"""
Steamworks Integration Manager.
Handles Steam Achievements, Stats, and Rich Presence.
Designed to run safely without crashes whether Steam is active or during local standalone development.
"""

import os
import sys

ACHIEVEMENTS = {
    "ACH_FIRST_BLOOD": {"name": "First Blood", "desc": "Slay your first dungeon monster."},
    "ACH_CHEST_HUNTER": {"name": "Treasure Hunter", "desc": "Open a hidden dungeon chest."},
    "ACH_LEVEL_5": {"name": "Seasoned Adventurer", "desc": "Reach level 5 in a run."},
    "ACH_BOSS_SLAYER": {"name": "Dungeon Liberator", "desc": "Defeat the Dungeon Overlord!"},
    "ACH_RICH": {"name": "Gold Digger", "desc": "Amass 100 gold coins in the dungeon."}
}


class SteamManager:
    def __init__(self, app_id=480):
        self.app_id = app_id
        self.initialized = False
        self.steamworks = None
        self.unlocked_achievements = set()
        self._init_steam()

    def _init_steam(self):
        # Check if steam_appid.txt exists or create it
        if not os.path.exists("steam_appid.txt"):
            try:
                with open("steam_appid.txt", "w") as f:
                    f.write(str(self.app_id))
            except Exception:
                pass

        try:
            # Check for steamworks-py or ctypes wrapper
            import steamworks
            self.steamworks = steamworks.STEAMWORKS()
            self.steamworks.initialize()
            self.initialized = True
            print(f"[SteamManager] Steamworks successfully initialized! App ID: {self.app_id}")
            self.set_rich_presence("Exploring the Dungeon")
        except ImportError:
            print("[SteamManager] Steamworks wrapper not installed; running in local offline / dev mode.")
        except Exception as e:
            print(f"[SteamManager] Could not connect to Steam Client ({e}). Running in offline mode.")

    def unlock_achievement(self, ach_id):
        if ach_id in self.unlocked_achievements:
            return

        self.unlocked_achievements.add(ach_id)
        info = ACHIEVEMENTS.get(ach_id, {"name": ach_id})
        print(f"[Steam] >>> ACHIEVEMENT UNLOCKED: {info['name']} ({ach_id}) <<<")

        if getattr(self, "companion_service", None):
            try:
                self.companion_service.unlock_achievement(ach_id)
            except Exception:
                pass

        if self.initialized and self.steamworks:
            try:
                self.steamworks.SetAchievement(ach_id)
            except Exception as e:
                print(f"[SteamManager] Error sending achievement to Steam: {e}")

    def set_rich_presence(self, status):
        if self.initialized and self.steamworks:
            try:
                self.steamworks.SetRichPresence("status", status)
            except Exception:
                pass

    def update(self):
        if self.initialized and self.steamworks:
            try:
                self.steamworks.RunCallbacks()
            except Exception:
                pass
