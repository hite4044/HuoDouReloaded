import pygame as pg

from lib.define import LAYERS

sprites = {}
for lay in LAYERS:
    sprites[lay] = []
layer_updates = []
screen: pg.surface.Surface | None = None
internal_log_func = print


def log_func(*values: object):
    internal_log_func(*values)
