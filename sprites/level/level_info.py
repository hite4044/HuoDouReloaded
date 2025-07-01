import engine.resource as rs
from engine.asset_parser import OldImageRender, image2surface
from lib.define import *
from lib.public_data import public
from sprites.base.base_sprite import BaseSprite
from sprites.base.text_sprite import OldTextSprite


class BrownPlayerPose(BaseSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(rs.sprites.brown_player.normal, loc)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE


class LevelLevelText(OldTextSprite):
    def __init__(self, loc):
        super().__init__(loc, "关卡 : ", 33.5, (150, 50), fill_color="#019901")
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY


class LevelLevelNumber(OldTextSprite):
    def __init__(self, loc):
        super().__init__(loc, "", 33, (150, 50), fill_color="#019901")
        self.show = False
        self.last_level = None

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY

    def update(self):
        if self.show:
            if self.last_level != public.level_manager.level_index:
                render = OldImageRender((150, 50))
                render.add_text(str(public.level_manager.level_index + 1), 33, (150, 50), text_color="#019901")
                self.update_image(image2surface(render.base))
                self.last_level = public.level_manager.level_index
        super().update()


class BeanCounter(OldTextSprite):
    def __init__(self, loc):
        super().__init__(loc, f"0    / 11",
                         30.5, (150, 50), fill_color="#019901")
        self.show = False
        self.last_beans = -2

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY

    def update(self):
        if self.show:
            if self.last_beans != public.level_manager.golden_bean:
                beans = public.level_manager.golden_bean
                self.last_beans = beans + 1 - 1
                render = OldImageRender((150, 50))
                render.add_text(f"{beans}{'' if beans > 9 else '  '} / {public.level_manager.golden_bean_all}",
                                30.5, (150, 50), text_color="#019901")
                self.update_image(image2surface(render.base))
        super().update()


class BeanShow(BaseSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(rs.sprites.golden_bean.counter, loc)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
