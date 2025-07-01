import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import pygame as pg

from lib.define import *
from lib.public_data import public, log_func
from sprites.base.base_sprite import BaseSprite
from sprites.level.elements.level_element import LevelElement
from sprites.level.elements import level_element as level_element_lib
from sprites.level.player import Player


@dataclass
class LevelData:
    name: str
    bean_count: int
    players: dict[str, tuple[int, int]]
    items: list[dict[str, Any]]

    file_name: str = None

    @classmethod
    def load(cls, data: dict[str, Any]):
        name = data.get("name", "无名")
        bean_count = data.get("bean_count", 0)
        players = data.get("players", {})
        items = data.get("items", [])
        return cls(name, bean_count, players, items)

    def save(self, elements: list[LevelElement]) -> dict[str, Any]:
        return {
            "name": self.name,
            "bean_count": self.bean_count,
            "players": self.players,
            "items": [sprite.save() for sprite in elements]
        }


class LevelManager(BaseSprite):
    def __init__(self):
        super().__init__()
        self.show = False

        self.left_players: int | None = None
        self.golden_bean = -1
        self.golden_bean_all = -1

        self.floor = pg.sprite.Group()
        self.kills = pg.sprite.Group()
        self.beans = pg.sprite.Group()
        self.edges = pg.sprite.Group()
        self.bombs = []
        self.elements = []
        self.players = []

        self.level_index: int = 0
        self.level_datas: list[LevelData] = []

        self.add_edge((-50, 750), (1100, 50))
        self.add_edge((-50, 0), (50, 750))
        self.add_edge((1050, 0), (50, 750))

        self.import_levels()

    def import_levels(self):
        with open("assets/data/levels.json") as f:
            level_names: list[str] = json.load(f)
        for level_file_name in level_names:
            with open(f"assets/data/levels/{level_file_name}") as f:
                log_func(f"Load Level: {level_file_name}")
                level_data = LevelData.load(json.load(f))
                level_data.file_name = level_file_name
                self.level_datas.append(level_data)

    def add_edge(self, loc: tuple[int, int], size: tuple[int, int]):
        edge = BaseSprite(loc=loc)
        edge.show = False
        edge.rect = pg.rect.Rect(*loc, *size)
        # noinspection PyTypeChecker
        self.edges.add(edge)

    def event_parse(self, event: int, level: int):
        if event == EVENT_TAKE_CHANGE:
            if level != TAKE_PLAY:
                self.level_index = -1
                self.unload_level()
        elif event == EVENT_LEVEL_ENTER:
            self.load_level(level)
        elif event == EVENT_REQ_CLONE:
            if public.move_target in self.elements:
                self.clone_sprite()
        elif event == EVENT_REQ_LEVEL_SAVE:
            self.save_level()
        elif event == EVENT_REQ_DELETE:
            if public.move_target in self.elements:
                self.remove_sprite()
        elif event == EVENT_LEVEL_EXIT:
            self.unload_level()
        elif event == EVENT_LEVEL_RESET:
            self.unload_level()
            self.load_level(self.level_index)
        elif event == EVENT_LEVEL_END:
            if level == LEVEL_END_WIN:
                public.sm.levels_container.unlock_level(self.level_index + 1)
        elif event == EVENT_LEVEL_NEXT:
            self.level_index += 1
            self.unload_level()
            self.load_level(self.level_index)

    def remove_sprite(self):
        if public.move_target in self.players:
            self.players.remove(public.move_target)
        public.move_target.kill()

    def clone_sprite(self):
        assert isinstance(public.move_target, LevelElement)
        sprite_data = public.move_target.save()
        log_func(f"Clone Sprite on {sprite_data['loc']}:", self.__class__.__name__)
        # noinspection PyArgumentList
        sprite = public.move_target.__class__(deepcopy(sprite_data))
        self.elements.append(sprite)

    def load_level(self, level_index: int):
        self.level_index = level_index
        self.left_players = int(public.players_count)
        self.golden_bean = 0

        level_data = self.level_datas[level_index]
        self.golden_bean_all = level_data.bean_count
        classes = {name: getattr(level_element_lib, name) for name in dir(level_element_lib)}
        for sprite_data in level_data.items:
            if sprite_data["type"] not in classes:
                print(f"Warning: no element named {sprite_data['type']}: {sprite_data}")
                continue
            sprite_class = classes[sprite_data["type"]]
            if not issubclass(sprite_class, LevelElement):
                print(f"Warning: unsupported kind name {sprite_data['type']}: {sprite_data}")
                continue
            p = sprite_data,
            sprite_class(*p)

        self.players = [Player(level_data.players[str(i + 1)], i + 1) for i in range(public.players_count)]
        if LEVEL_EDIT:
            public.move_target = self.elements[0]

    def unload_level(self):
        if public.move_target in self.elements:
            public.move_target = None
        for sprite in self.bombs + self.elements + self.players:
            sprite.kill()
        self.elements.clear()
        self.players.clear()

    def save_level(self):
        log_func("Save Level", self.level_index)
        level_data = self.level_datas[self.level_index]
        content = json.dumps(level_data.save(self.elements), indent=4)
        with open(f"assets/data/levels/{level_data.file_name}", "w+") as f:
            f.write(content)

    @property
    def name(self):
        return self.level_datas[self.level_index].name
