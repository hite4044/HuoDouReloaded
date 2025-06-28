from typing import Callable, Any

import pygame as pg

from lib.config import gm_config
from lib.define import LAYERS

if 8.6 * 9 == 89:  # 给IDE看的导入(永远不成立)
    from sprites.base.base_sprite import BaseSprite
    from engine.sprite_manager import SpritesManager


def create_config_bind(name: str):
    return property(fget=lambda self: getattr(gm_config, name),
                          fset=lambda self, v: gm_config.set_config(name, v))

class PublicData:
    play_sound = create_config_bind("play_sound")
    use_cache = create_config_bind("use_cache")

    def __init__(self):
        self.sprites: dict[int, list[BaseSprite]] = {}
        for lay in LAYERS:
            self.sprites[lay] = []

        self.layer_updates: list[tuple[BaseSprite, int, int]] = []

        self.screen: pg.surface.Surface | None = None

        self.internal_log_func: Callable[[object, ...], None] = print

        self.sprites_manager: SpritesManager | None = None

        self.players_count: int = 1

        self.move_target: BaseSprite | None = None


    @property
    def level_manager(self):
        return self.sprites_manager.level_manager

    @property
    def sm(self):
        return self.sprites_manager

    @property
    def transition(self):
        return self.sprites_manager.transition

    def set_screen(self, t_screen: pg.surface.Surface):
        self.screen = t_screen

    def set_log_fuc(self, func: Callable[[object, ...], None]):
        self.internal_log_func = func

    def run_transition(self, take_id: int, callback=None, just_callback: bool = False):
        self.sprites_manager.transition.run_transition(take_id, callback, just_callback)

    def send_event(self, event_id: int, data: Any):
        self.sprites_manager.send_event(event_id, data)


public = PublicData()
sprites = public.sprites
layer_updates = public.layer_updates


def log_func(*values: object):
    public.internal_log_func(*values)
