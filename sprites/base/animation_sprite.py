from time import perf_counter

from lib.define import OLD_ANIMATION
from sprites.base.base_sprite import Align
from sprites.base.frame_sprite import FrameSprite


class AnimationSprite(FrameSprite):
    def __init__(self, loc):
        super().__init__(loc)
        self.align = Align.CENTER
        self.animations = {}
        self.played_animation = None
        self.end_stop = False
        self.animation_index = 0
        self.ani_frame_start = 0
        self.ani_frame_count = 0
        self.ani_frame_time = 0
        self.last_update = perf_counter()

    def add_animation(self, resources, name: str, speed: int = 10):
        frames = resources if isinstance(resources, list) else resources.Frames
        for frame in frames:
            self.add_frame(frame)
        self.animations[name] = [len(self.frames) - len(frames), len(frames), 1 / speed]

    def play_animation(self, name: str, end_stop: bool = False):
        if name != self.played_animation:
            self.played_animation = name
            self.ani_frame_start, self.ani_frame_count, self.ani_frame_time = self.animations[self.played_animation]
            self.animation_index = 0
            self.last_update = perf_counter() - self.ani_frame_time
            self.end_stop = end_stop

    def switch_frame(self, index: int):
        super().switch_frame(index)

    def update(self):
        if self.show and self.played_animation and self.animation_index != -1:
            if perf_counter() - self.last_update > self.ani_frame_time:
                frame_delta = int((perf_counter() - self.last_update) // self.ani_frame_time)
                self.switch_frame(self.ani_frame_start + self.animation_index)
                self.animation_index += frame_delta
                if self.animation_index >= self.ani_frame_count:
                    if self.end_stop:
                        self.animation_index = -1
                        self.show = False
                    else:
                        self.animation_index = 0
                self.last_update += frame_delta * self.ani_frame_time
        if not OLD_ANIMATION:
            self.transform_location()
        super().update()

