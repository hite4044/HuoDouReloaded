from enum import Enum

import pygame as pg

from engine import resource as rs
from lib.define import *
from lib.public_data import sprites, log_func, layer_updates, public


class Align(Enum):
    TOPLEFT = 0
    CENTER = 1


class Vector2:
    def __init__(self, loc: tuple[int, int] | list[int] | int, y: int | None = None):
        if isinstance(loc, Vector2):
            self.x, self.y = loc.x, loc.y
        else:
            if y is not None:
                loc = [loc, y]
            self.x: int = loc[0]
            self.y: int = loc[1]

    def copy(self):
        return Vector2((self.x, self.y))

    def __add__(self, other: 'Vector2'):
        return Vector2((self.x + other.x, self.y + other.y))

    def __sub__(self, other: 'Vector2'):
        return Vector2((self.x - other.x, self.y - other.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __iter__(self):
        yield self.x
        yield self.y

    @property
    def tuple(self):
        return self.x, self.y

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"


class BaseSprite(pg.sprite.Sprite):
    def __init__(self, image=None, loc: list | tuple = (0, 0)):
        super().__init__()
        log_func(f"Creating Sprite {self.__class__.__name__} on {loc}", )
        if image is None:
            image = rs.empty

        self.show = True  # 是否显示
        self.raw_image: pg.surface.Surface = image  # 渲染图片
        self.rect: pg.rect.Rect = self.raw_image.get_rect()  # 图片矩形
        self.loc: Vector2 = Vector2(loc)  # 外部位置
        self.transformed_loc: tuple[int, int] = self.loc.tuple  # 变换后的位置
        self.align = Align.TOPLEFT  # 位置对齐
        self.image_update_callback = lambda _: None  # 图片更新回调函数

        if hasattr(self, "layer_def"):
            layer = self.layer_def
        else:
            layer = LAYER_COVER
        sprites[layer].append(self)
        self.layer = layer
        self.rect.topleft = self.transformed_loc
        self.transform_location()

    def update_image(self, image: pg.surface.Surface):  # 更新精灵图像
        self.raw_image = image
        self.rect: pg.rect.Rect = image.get_rect()  # 分离Rect更新逻辑到新的类
        if self.align != Align.TOPLEFT:
            self.transform_location()
        self.rect.topleft = self.transformed_loc
        self.image_update_callback(image)

    @property
    def image(self):  # 获取精灵图像
        return self.raw_image

    def event_parse(self, event: int, data):  # 消息处理函数
        pass

    def change_layer(self, layer_num: int):  # 更改层
        if layer_num != self.layer:
            layer_updates.append((self, int(self.layer), layer_num))
            self.layer = int(layer_num)

    def target(self, x: int, y: int):  # 移动精灵
        if ELE_EDIT:
            self.loc += Vector2(x, y)
            self.transform_location()

    def set_align(self, align: Align):
        self.align = align
        self.transform_location()

    def transform_location(self):  # 变换坐标
        if self.align == Align.TOPLEFT:
            self.transformed_loc = self.loc.tuple
        elif self.align == Align.CENTER:
            self.transformed_loc = (self.loc - Vector2(self.rect.width // 2, self.rect.height // 2)).tuple
        else:
            raise RuntimeError("游戏炸咯, 对齐类型不支持")

    def update(self):  # 渲染图像
        if self.show:
            public.screen.blit(self.raw_image, self.transformed_loc)

    def kill(self):  # 删除精灵
        sprites[self.layer].remove(self)
        super().kill()
