"""
玩家人数选择的页面
"""
import pygame as pg

import engine.resource as rs
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2
from sprites.base.button import Button
from sprites.base.frame_sprite import FrameSprite


class PlayerCntChooseBtn(Button):
    def __init__(self, loc, num: int):
        super().__init__(loc)
        frame_map = {
            1: rs.buttons.players1,
            2: rs.buttons.players2,
            3: rs.buttons.players3,
        }
        self.add_frame(frame_map[num].up)
        self.add_frame(frame_map[num].down)
        self.show = False
        self.num = num

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_up(self):
        public.send_event(EVENT_PLAYERS_COUNT_CHANGE, self.num)
        public.players_count = self.num


class Players1Button(PlayerCntChooseBtn):
    def __init__(self, loc):
        super().__init__(loc, 1)


class Players2Button(PlayerCntChooseBtn):
    def __init__(self, loc):
        super().__init__(loc, 2)


class Players3Button(PlayerCntChooseBtn):
    def __init__(self, loc):
        super().__init__(loc, 3)


class PlayersOKButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.player_ok.up)
        self.add_frame(rs.buttons.player_ok.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_up(self):
        public.run_transition(TAKE_LEVEL_CHOOSE)


class PlayersKeys(FrameSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.raw_loc: Vector2 = self.loc.copy
        self.add_frame(rs.sprites.player_keys.p_1)
        self.add_frame(rs.sprites.player_keys.p_2)
        self.add_frame(rs.sprites.player_keys.p_3)
        for frame in self.frames:
            print(frame.get_rect())
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE
        elif event == EVENT_PLAYERS_COUNT_CHANGE:
            self.update_count(data)

    def update_count(self, count: int):
        self.loc = self.raw_loc.copy
        if count == 3:
            self.loc.y -= 5
        self.transform_location()
        self.switch_frame(count - 1)

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
