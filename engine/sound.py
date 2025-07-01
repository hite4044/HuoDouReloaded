from time import perf_counter

import pygame as pg

from lib.config import gm_config

sound_in_playing: list[tuple[float, int, pg.mixer.Sound]] = []


def play_sound(sound: pg.mixer.Sound, loops: int = 0):
    if not gm_config.play_sound:
        sound.set_volume(0)
    sound.play(loops)
    for start_time, loops, t_sound in sound_in_playing:
        if sound is t_sound:
            return
    sound_in_playing.append((perf_counter(), loops, sound))


def on_music_cfg_change(enable: bool):
    if enable:
        for start_time, loops, sound in sound_in_playing:
            sound.set_volume(100)
    else:
        for start_time, loops, sound in sound_in_playing:
            sound.set_volume(0)


gm_config.reg_config_callback("play_sound", on_music_cfg_change)
