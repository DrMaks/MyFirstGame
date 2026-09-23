import os
import sys
sys.path.insert(0, os.path.abspath("."))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()

from src.engine.game import Game, STATE_MENU, STATE_PLAYING, STATE_SETTINGS
from src.world.lighting import LightingEngine
from src.engine.touch_controls import TouchControls
from src.services.google_play_manager import GooglePlayManager


def test_brightness_and_lighting():
    print("=== Testing Brightness & Lighting Engine ===")
    lighting = LightingEngine()
    initial_darkness = lighting.ambient_darkness
    print(f"Base ambient darkness: {initial_darkness} (out of 255)")
    assert initial_darkness <= 90, f"Expected bright base darkness <= 90, got {initial_darkness}"

    # Test brightness scaling
    lighting.set_brightness(1.4)
    brightened_darkness = lighting.ambient_darkness
    assert brightened_darkness < initial_darkness, f"Higher brightness should yield lower darkness overlay: {brightened_darkness}"
    print(f"[PASS] Brightness multiplier 1.4 -> darkness reduced to {brightened_darkness}")

    lighting.set_brightness(0.8)
    darkened = lighting.ambient_darkness
    assert darkened > initial_darkness
    print(f"[PASS] Brightness multiplier 0.8 -> darkness increased to {darkened}")


def test_mobile_edition_and_touch():
    print("\n=== Testing Google Play / Mobile Edition & Touch Controls ===")
    # 1. Initialize mobile game instance
    game = Game(is_mobile=True)
    assert game.is_mobile is True, "Game should have is_mobile flag set"
    assert game.input.touch_controls.enabled is True, "Touch controls should be enabled on mobile"
    assert game.google_play is not None, "GooglePlayManager should be attached"
    print("[PASS] Game(is_mobile=True) initialized cleanly")

    # 2. Test Google Play Manager Achievements & Leaderboards
    game.google_play.unlock_achievement("ACH_FIRST_BLOOD")
    assert "ACH_FIRST_BLOOD" in game.google_play.unlocked_achievements
    game.google_play.submit_score("LEADERBOARD_HIGH_SCORE", 1500)
    print("[PASS] Google Play achievements & leaderboard submission passed")

    # 3. Test Touch Controls Virtual Joystick
    tc = game.input.touch_controls
    assert tc.move_x == 0.0 and tc.move_y == 0.0

    # Touch down on joystick area (centers joystick at touch point)
    tc.handle_touch_down(101, tc.stick_base_x, tc.stick_base_y)
    assert tc.is_stick_active is True
    print("[PASS] Touch joystick touch down activated stick")

    # Touch motion (drag to the right)
    tc.handle_touch_motion(101, tc.stick_base_x + 20, tc.stick_base_y)
    assert tc.move_x > 0.0, f"Expected positive X move, got {tc.move_x}"
    print(f"[PASS] Touch joystick drag to right produced move_x={tc.move_x:.2f}")

    # Touch motion (drag upwards)
    tc.handle_touch_motion(101, tc.stick_base_x, tc.stick_base_y - 25)
    assert tc.move_y < 0.0, f"Expected upward move_y < 0, got {tc.move_y}"
    print(f"[PASS] Touch joystick drag upwards produced move_y={tc.move_y:.2f}")

    # Touch up
    tc.handle_touch_up(101)
    assert tc.is_stick_active is False
    assert tc.move_x == 0.0 and tc.move_y == 0.0
    print("[PASS] Touch joystick release returned to center")

    # 4. Test Touch Action Buttons (Attack, Dash, Interact, Pause)
    # Attack button touch
    atk_btn = tc.btn_attack
    tc.handle_touch_down(102, atk_btn["x"], atk_btn["y"])
    assert tc.just_attacked is True
    assert tc.is_attacking is True
    tc.handle_touch_up(102)
    assert tc.is_attacking is False
    print("[PASS] Touch attack button press/release passed")

    # Dash button touch
    dash_btn = tc.btn_dash
    tc.handle_touch_down(103, dash_btn["x"], dash_btn["y"])
    assert tc.just_dashed is True
    tc.handle_touch_up(103)
    print("[PASS] Touch dash button press passed")

    # Pause button touch
    pause_btn = tc.btn_pause
    tc.handle_touch_down(104, pause_btn["x"], pause_btn["y"])
    assert tc.just_paused is True
    tc.handle_touch_up(104)
    print("[PASS] Touch pause button press passed")

    # 5. Test Touch Overlay Rendering
    test_surf = pygame.Surface((480, 270))
    tc.draw(test_surf)
    print("[PASS] Touch controls overlay drawn without errors")

    # 6. Test Settings Menu Brightness Option
    game.state = STATE_SETTINGS
    # Index 3 is brightness in settings
    game.settings_menu.selected_idx = 3
    init_b = game.settings_menu.brightness
    game.settings_menu.handle_input("right")
    assert game.settings_menu.brightness == init_b + 10
    print(f"[PASS] SettingsMenu adjusted brightness: {init_b}% -> {game.settings_menu.brightness}%")

    # 7. Test Playing Update with Touch Inputs
    game.start_new_game()
    assert game.state == STATE_PLAYING
    game.update(0.016)
    game.render()
    print("[PASS] Full game loop with mobile touch controls executed successfully")

    print("\n=== ALL BRIGHTNESS & GOOGLE PLAY MOBILE TESTS COMPLETED CLEANLY ===")


if __name__ == "__main__":
    test_brightness_and_lighting()
    test_mobile_edition_and_touch()
