from time import perf_counter

import engine.resource as rs
from engine.asset_parser import image2surface, surface2image
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2, BaseSprite


class Cover(BaseSprite):
    def __init__(self, image, msg):
        self.layer_def = LAYER_END_UI_BG
        super().__init__(image, (0, 0))
        self.show = False
        self.y_in_move = False
        self.statics = []
        self.x_in_move = False
        self.static_cover = None
        self.saved_cover = None
        self.last_update = perf_counter()
        self.msg = msg
        self.stop_y = 0
        self.target_y = 100
        self.stop_x = 1050
        self.target_x = 1150

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if data != TAKE_PLAY:
                self.show = False
        elif event == EVENT_LEVEL_RESET:
            self.show = False
        elif event == EVENT_LEVEL_END:
            if data == self.msg:
                self.loc = Vector2(0, -750)
                self.show = True
                self.y_in_move = True
                self.last_update = 0
        elif event == EVENT_COVER_EXIT:
            if data == self.msg:
                self.x_in_move = True
                self.last_update = 0

    def update(self):
        if self.y_in_move and perf_counter() - self.last_update > 0.02:
            dy = self.target_y - self.loc.y
            delta_y = int(dy / 11)
            if self.loc.y + delta_y > self.stop_y:
                self.loc.y = int(self.stop_y)
                self.y_in_move = False
                public.send_event(EVENT_COVER_FINISH, self.msg)
            else:
                self.loc.y += delta_y
                self.rect.topleft = self.loc.tuple
                self.last_update = perf_counter()
            self.transform_location()
        if self.x_in_move and perf_counter() - self.last_update > 0.02:
            if not self.static_cover:
                image = surface2image(self.image)
                for static in self.statics:
                    assert isinstance(static, BaseSprite)
                    image.alpha_composite(surface2image(static.raw_image), static.rect.topleft)
                self.static_cover = image2surface(image)
                self.saved_cover = self.raw_image.copy()
            dx = self.target_x - self.loc.x
            delta_x = int(dx / 11)
            self.loc.x += delta_x
            if self.loc.x > self.stop_x:
                self.loc.x = int(self.stop_x)
                self.x_in_move = False
                self.update_image(self.saved_cover)
                public.send_event(EVENT_LEVEL_NEXT)
            else:
                self.rect.topleft = self.loc.tuple
                self.static_cover.set_alpha(int(dx / 900 * 255))
                self.update_image(self.static_cover)
                self.last_update = perf_counter()
            self.transform_location()
        super().update()


class WinCover(Cover):
    def __init__(self):
        super().__init__(rs.sprites.level_cover.win, LEVEL_END_WIN)


class LoseCover(Cover):
    def __init__(self):
        super().__init__(rs.sprites.level_cover.lose, LEVEL_END_LOSE)


class CompleteCover(Cover):
    def __init__(self):
        super().__init__(rs.sprites.level_cover.complete, LEVEL_END_ALL_COMPLETE)
