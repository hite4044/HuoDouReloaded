from os import getcwd, environ
from os.path import join
from time import perf_counter

environ["PATH"] += ";" + join(getcwd(), "base_library")
from sprites.base_sprite import BaseSprite


timers = [perf_counter()]
from copy import deepcopy
import resource as rs
from tools import *

timers.append(perf_counter())  # 库导入计时器
pg.init()
screen = pg.display.set_mode((1050, 750))


class VisualLogger(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = rs.empty
        self.last_render = perf_counter()
        self.texts = []
        self.text_images = []
        self.texts_counter = 0
        self.is_finish = False
        self.ft = ImageFont.load_default(16)

        self.start = perf_counter()
        self.last_times = json.load(open("assets/data/load_times.json"))
        self.times = []

    def log(self, *values: object):
        text = " ".join(map(str, values))
        print(text)
        if self.is_finish:
            return
        if LOADING_LOG:
            self.texts.append(text)
        if "Rendering" not in text:
            self.times.append(perf_counter())
            self.texts_counter += 1
        self.render_image()

    def render_image(self):
        if perf_counter() - self.last_render > 1 / LOADING_FPS:
            self.render_now()

    def render_text(self, *text: str):
        image = Image.new("RGB", (450, 20 * len(text)), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), "\n".join(text), font=self.ft)
        return image

    def render_now(self):
        self.text_images.append(self.render_text(*self.texts))
        self.texts.clear()

        image = Image.new("RGB", (1050, 750), (0, 0, 0))
        offset = 670
        for i in range(len(self.text_images)):
            text = self.text_images[0 - i]
            if offset < 0:
                del self.text_images[:0 - i]
                break
            image.paste(text, (0, offset - text.height))
            offset -= text.height

        draw = ImageDraw.Draw(image)
        try:
            draw.rectangle((0, 720, 1050 * self.last_times[self.texts_counter], 750), fill="white")
        except IndexError:
            draw.rectangle((0, 720, 1050, 750), fill="white")
        except ValueError:
            pass

        self.image = image2surface(image)
        self.update()
        self.last_render = perf_counter()

    def finish(self):
        times = [round((i - self.start) / (perf_counter() - self.start), 3) for i in self.times]
        json.dump(times, open("assets/data/load_times.json", "w+"))
        self.is_finish = True

    def update(self):
        pg.event.get()
        screen.fill((0, 0, 0))
        screen.blit(self.image, (0, 0))
        pg.display.update()


logger = VisualLogger()
players_count = 1
left_player = 1
level = "None"
sound = True
timers.append(perf_counter())  # 资源加载计时器
rs.load_resources(logger.log)
timers.append(perf_counter())  # 资源加载计时器
pg.display.set_caption("火柴人吃豆豆2")
pg.display.set_icon(rs.icon)
sprites = {}
for lay in LAYERS:
    sprites[lay] = []
layer_updates = []





class FrameSprite(BaseSprite):
    def __init__(self, loc):
        super().__init__(None, loc)
        self.frames: list[pg.surface.Surface] = []
        self.now_frame_index = None

    def add_frame(self, frame):
        self.frames.append(frame)
        if len(self.frames) == 1:
            self.switch_frame(0)
            self.first_frame()
        return len(self.frames) - 1

    def first_frame(self):
        pass

    def switch_frame(self, index: int):
        if index != self.now_frame_index:
            self.now_frame_index = index
            self.update_image(self.frames[index])


class Shadow(BaseSprite):
    # noinspection PyShadowingNames
    def __init__(self, sprite: BaseSprite, offset: int, radius: float = 3):
        self.parent = sprite
        self.offset = offset
        self.radius = radius
        self.layer_def = sprite.layer_ - 1
        super().__init__(self.make_cover(sprite.image, radius), self.pos().topleft)
        self.cbk = sprite.image_callback
        sprite.image_callback = self.image_update_callback
        self.image_callback(sprite.get_image())

    def image_update_callback(self, image: pg.surface.Surface):
        self.cbk(image)
        cover = self.make_cover(image, self.radius)
        self.update_image(cover)

    @staticmethod
    def make_cover(surface: pg.surface.Surface, radius: float):
        image = surface2image(surface)
        cover = get_image_cover(image)
        cover_new = Image.new("RGBA", [cover.width + 100, cover.height + 100], (0, 0, 0, 0))
        cover_new.paste(cover, (50, 50))
        blur_cover = cover_new.filter(ImageFilter.GaussianBlur(radius=radius))
        return pg.image.frombytes(blur_cover.tobytes(), blur_cover.size, "RGBA").convert_alpha()

    def update(self):
        self.rect = self.pos()
        self.show = self.parent.show
        super().update()

    def pos(self) -> pg.rect.Rect:
        new_rect: pg.rect.Rect = self.parent.rect.copy()
        new_rect = new_rect.move(-50, self.offset - 50)
        return new_rect


class LevelEnter(FrameSprite):
    def __init__(self, loc, _level: str, parent: BaseSprite = None):
        self.layer_def = LAYER_UI
        loc[0] += parent.loc[0]
        loc[1] += parent.loc[1]
        super().__init__(loc)
        self.level = _level
        self.add_frame(rs.sprites.level.lock)
        render = ImageRender((60, 70))
        render.add_text(str(_level), 50)
        render.add_shadow(8, [0.4, 2.5], False, 2)
        image = surface2image(rs.sprites.level.unlock)
        image.paste(render.base, (22, 28), mask=render.base.split()[3])
        self.add_frame(image2surface(image))

        self.show = False
        self.press_lock = False
        self.lock = _level != "1"

        if not self.lock:
            self.switch_frame(1)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE

    def set_lock(self, lock: bool):
        self.switch_frame(int(not lock))
        self.lock = lock

    def level_enter(self):
        sm.transition.run_transition(TAKE_PLAY, self.callback)

    def callback(self):
        sm.send_event(EVENT_LEVEL_ENTER, self.level)

    def update(self):
        if self.show:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if pg.mouse.get_pressed(3)[0]:
                    if not self.press_lock:
                        self.press_lock = True
                else:
                    if self.press_lock:
                        if not self.lock:
                            self.level_enter()
                    self.press_lock = False
            else:
                self.press_lock = False
        super().update()


class LevelsContainer(BaseSprite):
    def __init__(self, loc):
        super().__init__(loc=loc)
        self.show = False
        self.levels = []
        for y in range(4):
            for x in range(6):
                if y == 3:
                    _level = LevelEnter([x * 143 - 5, y * 136], str(6 * y + x + 1), self)
                else:
                    _level = LevelEnter([x * 143, y * 138], str(6 * y + x + 1), self)
                self.levels.append(_level)

    def unlock_level(self, level_name: str):
        for _level in self.levels:
            if _level.level == level_name:
                _level.set_lock(False)
                break

    def event_parse(self, event: int, data):
        for _level in self.levels:
            _level.event_parse(event, data)

    def update(self):
        for _level in self.levels:
            _level.update()
        super().update()


class BrownPlayerPose(BaseSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(rs.sprites.brown_player.normal, loc)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE


class Button(FrameSprite):
    def __init__(self, loc, shadow=True):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.rect.center = self.loc
        self.shadow = shadow
        self.press_lock = False
        self.enable = True

    def add_frame(self, frame):
        if self.shadow:
            render = ImageRender(frame.get_size(), frame)
            render.add_shadow(8, 2)
            frame = image2surface(render.base)
        super().add_frame(frame)

    def switch_frame(self, index: int):
        super().switch_frame(index)
        self.rect.center = self.loc

    def update(self):
        if self.show and self.enable:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if pg.mouse.get_pressed(3)[0]:
                    if not self.press_lock:
                        self.on_press()
                        self.press_lock = True
                    self.switch_frame(0)
                else:
                    if self.press_lock:
                        self.on_up()
                    self.press_lock = False
                    self.switch_frame(1)
            else:
                self.press_lock = False
                self.switch_frame(0)
        elif not self.enable:
            self.switch_frame(0)
        super().update()

    def on_press(self):
        pass

    def on_up(self):
        pass


class StartButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.start_game.up)
        self.add_frame(rs.buttons.start_game.down)

    def on_up(self):
        sm.transition.run_transition(TAKE_PLAYERS_CHOOSE)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_START


class MoreGameButton(Button):
    def __init__(self, loc):
        self.now_cover = None
        self.cover_offset = [0, 0]
        super().__init__(loc)
        self.add_frame(rs.buttons.more_game.up)
        self.add_frame(rs.buttons.more_game.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", [521, 379]),
            LEVEL_END_LOSE: ("sm.lose_cover", [521, 379]),
        }

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.change_layer(LAYER_UI)
            self.now_cover = None
            self.show = True
            if data == TAKE_START:
                self.loc = [546, 450]
            elif data == TAKE_LEVEL_CHOOSE:
                self.loc = [516, 698]
            else:
                self.show = False
        elif event == EVENT_LEVEL_RESET:
            self.show = False
            self.now_cover = None
        elif event == EVENT_LEVEL_END:
            self.change_layer(LAYER_END_UI)
            self.now_cover, self.cover_offset = self.cover_map[data]
            self.now_cover = eval(self.now_cover)

    def update(self):
        if self.now_cover:
            new_loc = list(self.now_cover.rect.topleft)
            new_loc[0] += self.cover_offset[0]
            new_loc[1] += self.cover_offset[1]
            self.loc = new_loc
            self.rect.center = tuple(self.loc)
            self.show = True
        super().update()


class CoverButton(Button):
    def __init__(self):
        super().__init__([0, 0])
        self.now_cover = None
        self.cover_offset = [0, 0]
        self.show = False
        self.cover_map = {}

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if event != TAKE_PLAY:
                self.show = False
                self.now_cover = None
        elif event == EVENT_LEVEL_END:
            print("Level was end, load cover")
            self.change_layer(LAYER_END_UI)
            self.now_cover, self.cover_offset = self.cover_map[data]
            self.now_cover = eval(self.now_cover)
        elif event == EVENT_LEVEL_RESET:
            print("Level Reset Del cover")
            self.show = False
            self.now_cover = None
        elif event == EVENT_COVER_RUN:
            if self.now_cover:
                self.show = False
                self.now_cover.statics.append(self)

    def update(self):
        if self.now_cover:
            new_loc = list(self.now_cover.rect.topleft)
            new_loc[0] += self.cover_offset[0]
            new_loc[1] += self.cover_offset[1]
            self.loc = new_loc
            self.rect.center = tuple(self.loc)
            self.show = True
        super().update()


class ReturnChooseButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.return_choose.up)
        self.add_frame(rs.buttons.return_choose.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", [425, 470]),
            LEVEL_END_LOSE: ("sm.lose_cover", [425, 470]),
        }

    def on_up(self):
        sm.transition.run_transition(TAKE_LEVEL_CHOOSE, lambda: sm.send_event(EVENT_LEVEL_EXIT, 0))


class NextLevelButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.next_level.up)
        self.add_frame(rs.buttons.next_level.down)
        self.cover_map = {
            LEVEL_END_WIN: ("sm.win_cover", [618, 467]),
        }

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            if data != LEVEL_END_WIN:
                return
        super().event_parse(event, data)

    def on_up(self):
        sm.send_event(EVENT_COVER_RUN, 0)


class RetryButton(CoverButton):
    def __init__(self):
        super().__init__()
        self.add_frame(rs.buttons.retry_level.up)
        self.add_frame(rs.buttons.retry_level.down)
        self.cover_map = {
            LEVEL_END_LOSE: ("sm.lose_cover", [618, 467]),
        }

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_END:
            if data != LEVEL_END_LOSE:
                return
        super().event_parse(event, data)

    @staticmethod
    def callback():
        sm.send_event(EVENT_LEVEL_RESET, 0)

    def on_up(self):
        sm.transition.run_transition(TAKE_EMPTY, self.callback, True)


class MusicButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.music.up)
        self.add_frame(rs.buttons.music.down)
        self.add_frame(rs.buttons.music.Aup)
        self.add_frame(rs.buttons.music.Adown)
        self.music_opened = True
        self.pause_lock = False
        self.on_play = False
        rs.sound.music.play(-1)
        if not sound:
            self.music_pause()

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.enable = True
            if data == TAKE_START:
                self.loc = [50, 56]
            elif data == TAKE_PLAYERS_CHOOSE:
                self.loc = [954, 100]
            elif data == TAKE_LEVEL_CHOOSE:
                self.loc = [984, 58]
            elif data == TAKE_PLAY:
                self.loc = [833, 46]
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    @staticmethod
    def music_pause():
        global sound
        sound = False
        rs.sound.music.set_volume(0)

    @staticmethod
    def music_resume():
        global sound
        sound = True
        rs.sound.music.set_volume(100)

    def update(self):
        if self.rect.collidepoint(pg.mouse.get_pos()) and self.enable:
            if pg.mouse.get_pressed(3)[0]:
                if not self.pause_lock:
                    self.music_opened = not self.music_opened
                    self.music_resume() if self.music_opened else self.music_pause()
                    self.pause_lock = True
                self.switch_frame(0 if self.music_opened else 2)
            else:
                self.pause_lock = False
                self.switch_frame(1 if self.music_opened else 3)
        else:
            self.switch_frame(0 if self.music_opened else 2)
        super(FrameSprite, self).update()


class ReturnButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.return_.up)
        self.add_frame(rs.buttons.return_.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE

    def on_up(self):
        sm.transition.run_transition(TAKE_START)


class Players1Button(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.players1.up)
        self.add_frame(rs.buttons.players1.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_press(self):
        global players_count
        sm.send_event(EVENT_PLAYERS_COUNT_CHANGE, 1)
        players_count = 1


class Players2Button(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.players2.up)
        self.add_frame(rs.buttons.players2.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_press(self):
        global players_count
        sm.send_event(EVENT_PLAYERS_COUNT_CHANGE, 2)
        players_count = 2


class Players3Button(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.players3.up)
        self.add_frame(rs.buttons.players3.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE

    def on_press(self):
        global players_count
        sm.send_event(EVENT_PLAYERS_COUNT_CHANGE, 3)
        players_count = 3


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
        sm.transition.transition_now(TAKE_LEVEL_CHOOSE)


class MoreGameLite(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.games.up)
        self.add_frame(rs.buttons.games.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False


class ResetButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.reset.up)
        self.add_frame(rs.buttons.reset.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    def on_up(self):
        sm.transition.run_transition(TAKE_PLAY, self.cbk)

    @staticmethod
    def cbk():
        sm.send_event(EVENT_LEVEL_RESET, 0)


class HomeButton(Button):
    def __init__(self, loc):
        super().__init__(loc)
        self.add_frame(rs.buttons.home.up)
        self.add_frame(rs.buttons.home.down)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY
        elif event == EVENT_LEVEL_ENTER or event == EVENT_LEVEL_RESET or event == EVENT_LEVEL_NEXT:
            self.enable = True
        elif event == EVENT_LEVEL_END:
            self.enable = False

    def on_up(self):
        sm.transition.run_transition(TAKE_LEVEL_CHOOSE, lambda: sm.send_event(EVENT_LEVEL_EXIT, 0))


class PlayersKeys(FrameSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.raw_loc = loc
        self.add_frame(rs.sprites.player_keys.p_1)
        self.add_frame(rs.sprites.player_keys.p_2)
        self.add_frame(rs.sprites.player_keys.p_3)
        self.show = False
        self.last_player_counter = 0

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE
        elif event == EVENT_PLAYERS_COUNT_CHANGE:
            self.update_count(data)

    def update_count(self, count: int):
        if count == 3:
            tmp = self.raw_loc.copy()
            tmp[1] -= 5
            self.loc = tmp
        else:
            self.loc = self.raw_loc
        self.switch_frame(count - 1)
        self.last_player_counter = count + 1 - 1

    def update(self):
        super().update()


class PlayersCH(FrameSprite):
    def __init__(self, loc, image: pg.surface.Surface, num: int):
        self.layer_def = LAYER_UI
        super().__init__(loc)
        self.add_frame(image)
        image_alpha = image.copy()
        image_alpha.set_alpha(128)
        self.add_frame(image_alpha)

        self.last_player_counter = 0
        self.show = False
        self.num = num
        self.update_count(players_count)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE
        elif event == EVENT_PLAYERS_COUNT_CHANGE:
            self.update_count(data)

    def update_count(self, count: int):
        if count >= self.num:
            self.switch_frame(0)
        else:
            self.switch_frame(1)


class TextSprite(BaseSprite):
    def __init__(self, loc, text: str, font_size: float,
                 image_size, outline_blur: bool = False, fill_color: str = "#FFCB00",
                 outline: bool = False, outline_color: str = "#990000",
                 shadow_offset: int = -1, shadow_radius: float = -1,
                 spacing: int = 4, cache: bool = True,
                 outline_width: float = 2, blur_radius: float = 2):
        render = ImageRender(image_size, use_cache=cache)
        render.add_text(text, font_size, image_size, text_color=fill_color,
                        outline=outline, outline_width=outline_width, outline_color=outline_color, faster_outline=True,
                        outline_blur=outline_blur, blur_radius=blur_radius, spacing=spacing)
        if shadow_offset > 0 or shadow_radius > 0:
            render.add_shadow(shadow_offset, shadow_radius)
        self.layer_def = LAYER_UI
        super().__init__(image2surface(render.base), loc)

        ft = ImageFont.truetype("assets/方正胖娃简体.ttf", font_size)
        text_image = Image.new("RGBA", image_size, (255, 255, 255, 255))
        draw = ImageDraw.Draw(text_image)
        x, y = (text_image.width // 2, text_image.height // 2)
        draw.text((x, y), text, font=ft, fill="#FFCB00", anchor="mm", spacing=6)
        self.text_image = image2surface(text_image)

    def get_image(self):
        return self.text_image


class GameTitle(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, "火柴人吃豆豆2", 95, (850, 200),
                         outline=True, outline_blur=True, outline_width=2.5, blur_radius=2.2)
        self.shadow = Shadow(self, 9, 2)
        self.rect.center = self.loc

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_START


class PlayersChooseTitle(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, "选 择 人 数", 90, (850, 200), True, outline=True)
        self.shadow = Shadow(self, 9, 2.5)
        self.rect.center = self.loc
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAYERS_CHOOSE


class LevelChooseTitle(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, "选 择 关 卡", 75, (350, 120), True, outline=True)
        self.shadow = Shadow(self, 9, 2.5)
        self.rect.center = self.loc
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_LEVEL_CHOOSE


class CoverTitle(TextSprite):
    def __init__(self, text: str, font_size: float,
                 fill_color: str = "#FFCB00", outline_color: str = "#990000",
                 spacing: int = 20,
                 end_msg: int = LEVEL_END_WIN, cover_offset: tuple[int, int] = [0, 0], cover: str = None):
        super().__init__([0, 0], text, font_size, (300, 180), True,
                         fill_color=fill_color,
                         outline=True, outline_color=outline_color,
                         spacing=spacing)
        self.change_layer(LAYER_END_UI)
        self.shadow = Shadow(self, 9, 2.5)
        self.rect.center = self.loc
        self.show = False
        self.end_msg = end_msg
        self.start_offset = False
        self.cover_offset = cover_offset
        self.cover_str = cover
        self.cover = None

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if data != TAKE_PLAY:
                self.show = False
                self.start_offset = False
        elif event == EVENT_LEVEL_RESET:
            self.show = False
            self.start_offset = False
        elif event == EVENT_LEVEL_END:
            if data == self.end_msg:
                self.cover = eval(self.cover_str)
                self.show = True
                self.start_offset = True
        elif event == EVENT_COVER_RUN:
            if data == self.end_msg:
                sm.win_cover.statics.append(self)
                self.show = False
                self.start_offset = False

    def update(self):
        if self.start_offset:
            new_loc = list(self.cover.rect.topleft)
            new_loc[0] += self.cover_offset[0]
            new_loc[1] += self.cover_offset[1]
            self.loc = new_loc
            self.rect.topleft = tuple(self.loc)
        super().update()


class WinCoverTitle(CoverTitle):
    def __init__(self):
        super().__init__(" 恭喜你\n过关了！", 67, spacing=20,
                         end_msg=LEVEL_END_WIN, cover_offset=(393, 137), cover="sm.win_cover")


class LoseCoverTitle(CoverTitle):
    def __init__(self):
        super().__init__(" 真遗憾\n失败了！", 67, "#B5FEFF", "#0033FF", 20,
                         end_msg=LEVEL_END_LOSE, cover_offset=(393, 137), cover="sm.lose_cover")


class LevelLevelText(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, "关卡 : ", 33.5, (150, 50), fill_color="#019901")
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY


class LevelLevelNumber(TextSprite):
    def __init__(self, loc):
        super().__init__(loc, level, 33, (150, 50), fill_color="#019901")
        self.show = False
        self.last_level = None

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY

    def update(self):
        if self.show:
            if self.last_level != level:
                render = ImageRender((150, 50))
                render.add_text(level, 33, (150, 50), text_color="#019901")
                self.image = image2surface(render.base)
                self.last_level = level[:]
        super().update()


class BeanCounter(TextSprite):
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
            if self.last_beans != sm.level_manager.golden_bean:
                beans = sm.level_manager.golden_bean
                self.last_beans = beans + 1 - 1
                render = ImageRender((150, 50))
                render.add_text(f"{beans}{'' if beans > 9 else '  '} / {sm.level_manager.golden_bean_all}",
                                30.5, (150, 50), text_color="#019901")
                self.image = image2surface(render.base)
        super().update()


class BeanShow(BaseSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_UI
        super().__init__(rs.sprites.golden_bean.counter, loc)
        self.show = False

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            self.show = data == TAKE_PLAY


class BackGround(FrameSprite):
    def __init__(self):
        self.layer_def = LAYER_BG
        super().__init__([-3, -2])
        self.add_frame(rs.bg.start)
        self.add_frame(rs.bg.choose)
        self.add_frame(rs.bg.play)

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if data == TAKE_START:
                self.switch_frame(0)
            elif data == TAKE_PLAYERS_CHOOSE:
                self.switch_frame(1)
            elif data == TAKE_PLAY:
                self.switch_frame(2)


class TransitionMask(FrameSprite):
    def __init__(self):
        self.layer_def = LAYER_COVER
        super().__init__([0, 0])
        self.show = False

        self.on_transition = False
        self.just_callback = False
        self.on_switch = lambda: None
        self.transition_take = None
        self.last_update = perf_counter()
        self.frame_index = 0
        self.frames_per = 32
        for i in range(1, 256, 15):
            image = Image.new("RGBA", (1050, 750), (0, 0, 0, i))
            self.add_frame(image2surface(image))

    def run_transition(self, take_id: int, callback=None, just_callback: bool = False):
        if not self.on_transition:
            self.show = True
            self.on_transition = True
            self.transition_take = take_id
            self.last_update = perf_counter()
            self.frame_index = 0
        if callback:
            self.just_callback = just_callback
            self.on_switch = callback
        else:
            self.on_switch = lambda: None

    @staticmethod
    def transition_now(take_id: int):
        sm.send_event(EVENT_TAKE_CHANGE, take_id)

    def update(self):
        if self.on_transition:
            if perf_counter() > self.last_update + 1 / self.frames_per - 0.003:
                if self.frame_index > 15:
                    if self.frame_index == 16:
                        if not self.just_callback:
                            self.transition_now(self.transition_take)
                        self.on_switch()
                    if self.frame_index > 30:
                        self.on_transition = False
                        self.show = False
                    self.switch_frame(31 - self.frame_index)
                else:
                    self.switch_frame(self.frame_index)
                self.frame_index += 1
                self.last_update = perf_counter()
        super().update()


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
        sm.level_manager.elements.remove(self)
        super().kill()

    def renew_loc(self, new_loc: list[int]):
        self.rect.topleft = tuple(new_loc)

    def update(self):
        if self.show:
            if self.wait_action:
                if perf_counter() - self.last_click > 0.1:
                    if pg.mouse.get_pressed(3)[0]:
                        self.drag_lock = True
                    self.wait_action = False

            global move_target
            if pg.mouse.get_pressed(3)[0] and move_target in sm.level_manager.elements:
                if self.rect.collidepoint(pg.mouse.get_pos()) and \
                        (not move_target.wait_action) and \
                        (not move_target.drag_lock):
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
                new_loc = list(pg.mouse.get_pos())
                new_loc[0] += self.drag_offset[0]
                new_loc[1] += self.drag_offset[1]
                self.renew_loc(new_loc)
                self.loc = new_loc
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
        sm.level_manager.beans.remove(self)
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
            new_loc = list(self.rect.topleft)
            new_loc[0] -= 42
            new_loc[1] -= 11
            speed = -self.speed + 1 - 1
        else:
            new_loc = list(self.rect.topright)
            new_loc[0] -= 42
            new_loc[1] -= 11
            speed = self.speed + 1 - 1
        bombs = Bombs(new_loc, speed)
        sm.level_manager.temps.append(bombs)
        # noinspection PyTypeChecker
        sm.level_manager.kills.add(bombs)


class Bombs(BaseSprite):
    def __init__(self, loc, speed: float):
        self.layer_def = LAYER_PLAY
        super().__init__(rs.sprites.bombs.normal, loc)
        self.last_update = perf_counter()
        self.self_group = pg.sprite.Group()
        self.speed = speed
        self.enable = True
        self.x = loc[0] + 1 - 1
        # noinspection PyTypeChecker
        self.self_group.add(self)

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
            self.loc[0] = int(self.x)
            self.rect.topleft = tuple(self.loc)
            if self.collide:
                self.kill()
            self.last_update = perf_counter()
        super().update()

    def killed(self):
        BombBoomAnimation(self.rect.topleft)
        self.kill()

    def kill(self):
        sm.level_manager.temps.remove(self)
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
            self.image = self.frames[self.frame_index]

            new_loc = self.loc[:]
            if not self.dir:
                new_loc[0] += self.speed
                if new_loc[0] > self.stop:
                    new_loc[0] = self.stop + 1 - 1
                    self.dir = 1
            else:
                new_loc[0] -= self.speed
                if new_loc[0] < self.start:
                    new_loc[0] = self.start + 1 - 1
                    self.dir = 0
            self.loc = new_loc

            self.rect = self.image.get_rect()
            self.rect.center = self.loc
            self.frame_index += 1
            self.last_update = perf_counter()
        super().update()


class BeanEatAnimation(FrameSprite):
    def __init__(self, loc):
        self.layer_def = LAYER_PLAY
        super().__init__(loc)
        self.frame_time = 1 / 20
        self.start_loc = self.loc[:]
        self.stop_loc = sm.bean_show.loc[:]
        self.last_frame = perf_counter()
        self.now_frame_index = -1
        if sound:
            rs.sound.eat.play()
        image = surface2image(rs.sprites.golden_bean.normal)
        size_list = list(range(10, 1, -1)) + [1, 1, 1]
        for size in size_list:
            frame = image.resize(tuple(map(lambda x: int(x * size / len(size_list)), image.size)))
            self.add_frame(image2surface(frame))

    def event_parse(self, event: int, data):
        if event == EVENT_LEVEL_RESET:
            self.kill()

    def get_inside_loc(self, percent: float):
        new_loc = self.start_loc[:]
        new_loc[0] += int((self.stop_loc[0] - self.start_loc[0]) * percent)
        new_loc[1] += int((self.stop_loc[1] - self.start_loc[1]) * percent)
        return new_loc

    def update(self):
        if perf_counter() - self.last_frame > self.frame_time:
            self.loc = self.get_inside_loc(self.now_frame_index / len(self.frames))
            try:
                self.switch_frame(self.now_frame_index + 1)
            except IndexError:
                sm.level_manager.golden_bean += 1
                if sm.level_manager.golden_bean >= sm.level_manager.golden_bean_all:
                    sm.send_event(EVENT_LEVEL_END, LEVEL_END_WIN)
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


class Cover(BaseSprite):
    def __init__(self, image, msg):
        self.layer_def = LAYER_END_UI_BG
        super().__init__(image, [0, 0])
        self.show = False
        self.y_in_move = False
        self.statics = []
        self.x_in_move = False
        self.static_cover = None
        self.saved_cover = None
        self.last_update = perf_counter()
        self.msg = msg
        self.stop_y = 0
        self.target_y = 100
        self.stop_x = 1050
        self.target_x = 1150

    def event_parse(self, event: int, data):
        if event == EVENT_TAKE_CHANGE:
            if data != TAKE_PLAY:
                self.show = False
        elif event == EVENT_LEVEL_RESET:
            self.show = False
        elif event == EVENT_LEVEL_END:
            if data == self.msg:
                self.loc = self.rect.topleft = [0, -750]
                self.show = True
                self.y_in_move = True
                self.last_update = perf_counter()
        elif event == EVENT_COVER_RUN:
            if data == self.msg:
                self.x_in_move = True

    def update(self):
        if self.y_in_move and perf_counter() - self.last_update > 0.02:
            dy = self.target_y - self.loc[1]
            self.loc[1] += int(dy / 11)
            if self.loc[1] > self.stop_y:
                self.loc[1] = self.stop_y + 1 - 1
                self.y_in_move = False
            self.rect.topleft = self.loc[:]
            self.last_update = perf_counter()
        if self.x_in_move and perf_counter() - self.last_update > 0.02:
            if not self.static_cover:
                image = surface2image(self.get_image())
                for static in self.statics:
                    assert isinstance(static, BaseSprite)
                    image.paste(surface2image(static.image), static.rect.topleft)
                self.static_cover = image2surface(image)
                self.saved_cover = self.image.copy()
            dx = self.target_x - self.loc[0]
            self.loc[0] += int(dx / 11)
            self.rect.topleft = self.loc[:]
            self.static_cover.set_alpha(int(255 * (1050 - dx)))
            self.image = self.static_cover
            self.last_update = perf_counter()
            if self.loc[0] > self.stop_x:
                self.loc[0] = self.stop_x + 1 - 1
                self.x_in_move = False
                self.image = self.saved_cover
                sm.send_event(EVENT_LEVEL_NEXT, 0)

        super().update()


class WinCover(Cover):
    def __init__(self):
        super().__init__(rs.sprites.level_cover.win, LEVEL_END_WIN)


class LoseCover(Cover):
    def __init__(self):
        super().__init__(rs.sprites.level_cover.lose, LEVEL_END_LOSE)


class CompleteCover(Cover):
    def __init__(self):
        super().__init__(rs.sprites.level_cover.complete, LEVEL_END_ALL_COMPLETE)


class AnimationSprite(FrameSprite):
    def __init__(self, loc):
        super().__init__(loc)
        self.rect.center = self.loc
        self.animations = {}
        self.played_animation = None
        self.end_stop = False
        self.animation_index = 0
        self.animation_time = 0
        self.last_update = perf_counter()

    def add_animation(self, resources, name: str, speed: int = 10):
        frames = resources if isinstance(resources, list) else resources.Frames
        for frame in frames:
            self.add_frame(frame)
        self.animations[name] = [len(self.frames) - len(frames), len(frames), 1 / speed]

    def play_animation(self, name: str, end_stop: bool = False):
        if name != self.played_animation:
            self.played_animation = name
            self.animation_time = self.animations[self.played_animation][2]
            self.animation_index = 0
            self.last_update = 0
            self.end_stop = end_stop

    def switch_frame(self, index: int):
        super().switch_frame(index)
        self.rect = self.image.get_rect()
        self.rect.center = self.loc

    def update(self):
        if self.show and self.played_animation and self.animation_index != -1:
            if perf_counter() - self.last_update > self.animation_time:
                self.switch_frame(self.animations[self.played_animation][0] + self.animation_index)
                self.animation_index += 1
                if self.animation_index >= self.animations[self.played_animation][1]:
                    if self.end_stop:
                        self.animation_index = -1
                        self.show = False
                    else:
                        self.animation_index = 0
                self.last_update = perf_counter()
        if not OLD_ANIMATION:
            self.rect = self.image.get_rect()
            self.rect.center = self.loc
        super().update()


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
        self.layer_def = LAYER_PLAY
        super().__init__(loc)
        rs_player = rs_map[player_id]
        self.add_frame(rs_player.box)
        self.add_animation(rs_player.stand, "stand", 24)
        self.add_animation(rs_player.run, "run", 24)
        self.add_animation(rs_player.die, "die", 20)
        self.add_animation(rs_player.jump, "jump", 20)

        self.Vy = 0
        self.x = self.rect.topleft[0]
        self.y = self.rect.topleft[1]
        self.k_jump, self.k_left, self.k_right = keys_map[player_id]
        self.jump_lock = False
        self.next_jump = False
        self.enable = True
        self.dir = "right"
        self.self_group = pg.sprite.Group()
        # noinspection PyTypeChecker
        self.self_group.add(self)
        self.last_pos_update = perf_counter()
        self.frame_time = 1 / 60
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
            left_frames.append(image2surface(image.transpose(Image.FLIP_LEFT_RIGHT)))
        super().add_animation(right_frames, name + "_right", speed)
        super().add_animation(left_frames, name + "_left", speed)

    def play_animation(self, name: str, end_stop: bool = False):
        super().play_animation(name + "_" + self.dir, end_stop)

    def move(self, x: float = 0, y: float = 0):
        self.x += x
        self.y -= y

        top = list(self.rect.topleft)
        top[0] = int(self.x)
        top[1] = int(self.y)
        self.rect.topleft = tuple(top)

        self.loc = self.rect.center

    @property
    def collide(self):
        return pg.sprite.groupcollide(sm.level_manager.floor, self.self_group, False, False) or \
            pg.sprite.groupcollide(sm.level_manager.edges, self.self_group, False, False)

    def update(self):
        if perf_counter() - self.last_pos_update > self.frame_time and self.enable:
            self.saved_rect = self.rect.copy()
            self.rect = self.frames[0].get_rect()
            self.rect.center = self.loc

            self.move(y=self.Vy)

            self.Vy -= G
            if self.Vy + G != 0:
                if self.Vy + G > 0:
                    if self.collide:
                        while self.collide:
                            self.move(y=-G)
                        self.Vy = 0
                if self.Vy + G < 0:
                    if self.collide:
                        while self.collide:
                            self.move(y=G)
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
                    if sound:
                        rs.sound.jump.play()
                    self.Vy = 9
                    self.jump_lock = True
                    self.next_jump = False
            else:
                self.next_jump = True

            # 移动逻辑
            if key_map[self.k_left]:
                self.dir = "left"
                self.move(x=-5.2)
                while self.collide:
                    self.move(x=1)
                if not self.jump_lock:
                    self.play_animation("run")
            else:
                if key_map[self.k_right]:
                    self.dir = "right"
                    self.move(x=5.2)
                    while self.collide:
                        self.move(x=-1)
                    if not self.jump_lock:
                        self.play_animation("run")
                elif not self.jump_lock:
                    self.play_animation("stand")

            # 吃金豆判断
            beans = pg.sprite.groupcollide(sm.level_manager.beans, self.self_group, False, False)
            for bean in beans:
                bean.eat()

            # 死亡逻辑
            kills = pg.sprite.groupcollide(sm.level_manager.kills, self.self_group, False, False)
            if kills:
                for sprite in kills:
                    if isinstance(sprite, Bombs):
                        sprite.killed()
                self.play_animation("die", end_stop=True)
                self.enable = False
                if sound:
                    rs.sound.die.play()
                global left_player
                left_player -= 1
                if left_player <= 0:
                    sm.send_event(EVENT_LEVEL_END, LEVEL_END_LOSE)

            self.last_pos_update = perf_counter()
            self.rect = self.saved_rect.copy()
        super().update()


class LevelManager(BaseSprite):
    def __init__(self):
        super().__init__()
        self.level = 0
        self.golden_bean = -1
        self.golden_bean_all = -1
        self.floor = pg.sprite.Group()
        self.kills = pg.sprite.Group()
        self.beans = pg.sprite.Group()
        self.edges = pg.sprite.Group()
        self.temps = []
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

    def event_parse(self, event: int, data):
        global level
        if event == EVENT_TAKE_CHANGE:
            if data != TAKE_PLAY:
                level = "None"
                self.unload_level()
        elif event == EVENT_LEVEL_ENTER:
            level = data[:]
            self.load_level(data)
            self.level = data
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
            if data == LEVEL_END_WIN:
                levels = list(self.level_datas.keys())
                next_level = levels[levels.index(level) + 1]
                sm.levels_container.unlock_level(next_level)
        elif event == EVENT_LEVEL_NEXT:
            levels = list(self.level_datas.keys())
            print(level)
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
        if move_target in self.players:
            self.players.remove(move_target)
        self.elements.remove(move_target)
        move_target.kill()

    def clone_sprite(self):
        assert isinstance(move_target, LevelElement)
        sprite_data = move_target.get_sprite_data()
        logger.log(f"Clone Sprite on {sprite_data['loc']}:", self.__class__.__name__)
        # noinspection PyArgumentList
        sprite = move_target.__class__(deepcopy(sprite_data))
        self.add_sprite_kinds(sprite, sprite_data)
        self.elements.append(sprite)

    def load_level(self, _level: str):
        global left_player
        left_player = players_count + 1 - 1
        self.level = _level
        level_data = self.level_datas[_level]
        self.golden_bean = 0
        self.golden_bean_all = level_data["bean_count"]
        for sprite_data in level_data["items"]:
            sprite = self.create_map[sprite_data["type"]](sprite_data)
            self.add_sprite_kinds(sprite, sprite_data)
            self.elements.append(sprite)

        self.players = [Player(level_data["players"][i], i + 1) for i in range(players_count)]
        global move_target
        if LEVEL_EDIT:
            move_target = self.elements[0]

    def unload_level(self):
        global move_target
        if move_target in self.elements:
            move_target = None
        for sprite in self.temps + self.elements + self.players:
            sprite.kill()
        self.elements.clear()
        self.players.clear()
        self.floor.remove(*self.floor.sprites())
        self.beans.remove(*self.beans.sprites())
        self.kills.remove(*self.floor.sprites())

    def save_level(self):
        logger.log("Save Level", self.level)
        new_level_datas = deepcopy(self.level_datas)
        new_level_datas[str(self.level)]["items"] = [sprite.get_sprite_data() for sprite in self.elements]
        json.dump(new_level_datas, open("assets/data/level_data.json", "w+"), indent=4)


class SpritesManager:
    def __init__(self):
        self.background = BackGround()
        self.brown_player_pose = BrownPlayerPose([870, 520])
        self.game_title = GameTitle([524, 114])
        self.player_choose_title = PlayersChooseTitle([540, 100])
        self.level_choose_title = LevelChooseTitle([538, 54])
        self.win_cover_title = WinCoverTitle()
        self.lose_cover_title = LoseCoverTitle()
        self.start_button = StartButton([546, 321])
        self.more_game_button = MoreGameButton([546, 450])
        self.music_button = MusicButton([50, 56])
        self.return_button = ReturnButton([733, 697])

        self.players1_button = Players1Button([364, 262])
        self.players2_button = Players2Button([560, 262])
        self.players3_button = Players3Button([750, 262])
        self.players_ok_button = PlayersOKButton([558, 683])
        self.players_keys = PlayersKeys([292, 516])
        self.players1_choose = PlayersCH([281, 324], rs.sprites.player_pose.black, 1)
        self.players2_choose = PlayersCH([483, 324], rs.sprites.player_pose.red, 2)
        self.players3_choose = PlayersCH([663, 323], rs.sprites.player_pose.purple, 3)

        self.levels_container = LevelsContainer([123, 120])

        self.level_manager = LevelManager()
        self.more_game_play_button = MoreGameLite([760, 43])
        self.reset_button = ResetButton([907, 45])
        self.home_button = HomeButton([981, 45])
        self.level_level_text = LevelLevelText([15, 12])
        self.level_level_number = LevelLevelNumber([80, 15])
        self.bean_counter = BeanCounter([255, 9])
        self.bean_show = BeanShow([219, 14])

        self.return_choose = ReturnChooseButton()
        self.next_level = NextLevelButton()
        self.retry_button = RetryButton()

        self.win_cover = WinCover()
        self.lose_cover = LoseCover()
        self.complete_cover = CompleteCover()

        self.transition = TransitionMask()

    @staticmethod
    def send_event(event_id: int, data):
        for _sprites in list(sprites.values()):
            for sprite in _sprites:
                sprite.event_parse(event_id, data)


timers.append(perf_counter())  # 元素定义计时器
logger.log("Creating Sprites...")
sm = SpritesManager()
logger.log("Sprites Creating Done!")
timers.append(perf_counter())  # 元素创建计时器

logger.log("Game Loading Over!")
logger.log(f"Library Load Use: {ms(timers[0], timers[1])} ms")
logger.log(f"Resource Loading Use: {ms(timers[2], timers[3])} ms")
logger.log(f"Sprites Create Use: {ms(timers[4], timers[5])} ms")
logger.log(f"Game Launch Use: {ms(timers[0], timers[5])} ms")

logger.finish()
logger.render_now()
move_target = sm.return_choose
clock = pg.time.Clock()
pg.key.stop_text_input()
st = perf_counter()

while True:
    _events = pg.event.get()
    for _event in _events:
        if _event.type == pg.QUIT:
            break
        if _event.type == pg.KEYDOWN:
            if _event.key == pg.K_UP:
                move_target.target(0, -1)
            elif _event.key == pg.K_DOWN:
                move_target.target(0, 1)
            elif _event.key == pg.K_RIGHT:
                move_target.target(1, 0)
            elif _event.key == pg.K_LEFT:
                move_target.target(-1, 0)
            elif _event.key == pg.K_KP_PLUS:
                sm.send_event(EVENT_REQ_CLONE, 0)
            elif _event.key == pg.K_KP0:
                sm.send_event(EVENT_REQ_LEVEL_SAVE, 0)
            elif _event.key == pg.K_DELETE:
                sm.send_event(EVENT_REQ_DELETE, 0)
            elif _event.key == pg.K_KP_ENTER:
                print(move_target.loc)
            elif _event.key == pg.K_p:
                sm.send_event(EVENT_LEVEL_END, LEVEL_END_WIN)
            elif _event.key == pg.K_l:
                print("FPS:", round(clock.get_fps(), 2))
    else:
        pg.event.pump()
        screen.fill((255, 255, 255))
        max_upt = 0
        updates = {}
        for _layer in LAYERS:
            layer_sprites = sprites[_layer]
            for _sprite in layer_sprites:
                if SHOW_PERF and SPRITE_PERF:
                    timer = perf_counter()
                    _sprite.update()
                    time = ms(timer, perf_counter())
                    if time > 0.01:
                        updates[time] = _sprite.__class__.__name__
                else:
                    _sprite.update()
        if SHOW_PERF and perf_counter() - st > 1:
            if SPRITE_PERF:
                print("-" * 50)
                _times = sorted(updates.keys())
                for time in _times:
                    _name = updates[time]
                    print("Max Update Time:", _name, time)
            print("FPS:", round(clock.get_fps(), 2))
            st = perf_counter()

        for _sprite, old_layer, new_layer in layer_updates:
            sprites[old_layer].remove(_sprite)
            sprites[new_layer].append(_sprite)
        layer_updates.clear()
        pg.display.update()
        clock.tick()
        continue
    break

pg.quit()
