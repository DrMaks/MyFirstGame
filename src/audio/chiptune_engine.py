"""
Chiptune Music Engine.
Synthesizes retro multi-channel 8-bit background music tracks into looping Pygame sounds.
Channels: Pulse 1 (Lead), Pulse 2 (Arp/Harmony), Triangle (Bass), White Noise (Drums).
"""

import math
import numpy as np
import pygame

SAMPLE_RATE = 44100


# Frequency lookup table for musical notes (C2 to B6)
def note_freq(note_name):
    flats_to_sharps = {
        'BB': 'A#',
        'DB': 'C#',
        'EB': 'D#',
        'GB': 'F#',
        'AB': 'G#'
    }
    raw_name = note_name[:-1].upper()
    octave = int(note_name[-1])
    name = flats_to_sharps.get(raw_name, raw_name)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    semitone = notes.index(name)
    distance_from_a4 = (octave - 4) * 12 + (semitone - 9)
    return 440.0 * (2.0 ** (distance_from_a4 / 12.0))


class ChiptuneEngine:
    def __init__(self):
        self.tracks = {}
        self.current_track = None
        self.channel = None
        self.music_volume = 0.6
        self.master_volume = 0.8
        self.enabled = True

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            self.channel = pygame.mixer.Channel(0)
            self._render_tracks()
        except Exception as e:
            print(f"[ChiptuneEngine] Warning: Audio init failed ({e}). Running in silent mode.")
            self.enabled = False

    def _synth_pulse(self, freq, duration, duty=0.5):
        if freq <= 0:
            return np.zeros(int(SAMPLE_RATE * duration))
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        phase = (t * freq) % 1.0
        wave = np.where(phase < duty, 0.7, -0.7)
        # Apply slight pluck decay envelope
        env = np.exp(-t * 2.5)
        return wave * (0.3 + 0.7 * env)

    def _synth_triangle(self, freq, duration):
        if freq <= 0:
            return np.zeros(int(SAMPLE_RATE * duration))
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        phase = (t * freq) % 1.0
        wave = 2.0 * np.abs(2.0 * (phase - np.floor(phase + 0.5))) - 1.0
        return wave * 0.8

    def _synth_kick(self, duration):
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        freq = np.linspace(150, 40, samples)
        phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
        env = np.exp(-t * 18.0)
        return np.sin(phase) * env

    def _synth_snare(self, duration):
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, samples)
        body = np.sin(2 * np.pi * 180 * t) * 0.4
        env = np.exp(-t * 14.0)
        return (noise * 0.6 + body) * env

    def _synth_hihat(self, duration):
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, samples)
        env = np.exp(-t * 40.0)
        return noise * env * 0.5

    def _render_tracks(self):
        """Render all chiptune tracks into looped Pygame Sound buffers."""
        print("[ChiptuneEngine] Synthesizing retro chiptune soundtracks...")
        self.tracks['dungeon'] = self._build_dungeon_track()
        self.tracks['boss'] = self._build_boss_track()
        self.tracks['menu'] = self._build_menu_track()
        print("[ChiptuneEngine] Soundtracks ready!")

    def _build_dungeon_track(self):
        # 135 BPM dungeon track in D minor
        bpm = 135
        beat_dur = 60.0 / bpm
        step_dur = beat_dur / 4.0  # 16th note

        # Lead melody (16 bars = 64 steps)
        lead_notes = [
            'D4', 'F4', 'A4', 'D5', 'C5', 'A4', 'F4', 'E4',
            'D4', 'D4', 'F4', 'G4', 'A4', 'G4', 'F4', 'E4',
            'D4', 'F4', 'A4', 'D5', 'E5', 'D5', 'C5', 'A4',
            'Bb4', 'A4', 'G4', 'F4', 'E4', 'F4', 'E4', 'C4',

            'D4', 'F4', 'A4', 'D5', 'F5', 'E5', 'D5', 'C5',
            'D5', 'A4', 'F4', 'A4', 'G4', 'F4', 'E4', 'C4',
            'D4', 'A4', 'D5', 'F5', 'E5', 'D5', 'C5', 'A4',
            'G4', 'Bb4', 'A4', 'F4', 'E4', 'D4', 'C#4', 'D4'
        ]

        # Bass notes (quarter note root pulses: D2, F2, C2, Bb1)
        bass_roots = [
            'D2', 'D2', 'D2', 'D2', 'F2', 'F2', 'F2', 'F2',
            'C2', 'C2', 'C2', 'C2', 'Bb1', 'Bb1', 'A1', 'A1',
            'D2', 'D2', 'D2', 'D2', 'F2', 'F2', 'F2', 'F2',
            'G2', 'G2', 'G2', 'G2', 'A1', 'A1', 'A1', 'A1'
        ]

        num_steps = len(lead_notes)
        total_samples = int(SAMPLE_RATE * num_steps * step_dur)

        lead_buf = np.zeros(total_samples)
        bass_buf = np.zeros(total_samples)
        drums_buf = np.zeros(total_samples)

        # Synthesize Lead
        for i, note in enumerate(lead_notes):
            start = int(i * step_dur * SAMPLE_RATE)
            f = note_freq(note)
            wave = self._synth_pulse(f, step_dur, duty=0.25 if (i % 2 == 0) else 0.5)
            end = min(total_samples, start + len(wave))
            lead_buf[start:end] += wave[:end - start]

        # Synthesize Bass (half steps)
        for i, note in enumerate(bass_roots):
            start = int(i * (step_dur * 2) * SAMPLE_RATE)
            f = note_freq(note)
            wave = self._synth_triangle(f, step_dur * 1.8)
            end = min(total_samples, start + len(wave))
            bass_buf[start:end] += wave[:end - start]

        # Synthesize 8-bit Drums
        for i in range(num_steps):
            start = int(i * step_dur * SAMPLE_RATE)
            step_mod = i % 4
            if step_mod == 0:  # Kick on beats
                drum = self._synth_kick(0.12)
            elif step_mod == 2:  # Snare on backbeats
                drum = self._synth_snare(0.10)
            else:  # Hi-hat
                drum = self._synth_hihat(0.05)
            end = min(total_samples, start + len(drum))
            drums_buf[start:end] += drum[:end - start]

        # Mix and balance
        mix = lead_buf * 0.45 + bass_buf * 0.50 + drums_buf * 0.35
        return self._to_sound(mix)

    def _build_boss_track(self):
        # 150 BPM aggressive track in E minor
        bpm = 150
        beat_dur = 60.0 / bpm
        step_dur = beat_dur / 4.0

        lead_notes = [
            'E4', 'G4', 'B4', 'E5', 'D#5', 'B4', 'G4', 'F#4',
            'E4', 'E4', 'G4', 'A4', 'B4', 'C5', 'B4', 'A4',
            'E4', 'B4', 'E5', 'G5', 'F#5', 'E5', 'D#5', 'B4',
            'C5', 'B4', 'A4', 'G4', 'F#4', 'G4', 'F#4', 'D#4'
        ] * 2

        bass_roots = ['E2', 'E2', 'G2', 'G2', 'C2', 'C2', 'B1', 'B1'] * 4
        num_steps = len(lead_notes)
        total_samples = int(SAMPLE_RATE * num_steps * step_dur)

        lead_buf = np.zeros(total_samples)
        bass_buf = np.zeros(total_samples)
        drums_buf = np.zeros(total_samples)

        for i, note in enumerate(lead_notes):
            start = int(i * step_dur * SAMPLE_RATE)
            f = note_freq(note)
            wave = self._synth_pulse(f, step_dur, duty=0.125)  # Thin gritty pulse
            end = min(total_samples, start + len(wave))
            lead_buf[start:end] += wave[:end - start]

        for i, note in enumerate(bass_roots):
            start = int(i * (step_dur * 2) * SAMPLE_RATE)
            f = note_freq(note)
            wave = self._synth_triangle(f, step_dur * 1.9)
            end = min(total_samples, start + len(wave))
            bass_buf[start:end] += wave[:end - start]

        for i in range(num_steps):
            start = int(i * step_dur * SAMPLE_RATE)
            # Double bass kick pattern
            if i % 2 == 0:
                drum = self._synth_kick(0.09)
            if i % 4 == 2:
                drum = self._synth_snare(0.12)
            else:
                drum = self._synth_hihat(0.04)
            end = min(total_samples, start + len(drum))
            drums_buf[start:end] += drum[:end - start]

        mix = lead_buf * 0.50 + bass_buf * 0.55 + drums_buf * 0.40
        return self._to_sound(mix)

    def _build_menu_track(self):
        # 105 BPM mystical nostalgic intro track in A minor
        bpm = 105
        beat_dur = 60.0 / bpm
        step_dur = beat_dur / 2.0  # 8th notes

        lead_notes = [
            'A3', 'C4', 'E4', 'A4', 'B4', 'G4', 'E4', 'G4',
            'F4', 'A4', 'C5', 'B4', 'A4', 'G4', 'E4', 'G4',
            'D4', 'F4', 'A4', 'C5', 'B4', 'G4', 'D4', 'E4',
            'F4', 'E4', 'D4', 'C4', 'B3', 'C4', 'B3', 'G#3'
        ]

        num_steps = len(lead_notes)
        total_samples = int(SAMPLE_RATE * num_steps * step_dur)
        lead_buf = np.zeros(total_samples)

        for i, note in enumerate(lead_notes):
            start = int(i * step_dur * SAMPLE_RATE)
            f = note_freq(note)
            wave = self._synth_pulse(f, step_dur * 0.9, duty=0.5)
            end = min(total_samples, start + len(wave))
            lead_buf[start:end] += wave[:end - start]

        mix = lead_buf * 0.55
        return self._to_sound(mix)

    def _to_sound(self, mono):
        max_val = np.max(np.abs(mono))
        if max_val > 0:
            mono = mono / max_val * 0.75
        int_data = (mono * 32767).astype(np.int16)
        stereo = np.column_stack((int_data, int_data))
        return pygame.sndarray.make_sound(stereo)

    def play_track(self, name):
        if not self.enabled or not self.channel:
            return
        if self.current_track == name:
            return
        sound = self.tracks.get(name)
        if sound:
            effective_vol = self.master_volume * self.music_volume
            self.channel.set_volume(effective_vol)
            self.channel.play(sound, loops=-1, fade_ms=500)
            self.current_track = name

    def set_volume(self, music_vol=None, master_vol=None):
        if music_vol is not None:
            self.music_volume = max(0.0, min(1.0, music_vol))
        if master_vol is not None:
            self.master_volume = max(0.0, min(1.0, master_vol))
        if self.channel:
            self.channel.set_volume(self.master_volume * self.music_volume)

    def stop(self):
        if self.channel:
            self.channel.stop()
            self.current_track = None
