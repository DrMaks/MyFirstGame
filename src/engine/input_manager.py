"""
Unified Input Manager supporting Keyboard, Mouse, and Gamepad / Controller.
Handles smooth custom cursor rendering and mouse UI interactions.
"""

import math
import pygame


from src.config import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from src.engine.touch_controls import TouchControls


class InputManager:
    def __init__(self, enable_touch=False):
        self.joysticks = []
        self._init_joysticks()
        self.touch_controls = TouchControls()
        self.touch_controls.enabled = enable_touch

        # Mouse & Aim cache
        self.virtual_mouse_x = 0.0
        self.virtual_mouse_y = 0.0
        self.aim_angle = 0.0
        self.aim_world_x = 0.0
        self.aim_world_y = 0.0
        self.mouse_clicked = False
        self.prev_mouse_lmb = False
        self.is_hovering_interactive = False

        # Movement & Actions
        self.move_x = 0.0
        self.move_y = 0.0
        self.action_attack = False
        self.action_dash = False
        self.action_interact = False
        self.action_pause = False

        # Previous frame button states for "just pressed" detection
        self.prev_attack = False
        self.prev_dash = False
        self.prev_interact = False
        self.prev_pause = False

        self.just_attacked = False
        self.just_dashed = False
        self.just_interacted = False
        self.just_paused = False

        # Hide default Windows arrow cursor for custom retro crosshair
        try:
            if not enable_touch:
                pygame.mouse.set_visible(False)
        except Exception:
            pass

    def _init_joysticks(self):
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joy in self.joysticks:
            joy.init()

    def handle_event(self, event, window_w=DEFAULT_WINDOW_WIDTH, window_h=DEFAULT_WINDOW_HEIGHT):
        if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
            self._init_joysticks()
            return

        # Touch events (Android / Mobile multi-touch)
        if event.type == pygame.FINGERDOWN:
            vx, vy = self.touch_controls.screen_to_virtual(
                event.x * window_w, event.y * window_h, window_w, window_h
            )
            self.virtual_mouse_x = vx
            self.virtual_mouse_y = vy
            self.mouse_clicked = True
            self.touch_controls.handle_touch_down(event.finger_id, vx, vy)
        elif event.type == pygame.FINGERMOTION:
            vx, vy = self.touch_controls.screen_to_virtual(
                event.x * window_w, event.y * window_h, window_w, window_h
            )
            self.virtual_mouse_x = vx
            self.virtual_mouse_y = vy
            self.touch_controls.handle_touch_motion(event.finger_id, vx, vy)
        elif event.type == pygame.FINGERUP:
            self.touch_controls.handle_touch_up(event.finger_id)

        # Mouse touch simulation if touch controls are enabled
        elif self.touch_controls.enabled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.touch_controls.handle_touch_down(999, self.virtual_mouse_x, self.virtual_mouse_y)
            elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                self.touch_controls.handle_touch_motion(999, self.virtual_mouse_x, self.virtual_mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.touch_controls.handle_touch_up(999)

    def update(self, camera, player_world_x, player_world_y, window_scale=(1.0, 1.0)):
        # 1. Update previous button states
        self.prev_attack = self.action_attack
        self.prev_dash = self.action_dash
        self.prev_interact = self.action_interact
        self.prev_pause = self.action_pause

        # 2. Reset raw states
        raw_move_x = 0.0
        raw_move_y = 0.0
        attack_pressed = False
        dash_pressed = False
        interact_pressed = False
        pause_pressed = False

        # 3. Read Keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            raw_move_y -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            raw_move_y += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            raw_move_x -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            raw_move_x += 1.0

        if keys[pygame.K_SPACE]:
            dash_pressed = True
        if keys[pygame.K_e] or keys[pygame.K_f]:
            interact_pressed = True
        if keys[pygame.K_ESCAPE] or keys[pygame.K_p]:
            pause_pressed = True

        # 4. Read Mouse
        mouse_buttons = pygame.mouse.get_pressed()
        lmb = mouse_buttons[0]
        if lmb:
            attack_pressed = True
        if mouse_buttons[2]:
            dash_pressed = True

        self.mouse_clicked = (lmb and not self.prev_mouse_lmb)
        self.prev_mouse_lmb = lmb

        mouse_pos = pygame.mouse.get_pos()
        scale_x = max(0.001, window_scale[0])
        scale_y = max(0.001, window_scale[1])
        self.virtual_mouse_x = mouse_pos[0] / scale_x
        self.virtual_mouse_y = mouse_pos[1] / scale_y

        self.aim_world_x, self.aim_world_y = camera.screen_to_world(self.virtual_mouse_x, self.virtual_mouse_y)

        dx = self.aim_world_x - player_world_x
        dy = self.aim_world_y - player_world_y
        self.aim_angle = math.atan2(dy, dx)

        # 5. Read Gamepad if connected
        if self.joysticks:
            joy = self.joysticks[0]
            joy_x = joy.get_axis(0)
            joy_y = joy.get_axis(1)
            deadzone = 0.22
            if abs(joy_x) > deadzone:
                raw_move_x = joy_x
            if abs(joy_y) > deadzone:
                raw_move_y = joy_y

            # Aiming stick
            if joy.get_numaxes() >= 4:
                rx = joy.get_axis(2) if joy.get_numaxes() == 4 else joy.get_axis(3)
                ry = joy.get_axis(3) if joy.get_numaxes() == 4 else joy.get_axis(4)
                if abs(rx) > deadzone or abs(ry) > deadzone:
                    self.aim_angle = math.atan2(ry, rx)

            # Buttons
            num_buttons = joy.get_numbuttons()
            if num_buttons > 0 and joy.get_button(0):  # A
                dash_pressed = True
            if num_buttons > 2 and (joy.get_button(2) or (joy.get_numaxes() > 5 and joy.get_axis(5) > 0.5)):
                attack_pressed = True
            if num_buttons > 3 and joy.get_button(3):  # Y
                interact_pressed = True
            if num_buttons > 7 and joy.get_button(7):  # Start
                pause_pressed = True

        # 6. Read Touch Controls if enabled
        if self.touch_controls.enabled:
            if abs(self.touch_controls.move_x) > 0.05 or abs(self.touch_controls.move_y) > 0.05:
                raw_move_x = self.touch_controls.move_x
                raw_move_y = self.touch_controls.move_y
                self.aim_angle = math.atan2(raw_move_y, raw_move_x)

            if self.touch_controls.is_attacking or self.touch_controls.just_attacked:
                attack_pressed = True
            if self.touch_controls.just_dashed:
                dash_pressed = True
            if self.touch_controls.just_interacted:
                interact_pressed = True
            if self.touch_controls.just_paused:
                pause_pressed = True

        # Normalize movement vector
        mag = math.hypot(raw_move_x, raw_move_y)
        if mag > 1.0:
            self.move_x = raw_move_x / mag
            self.move_y = raw_move_y / mag
        elif mag > 0.1:
            self.move_x = raw_move_x
            self.move_y = raw_move_y
        else:
            self.move_x = 0.0
            self.move_y = 0.0

        self.action_attack = attack_pressed
        self.action_dash = dash_pressed
        self.action_interact = interact_pressed
        self.action_pause = pause_pressed

        self.just_attacked = (self.action_attack and not self.prev_attack)
        self.just_dashed = (self.action_dash and not self.prev_dash)
        self.just_interacted = (self.action_interact and not self.prev_interact)
        self.just_paused = (self.action_pause and not self.prev_pause)

        # Clear touch triggers for next frame
        if self.touch_controls.enabled:
            self.touch_controls.reset_frame_triggers()

    def draw_cursor(self, surface, pixel_art):
        if self.touch_controls.enabled:
            self.touch_controls.draw(surface)
            return

        sprite_name = "cursor_interact" if self.is_hovering_interactive else "cursor_normal"
        cursor_surf = pixel_art.get_sprite(sprite_name)
        cx = int(self.virtual_mouse_x) - 7
        cy = int(self.virtual_mouse_y) - 7
        surface.blit(cursor_surf, (cx, cy))
