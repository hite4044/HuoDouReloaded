from PIL import ImageDraw, Image, ImageFont

from engine.asset_parser import image2surface, OldImageRender
from lib.define import LAYER_UI
from lib.image_render import ImageRender
from sprites.base.base_sprite import BaseSprite


class OldTextSprite(BaseSprite):
    def __init__(self, loc, text: str, font_size: float,
                 image_size, outline_blur: bool = False, fill_color: str = "#FFCB00",
                 outline: bool = False, outline_color: str = "#990000",
                 shadow_offset: int = -1, shadow_radius: float = -1,
                 spacing: int = 4, cache: bool = True,
                 outline_width: float = 2, blur_radius: float = 2):
        render = OldImageRender(image_size, use_cache=cache)
        render.add_text(text, font_size, image_size, text_color=fill_color,
                        outline=outline, outline_width=outline_width, outline_color=outline_color, faster_outline=True,
                        outline_blur=outline_blur, blur_radius=blur_radius, spacing=spacing)
        if shadow_offset > 0 or shadow_radius > 0:
            render.add_shadow(shadow_offset, shadow_radius)
        self.layer_def = LAYER_UI
        super().__init__(image2surface(render.base), loc)

        ft = ImageFont.truetype("assets/方正胖娃简体.ttf", font_size)
        text_image = Image.new("RGBA", image_size, (255, 255, 255, 255))
        draw = ImageDraw.Draw(text_image)
        x, y = (text_image.width // 2, text_image.height // 2)
        draw.text((x, y), text, font=ft, fill="#FFCB00", anchor="mm", spacing=6)
        self.text_image = image2surface(text_image)

    def get_image(self):
        return self.text_image


class TextSprite(BaseSprite):
    def __init__(self, loc: tuple[int, int], size: tuple[int, int]):
        self.render = ImageRender(size)
        super().__init__(loc=loc)

    def finish_render(self):
        image = self.render.image
        surface = image2surface(image)
        self.update_image(surface)
