import engine.resource as rs
from lib.define import *
from sprites.base.base_sprite import Vector2
from sprites.base.frame_sprite import FrameSprite


class BackGround(FrameSprite):
    def __init__(self):
        self.layer_def = LAYER_BG
        super().__init__((-2, -2))
        self.raw_loc = self.loc.copy
        self.add_frame(rs.bg.start)
        self.add_frame(rs.bg.choose)
        self.add_frame(rs.bg.play)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.loc = self.raw_loc.copy
            if data == TAKE_START:
                self.switch_frame(0)
            elif data == TAKE_PLAYERS_CHOOSE:
                self.switch_frame(1)
            elif data == TAKE_PLAY:
                self.switch_frame(2)
                self.loc += Vector2(-2, 0)
            self.transform_location()
