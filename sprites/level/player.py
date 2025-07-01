from time import perf_counter

import pygame as pg
from PIL import Image

from engine import resource as rs
from engine.asset_parser import image2surface, surface2image
from engine.sound import play_sound
from lib.config import gm_config
from lib.define import *
from lib.public_data import public
from sprites.base.animation_sprite import AnimationSprite
from sprites.base.base_sprite import Align
from sprites.level.elements.level_element import Bomb


class Player(AnimationSprite):
    def __init__(self, loc, player_id: int):
        self.saved_rect = None
        rs_map = {
            1: rs.sprites.player1,
            2: rs.sprites.player2,
            3: rs.sprites.player3,
        }
        keys_map = {
            1: (pg.K_w, pg.K_a, pg.K_d),
            2: (pg.K_UP, pg.K_LEFT, pg.K_RIGHT),
            3: (pg.K_i, pg.K_j, pg.K_l),
        }
        self.translate_lock = False
        self.layer_def = LAYER_PLAY
        super().__init__(tuple(loc))
        self.set_align(Align.CENTER)
        rs_player = rs_map[player_id]
        self.box = rs_player.box
        self.add_animation(rs_player.stand, "stand", 12)
        self.add_animation(rs_player.run, "run", 24)
        self.add_animation(rs_player.die, "die", 20)
        self.add_animation(rs_player.jump, "jump", 24)

        self.Vy = 0
        self.x = self.loc.x
        self.y = self.loc.y
        self.k_jump, self.k_left, self.k_right = keys_map[player_id]
        self.jump_lock = False
        self.next_jump = False
        self.enable = True
        self.dir = "right"
        self.self_group = pg.sprite.Group()
        # noinspection PyTypeChecker
        self.self_group.add(self)
        self.last_pos_calc = self.last_pos_update = perf_counter()
        self.calc_frame_time = 1 / 60
        self.show_frame_time = 1 / 28 if gm_config.sim_player_fps else 1 / 60
        self.play_animation("stand")

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_ENTER:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False
            if data != LEVEL_END_LOSE:
                self.play_animation("stand")

    # noinspection PyTypeChecker
    def add_animation(self, resources, name: str, speed: int = 10):
        right_frames = []
        left_frames = []
        for i in range(len(resources.frames)):
            image = surface2image(resources.frames[i])
            image = image.resize((int(image.width * 1.18), int(image.height // 1.3)))
            right_frames.append(image2surface(image))
            left_frames.append(image2surface(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)))
        super().add_animation(right_frames, name + "_right", speed)
        super().add_animation(left_frames, name + "_left", speed)

    def play_animation(self, name: str, end_stop: bool = False):
        super().play_animation(name + "_" + self.dir, end_stop)

    def move(self, x: float = 0, y: float = 0):
        self.x += x
        self.y -= y

        self.loc.x = int(self.x)
        self.loc.y = int(self.y)
        self.transform_location()
        self.rect.topleft = self.transformed_loc

    @property
    def collide(self):
        return pg.sprite.groupcollide(public.level_manager.floor, self.self_group, False, False) or \
            pg.sprite.groupcollide(public.level_manager.edges, self.self_group, False, False)

    def update(self):
        if perf_counter() - self.last_pos_calc > self.calc_frame_time and self.enable:
            delta = self.calc_frame_time
            last_loc = self.loc.copy
            self.saved_rect = self.rect.copy()
            self.rect = self.box.get_rect()
            self.rect.center = self.loc.tuple

            self.move(y=self.Vy)

            off_G = round(G * delta, 2)
            self.Vy -= off_G
            if self.Vy + off_G != 0:
                if self.Vy + off_G > 0:
                    if self.collide:
                        while self.collide:
                            self.move(y=-off_G)
                        self.Vy = 0
                if self.Vy + off_G < 0:
                    if self.collide:
                        while self.collide:
                            self.move(y=off_G)
                        self.jump_lock = False
                        self.Vy = 0
                    else:
                        self.jump_lock = True

            key_map = pg.key.get_pressed()
            # 跳跃逻辑
            if self.jump_lock:
                self.play_animation("jump")
            if key_map[self.k_jump]:
                if not self.jump_lock and self.next_jump:
                    play_sound(rs.sound.jump)
                    self.Vy = 9
                    self.jump_lock = True
                    self.next_jump = False
            else:
                self.next_jump = True

            # 移动逻辑
            if key_map[self.k_left]:
                self.dir = "left"
                self.move(x=-PLAYER_MOVE_SPEED)
                while self.collide:
                    self.move(x=1)
                if not self.jump_lock:
                    self.play_animation("run")
            elif key_map[self.k_right]:
                self.dir = "right"
                self.move(x=PLAYER_MOVE_SPEED)
                while self.collide:
                    self.move(x=-1)
                if not self.jump_lock:
                    self.play_animation("run")
            elif not self.jump_lock:
                self.play_animation("stand")

            # 吃金豆判断
            beans = pg.sprite.groupcollide(public.sm.level_manager.beans, self.self_group, False, False)
            for bean in beans:
                bean.eat()

            # 死亡逻辑
            kills = pg.sprite.groupcollide(public.sm.level_manager.kills, self.self_group, False, False)
            if kills:
                for sprite in kills:
                    if isinstance(sprite, Bomb):
                        sprite.boom_plus_kill()
                self.play_animation("die", end_stop=True)
                self.set_align(Align.TOPLEFT)
                self.enable = False
                play_sound(rs.sound.die)
                public.level_manager.left_players -= 1
                if public.level_manager.left_players <= 0:
                    public.send_event(EVENT_LEVEL_END, LEVEL_END_LOSE)

            self.last_pos_calc = perf_counter()
            self.rect = self.saved_rect.copy()
            if perf_counter() - self.last_pos_update > self.show_frame_time:
                self.last_pos_update = perf_counter()
            else:
                self.loc = last_loc.copy
            self.transform_location()
        super().update()
