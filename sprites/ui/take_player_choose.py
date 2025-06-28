import engine.resource as rs
from lib.define import *
from lib.public_data import public
from sprites.base.frame_sprite import FrameSprite
import pygame as pg


class PlayersKeys(FrameSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.raw_loc = loc
        self.add_frame(rs.sprites.player_keys.p_1)
        self.add_frame(rs.sprites.player_keys.p_2)
        self.add_frame(rs.sprites.player_keys.p_3)
        for frame in self.frames:
            print(frame.get_rect())
        self.show = False
        self.last_player_counter = 0

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE
        elif event == EVENT_PLAYERS_COUNT_CHANGE:
            self.update_count(data)

    def update_count(self, count: int):
        if count == 3:
            tmp = self.raw_loc.copy()
            tmp[1] -= 5
            self.loc = tmp
        else:
            self.loc = self.raw_loc
        self.switch_frame(count - 1)
        self.last_player_counter = count + 1 - 1

    def update(self):
        super().update()


class PlayersCH(FrameSprite):
    def __init__(self, loc, image: pg.surface.Surface, num: int):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.add_frame(image)
        image_alpha = image.copy()
        image_alpha.set_alpha(128)
        self.add_frame(image_alpha)

        self.last_player_counter = 0
        self.show = False
        self.num = num
        self.update_count(public.players_count)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE
        elif event == EVENT_PLAYERS_COUNT_CHANGE:
            self.update_count(data)

    def update_count(self, count: int):
        if count >= self.num:
            self.switch_frame(0)
        else:
            self.switch_frame(1)
