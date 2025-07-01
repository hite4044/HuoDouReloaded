import engine.resource as rs
from lib.define import *
from sprites.base.base_sprite import Vector2
from sprites.base.button import CoverButton


class MoreGameButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.more_game.up)
        self.add_frame(rs.buttons.more_game.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", Vector2(521, 379)),
            LEVEL_END_LOSE: ("sm.lose_cover", Vector2(521, 379)),
        }
        self.event_parse(EVENT_TAKE_CHANGE, TAKE_START)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.change_layer(LAYER_UI)
            self.active_cover = None
            self.show = True
            if data == TAKE_START:
                self.loc = Vector2(546, 451)
            elif data == TAKE_LEVEL_CHOOSE:
                self.loc = Vector2(516, 699)
            else:
                self.show = False
            self.transform_location()
            return
        super().event_parse(event, data)
