import pygame as pg
from PIL import Image, ImageFilter

from engine.asset_parser import surface2image, get_image_cover
from sprites.base.base_sprite import BaseSprite, Vector2


class Shadow(BaseSprite):
    # noinspection PyShadowingNames
    def __init__(self, sprite: BaseSprite, offset: int, radius: float = 2):
        self.parent = sprite
        self.offset = offset
        self.radius = radius
        self.layer_def = sprite.layer - 1
        super().__init__(self.make_cover(sprite.image, radius), (sprite.loc + Vector2(0, self.offset)).tuple)
        self.set_align(sprite.align)
        self.raw_cbk = sprite.image_update_callback
        sprite.image_update_callback = self.image_update_callback
        self.image_update_callback(sprite.image)

    def image_update_callback(self, image: pg.surface.Surface):
        self.raw_cbk(image)
        cover = self.make_cover(image, self.radius)
        self.update_image(cover)

    @staticmethod
    def make_cover(surface: pg.surface.Surface, radius: float):
        image = surface2image(surface)
        cover = get_image_cover(image)
        cover_new = Image.new("RGBA", [cover.width + 100, cover.height + 100], (0, 0, 0, 0))
        cover_new.paste(cover, (50, 50))
        blur_cover = cover_new.filter(ImageFilter.GaussianBlur(radius=radius))
        return pg.image.frombytes(blur_cover.tobytes(), blur_cover.size, "RGBA").convert_alpha()

    def update(self):
        self.show = self.parent.show
        if self.show:
            self.loc = self.parent.loc + Vector2(0, self.offset)
            self.transform_location()
        super().update()
