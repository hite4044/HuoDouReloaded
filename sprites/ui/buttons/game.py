import pygame as pg

import engine.resource as rs
from engine.sound import play_sound
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2
from sprites.base.button import Button, CoverButton
from sprites.base.frame_sprite import FrameSprite

class NextLevelButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.next_level.up)
        self.add_frame(rs.buttons.next_level.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", Vector2(618, 467)),
        }

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            if data != LEVEL_END_WIN:
                return
        super().event_parse(event, data)

    def on_up(self):
        public.send_event(EVENT_COVER_RUN, 0)


class RetryButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.retry_level.up)
        self.add_frame(rs.buttons.retry_level.down)
        self.cover_map = {
            LEVEL_END_LOSE: ("sm.lose_cover", Vector2(618, 467)),
        }

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            if data != LEVEL_END_LOSE:
                return
        super().event_parse(event, data)

    @staticmethod
    def callback():
        public.send_event(EVENT_LEVEL_RESET, 0)

    def on_up(self):
        public.run_transition(TAKE_EMPTY, self.callback, True)


class ReturnButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.return_.up)
        self.add_frame(rs.buttons.return_.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE

    def on_up(self):
        public.run_transition(TAKE_START)


class MoreGameLite(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.games.up)
        self.add_frame(rs.buttons.games.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False


class ResetButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.reset.up)
        self.add_frame(rs.buttons.reset.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    def on_up(self):
        public.run_transition(TAKE_PLAY, self.cbk)

    @staticmethod
    def cbk():
        public.send_event(EVENT_LEVEL_RESET, 0)


class HomeButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.home.up)
        self.add_frame(rs.buttons.home.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    def on_up(self):
        public.run_transition(TAKE_LEVEL_CHOOSE, lambda: public.send_event(EVENT_LEVEL_EXIT, 0))
