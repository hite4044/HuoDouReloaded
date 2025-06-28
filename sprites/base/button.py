import pygame as pg

from engine.asset_parser import OldImageRender, image2surface, surface2image
from lib.define import *
from lib.image_render import ImageRender, RenderShadowArgs
from lib.public_data import public
from sprites.base.base_sprite import Align, Vector2
from sprites.base.frame_sprite import FrameSprite


class Button(FrameSprite):
    def __init__(self, loc, shadow=True):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.set_align(Align.CENTER)
        self.shadow = shadow
        self.press_lock = False
        self.enable = True

    def add_frame(self, frame: pg.surface.Surface):
        if self.shadow:
            render = ImageRender(frame.get_size(), surface2image(frame))
            render.add_shadow(RenderShadowArgs(6, 2.5))
            frame = image2surface(render.image)
        super().add_frame(frame)

    def update(self):
        if self.show and self.enable:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if pg.mouse.get_pressed(3)[0]:
                    if not self.press_lock:
                        self.on_press()
                        self.press_lock = True
                    self.switch_frame(0)
                else:
                    if self.press_lock:
                        self.on_up()
                    self.press_lock = False
                    self.switch_frame(1)
            else:
                self.press_lock = False
                self.switch_frame(0)
        elif not self.enable:
            self.switch_frame(0)
        super().update()

    def on_press(self):
        pass

    def on_up(self):
        pass



class CoverButton(Button):
    def __init__(self):
        super().__init__((0, 0))
        self.active_cover = None
        self.cover_offset: Vector2 = Vector2(0, 0)
        self.show = False
        self.cover_map: dict[int, tuple[str, Vector2]] = {}

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if event != TAKE_PLAY:
                self.show = False
                self.active_cover = None
        elif event == EVENT_LEVEL_END:
            self.change_layer(LAYER_END_UI)
            cover_path, self.cover_offset = self.cover_map[data]
            globals_vars = {"sm": public.sprites_manager}
            self.active_cover = eval(cover_path, globals_vars)
        elif event == EVENT_LEVEL_RESET:
            self.show = False
            self.active_cover = None
        elif event == EVENT_COVER_RUN:
            if self.active_cover:
                self.show = False
                self.active_cover.statics.append(self)

    def transform_location(self):
        super().transform_location()
        self.rect.topleft = self.transformed_loc

    def update(self):
        if self.active_cover:
            self.loc = self.active_cover.loc + self.cover_offset
            self.transform_location()
            self.show = True
        super().update()

