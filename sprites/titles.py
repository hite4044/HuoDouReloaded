from lib.define import *
from lib.image_render import RenderTextArgs, RenderGrowArgs, RenderShadowArgs
from sprites.base.base_sprite import Align
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
        self.render.add_shadow(RenderShadowArgs(blur=2, offset=6))
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
