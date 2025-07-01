from time import perf_counter

import pygame as pg

from lib.config import gm_config

sound_in_playing: list[tuple[float, int, pg.mixer.Sound]] = []


def play_sound(sound: pg.mixer.Sound, loops: int = 0):
    if not gm_config.play_sound:
        sound.set_volume(0)
    clear_stopped_sound()
    sound.play(loops)
    sound_in_playing.append((perf_counter(), loops, sound))


def clear_stopped_sound():
    for data in sound_in_playing[:]:
        start_time, loops, sound = data
        if loops != -1 and perf_counter() - start_time > sound.get_length():
            sound_in_playing.remove(data)


def on_music_cfg_change(enable: bool):
    if enable:
        for start_time, loops, sound in sound_in_playing:
            sound.set_volume(100)
    else:
        for start_time, loops, sound in sound_in_playing:
            sound.set_volume(0)


gm_config.reg_config_callback("play_sound", on_music_cfg_change)
