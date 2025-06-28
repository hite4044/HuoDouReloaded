import pygame as pg

import engine.resource as rs
from engine.sound import play_sound
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import Vector2
from sprites.base.button import Button, CoverButton
from sprites.base.frame_sprite import FrameSprite


class StartButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.start_game.up)
        self.add_frame(rs.buttons.start_game.down)

    def on_up(self):
        public.sm.transition.run_transition(TAKE_PLAYERS_CHOOSE)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_START


class MoreGameButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.more_game.up)
        self.add_frame(rs.buttons.more_game.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", Vector2(521, 379)),
            LEVEL_END_LOSE: ("sm.lose_cover", Vector2(521, 379)),
        }
        self.event_parse(EVENT_TAKE_CHANGE, TAKE_START)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.change_layer(LAYER_UI)
            self.active_cover = None
            self.show = True
            if data == TAKE_START:
                self.loc = Vector2(545, 450)
            elif data == TAKE_LEVEL_CHOOSE:
                self.loc = Vector2(516, 698)
            else:
                self.show = False
            self.transform_location()
            return
        super().event_parse(event, data)


class MusicButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.music.up)
        self.add_frame(rs.buttons.music.down)
        self.add_frame(rs.buttons.music.A_up)
        self.add_frame(rs.buttons.music.A_down)
        self.music_opened = public.play_sound
        self.switch_lock = False
        self.is_clicking = False
        play_sound(rs.sound.music, -1)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.enable = True
            if data == TAKE_START:
                self.loc = Vector2(50, 56)
            elif data == TAKE_PLAYERS_CHOOSE:
                self.loc = Vector2(954, 100)
            elif data == TAKE_LEVEL_CHOOSE:
                self.loc = Vector2(984, 58)
            elif data == TAKE_PLAY:
                self.loc = Vector2(833, 46)
            else:
                return
            self.transform_location()
            self.rect.topleft = self.transformed_loc
        elif event in [EVENT_LEVEL_ENTER, EVENT_LEVEL_RESET, EVENT_LEVEL_NEXT]:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    @staticmethod
    def music_pause():
        public.play_sound = False
        # rs.sound.music.set_volume(0)

    @staticmethod
    def music_resume():
        public.play_sound = True
        # rs.sound.music.set_volume(100)

    @staticmethod
    def get_index(active: bool, down: bool):
        if active:
            return 1 if down else 0
        else:
            return 3 if down else 2

    def update(self):
        if self.enable:
            clicking = pg.mouse.get_pressed(3)[0]
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if clicking:
                    if not self.switch_lock:
                        self.switch_lock = True
                    self.switch_frame(self.get_index(not self.music_opened, False))
                elif self.switch_lock:
                    self.music_pause() if self.music_opened else self.music_resume()
                    self.music_opened = not self.music_opened
                    self.switch_lock = False
                    self.switch_frame(self.get_index(self.music_opened, False))
                else:
                    self.switch_frame(self.get_index(self.music_opened, True))
            elif self.switch_lock:
                if clicking:
                    self.switch_frame(self.get_index(self.music_opened, True))
                else:
                    self.switch_lock = False
                    self.switch_frame(self.get_index(self.music_opened, False))
            else:
                self.switch_frame(self.get_index(self.music_opened, False))
        else:
            self.switch_frame(self.get_index(self.music_opened, False))
        super(FrameSprite, self).update()


class PlayerCntChooseBtn(Button):
    def __init__(self, loc, num: int):
        super().__init__(loc)
        frame_map = {
            1: rs.buttons.players1,
            2: rs.buttons.players2,
            3: rs.buttons.players3,
        }
        self.add_frame(frame_map[num].up)
        self.add_frame(frame_map[num].down)
        self.show = False
        self.num = num

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_up(self):
        public.send_event(EVENT_PLAYERS_COUNT_CHANGE, self.num)
        public.players_count = self.num


class Players1Button(PlayerCntChooseBtn):
    def __init__(self, loc):
        super().__init__(loc, 1)


class Players2Button(PlayerCntChooseBtn):
    def __init__(self, loc):
        super().__init__(loc, 2)


class Players3Button(PlayerCntChooseBtn):
    def __init__(self, loc):
        super().__init__(loc, 3)


class PlayersOKButton(Button):
    def __init__(self, loc):
        super().__init__(loc, False)
        self.add_frame(rs.buttons.player_ok.up)
        self.add_frame(rs.buttons.player_ok.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_up(self):
        public.run_transition(TAKE_LEVEL_CHOOSE)


class ReturnChooseButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.return_choose.up)
        self.add_frame(rs.buttons.return_choose.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", Vector2(425, 470)),
            LEVEL_END_LOSE: ("sm.lose_cover", Vector2(425, 470)),
        }

    def on_up(self):
        public.transition.run_transition(TAKE_LEVEL_CHOOSE, lambda: public.send_event(EVENT_LEVEL_EXIT, 0))
