import engine.resource as rs
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2
from sprites.base.button import CoverButton


class ReturnChooseButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.return_choose.up)
        self.add_frame(rs.buttons.return_choose.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", Vector2(425, 470)),
            LEVEL_END_LOSE: ("sm.lose_cover", Vector2(425, 470)),
        }

    def on_up(self):
        public.transition.run_transition(TAKE_LEVEL_CHOOSE, lambda: public.send_event(EVENT_LEVEL_EXIT, 0))
