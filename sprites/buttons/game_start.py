import engine.resource as rs
from lib.define import *
from lib.public_data import public
from sprites.base.button import Button


class StartButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.start_game.up)
        self.add_frame(rs.buttons.start_game.down)

    def on_up(self):
        public.sm.transition.run_transition(TAKE_PLAYERS_CHOOSE)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_START
