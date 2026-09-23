"""
Procedural 8-bit Sound Effects Synthesizer using NumPy and Pygame Mixer.
Generates authentic retro sound effects directly in memory without external audio files.
"""

import math
import numpy as np
import pygame

SAMPLE_RATE = 44100


class SoundSynth:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            self._generate_all_sounds()
        except Exception as e:
            print(f"[SoundSynth] Warning: Audio init failed ({e}). Running in silent mode.")
            self.enabled = False

    def _make_square(self, freq, duration, duty=0.5):
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        phase = (t * freq) % 1.0
        wave = np.where(phase < duty, 1.0, -1.0)
        return wave

    def _make_noise(self, duration):
        samples = int(SAMPLE_RATE * duration)
        return np.random.uniform(-1.0, 1.0, samples)

    def _apply_envelope(self, wave, attack=0.01, decay=0.1, sustain=0.5, release=0.1):
        total_len = len(wave)
        a_len = int(attack * SAMPLE_RATE)
        d_len = int(decay * SAMPLE_RATE)
        r_len = int(release * SAMPLE_RATE)
        s_len = max(0, total_len - a_len - d_len - r_len)

        env = []
        if a_len > 0:
            env.append(np.linspace(0, 1, a_len))
        if d_len > 0:
            env.append(np.linspace(1, sustain, d_len))
        if s_len > 0:
            env.append(np.full(s_len, sustain))
        if r_len > 0:
            env.append(np.linspace(sustain, 0, r_len))

        full_env = np.concatenate(env)
        if len(full_env) < total_len:
            full_env = np.pad(full_env, (0, total_len - len(full_env)), 'constant')
        else:
            full_env = full_env[:total_len]
        return wave * full_env

    def _to_pygame_sound(self, mono_samples):
        # Normalize and clip to 16-bit signed integer range
        max_val = np.max(np.abs(mono_samples))
        if max_val > 0:
            mono_samples = mono_samples / max_val * 0.8
        int_samples = (mono_samples * 32767).astype(np.int16)
        # Create stereo by duplicating channel
        stereo_samples = np.column_stack((int_samples, int_samples))
        return pygame.sndarray.make_sound(stereo_samples)

    def _generate_all_sounds(self):
        """Pre-generate all sound effects into memory."""
        # 1. Shoot / Magic Laser (Rapid frequency sweep down)
        dur = 0.15
        t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
        freq = np.linspace(880, 220, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
        laser_wave = np.where(np.sin(phase) > 0, 1.0, -1.0)
        laser_wave = self._apply_envelope(laser_wave, attack=0.005, decay=0.04, sustain=0.3, release=0.1)
        self.sounds['shoot'] = self._to_pygame_sound(laser_wave)

        # 2. Sword Swing (Whoosh shaped noise)
        dur = 0.12
        noise = self._make_noise(dur)
        swing = self._apply_envelope(noise, attack=0.02, decay=0.04, sustain=0.2, release=0.06)
        self.sounds['swing'] = self._to_pygame_sound(swing)

        # 3. Hit / Damage (Crunchy punch)
        dur = 0.14
        noise = self._make_noise(dur) * 0.6
        t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
        low_tone = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.4
        hit = self._apply_envelope(noise + low_tone, attack=0.002, decay=0.05, sustain=0.2, release=0.08)
        self.sounds['hit'] = self._to_pygame_sound(hit)

        # 4. Enemy Die (Descending arpeggio)
        dur = 0.22
        t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
        freq = np.linspace(440, 110, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
        enemy_die = np.sign(np.sin(phase)) * 0.7 + self._make_noise(dur) * 0.3
        enemy_die = self._apply_envelope(enemy_die, attack=0.01, decay=0.08, sustain=0.2, release=0.13)
        self.sounds['enemy_die'] = self._to_pygame_sound(enemy_die)

        # 5. Coin / Gem Pickup (Dual high ping)
        p1 = self._make_square(987.77, 0.06, 0.5)  # B5
        p1 = self._apply_envelope(p1, attack=0.005, decay=0.02, sustain=0.6, release=0.035)
        p2 = self._make_square(1318.51, 0.12, 0.5)  # E6
        p2 = self._apply_envelope(p2, attack=0.005, decay=0.03, sustain=0.4, release=0.085)
        coin_wave = np.concatenate([p1, p2])
        self.sounds['coin'] = self._to_pygame_sound(coin_wave)

        # 6. Chest Open (Arpeggio: C5 - E5 - G5 - C6)
        notes = [523.25, 659.25, 783.99, 1046.50]
        chunks = []
        for n in notes:
            chunk = self._make_square(n, 0.07, 0.5)
            chunk = self._apply_envelope(chunk, attack=0.005, decay=0.02, sustain=0.6, release=0.045)
            chunks.append(chunk)
        self.sounds['chest'] = self._to_pygame_sound(np.concatenate(chunks))

        # 7. Dash (Air whoosh)
        dur = 0.18
        noise = self._make_noise(dur)
        dash_wave = self._apply_envelope(noise, attack=0.01, decay=0.05, sustain=0.4, release=0.12)
        self.sounds['dash'] = self._to_pygame_sound(dash_wave)

        # 8. Level Up Fanfare
        lvl_notes = [440.0, 554.37, 659.25, 880.0]
        lvl_chunks = []
        for i, n in enumerate(lvl_notes):
            d = 0.08 if i < 3 else 0.28
            chunk = self._make_square(n, d, 0.3)
            chunk = self._apply_envelope(chunk, attack=0.01, decay=0.03, sustain=0.7, release=0.1)
            lvl_chunks.append(chunk)
        self.sounds['level_up'] = self._to_pygame_sound(np.concatenate(lvl_chunks))

        # 9. Player Hurt (Ouch crunch)
        dur = 0.18
        t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
        hurt_wave = np.sign(np.sin(2 * np.pi * np.linspace(300, 90, len(t)) * t)) * 0.7 + self._make_noise(dur) * 0.3
        hurt_wave = self._apply_envelope(hurt_wave, attack=0.005, decay=0.05, sustain=0.3, release=0.125)
        self.sounds['player_hurt'] = self._to_pygame_sound(hurt_wave)

        # 10. Explosion (Bomb / Boss hit)
        dur = 0.35
        noise = self._make_noise(dur)
        t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
        rumble = np.sin(2 * np.pi * np.linspace(80, 20, len(t)) * t) * 0.6
        exp_wave = self._apply_envelope(noise * 0.8 + rumble, attack=0.005, decay=0.1, sustain=0.3, release=0.245)
        self.sounds['explosion'] = self._to_pygame_sound(exp_wave)

    def play(self, name, volume=1.0):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(max(0.0, min(1.0, volume)))
            sound.play()
