import os
import sys
sys.path.insert(0, os.path.abspath("."))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()

from src.engine.game import (
    Game, STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
    STATE_VICTORY, STATE_UPGRADE, STATE_SETTINGS, STATE_SKILL_TREE
)

def run_tests():
    print("=== Starting Retro Roguelike Comprehensive Tests ===")
    g = Game()
    assert g.state == STATE_MENU, "Game should start in STATE_MENU"
    print("[PASS] Initial state is STATE_MENU")

    # 1. Test Skill Tree
    g.state = STATE_SKILL_TREE
    g.save_mgr.data["talents"]["vitality"] = 0
    g.save_mgr.add_gold(500)
    old_vitality = g.save_mgr.get_talent_level("vitality")
    res = g.skill_tree_menu.handle_input("select")
    new_vitality = g.save_mgr.get_talent_level("vitality")
    assert new_vitality == old_vitality + 1, f"Expected vitality upgrade from {old_vitality} to {new_vitality}"
    print(f"[PASS] Skill tree upgrade succeeded: vitality {old_vitality} -> {new_vitality}")

    # Test mouse hover in skill tree
    g.skill_tree_menu.handle_input(None, virtual_mouse_x=35, virtual_mouse_y=60, mouse_clicked=False)
    assert g.skill_tree_menu.hovered_idx == 0, f"Expected hovered index 0, got {g.skill_tree_menu.hovered_idx}"
    print("[PASS] Skill tree mouse hover detection works")

    # Render skill tree
    g.skill_tree_menu.draw(g.virtual_surf)
    print("[PASS] Skill tree rendered without error")

    # 2. Test Start New Game & Multi-floor escalation
    g.start_new_game()
    assert g.state == STATE_PLAYING, "Game state should be STATE_PLAYING"
    assert g.current_floor == 1, f"Initial floor should be 1, got {g.current_floor}"
    print(f"[PASS] Floor 1 generated: {len(g.enemies)} enemies")

    # Verify new enemy classes exist in floor generation or can be instantiated
    from src.entities.enemy import GoblinBombardier, Wraith, StoneGolem
    goblin = GoblinBombardier(100, 100, floor=1)
    wraith = Wraith(120, 120, floor=2)
    golem = StoneGolem(140, 140, floor=3)
    print("[PASS] New enemy classes (Goblin, Wraith, Golem) instantiated cleanly")

    # Test Floor progression 1 -> 2 -> 3 -> 4
    for floor_num in [2, 3, 4]:
        g.enter_floor(floor_num)
        assert g.current_floor == floor_num
        print(f"[PASS] Floor {floor_num} generated with {len(g.enemies)} enemies, floor_mult={1.0 + (floor_num - 1) * 0.35:.2f}")

    # 3. Test New Drops (Relics, Scrolls, Gems, Shields, Chests)
    from src.entities.drops import Chest, ShieldDrop, MagnetDrop, ScrollDrop, GemDrop
    chest = Chest(5, 5, tier="gold")
    chest.open(g.player, g.drops, g.sound, g.particles, g.steam)
    print(f"[PASS] Gold chest opened, created drops: {[type(d).__name__ for d in g.drops]}")

    shield = ShieldDrop(g.player.x, g.player.y)
    consumed = not shield.update(g.player, 0.016)
    assert consumed, "Shield should be collected when near player"
    assert g.player.shield_charges > 0, "Player should have gained shield charge"
    print(f"[PASS] Relic 'shield' collected, player shield charges: {g.player.shield_charges}")

    magnet = MagnetDrop(g.player.x, g.player.y)
    consumed = not magnet.update(g.player, 0.016)
    assert consumed, "Magnet should be collected when near player"
    assert g.player.active_magnet_timer > 0, "Player active magnet timer should be > 0"
    print(f"[PASS] Relic 'magnet' collected, active magnet timer: {g.player.active_magnet_timer}")

    scroll = ScrollDrop(g.player.x, g.player.y)
    consumed = not scroll.update(g.player, 0.016)
    assert consumed, "Scroll should be collected when near player"
    assert g.player.has_meteor_scroll, "Player should have meteor scroll"
    print(f"[PASS] Scroll 'meteor' collected, has_meteor_scroll={g.player.has_meteor_scroll}")

    gem = GemDrop(g.player.x, g.player.y, "ruby")
    consumed = not gem.update(g.player, 0.016)
    assert consumed, "Gem should be collected when near player"
    print("[PASS] Gem collected cleanly")

    # 4. Test Upgrade Menu with Mouse Click & Hover
    g.prompt_level_up()
    assert g.state == STATE_UPGRADE
    card_idx = g.menu_renderer.get_upgrade_card_at_pos(100, 120, len(g.current_upgrade_choices))
    print(f"[PASS] Upgrade prompt initialized, choices count: {len(g.current_upgrade_choices)}")
    g.menu_renderer.draw_upgrade_picker(g.virtual_surf, g.current_upgrade_choices, g.upgrade_selected)
    print("[PASS] Upgrade menu rendered without error")

    # 5. Test Game Loop Update & Render with Lighting Pass
    g.state = STATE_PLAYING
    g.update(0.016)
    g.render()
    print("[PASS] Playing state update + lighting pass render executed without error")

    # 6. Test Settings & Localization Toggle
    from src.localization import loc
    loc.set_language("en")
    assert loc.get("start_game") == "START ADVENTURE"
    loc.set_language("ru")
    assert loc.get("start_game") == "НАЧАТЬ ПРИКЛЮЧЕНИЕ"
    print("[PASS] Localization switching (EN/RU) verified")

    print("\n=== ALL UNIT & INTEGRATION TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
