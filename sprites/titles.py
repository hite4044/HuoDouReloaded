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
        self.render.add_grow(RenderGrowArgs(width=2.3, blur=2))
        self.render.add_shadow(RenderShadowArgs(blur=2, offset=7))
        self.finish_render()

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_START


class PlayersChooseTitle(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, (850, 200))
        self.show = False
        self.set_align(Align.CENTER)
        self.render.add_text(RenderTextArgs(generate_space("选择人数", 48), 90))
        self.render.add_grow(RenderGrowArgs(width=2.1, blur=2))
        self.render.add_shadow(RenderShadowArgs(blur=2, offset=7))
        self.finish_render()

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
                 end_msg: int = LEVEL_END_WIN, cover_offset: tuple[int, int] = (0, 0), cover: str = None,
                 line1_loc: tuple[int, int] = (0, 0),
                 line2_loc: tuple[int, int] = (0, 0)):
        super().__init__((0, 0), (300, 180))
        self.change_layer(LAYER_END_UI)
        self.set_align(Align.TOPLEFT)
        self.show = False
        self.need_follow = False
        self.end_msg = end_msg
        self.cover_offset = cover_offset
        self.cover_str = cover
        self.cover = None

        line1, line2 = text.split("\n")
        self.render.add_text(RenderTextArgs(line1, font_size, color=fill_color, loc = line1_loc))
        self.render.add_text(RenderTextArgs(line2, font_size, color=fill_color, loc = line2_loc))
        self.render.add_grow(RenderGrowArgs(width=2, blur=2, color=outline_color))
        self.render.add_shadow(RenderShadowArgs(offset=7, blur=2))
        self.finish_render()

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if data != TAKE_PLAY:
                self.show = False
        elif event == EVENT_LEVEL_RESET:
            self.show = self.need_follow = False
        elif event == EVENT_LEVEL_END:
            if data == self.end_msg:
                self.cover = eval(self.cover_str, {"sm": public.sm})
                self.show = self.need_follow = True
        elif event == EVENT_COVER_FINISH:
            if data == self.end_msg:
                self.need_follow = False
        elif event == EVENT_COVER_EXIT:
            if data == self.end_msg:
                public.sm.win_cover.statics.append(self)
                self.show = False

    def update(self):
        if self.need_follow:
            self.loc: tuple[int, int] = self.cover.loc + Vector2(self.cover_offset)
            self.transform_location()
            self.rect.topleft = self.transformed_loc
        super().update()


class WinCoverTitle(CoverTitle):
    def __init__(self):
        super().__init__("恭喜你\n过关了！", 67,
                         end_msg=LEVEL_END_WIN, cover_offset=(393, 136), cover="sm.win_cover",
                         line1_loc=(18, 21),
                         line2_loc=(12, 100))


class LoseCoverTitle(CoverTitle):
    def __init__(self):#  
        super().__init__("真遗憾\n失败了！", 67, "#B5FEFF", "#0033FF",
                         end_msg=LEVEL_END_LOSE, cover_offset=(393, 136), cover="sm.lose_cover",
                         line1_loc=(28, 25),
                         line2_loc=(12, 104))
