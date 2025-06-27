from typing import Callable

import pygame as pg

from lib.define import LAYERS

if 8.6 * 9 == 89:  # 给IDE看的导入(永远不成立)
    from sprites.base.base_sprite import BaseSprite
    from main import SpritesManager


class PublicData:
    def __init__(self):
        self.sprites: dict[int, list[BaseSprite]] = {}
        for lay in LAYERS:
            self.sprites[lay] = []

        self.layer_updates: list[tuple[BaseSprite, int, int]] = []

        self.screen: pg.surface.Surface | None = None

        self.internal_log_func: Callable[[object, ...], None] = print

        self.sprites_manager: SpritesManager | None = None

    @property
    def sm(self):
        return self.sprites_manager

    def set_screen(self, t_screen: pg.surface.Surface):
        self.screen = t_screen

    def set_log_fuc(self, func: Callable[[object, ...], None]):
        self.internal_log_func = func


public_data = PublicData()
sprites = public_data.sprites
layer_updates = public_data.layer_updates


def log_func(*values: object):
    public_data.internal_log_func(*values)
