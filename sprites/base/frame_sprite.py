import pygame as pg

from sprites.base.base_sprite import BaseSprite


class FrameSprite(BaseSprite):
    def __init__(self, loc):
        super().__init__(None, loc)
        self.frames: list[pg.surface.Surface] = []
        self.now_frame_index = None

    def add_frame(self, frame):
        self.frames.append(frame)
        if len(self.frames) == 1:
            self.switch_frame(0)
        return len(self.frames) - 1

    def switch_frame(self, index: int):
        if index != self.now_frame_index:
            self.now_frame_index = index
            self.update_image(self.frames[index])
