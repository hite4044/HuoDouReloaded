import inspect
from os.path import join

from tools import *


class Background:
    start = "assets/bg/start.svg"
    play = "assets/bg/play.svg"
    choose = "assets/bg/choose.svg"


class Sprites:
    class BombKill:
        frames_scale = 5
        frames = [join("assets/sprites/bomb_kill/", str(i) + ".svg") for i in range(15)]

    class Bombs:
        normal = "assets/sprites/bombs/normal.svg"

    class BrownPlayer:
        normal = "assets/sprites/brown_player/normal.svg"

    class Burr:
        def load_after(self, log_func):
            image = render_svg2image("assets/sprites/burr/normal.svg", log_func=log_func, force_image=True)

            # noinspection PyAttributeOutsideInit
            self.reverse = image2surface(image.rotate(180, expand=True))

        normal = "assets/sprites/burr/normal.svg"

    class GoldenBean:
        def load(self, log_func):
            image = surface2image(load_svg(self.normal, log_func=log_func))
            for size in range(10, 1, -1):
                frame = image.resize(tuple(map(lambda x: int(x * size / 10), image.size)))
                self.ani_frames.append(image2surface(frame))

        normal = "assets/sprites/golden_bean/normal.svg"
        counter = "assets/sprites/golden_bean/counter.svg"
        ani_frames = []

    class Ground:
        def load_after(self, log_func):
            image = render_svg2image("assets/sprites/ground/normal.svg", log_func=log_func, force_image=True)

            # noinspection PyAttributeOutsideInit
            self.v_normal = image2surface(image.rotate(-90, expand=True))

        normal = "assets/sprites/ground/normal.svg"
        long = "assets/sprites/ground/long.svg"

    class Gun:
        left = "assets/sprites/gun/left.svg"
        right = "assets/sprites/gun/right.svg"

    class IceBurr:
        normal = "assets/sprites/ice_burr/normal.svg"

    class Level:
        lock = "assets/sprites/level/lock.svg"
        unlock = "assets/sprites/level/unlock.svg"

    class LevelEndCover:
        complete = "assets/sprites/level_end_cover/complete.svg"
        lose = "assets/sprites/level_end_cover/lose.svg"
        win = "assets/sprites/level_end_cover/win.svg"

    class Player:
        def __init__(self, root: str):
            self.box = ""

            class Stand:
                frames = [join(root + "/stand", str(i) + ".svg") for i in range(4)]
                frames.append(frames[0])
                frames.append(frames[0])

            class Run:
                frames = [join(root + "/run", str(i) + ".svg") for i in range(9)]

            class Die:
                frames = [join(root + "/die", str(i) + ".svg") for i in range(9)]

            class Jump:
                frames = [root + "/jump.svg"]

            self.stand = Stand()
            self.run = Run()
            self.die = Die()
            self.jump = Jump()

        def load_after(self, _):
            self.box = pg.surface.Surface((30, 55))

    class Player1(Player):
        def __init__(self):
            super().__init__("assets/sprites/player1")

    class Player2(Player):
        def __init__(self):
            super().__init__("assets/sprites/player2")

    class Player3(Player):
        def __init__(self):
            super().__init__("assets/sprites/player3")

    class PlayerPose:  # 关卡选择界面人物
        black = "assets/sprites/player_pose/black.svg"
        purple = "assets/sprites/player_pose/purple.svg"
        red = "assets/sprites/player_pose/red.svg"
        black_scale = 2.5
        purple_scale = 2.5
        red_scale = 2.5

    class PlayerKeys:  # 关卡选择界面按键
        p_1 = "assets/sprites/players_keys/p_1.svg"
        p_2 = "assets/sprites/players_keys/p_2.svg"
        p_3 = "assets/sprites/players_keys/p_3.svg"

    class Water:
        normal = "assets/sprites/water/normal.svg"

    class WaterTimer:
        p_0 = "assets/sprites/water_timer/p_0.svg"
        p_1 = "assets/sprites/water_timer/p_1.svg"
        p_2 = "assets/sprites/water_timer/p_2.svg"
        p_3 = "assets/sprites/water_timer/p_3.svg"
        p_4 = "assets/sprites/water_timer/p_4.svg"
        p_5 = "assets/sprites/water_timer/p_5.svg"

    class XKill:
        def load_only(self, log_func):
            image = render_svg2image("assets/sprites/x_kill/normal.svg", 3, log_func, True)
            # noinspection PyAttributeOutsideInit
            self.frames = []
            for r in range(0, 360, 15):
                frame_image = image.rotate(-r, expand=True)
                frame_image = frame_image.resize([i // 2 for i in frame_image.size])
                self.frames.append(image2surface(frame_image))

    class XTerrace:
        normal = "assets/sprites/x_terrace/normal.svg"

    class YKill:
        def load_only(self, log_func):
            image = render_svg2image("assets/sprites/y_kill/normal.svg", log_func=log_func, force_image=True)
            # noinspection PyAttributeOutsideInit
            self.frames = []
            for r in range(0, 360, 15):
                self.frames.append(image2surface(image.rotate(-r, expand=True)))

    class YTerrace:
        normal = "assets/sprites/y_terrace/normal.svg"

    bomb_kill = BombKill()
    bombs = Bombs()
    brown_player = BrownPlayer()
    burr = Burr()
    golden_bean = GoldenBean()
    ground = Ground()
    gun = Gun()
    ice_burr = IceBurr()
    level = Level()
    level_cover = LevelEndCover()
    player1 = Player1()
    player2 = Player2()
    player3 = Player3()
    player_pose = PlayerPose()
    player_keys = PlayerKeys()
    water = Water()
    water_timer = WaterTimer()
    x_kill = XKill()
    x_terrace = XTerrace()
    y_kill = YKill()
    y_terrace = YTerrace()


class Buttons:
    class Games:
        up = "assets/buttons/games/up.svg"
        down = "assets/buttons/games/down.svg"

    class Home:
        up = "assets/buttons/home/up.svg"
        down = "assets/buttons/home/down.svg"

    class Music:
        up = "assets/buttons/music/up.svg"
        down = "assets/buttons/music/down.svg"
        Aup = "assets/buttons/music/Aup.svg"
        Adown = "assets/buttons/music/Adown.svg"

    class Reset:
        up = "assets/buttons/reset/up.svg"
        down = "assets/buttons/reset/down.svg"

    class TextButton:
        def __init__(self, ):
            self.up = None
            self.down = None

        def _load_images(self,
                         text: str = "123",
                         text_size_up: float = 41.5, text_size_down: float = 37.5,
                         text_loc_up: tuple[int, int] = (124, 37), text_loc_down: tuple[int, int] = (112, 34),
                         bg_up: str = "assets/buttons/text_4/up.svg",
                         bg_down: str = "assets/buttons/text_4/down.svg",
                         scale: float = 1.5) -> None:

            self.up = self.get_text_button(bg_up, text, text_loc_up, text_size_up, scale)
            self.down = self.get_text_button(bg_down, text, text_loc_down, text_size_down, scale)

        @staticmethod
        def get_text_button(fp: str, text: str, loc: tuple[int, int],
                            font_size: float, scale: float):
            image = render_svg2image(fp, scale=scale, force_image=True)
            render = ImageRender(image.size, image)
            render.add_text(text, font_size, image.size, "#FFCB00",
                            True, 3, "#990000",
                            text_loc=loc)
            return image2surface(render.base)

    class Text4Button(TextButton):
        def load_images(self,
                        text: str = "123",
                        text_size_up: float = 41.5, text_size_down: float = 37.5,
                        text_loc_up: tuple[int, int] = (124, 37), text_loc_down: tuple[int, int] = (112, 34),
                        scale: float = 1.5,
                        ) -> None:
            self._load_images(text,
                              text_size_up, text_size_down,
                              text_loc_up, text_loc_down,
                              "assets/buttons/text_4/up.svg", "assets/buttons/text_4/down.svg",
                              scale)

    class Text2Button(TextButton):
        def load_images(self,
                        text: str = "123",
                        text_size_up: float = 41.5, text_size_down: float = 37.5,
                        text_loc_up: tuple[int, int] = (124, 37), text_loc_down: tuple[int, int] = (112, 34),
                        scale: float = 1.5,
                        ) -> None:
            self._load_images(text,
                              text_size_up, text_size_down,
                              text_loc_up, text_loc_down,
                              "assets/buttons/text_2/up.svg", "assets/buttons/text_2/down.svg",
                              scale)

    class NumberButton(TextButton):
        # noinspection PyDefaultArgument
        def load_images(self,
                        text: str = "123",
                        text_size_up: float = 41.5, text_size_down: float = 37.5,
                        text_loc_up: tuple[int, int] = (124, 37), text_loc_down: tuple[int, int] = (112, 34),
                        scale: float = 1.5,
                        ) -> None:
            self._load_images(text,
                              text_size_up, text_size_down,
                              text_loc_up, text_loc_down,
                              "assets/buttons/players_choose/up.svg", "assets/buttons/players_choose/down.svg",
                              scale)

    class StartGame(Text4Button):
        def load_only(self, _):
            self.load_images(text_loc_up=(124, 37), text_loc_down=(112, 34), text="开始游戏")

    class MoreGame(TextButton):
        def load_only(self, _):
            self._load_images(text_loc_up=(124, 37), text_loc_down=(122, 37),
                              bg_up="assets/buttons/text_4/up.svg", bg_down="assets/buttons/text_4/up.svg",
                              text="更多游戏")

    class Players1(NumberButton):
        def load_only(self, _):
            self.load_images("1", 65, 58, (45, 40), (40, 37))

    class Players2(NumberButton):
        def load_only(self, _):
            self.load_images("2", 65, 58, (45, 40), (40, 37))

    class Players3(NumberButton):
        def load_only(self, _):
            self.load_images("3", 65, 58, (45, 40), (40, 37))

    class PlayersOK(Text2Button):
        def load_only(self, _):
            self.load_images(text_loc_up=(95, 35), text_loc_down=(85, 32), text="确 定")

    class Return(Text2Button):
        def load_only(self, _):
            self.load_images(text_loc_up=(95, 35), text_loc_down=(85, 32), text="返 回")

    class ReturnChoose(Text4Button):
        def load_only(self, _):
            self.load_images("返回主页",
                             36, 32, (105, 30), (95, 28),
                             scale=1.28)

    class NextLevelButton(TextButton):
        def load_only(self, _):
            self._load_images("下 一 关",
                              40, 36, (106, 37), (96, 33),
                              bg_up="assets/buttons/text_3/up.svg", bg_down="assets/buttons/text_3/down.svg",
                              scale=1.4)

    class RetryLevelButton(Text4Button):
        def load_only(self, _):
            self._load_images("再玩一次",
                              36, 32, (105, 30), (95, 28),
                              scale=1.28)

    start_game = StartGame()
    more_game = MoreGame()
    music = Music()
    games = Games()
    home = Home()
    reset = Reset()
    players1 = Players1()
    players2 = Players2()
    players3 = Players3()
    player_ok = PlayersOK()
    return_ = Return()
    return_choose = ReturnChoose()
    next_level = NextLevelButton()
    retry_level = RetryLevelButton()


class Sound:
    music = "assets/music/music.mp3"
    jump = "assets/music/jump.mp3"
    eat = "assets/music/eat.mp3"
    die = "assets/music/die.mp3"


bg = Background()
sprites = Sprites()
buttons = Buttons()
sound = Sound()
empty = ""
empty_alpha = ""
icon = "assets/icon.png"


def load_resources(log_func=print):
    log_func("Loading Assets...")

    def load_assets(obj: object | list):
        if hasattr(obj, "load"):
            obj.load(log_func)
        elif hasattr(obj, "load_only"):
            obj.load_only(log_func)
            return
        for name, value in inspect.getmembers(obj):
            #  不能为函数 不能为内置类型 不能为缩放定义
            if not hasattr(value, "__call__") and not name.startswith("__") and not name.endswith("_scale"):
                if isinstance(value, str):  # 为字符串类型
                    if value.endswith(".svg"):  # svg资源加载为surface
                        if hasattr(obj, name + "_scale"):
                            setattr(obj, name, load_svg(value, getattr(obj, name + "_scale") * 1.5, log_func=log_func))
                        else:
                            setattr(obj, name, load_svg(value, log_func=log_func))
                    elif value.endswith(".mp3"):  # mp3资源加载为绝对地址
                        log_func("Loading Assets:", value)
                        setattr(obj, name, pg.mixer.Sound(abspath(value)))
                elif name == "frames":  # 对于每一帧执行加载
                    scale = getattr(obj, name + "_scale") if hasattr(obj, name + "_scale") else 1.5
                    setattr(obj, name, [load_svg(fp, scale=scale, log_func=log_func) for fp in value])
                else:
                    load_assets(value)

        if hasattr(obj, "load_after"):
            obj.load_after(log_func)

    global empty
    empty = pg.surface.Surface((50, 50))
    global empty_alpha
    empty_alpha = empty.convert_alpha().fill((255, 255, 255, 255))
    global icon
    icon = pg.image.load(icon[:]).convert_alpha()
    load_assets(bg)
    load_assets(sprites)
    load_assets(buttons)
    load_assets(sound)
    log_func("Assets Load Done!")
