import json
from copy import deepcopy

from lib.define import *
from lib.public_data import public, log_func
from sprites.base.base_sprite import BaseSprite
import pygame as pg

from sprites.level.elements.level_element import Ground, Burr, GoldenBean, Gun, XKill, LevelElement
from sprites.level.player import Player


class LevelManager(BaseSprite):
    def __init__(self):
        super().__init__()
        self.level: str|None = None
        self.left_players: int|None = None
        self.golden_bean = -1
        self.golden_bean_all = -1
        self.floor = pg.sprite.Group()
        self.kills = pg.sprite.Group()
        self.beans = pg.sprite.Group()
        self.edges = pg.sprite.Group()
        self.others = []
        self.elements = []
        self.players = []
        self.level_datas = json.load(open("assets/data/level_data.json"))
        self.show = False
        self.create_map = {
            "ground": Ground,
            "burr": Burr,
            "golden_bean": GoldenBean,
            "gun": Gun,
            "x_kill": XKill
        }
        self.add_edge((-50, 750), (1100, 50))
        self.add_edge((-50, 0), (50, 750))
        self.add_edge((1050, 0), (50, 750))

    def add_edge(self, loc: tuple[int, int], size: tuple[int, int]):
        edge = BaseSprite(loc=loc)
        edge.show = False
        edge.rect = pg.rect.Rect(*loc, *size)
        # noinspection PyTypeChecker
        self.edges.add(edge)

    def event_parse(self, event: int, level: str):
        if event == EVENT_TAKE_CHANGE:
            if level != TAKE_PLAY:
                self.level = None
                self.unload_level()
        elif event == EVENT_LEVEL_ENTER:
            self.load_level(level)
            self.level = level
        elif event == EVENT_REQ_CLONE:
            if move_target in self.elements:
                self.clone_sprite()
        elif event == EVENT_REQ_LEVEL_SAVE:
            self.save_level()
        elif event == EVENT_REQ_DELETE:
            if move_target in self.elements:
                self.remove_sprite()
        elif event == EVENT_LEVEL_EXIT:
            self.unload_level()
        elif event == EVENT_LEVEL_RESET:
            self.unload_level()
            self.load_level(self.level)
        elif event == EVENT_LEVEL_END:
            if level == LEVEL_END_WIN:
                levels = list(self.level_datas.keys())
                next_level = levels[levels.index(level) + 1]
                public.sm.levels_container.unlock_level(next_level)
        elif event == EVENT_LEVEL_NEXT:
            levels = list(self.level_datas.keys())
            level = levels[levels.index(level) + 1]
            self.unload_level()
            self.load_level(level)

    def add_sprite_kinds(self, sprite, sprite_data: dict):
        if sprite_data["type"] == "ground":
            self.floor.add(sprite)
        elif sprite_data["type"] in ["burr", "x_kill"]:
            self.kills.add(sprite)
        elif sprite_data["type"] == "golden_bean":
            self.beans.add(sprite)

    def remove_sprite(self):
        if public.move_target in self.players:
            self.players.remove(public.move_target)
        self.elements.remove(public.move_target)
        public.move_target.kill()

    def clone_sprite(self):
        assert isinstance(public.move_target, LevelElement)
        sprite_data = public.move_target.get_sprite_data()
        log_func(f"Clone Sprite on {sprite_data['loc']}:", self.__class__.__name__)
        # noinspection PyArgumentList
        sprite = public.move_target.__class__(deepcopy(sprite_data))
        self.add_sprite_kinds(sprite, sprite_data)
        self.elements.append(sprite)

    def load_level(self, _level: str):
        self.left_players = int(public.players_count)
        self.level = _level
        level_data = self.level_datas[_level]
        self.golden_bean = 0
        self.golden_bean_all = level_data["bean_count"]
        for sprite_data in level_data["items"]:
            sprite = self.create_map[sprite_data["type"]](sprite_data)
            self.add_sprite_kinds(sprite, sprite_data)
            self.elements.append(sprite)

        self.players = [Player(level_data["players"][i], i + 1) for i in range(public.players_count)]
        if LEVEL_EDIT:
            public.move_target = self.elements[0]

    def unload_level(self):
        if public.move_target in self.elements:
            public.move_target = None
        for sprite in self.others + self.elements + self.players:
            sprite.kill()
        self.elements.clear()
        self.players.clear()
        self.floor.remove(*self.floor.sprites())
        self.beans.remove(*self.beans.sprites())
        self.kills.remove(*self.floor.sprites())

    def save_level(self):
        log_func("Save Level", self.level)
        new_level_datas = deepcopy(self.level_datas)
        new_level_datas[str(self.level)]["items"] = [sprite.get_sprite_data() for sprite in self.elements]
        json.dump(new_level_datas, open("assets/data/level_data.json", "w+"), indent=4)
