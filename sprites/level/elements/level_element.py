from time import perf_counter
from typing import Any

import pygame as pg

import engine.resource as rs
from engine.sound import play_sound
from lib.config import gm_config
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import BaseSprite, Vector2, Align
from sprites.base.frame_sprite import FrameSprite


class LevelElement(BaseSprite):
    def __init__(self, image, data: dict[str, Any]):
        self.layer_def = LAYER_PLAY
        super().__init__(image, data["loc"])
        public.level_manager.elements.append(self)
        self.sprite_data: dict[str, Any] = {}

        self.wait_action = False
        self.drag_lock = False
        self.drag_offset = (0, 0)
        self.last_click = perf_counter()

    @classmethod
    def load(cls, data: dict[str, Any]):
        p = data,
        return cls(*p)

    def save(self) -> dict:
        return {"type": self.__class__.__name__, "loc": self.loc.list}

    def kill(self):
        public.level_manager.elements.remove(self)
        super().kill()

    def on_change_state(self):
        pass

    def update(self):
        if self.show:
            if self.wait_action:
                if perf_counter() - self.last_click > 0.1:
                    if pg.mouse.get_pressed(3)[0]:
                        self.drag_lock = True
                    self.wait_action = False

            if pg.mouse.get_pressed(3)[0] and public.move_target in public.sm.level_manager.elements:
                assert isinstance(public.move_target, LevelElement)
                if self.rect.collidepoint(pg.mouse.get_pos()) and \
                        (not public.move_target.wait_action) and \
                        (not public.move_target.drag_lock):
                    self.wait_action = True
                    public.move_target = self
                    self.last_click = perf_counter()

                    x, y = pg.mouse.get_pos()
                    wx, wy = self.rect.topleft
                    self.drag_offset = (wx - x, wy - y)
            elif pg.mouse.get_pressed(3)[2]:
                if self.rect.collidepoint(pg.mouse.get_pos()):
                    self.on_change_state()
            elif self.drag_lock:
                self.drag_lock = False

            if self.drag_lock:
                mouse_loc = pg.mouse.get_pos()
                mouse_loc = (mouse_loc[0] + self.drag_offset[0], mouse_loc[1] + self.drag_offset[1])
                self.rect.topleft = mouse_loc
                self.loc = Vector2(mouse_loc)
                self.transform_location()
        super().update()


class Ground(LevelElement):
    def __init__(self, data: dict[str, Any]):
        self.IMAGE_MAP = {
            0: rs.sprites.ground.normal,
            1: rs.sprites.ground.v_normal,
            2: rs.sprites.ground.long,
        }
        super().__init__(self.IMAGE_MAP[data["state"]], data)
        public.level_manager.floor.add(self)
        self.state: int = data["state"]

    def save(self) -> dict:
        data = super().save()
        data["state"] = self.state
        return data


class Burr(LevelElement):
    def __init__(self, data: dict[str, Any]):
        self.IMAGE_MAP = {
            0: rs.sprites.burr.normal,
            1: rs.sprites.burr.reverse,
        }
        super().__init__(self.IMAGE_MAP[data["state"]], data)
        public.level_manager.kills.add(self)
        self.state: int = data["state"]

    def save(self) -> dict:
        data = super().save()
        data["state"] = self.state
        return data

    def kill(self):
        public.level_manager.kills.remove(self)
        super().kill()


class GoldenBean(LevelElement):
    def __init__(self, data: dict[str, Any]):
        super().__init__(rs.sprites.golden_bean.normal, data)
        public.level_manager.beans.add(self)

    def eat(self):
        BeanEatAnimation(self.loc)
        self.kill()

    def kill(self):
        public.level_manager.beans.remove(self)
        super().kill()


class Gun(LevelElement):
    def __init__(self, data: dict[str, Any]):
        self.IMAGE_MAP = {
            0: rs.sprites.gun.right,
            1: rs.sprites.gun.left
        }
        super().__init__(self.IMAGE_MAP[data["state"]], data)
        self.state: int = data["state"]
        self.inv: float = data["inv"]
        self.use_new_speed: bool = data.get("use_new_speed", False)
        self.speed: float = data["speed"] if self.use_new_speed else data["speed"] * 40  # pixel/s
        self.last_shoot: float = perf_counter()
        self.enable = True

    def save(self) -> dict:
        data = super().save()
        data["state"] = self.state
        data["inv"] = self.inv
        if self.use_new_speed:
            data["speed"] = self.speed
            data["use_new_speed"] = True
        else:
            data["speed"] = self.sprite_data["speed"]
        return data

    def update(self):
        if perf_counter() - self.last_shoot > self.inv and self.enable:
            self.shoot()
            self.last_shoot = perf_counter()
        super().update()

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            self.enable = False
        super().event_parse(event, data)

    def shoot(self):
        self.rect.topleft = self.loc.tuple
        if self.state:  # 向左
            bomb_loc = self.rect.topleft
            bomb_loc = (bomb_loc[0] - 42, bomb_loc[1] - 11)
        else:  # 向右
            bomb_loc = self.rect.topright
            bomb_loc = (bomb_loc[0] + 27, bomb_loc[1] - 11)
        Bomb(bomb_loc, self.speed if self.state == 0 else -self.speed)


class Bomb(BaseSprite):
    # 5 dis/s (swf speed) - 270 pixel/s
    def __init__(self, loc: tuple[int, int], speed: float):
        self.layer_def = LAYER_PLAY
        super().__init__(rs.sprites.bombs.normal, loc)
        public.level_manager.bombs.append(self)
        public.level_manager.kills.add(self)
        self.last_update = perf_counter()
        self.speed = speed
        self.enable = True
        self.x: float = self.loc.x
        self.frame_time = 1 / 24 if gm_config.sim_bomb_fps else 1 / 40

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            self.enable = False
        super().event_parse(event, data)

    @property
    def touch_border(self) -> bool:
        return any(
            [
                self.loc.x > 1550,
                self.loc.x < -500
            ]
        )

    def update(self):
        if perf_counter() - self.last_update > self.frame_time and self.enable:
            self.last_update = perf_counter()
            self.x += self.speed * self.frame_time
            self.loc.x = int(self.x)
            self.transform_location()
            self.rect.topleft = self.transformed_loc
            if self.touch_border:
                self.kill()
        super().update()

    def boom_plus_kill(self):
        BombBoomAnimation(self.rect.topleft)
        self.kill()

    def kill(self):
        public.level_manager.bombs.remove(self)
        public.level_manager.kills.remove(self)
        super().kill()


class XKill(LevelElement):
    def __init__(self, sprite_data: dict):
        super().__init__(rs.sprites.x_kill.frames[0], sprite_data)
        public.level_manager.kills.add(self)
        self.set_align(Align.CENTER)
        self.start = min(sprite_data["start"], sprite_data["stop"])
        self.stop = max(sprite_data["start"], sprite_data["stop"])
        self.speed = sprite_data["speed"]
        self.dir = sprite_data["dir"]
        self.last_update = perf_counter()
        self.frame_time = 1 / 26
        self.frame_index = 0
        self.frames = rs.sprites.x_kill.frames

    def save(self) -> dict:
        data = super().save()
        data["loc"] = self.sprite_data["loc"]
        data["start"] = self.start
        data["stop"] = self.stop
        data["speed"] = self.speed
        data["dir"] = self.dir
        return data

    def update(self):
        if perf_counter() - self.last_update > self.frame_time:
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.update_image(self.frames[self.frame_index])

            if not self.dir:
                if self.loc.x + self.speed > self.stop:
                    self.loc.x = self.stop
                    self.dir = 1
                else:
                    self.loc.x += self.speed

            else:
                if self.loc.x - self.speed < self.start:
                    self.loc.x = self.start
                    self.dir = 0
                else:
                    self.loc.x -= self.speed

            self.transform_location()
            self.frame_index += 1
            self.last_update = perf_counter()
        super().update()


class BeanEatAnimation(FrameSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_END_UI
        super().__init__(loc)
        self.frame_time = 1 / 20
        self.start_loc = tuple(self.loc)
        self.stop_loc = tuple(public.sm.bean_show.loc)
        self.last_frame = perf_counter()
        self.now_frame_index = -1
        play_sound(rs.sound.eat)

        for frame in rs.sprites.golden_bean.eat_animation:
            self.add_frame(frame)

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_RESET:
            self.kill()

    def get_move_animation_loc(self, percent: float):
        delta_x = int((self.stop_loc[0] - self.start_loc[0]) * percent)
        delta_y = int((self.stop_loc[1] - self.start_loc[1]) * percent)
        return Vector2(self.loc.x + delta_x, self.loc.y + delta_y)

    def update(self):
        if perf_counter() - self.last_frame > self.frame_time:
            self.loc = self.get_move_animation_loc(self.now_frame_index / len(self.frames))
            self.transform_location()
            try:
                self.switch_frame(self.now_frame_index + 1)
            except IndexError:
                public.level_manager.golden_bean += 1
                if public.level_manager.golden_bean >= public.level_manager.golden_bean_all:
                    public.send_event(EVENT_LEVEL_END, LEVEL_END_WIN)
                self.kill()
                return
            self.last_frame = perf_counter()
        super().update()


class BombBoomAnimation(FrameSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_PLAY
        new_loc = list(loc)
        new_loc[0] -= 210
        new_loc[1] -= 380
        super().__init__(new_loc)
        self.frame_time = 1 / 15
        self.now_index = 0
        self.last_update = perf_counter()
        for frame in rs.sprites.bomb_kill.frames:
            self.add_frame(frame)

    def update(self):
        if perf_counter() - self.last_update > self.frame_time:
            self.now_index += 1
            try:
                self.switch_frame(self.now_index)
            except IndexError:
                self.kill()
                return
            self.last_update = perf_counter()
        super().update()
