import pygame as pg

import engine.resource as rs
from engine.sound import play_sound
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2
from sprites.base.button import Button
from sprites.base.frame_sprite import FrameSprite


class MusicButton(Button):
    def __init__(self):
        super().__init__((0, 0), shadow=True)
        self.add_frame(rs.buttons.music.up)
        self.add_frame(rs.buttons.music.down)
        self.add_frame(rs.buttons.music.A_up)
        self.add_frame(rs.buttons.music.A_down)
        self.music_opened = public.play_sound
        self.switch_lock = False
        self.is_clicking = False
        play_sound(rs.sound.music, -1)
        self.event_parse(EVENT_TAKE_CHANGE, TAKE_START)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.enable = True
            if data == TAKE_START:
                self.loc = Vector2(50, 57)
            elif data == TAKE_PLAYERS_CHOOSE:
                self.loc = Vector2(953, 101)
            elif data == TAKE_LEVEL_CHOOSE:
                self.loc = Vector2(983, 59)
            elif data == TAKE_PLAY:
                self.loc = Vector2(833, 47)
            else:
                return
            self.transform_location()
            self.rect.topleft = self.transformed_loc
        elif event in [EVENT_LEVEL_ENTER, EVENT_LEVEL_RESET, EVENT_LEVEL_NEXT]:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    @staticmethod
    def music_pause():
        public.play_sound = False

    @staticmethod
    def music_resume():
        public.play_sound = True

    @staticmethod
    def get_index(active: bool, down: bool):
        if active:
            return 1 if down else 0
        else:
            return 3 if down else 2

    def update(self):
        if self.enable:
            clicking = pg.mouse.get_pressed(3)[0]
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if clicking:
                    if not self.switch_lock:
                        self.switch_lock = True
                    self.switch_frame(self.get_index(not self.music_opened, False))
                elif self.switch_lock:
                    self.music_pause() if self.music_opened else self.music_resume()
                    self.music_opened = not self.music_opened
                    self.switch_lock = False
                    self.switch_frame(self.get_index(self.music_opened, False))
                else:
                    self.switch_frame(self.get_index(self.music_opened, True))
            elif self.switch_lock:
                if clicking:
                    self.switch_frame(self.get_index(self.music_opened, True))
                else:
                    self.switch_lock = False
                    self.switch_frame(self.get_index(self.music_opened, False))
            else:
                self.switch_frame(self.get_index(self.music_opened, False))
        else:
            self.switch_frame(self.get_index(self.music_opened, False))
        super(FrameSprite, self).update()
