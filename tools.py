import hashlib
import json
from io import BytesIO
from os import mkdir
from os.path import abspath, isfile, join as path_join, expandvars, isdir
from shutil import rmtree

import pygame as pg
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from cairosvg import svg2png

RENDER_SCALE = 3
re_render = False
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("product")

# 常量定义
from lib.define import *


def db(n: float):
    if n > 255:
        return 255
    if n < 0:
        return 0
    return n


def ms(n1: float, n2: float):
    return round((n2 - n1) * 1000, 4)


def surface2image(surface: pg.surface.Surface):
    image_bytes = pg.image.tobytes(surface, "RGBA")
    return Image.frombytes("RGBA", surface.get_size(), image_bytes)


def image2surface(image: Image.Image | str):
    if isinstance(image, Image.Image):
        image_bytes = image.tobytes()
        # noinspection PyTypeChecker
        return pg.image.frombuffer(image_bytes, (image.width, image.height), image.mode).convert_alpha()
    return pg.image.load(image).convert_alpha()


def render_svg2image(fp, scale: float = 1.5, log_func=print, force_image: bool = False):
    load_path = abspath(fp)
    fp_hash = hashlib.sha1((fp if scale == 1.5 else fp + str(scale)).encode("utf-8")).hexdigest()
    image_cache_fp = path_join(cache_path, f"{fp_hash}.png")
    if not re_render:
        if force_image:
            try:
                image = Image.open(image_cache_fp)
                return image
            except FileNotFoundError:
                pass
        else:
            if isfile(image_cache_fp):
                return image_cache_fp

    png_bytes = svg2png(url=load_path, scale=scale * RENDER_SCALE)
    log_func("Rendering Assets:", fp)
    image = Image.open(BytesIO(png_bytes))
    image = image.resize((int(image.width / RENDER_SCALE), int(image.height / RENDER_SCALE)))
    image.save(image_cache_fp)
    return image


def load_svg(fp: str, scale: float = 1.5, log_func=print, force_image: bool = False):
    png_image = render_svg2image(fp, scale, log_func, force_image)
    log_func("Loading Assets:", fp)
    return image2surface(png_image)


def get_image_cover(_image: Image.Image, use_alpha: bool = True, cover_color=(0, 0, 0)):
    image = _image.copy()

    cover = Image.new("RGBA", image.size, cover_color + (0,))
    if use_alpha:
        cover.putalpha(image.split()[3])
    else:
        cover.putalpha(image.split()[3].point(lambda p: p > 0 and 255))

    return cover


def draw_text_outline(draw, text: str, font, loc,
                      outline_width: int = 3, outline_color="#990000"):
    draw_text = lambda xy: draw.text(xy, text, font=font, fill=outline_color, anchor="mm")
    x, y = loc
    # thin border
    for i in range(1, outline_width):
        draw_text((x - i, y))
    for i in range(1, outline_width):
        draw_text((x + i, y))
    for i in range(1, outline_width):
        draw_text((x, y - i))
    for i in range(1, outline_width):
        draw_text((x, y + i))

    # thicker border
    for i in range(1, outline_width):
        draw_text((x - i, y - i))
    for i in range(1, outline_width):
        draw_text((x + i, y - i))
    for i in range(1, outline_width):
        draw_text((x - i, y + i))
    for i in range(1, outline_width):
        draw_text((x + i, y + i))


def draw_outline_text(draw: ImageDraw.ImageDraw,
                      loc,
                      text: str,
                      font,
                      shadow_color: str = "#990000",
                      fillcolor: str = "#FFCB00",
                      outline_width: int = 1,
                      spacing: int = 5
                      ):
    draw_text_outline(draw, text, font, loc, outline_width, shadow_color)
    x, y = loc
    draw.text((x, y), text, font=font, fill=fillcolor, anchor="mm", spacing=spacing)


class ImageRender:
    def __init__(self, size: list[int] | tuple[int, int] = [50, 50],
                 base_image: pg.surface.Surface | Image.Image = None,
                 use_cache: bool = False):
        if base_image:
            if isinstance(base_image, pg.surface.Surface):
                base_image = surface2image(base_image)
            self._base = base_image
        else:
            self._base = Image.new("RGBA", size, (255, 255, 255, 0))
        self.do = {}
        self.cache = use_cache

    def _add_image(self, image, loc: list[int] | tuple[int, int]):
        if isinstance(image, pg.surface.Surface):
            image = surface2image(image)
        self._base.paste(image, loc)

    def add_image(self, image, loc: list[int] | tuple[int, int]):
        if self.cache:
            self.do[self._add_image] = (image, loc)
        else:
            self._add_image(image, loc)

    def _add_shadow(self, offset: int, blur_radius: float | list[float] = 3,
                    use_alpha: bool = True, cover_times: int = 1):
        cover = self._base
        for i in range(cover_times):
            cover = get_image_cover(cover, use_alpha)
            if i == 0:
                cover_new = Image.new("RGBA", [self._base.width + 100, self._base.height + 100], (0, 0, 0, 0))
                cover_new.paste(cover, (50, 50))
            if cover_times != 1:
                if i == 0:
                    # noinspection PyUnboundLocalVariable
                    cover = cover_new.filter(ImageFilter.GaussianBlur(radius=blur_radius[i]))
                else:
                    cover = cover.filter(ImageFilter.GaussianBlur(radius=blur_radius[i]))
            else:
                # noinspection PyUnboundLocalVariable
                cover = cover_new.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        if cover_times != 1:
            blur_radius = max(blur_radius)

        new_size = list(self._base.size)
        new_size[0] += 2 * int(blur_radius + 1)
        new_size[1] += offset + int(blur_radius) + 1
        new_base = Image.new("RGBA", new_size, (255, 255, 255, 0))
        new_base.paste(cover, (-50 + int(blur_radius) + 1, -50 + offset))
        new_base.paste(self._base, (int(blur_radius) + 1, 0), mask=self._base.split()[3])
        self._base = new_base

    def add_shadow(self, offset: int, blur_radius: float | list[float] = 3,
                   use_alpha: bool = True, cover_times: int = 1):
        if self.cache:
            self.do[self._add_shadow] = (offset, blur_radius, use_alpha, cover_times)
        else:
            self._add_shadow(offset, blur_radius, use_alpha, cover_times)

    def _add_text(self,
                  text: str, font_size: float = 18, image_size=[50, 50], text_color="#FFCB00",
                  outline: bool = False, outline_width: float | int = 3, outline_color="#990000",
                  faster_outline: bool = False, text_loc: tuple[int, int] | list[int] = None,
                  outline_blur: bool = False, blur_radius: float = 3,
                  spacing: int = 4):
        ft = ImageFont.truetype("assets/方正胖娃简体.ttf", font_size)
        image = Image.new("RGBA", image_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        text_image = Image.new("RGBA", image_size, (255, 255, 255, 0))
        if text_loc is None:
            text_loc = (image.width // 2, image.height // 2)
        ImageDraw.Draw(text_image).text(text_loc, text,
                                        font=ft, fill=text_color, anchor="mm", spacing=spacing)

        if outline:
            if faster_outline:
                image = text_image.filter(ImageFilter.GaussianBlur(radius=outline_width))
                cover_color = tuple(map(lambda x: int(x, 16), [outline_color[i:i + 2] for i in range(1, 6, 2)]))
                image = get_image_cover(image, False, cover_color)
                if outline_blur:
                    image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            else:
                draw_text_outline(draw, text, ft, text_loc, outline_width, outline_color)
                if outline_blur:
                    image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        image.paste(text_image, (0, 0), mask=text_image.split()[3])

        self._base.paste(image, (0, 0), mask=image.split()[3])

    def add_text(self,
                 text: str, font_size: float = 18, image_size=[50, 50], text_color="#FFCB00",
                 outline: bool = False, outline_width: float | int = 3, outline_color="#990000",
                 faster_outline: bool = False, text_loc: tuple[int, int] | list[int] = None,
                 outline_blur: bool = False, blur_radius: float = 3,
                 spacing: int = 4):
        if self.cache:
            self.do[self._add_text] = (text, font_size, image_size, text_color, outline, outline_width, outline_color,
                                       faster_outline, text_loc, outline_blur, blur_radius, spacing)
        else:
            self._add_text(text, font_size, image_size, text_color, outline, outline_width, outline_color,
                           faster_outline, text_loc, outline_blur, blur_radius, spacing)

    def calc_image(self):
        for func, args in self.do.items():
            func(*args)
        return self._base

    @property
    def base(self) -> Image.Image:
        if self.cache:
            do_hash = hashlib.sha1()
            for args in self.do.values():
                for arg in args:
                    try:
                        do_hash.update(str(hash(arg)).encode("utf-8"))
                    except TypeError:
                        pass
            image_path = path_join(cache_path, f"{do_hash.hexdigest()}.png")
            if not isfile(image_path):
                image = self.calc_image()
                image.save(image_path)
                return image
            image = Image.open(image_path)
            return image

        else:
            return self._base


# default
cache_path = path_join(expandvars("%TEMP%"), "HuoDouReloadedTemp")
if not isdir(cache_path):
    mkdir(cache_path)


def remove_assets():
    if isdir(cache_path):
        rmtree(cache_path)
        mkdir(cache_path)


info_fp = path_join(cache_path, "info.json")
if isfile(info_fp):
    try:
        with open(info_fp) as f:
            _data = json.load(f)
            if _data["version"] != VERSION:
                remove_assets()
    except (OSError, json.JSONDecodeError):
        remove_assets()
else:
    remove_assets()
    with open(info_fp, "w+") as f:
        json.dump({"version": VERSION}, f)
