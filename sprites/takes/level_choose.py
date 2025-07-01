import pygame as pg

import engine.resource as rs
from engine.asset_parser import image2surface, surface2image, OldImageRender
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import BaseSprite
from sprites.base.frame_sprite import FrameSprite


class LevelEnter(FrameSprite):
    def __init__(self, loc: tuple[int, int], level_index: int, parent: BaseSprite = None):
        self.layer_def = LAYER_UI
        super().__init__((loc[0] + parent.loc.x, loc[1] + parent.loc.y))
        self.level = level_index
        self.add_frame(rs.sprites.level.lock)
        render = OldImageRender((60, 70))
        render.add_text(str(level_index + 1), 50)
        render.add_shadow(8, [0.4, 2.5], False, 2)
        image = surface2image(rs.sprites.level.unlock)
        image.paste(render.base, (22, 28), mask=render.base.split()[3])
        self.add_frame(image2surface(image))

        self.show = False
        self.press_lock = False
        self.lock = level_index != 0

        if not self.lock:
            self.switch_frame(1)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE

    def set_lock(self, lock: bool):
        self.switch_frame(int(not lock))
        self.lock = lock

    def level_enter(self):
        public.transition.run_transition(TAKE_PLAY, self.callback)

    def callback(self):
        public.send_event(EVENT_LEVEL_ENTER, self.level)

    def update(self):
        if self.show:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if pg.mouse.get_pressed(3)[0]:
                    if not self.press_lock:
                        self.press_lock = True
                else:
                    if self.press_lock:
                        if not self.lock:
                            self.level_enter()
                    self.press_lock = False
            else:
                self.press_lock = False
        super().update()


class LevelsContainer(BaseSprite):
    def __init__(self, loc):
        super().__init__(loc=loc)
        self.show = False
        self.levels = []
        for y in range(4):
            for x in range(6):
                if y == 3:
                    _level = LevelEnter((x * 143 - 5, y * 136), 6 * y + x, self)
                else:
                    _level = LevelEnter((x * 143, y * 138), 6 * y + x, self)
                self.levels.append(_level)

    def unlock_level(self, level_name: str):
        for _level in self.levels:
            if _level.level == level_name:
                _level.set_lock(False)
                break

    def event_parse(self, event: int, data):
        for _level in self.levels:
            _level.event_parse(event, data)

    def update(self):
        for _level in self.levels:
            _level.update()
        super().update()
