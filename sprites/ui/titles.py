from lib.define import *
from lib.image_render import RenderTextArgs, RenderGrowArgs, RenderShadowArgs
from lib.public_data import public
from sprites.base.base_sprite import Align, Vector2
from sprites.base.shadow import Shadow
from sprites.base.text_sprite import TextSprite, OldTextSprite


SPACE_MAP: dict[int, int] = {
    64: 0xE006,
    32: 0xE005,
    16: 0xE004,
    8: 0xE003,
    4: 0xE002,
    2: 0xE001,
    1: 0xE000,
}

def space(size: int) -> str:
    space_string = ""
    left = size
    for width, char_index in SPACE_MAP.items():
        if left >= width:
            space_string += chr(char_index)
            left -= width
            if left == 0:
                break
    return space_string


def generate_space(string: str, size: int):
    return space(size).join(list(string))

class GameTitle(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, (711, 137))
        self.set_align(Align.CENTER)
        self.render.add_text(RenderTextArgs(generate_space("火柴人吃豆豆2", 28), 98))
        self.render.add_grow(RenderGrowArgs(width=1.9, blur=2.5))
        self.render.add_shadow(RenderShadowArgs(blur=2, offset=7))
        self.finish_render()

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_START


class PlayersChooseTitle(OldTextSprite):
    def __init__(self, loc):
        super().__init__(loc, "选 择 人 数", 90, (850, 200), True, outline=True)
        self.set_align(Align.CENTER)
        self.shadow = Shadow(self, 9, 2.5)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE


class LevelChooseTitle(OldTextSprite):
    def __init__(self, loc):
        super().__init__(loc, "选 择 关 卡", 75, (350, 120), True, outline=True)
        self.set_align(Align.CENTER)
        self.shadow = Shadow(self, 9, 2.5)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE


class CoverTitle(TextSprite):
    def __init__(self, text: str, font_size: float,
                 fill_color: str = "#FFCB00", outline_color: str = "#990000",
                 end_msg: int = LEVEL_END_WIN, cover_offset: tuple[int, int] = (0, 0), cover: str = None):
        super().__init__((0, 0), (300, 180))
        self.change_layer(LAYER_END_UI)
        self.set_align(Align.TOPLEFT)
        self.show = False
        self.end_msg = end_msg
        self.cover_offset = cover_offset
        self.cover_str = cover
        self.cover = None

        self.render.add_text(RenderTextArgs(text, font_size, color=fill_color))
        self.render.add_grow(RenderGrowArgs(width=2, blur=2, color=outline_color))
        self.render.add_shadow(RenderShadowArgs(blur=2.5, offset=9))
        self.finish_render()

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if data != TAKE_PLAY:
                self.show = False
        elif event == EVENT_LEVEL_RESET:
            self.show = False
        elif event == EVENT_LEVEL_END:
            if data == self.end_msg:
                self.cover = eval(self.cover_str, {"sm": public.sm})
                self.show = True
        elif event == EVENT_COVER_RUN:
            if data == self.end_msg:
                public.sm.win_cover.statics.append(self)
                self.show = False

    def update(self):
        if self.show:
            self.loc: tuple[int, int] = self.cover.loc + Vector2(self.cover_offset)
            self.transform_location()
        super().update()


class WinCoverTitle(CoverTitle):
    def __init__(self):
        super().__init__(" 恭喜你\n过关了！", 67,
                         end_msg=LEVEL_END_WIN, cover_offset=(393, 137), cover="sm.win_cover")


class LoseCoverTitle(CoverTitle):
    def __init__(self):
        super().__init__(" 真遗憾\n失败了！", 67, "#B5FEFF", "#0033FF",
                         end_msg=LEVEL_END_LOSE, cover_offset=(393, 137), cover="sm.lose_cover")
