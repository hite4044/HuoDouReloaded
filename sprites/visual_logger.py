import json
from os import makedirs
from os.path import isfile
from time import perf_counter

import pygame as pg
from PIL import ImageFont, ImageDraw, Image

from engine import resource as rs
from engine.asset_parser import image2surface
from lib.define import *
from lib.public_data import public_data


class VisualLogger(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = rs.empty
        self.last_render = perf_counter()
        self.texts: list[str] = []
        self.text_images: list[Image.Image] = []
        self.texts_counter = 0
        self.is_finish = False
        self.ft = ImageFont.truetype("assets/UnifontExMono.ascii.ttf", 16)

        self.start = perf_counter()
        if isfile("data/load_times.json"):
            self.last_times = json.load(open("data/load_times.json"))
        else:
            self.last_times = json.load(open("assets/data/load_times.json"))
        self.times = []

    def log(self, *values: object):
        text = " ".join(map(str, values))
        print(text)
        if self.is_finish:
            return
        if LOADING_LOG:
            self.texts.append(text)
        if "Rendering" not in text:
            self.times.append(perf_counter())
            self.texts_counter += 1
        self.render_image()

    def render_image(self):
        if perf_counter() - self.last_render > 1 / LOADING_FPS:
            self.render_now()

    def render_text(self, *lines: str):
        text = "\n".join(lines)
        image = Image.new("RGB", (450, 18 * len(lines)), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=self.ft)
        left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=self.ft)
        width = right - left
        image = image.crop((0, 0, width, image.height))
        return image

    def render_now(self):
        self.text_images.append(self.render_text(*self.texts))
        self.texts.clear()

        image = Image.new("RGB", (1050, 750), (0, 0, 0))
        text_offset = 680
        for i in range(1, len(self.text_images) + 1):
            text_image = self.text_images[-i]
            text_offset -= text_image.height
            image.paste(text_image, (0, text_offset))

        draw = ImageDraw.Draw(image)
        try:
            draw.rectangle((0, 720, 1050 * self.last_times[self.texts_counter], 750), fill="white")
        except IndexError:
            draw.rectangle((0, 720, 1050, 750), fill="white")
        except ValueError:
            pass

        self.image = image2surface(image)
        self.update()
        self.last_render = perf_counter()

    def finish(self):
        times = [round((i - self.start) / (perf_counter() - self.start), 3) for i in self.times]
        makedirs("data", exist_ok=True)
        json.dump(times, open("data/load_times.json", "w+"))
        self.is_finish = True

    def update(self):
        pg.event.get()
        public_data.screen.fill((0, 0, 0))
        public_data.screen.blit(self.image, (0, 0))
        pg.display.update()
