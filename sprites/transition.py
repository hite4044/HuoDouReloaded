from time import perf_counter

from PIL import Image

import engine.resource as rs
from engine.asset_parser import image2surface, surface2image
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2, BaseSprite
from sprites.base.frame_sprite import FrameSprite


class TransitionMask(FrameSprite):
    def __init__(self):
        self.layer_def = LAYER_COVER
        super().__init__([0, 0])
        self.show = False

        self.on_transition = False
        self.just_callback = False
        self.on_switch = lambda: None
        self.transition_take = None
        self.last_update = perf_counter()
        self.frame_index = 0
        self.frames_per = 32
        for i in range(1, 256, 15):
            image = Image.new("RGBA", (1050, 750), (0, 0, 0, i))
            self.add_frame(image2surface(image))

    def run_transition(self, take_id: int, callback=None, just_callback: bool = False):
        if not self.on_transition:
            self.show = True
            self.on_transition = True
            self.transition_take = take_id
            self.last_update = perf_counter()
            self.frame_index = 0
        if callback:
            self.just_callback = just_callback
            self.on_switch = callback
        else:
            self.on_switch = lambda: None

    @staticmethod
    def transition_now(take_id: int):
        public.send_event(EVENT_TAKE_CHANGE, take_id)

    def update(self):
        if self.on_transition:
            if perf_counter() > self.last_update + 1 / self.frames_per - 0.003:
                if self.frame_index > 15:
                    if self.frame_index == 16:
                        if not self.just_callback:
                            if self.transition_take != TAKE_EMPTY:
                                self.transition_now(self.transition_take)
                        self.on_switch()
                    if self.frame_index > 30:
                        self.on_transition = False
                        self.show = False
                    self.switch_frame(31 - self.frame_index)
                else:
                    self.switch_frame(self.frame_index)
                self.frame_index += 1
                self.last_update = perf_counter()
        super().update()
