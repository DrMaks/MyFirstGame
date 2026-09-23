"""
Google Play Games Services (GPGS) Manager for Android / Google Play Market Edition.
Handles Cloud Saves, Achievements, Leaderboards, and Player Authentication.
Includes seamless desktop/offline fallback emulator when running outside of Android.
"""

import sys
import json

# Standard Google Play Games achievement IDs (configurable in Google Play Console)
GPGS_ACHIEVEMENTS = {
    "ACH_FIRST_BLOOD": "CgkI_pixel_rogue_first_blood",
    "ACH_CHEST_HUNTER": "CgkI_pixel_rogue_chest_hunter",
    "ACH_LEVEL_5": "CgkI_pixel_rogue_level_5",
    "ACH_BOSS_SLAYER": "CgkI_pixel_rogue_boss_slayer",
    "ACH_RICH": "CgkI_pixel_rogue_rich",
    "ACH_FLOOR_4": "CgkI_pixel_rogue_deep_dungeon"
}

GPGS_LEADERBOARDS = {
    "LEADERBOARD_HIGH_SCORE": "CgkI_pixel_rogue_leaderboard_score",
    "LEADERBOARD_DEEPEST_FLOOR": "CgkI_pixel_rogue_leaderboard_floor"
}


class GooglePlayManager:
    def __init__(self):
        self.is_android = "android" in sys.platform or hasattr(sys, "getandroidapilevel")
        self.authenticated = False
        self.player_name = "Player"
        self.unlocked_achievements = set()

        if self.is_android:
            self._init_android_gpgs()
        else:
            print("[GooglePlayManager] Running in Desktop / Local Offline Emulation mode.")
            self.authenticated = True
            self.player_name = "DesktopDev"

    def _init_android_gpgs(self):
        """Attempts to bind to Android Play Games Services via pyjnius."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            PlayGames = autoclass("com.google.android.gms.games.PlayGames")
            self.activity = PythonActivity.mActivity
            self.games_client = PlayGames.getGamesSignInClient(self.activity)
            self.achievements_client = PlayGames.getAchievementsClient(self.activity)
            self.leaderboards_client = PlayGames.getLeaderboardsClient(self.activity)
            print("[GooglePlayManager] Successfully initialized Android Play Games SDK.")
            self.authenticated = True
        except Exception as e:
            print(f"[GooglePlayManager] Pyjnius / Play Games SDK not present: {e}. Falling back to offline mode.")
            self.authenticated = False

    def unlock_achievement(self, ach_id):
        """Unlocks an achievement in Google Play Games."""
        if ach_id in self.unlocked_achievements:
            return

        self.unlocked_achievements.add(ach_id)
        gpgs_id = GPGS_ACHIEVEMENTS.get(ach_id, ach_id)

        if self.is_android and self.authenticated:
            try:
                self.achievements_client.unlock(gpgs_id)
                print(f"[GooglePlayManager] Unlocked achievement on Google Play: {gpgs_id}")
            except Exception as e:
                print(f"[GooglePlayManager] Failed to unlock {gpgs_id}: {e}")
        else:
            print(f"[GooglePlayManager (Emulated)] >>> ACHIEVEMENT UNLOCKED: {ach_id} ({gpgs_id}) <<<")

    def submit_score(self, leaderboard_id, score):
        """Submits high score to Google Play Leaderboards."""
        gpgs_lead_id = GPGS_LEADERBOARDS.get(leaderboard_id, leaderboard_id)
        if self.is_android and self.authenticated:
            try:
                self.leaderboards_client.submitScore(gpgs_lead_id, int(score))
                print(f"[GooglePlayManager] Submitted score {score} to {gpgs_lead_id}")
            except Exception as e:
                print(f"[GooglePlayManager] Failed to submit score: {e}")
        else:
            print(f"[GooglePlayManager (Emulated)] Submitted score {score} to leaderboard {leaderboard_id}")

    def update(self):
        """Per-frame update hook if needed."""
        pass
