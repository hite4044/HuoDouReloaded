from copy import copy
from typing import cast as type_cast

import pygame as pg

from engine import resource as rs
from lib import public_data
from lib.define import *
from lib.public_data import sprites, log_func, layer_updates



class BaseSprite(pg.sprite.Sprite):
    def __init__(self, image=None, loc: list | tuple = [0, 0]):
        super().__init__()
        if image is None:
            image = rs.empty

        self.image: pg.surface.Surface = image
        self.rect: pg.rect.Rect = self.image.get_rect()
        self.loc = type_cast(tuple[int, int], tuple(loc))
        self.show = True
        self.image_callback = lambda _: None
        self.get_update_image = lambda: self.image

        self.rect.topleft = type_cast(tuple[int, int], tuple(loc))
        if hasattr(self, "layer_def"):
            layer = self.layer_def
        else:
            layer = LAYER_COVER
        sprites[layer].append(self)
        self.layer_ = layer
        log_func(f"Creating Sprite {self.__class__.__name__} on {loc}", )

    def update_image(self, image: pg.surface.Surface):
        self.image = image
        self.rect: pg.rect.Rect = self.image.get_rect()
        self.rect.topleft = copy(self.loc)
        self.image_callback(image)

    def get_image(self):
        return self.image

    def event_parse(self, event: int, data):
        pass

    def change_layer(self, layer_num: int):
        if layer_num != self.layer_:
            layer_updates.append((self, self.layer_ + 1 - 1, layer_num))
            self.layer_ = layer_num + 1 - 1

    def target(self, x: int, y: int):
        if ELE_EDIT:
            self.loc = (self.loc[0] + x, self.loc[1] + y)
            self.rect.topleft = tuple(self.loc)

    def kill(self):
        sprites[self.layer_].remove(self)
        super().kill()

    def update(self):
        if self.show:
            public_data.screen.blit(self.image, self.rect.topleft)
