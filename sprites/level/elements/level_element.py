from time import perf_counter

import pygame as pg

import engine.resource as rs
from engine.sound import play_sound
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import BaseSprite, Vector2
from sprites.base.frame_sprite import FrameSprite


class LevelElement(BaseSprite):
    def __init__(self, image, sprite_data: dict):
        self.layer_def = LAYER_PLAY
        super().__init__(image, sprite_data["loc"])
        self.sprite_data = sprite_data
        self.wait_action = False
        self.drag_lock = False
        self.drag_offset = (0, 0)
        self.last_click = perf_counter()

    def get_sprite_data(self):
        self.sprite_data["loc"] = self.loc
        return self.sprite_data

    def kill(self):
        public.sm.level_manager.elements.remove(self)
        super().kill()

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
                    move_target = self
                    self.last_click = perf_counter()

                    x, y = pg.mouse.get_pos()
                    wx, wy = self.rect.topleft
                    self.drag_offset = (wx - x, wy - y)
            elif pg.mouse.get_pressed(3)[2]:
                if self.rect.collidepoint(pg.mouse.get_pos()):
                    if "state" in self.sprite_data:
                        self.sprite_data["state"] = 0 if self.sprite_data["state"] else 1
            elif self.drag_lock:
                self.drag_lock = False

            if self.drag_lock:
                mouse_loc = pg.mouse.get_pos()
                mouse_loc = (mouse_loc[0] + self.drag_offset[0], mouse_loc[1] + self.drag_offset[1])
                self.rect.topleft = mouse_loc
                self.loc = mouse_loc
        super().update()


class Ground(LevelElement):
    def __init__(self, sprite_data: dict):
        if sprite_data["state"]:
            super().__init__(rs.sprites.ground.v_normal, sprite_data)
        else:
            super().__init__(rs.sprites.ground.normal, sprite_data)


class Burr(LevelElement):
    def __init__(self, sprite_data: dict):
        if sprite_data["state"] == 0:
            super().__init__(rs.sprites.burr.normal, sprite_data)
        else:
            super().__init__(rs.sprites.burr.reverse, sprite_data)


class GoldenBean(LevelElement):
    def __init__(self, sprite_data: dict):
        super().__init__(rs.sprites.golden_bean.normal, sprite_data)

    def eat(self):
        BeanEatAnimation(self.loc)
        self.kill()

    # noinspection PyTypeChecker
    def kill(self):
        public.level_manager.beans.remove(self)
        super().kill()


class Gun(LevelElement):
    def __init__(self, sprite_data: dict):
        if sprite_data["state"]:
            super().__init__(rs.sprites.gun.left, sprite_data)
        else:
            super().__init__(rs.sprites.gun.right, sprite_data)
        self.state: int = sprite_data["state"]
        self.inv: float = sprite_data["inv"]
        self.speed: float = sprite_data["speed"]
        self.last_shoot: float = perf_counter()
        self.enable = True

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
        if self.state:
            new_loc = self.rect.topleft
        else:
            new_loc = self.rect.topright
        new_loc = (new_loc[0] - 42, new_loc[1] - 11)
        bombs = Bombs(new_loc, int(self.speed))
        public.level_manager.others.append(bombs)
        # noinspection PyTypeChecker
        public.level_manager.kills.add(bombs)


class Bombs(BaseSprite):
    def __init__(self, loc: tuple[int, int], speed: float):
        self.layer_def = LAYER_PLAY
        super().__init__(rs.sprites.bombs.normal, loc)
        self.last_update = perf_counter()
        self.speed = speed
        self.enable = True
        self.x: float = loc[0]

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            self.enable = False
        super().event_parse(event, data)

    @property
    def collide(self) -> bool:
        return any(
            [
                self.rect.x > 1550,
                self.rect.x < -500
            ]
        )

    def update(self):
        if perf_counter() - self.last_update > 1 / 40 and self.enable:
            self.x += self.speed
            self.loc.x = int(self.x)
            self.transform_location()
            if self.collide:
                self.kill()
            self.last_update = perf_counter()
        super().update()

    def killed(self):
        BombBoomAnimation(self.rect.topleft)
        self.kill()

    def kill(self):
        public.level_manager.others.remove(self)
        super().kill()


class XKill(LevelElement):
    def __init__(self, sprite_data: dict):
        super().__init__(rs.sprites.x_kill.frames[0], sprite_data)
        self.rect.center = self.loc
        self.start = min(sprite_data["start"], sprite_data["stop"])
        self.stop = max(sprite_data["start"], sprite_data["stop"])
        self.speed = sprite_data["speed"]
        self.dir = sprite_data["dir"]
        self.last_update = perf_counter()
        self.frame_time = 1 / 26
        self.frame_index = 0
        self.frames = rs.sprites.x_kill.frames

    def renew_loc(self, new_loc: list[int]):
        self.rect.center = tuple(new_loc)

    def update(self):
        if perf_counter() - self.last_update > self.frame_time:
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.update_image(self.frames[self.frame_index])

            new_loc = self.loc
            if not self.dir:
                if new_loc[0] + self.speed > self.stop:
                    new_loc = (self.stop, new_loc[1])
                    self.dir = 1
                else:
                    new_loc = (new_loc[0] + self.speed, new_loc[1])

            else:
                if new_loc[0] - self.speed < self.start:
                    new_loc = (self.start, new_loc[1])
                    self.dir = 0
                else:
                    new_loc = (new_loc[0] - self.speed, new_loc[1])
            self.loc = new_loc

            self.rect = self.image.get_rect()
            self.rect.center = self.loc
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
