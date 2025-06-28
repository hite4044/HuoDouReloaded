import hashlib
from dataclasses import dataclass, asdict
from math import ceil
from os.path import isfile
from typing import Callable, Any

from PIL import Image, ImageFilter, ImageOps
from PIL import ImageDraw
from PIL import ImageFont

from engine.cache import mk_cache
from lib.public_data import public

USE_CACHE = False


def get_image_cover(raw_image: Image.Image, binary_alpha: bool = False, cover_color=(0, 0, 0)):
    cover = Image.new("RGBA", raw_image.size, cover_color + (0,))
    if binary_alpha:
        cover.putalpha(raw_image.split()[3].point(lambda p: p > 0 and 255))
    else:
        cover.putalpha(raw_image.split()[3])
    return cover


def cvt_hex_color(color: str) -> tuple[int, int, int]:
    color = color.lstrip('#')
    return int(color[0: 2], 16), int(color[2: 4], 16), int(color[4: 6], 16)


@dataclass
class RenderTextArgs:
    text: str
    font_size: float = 48
    anchor: str | None = None
    loc: tuple[int, int] | None = None
    color: str = "#FFCB00"


@dataclass
class RenderGrowArgs:
    width: float | tuple[float, float]
    blur: float | tuple[float, float] = 0
    color: str = "#990000"


@dataclass
class RenderShadowArgs:
    offset: int = 10
    blur: float | tuple[float, float] = 0
    color = "#000000"


@dataclass
class RenderImageArgs:
    image: Image.Image
    loc: tuple[int, int] = (0, 0)


def task_func(func):
    def wrapper(*args, **kwargs):
        render: ImageRender = args[0]
        render.render_tasks.append((func, args[1]))
        return None

    return wrapper


class RenderLow:
    @staticmethod
    def render_text(image: Image.Image, args: RenderTextArgs):
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("assets/方正胖娃简体-CustomSpace.ttf", args.font_size)
        if args.loc is None:
            left, top, right, bottom = draw.textbbox((0, 0), args.text, font=font, anchor=args.anchor)
            args.loc = ((image.width - (right - left)) // 2, (image.height - (bottom - top)) // 2)  # 计算居中位置
        draw.text(args.loc, args.text, args.color, font=font, anchor=args.anchor)
        return image

    @staticmethod
    def render_grow(image: Image.Image, args: RenderGrowArgs):
        cover = image.filter(ImageFilter.GaussianBlur(args.width))
        cover = get_image_cover(cover, True, cvt_hex_color(args.color))
        return cover.filter(ImageFilter.BoxBlur(args.blur))

    @staticmethod
    def render_shadow(image: Image.Image, args: RenderShadowArgs):
        cover = get_image_cover(image, False)  # 先获取原图的遮罩
        before = cover.size
        exp = ceil(args.blur * 2)
        cover = ImageOps.expand(cover,
                                (exp, ceil(args.offset), exp, exp),
                                image.getpixel((0, 0)))  # 拓展大小以准备放置阴影
        print(cover.size, before, ceil(args.blur), ceil(args.offset + args.blur))
        cover = cover.filter(ImageFilter.GaussianBlur(args.blur))  # 高斯模糊遮罩
        # draw = ImageDraw.Draw(cover)
        # draw.rectangle((0, 0, cover.width-1, cover.height-1), (255, 0, 0, 255))
        return cover


class ImageRender:
    def __init__(self, size: tuple[int, int], base: Image.Image = None):
        if base:
            self.base = base
        else:
            self.base = Image.new("RGBA", size, (153, 0, 0, 0))
        self.render_tasks: list[tuple[Callable, Any]] = []
        self.last_task: tuple[Callable, Any] | None = None

    @task_func
    def add_text(self, args: RenderTextArgs):
        RenderLow.render_text(self.base, args)

    @task_func
    def add_grow(self, args: RenderGrowArgs):
        grow = RenderLow.render_grow(self.base, args)
        grow.alpha_composite(self.base, (0, 0))
        self.base = grow

    @task_func
    def add_shadow(self, args: RenderShadowArgs):
        shadow = RenderLow.render_shadow(self.base, args)
        # draw = ImageDraw.Draw(self.base)
        # draw.rectangle((0, 0, self.base.width-1, self.base.height-1), (0, 0, 255, 255))
        shadow.alpha_composite(self.base, (ceil(args.blur * 2), 0))
        self.base = shadow

    @task_func
    def add_image(self, args: RenderImageArgs):
        self.base.paste(args.image, args.loc)

    def get_tasks_hash(self):
        value = hashlib.md5()
        for func, args in self.render_tasks:
            value.update(str(asdict(args)).encode("utf-8"))
        return value.hexdigest()

    @property
    def image(self) -> Image.Image:
        if self.render_tasks:
            tasks_hash = self.get_tasks_hash()
            cache_path = mk_cache(f"{tasks_hash}.png")
            if isfile(cache_path) and public.use_cache:
                return Image.open(cache_path)
            self.last_task = None
            for t_task_func, args in self.render_tasks:
                t_task_func(self, args)
                self.last_task = (t_task_func, args)
            self.last_task = None
            self.render_tasks.clear()
            self.base.save(cache_path)
        return self.base
