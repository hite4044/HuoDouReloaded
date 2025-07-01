import inspect
from enum import Enum
from typing import Callable

from engine.asset_parser import *
from lib.define import *
from lib.image_render import ImageRender, RenderTextArgs, RenderGrowArgs, RenderShadowArgs, RenderImageArgs


class ReverseWay(Enum):
    FLIP_LEFT_RIGHT = 0
    FLIP_TOP_BOTTOM = 1
    ROTATE_90 = 2
    ROTATE_180 = 3
    ROTATE_270 = 4
    TRANSPOSE = 5
    TRANSVERSE = 6


class RotateArg(float):
    def __init__(self, rotate: float, expand: bool = False):
        super().__init__()
        self.expand = expand

    def __new__(cls, rotate: float, expand: bool = False):
        return super().__new__(cls, rotate)


def load_asset(fp: str,
               scale: float = GAME_SCALE,
               resize: tuple[int | float, int | float] | None = None,
               transpose: ReverseWay | None = None,
               rotate: float | None = None) -> Image.Image | pg.mixer.Sound:
    if fp.endswith(".svg"):
        return load_svg_asset(fp, scale, resize, transpose, rotate)
    elif fp.endswith(".png"):
        return Image.open(fp)
    elif fp.endswith(".mp3"):
        return pg.mixer.Sound(fp)
    else:
        raise ValueError("Invalid asset type")


def load_svg_asset(fp: str,
                   scale: float = GAME_SCALE,
                   resize: tuple[int | float, int | float] | None = None,
                   transpose: ReverseWay | None = None,
                   rotate: float | None = None):
    image = render_svg2image(fp, scale)
    if transpose:
        image = image.transpose(Image.Transpose(transpose.value))
    if resize:
        if isinstance(resize[0], int):
            image = image.resize(resize)
        elif isinstance(resize[0], float):
            new_size = (image.width * resize[0], image.height * resize[1])
            image = image.resize(new_size)
    if rotate:
        expand = False
        if isinstance(rotate, RotateArg):
            expand = rotate.expand
        image = image.rotate(rotate, expand=expand)
    return image


class GA(pg.surface.Surface):
    """GameAsset 游戏资源"""

    def __init__(self,
                 asset: str | None = None,
                 scale: float = GAME_SCALE,
                 resize: tuple[int | float, int | float] | None = None,
                 transpose: ReverseWay | None = None,
                 rotate: float | None = None,
                 custom_load_func: Callable[[], pg.surface.Surface] | None = None):
        if 89 * 8.2 == 114514:
            super().__init__((114, 514))
        self.asset_path = asset
        self.scale = scale
        self.resize = resize
        self.transpose = transpose
        self.rotate = rotate

        self.before_load_func = lambda: None
        self.after_load_func = lambda: None
        self.transform_func = None
        self.custom_load_func = custom_load_func

    def load(self):
        if self.custom_load_func:
            return self.custom_load_func()

        self.before_load_func()

        asset = load_asset(self.asset_path, self.scale, self.resize, self.transpose, self.rotate)
        if self.transform_func:
            asset = self.transform_func(asset)

        self.after_load_func()

        if isinstance(asset, Image.Image):
            return image2surface(asset)
        else:
            return asset


class AssetList(list):
    pass


def FRAME_GEN(path: str, num: int, **kwargs) -> AssetList[GA]:
    return AssetList(GA(path.format(i), **kwargs) for i in range(num))


class Background:
    start = GA("assets/bg/start.svg")
    play = GA("assets/bg/play.svg")
    choose = GA("assets/bg/choose.svg")


class Sprites:
    class BombKill:
        frames = FRAME_GEN("assets/sprites/bomb_kill/{}.svg", 15, scale=5)

    class Bombs:
        normal = GA("assets/sprites/bombs/normal.svg")

    class BrownPlayer:
        normal = GA("assets/sprites/brown_player/normal.svg")

    class Burr:
        __path = "assets/sprites/burr/normal.svg"
        normal = GA(__path)
        reverse = GA(__path, transpose=ReverseWay.ROTATE_180)

    class GoldenBean:
        normal = GA("assets/sprites/golden_bean/normal.svg")
        counter = GA("assets/sprites/golden_bean/counter.svg")
        # 从 100% 到 10% 大小
        eat_animation = AssetList(GA("assets/sprites/golden_bean/normal.svg",
                                     scale=GAME_SCALE * (size / 100)) for size in
                                  (list(range(100, 10, -8)) + [10, 10, 10]))

    class Ground:
        normal = GA("assets/sprites/ground/normal.svg")
        long = GA("assets/sprites/ground/long.svg")
        v_normal = GA(normal.asset_path, transpose=ReverseWay.ROTATE_270)

    class Gun:
        left = GA("assets/sprites/gun/left.svg")
        right = GA("assets/sprites/gun/right.svg")

    class IceBurr:
        normal = GA("assets/sprites/ice_burr/normal.svg")

    class Level:
        lock = GA("assets/sprites/level/lock.svg")
        unlock = GA("assets/sprites/level/unlock.svg")

    class LevelEndCover:
        complete = GA("assets/sprites/level_end_cover/complete.svg")
        lose = GA("assets/sprites/level_end_cover/lose.svg")
        win = GA("assets/sprites/level_end_cover/win.svg")

    class Player:
        def __init__(self, root: str):
            class Stand:
                frames = FRAME_GEN(root + "/stand/{}.svg", 4)
                frames.append(GA(frames[0].asset_path))

            class Run:
                frames = FRAME_GEN(root + "/run/{}.svg", 9)

            class Die:
                frames = FRAME_GEN(root + "/die/{}.svg", 9)

            class Jump:
                frames = AssetList([GA(f"{root}/jump.svg")])

            self.stand = Stand()
            self.run = Run()
            self.die = Die()
            self.jump = Jump()

            self.box = GA(custom_load_func=lambda: pg.surface.Surface((30, 55)))

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
        black = GA("assets/sprites/player_pose/black.svg", scale=GAME_SCALE * 2.5)
        purple = GA("assets/sprites/player_pose/purple.svg", scale=GAME_SCALE * 2.5)
        red = GA("assets/sprites/player_pose/red.svg", scale=GAME_SCALE * 2.5)

    class PlayerKeys:  # 关卡选择界面按键
        p_1 = GA("assets/sprites/players_keys/p_1.svg")
        p_2 = GA("assets/sprites/players_keys/p_2.svg")
        p_3 = GA("assets/sprites/players_keys/p_3.svg")

    class Water:
        normal = GA("assets/sprites/water/normal.svg")

    class WaterTimer:
        frames = FRAME_GEN("assets/sprites/water_timer/{}.svg", 6)

    class KillBase:
        @staticmethod
        def transform_func(image: Image.Image):
            return image.resize((image.width // 2, image.height // 2))

        def __init__(self, asset_path: str):
            self.frames = AssetList()
            for r in range(0, 360, 15):
                frame = GA(asset_path, scale=GAME_SCALE * 2, rotate=RotateArg(r, expand=True))
                frame.transform_func = self.transform_func
                self.frames.append(frame)

    class XKill(KillBase):
        def __init__(self):
            super().__init__("assets/sprites/x_kill/normal.svg")

    class YKill(KillBase):
        def __init__(self):
            super().__init__("assets/sprites/y_kill/normal.svg")

    class XTerrace:
        normal = GA("assets/sprites/x_terrace/normal.svg")

    class YTerrace:
        normal = GA("assets/sprites/y_terrace/normal.svg")

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


TBD_SIZE_UP = 42.5  # 41.5
TBD_SIZE_DOWN = 38  # 37.5
TBD_LOC_UP = (124, 37)
TBD_LOC_DOWN = (112, 34)
TBD_BG_UP = "assets/buttons/text_4/up.svg"
TBD_BG_DOWN = "assets/buttons/text_4/down.svg"


class Buttons:
    class Games:
        up = GA("assets/buttons/games/up.svg")
        down = GA("assets/buttons/games/down.svg")

    class Home:
        up = GA("assets/buttons/home/up.svg")
        down = GA("assets/buttons/home/down.svg")

    class Music:
        up = GA("assets/buttons/music/up.svg")
        down = GA("assets/buttons/music/down.svg")
        A_up = GA("assets/buttons/music/A_up.svg")
        A_down = GA("assets/buttons/music/A_down.svg")

    class Reset:
        up = GA("assets/buttons/reset/up.svg")
        down = GA("assets/buttons/reset/down.svg")

    class TextButton:
        def __init__(self,
                     text: str,
                     size_up: float = TBD_SIZE_UP, size_down: float = TBD_SIZE_DOWN,
                     loc_up: tuple[int, int] = TBD_LOC_UP, loc_down: tuple[int, int] = TBD_LOC_DOWN,
                     bg_up: str = TBD_BG_UP, bg_down: str = TBD_BG_DOWN,
                     scale: float = GAME_SCALE,
                     use_shadow: bool = True):
            self.up = GA()
            self.up.custom_load_func = lambda: self.get_text_button(bg_up, text, loc_up, size_up, scale, use_shadow)
            self.down = GA()
            self.down.custom_load_func = lambda: self.get_text_button(bg_down, text, loc_down, size_down,
                                                                      scale, use_shadow)

        @staticmethod
        def get_text_button(bg_path: str,
                            text: str,
                            loc: tuple[int, int],
                            font_size: float,
                            scale: float, use_shadow: bool):
            image = render_svg2image(bg_path, scale=scale)
            render = ImageRender(image.size)
            render.add_text(RenderTextArgs(text, font_size, "mm", loc))
            render.add_grow(RenderGrowArgs(1, 0.8))
            render.add_bg_image(RenderImageArgs(image))
            if use_shadow:
                render.add_shadow(RenderShadowArgs(8, 2.4))
            return image2surface(render.image)

    class RelativeTextButton(TextButton):
        pass

    class Text4Button(TextButton):
        def __init__(self,
                     text: str,
                     size_up: float = TBD_SIZE_UP, size_down: float = TBD_SIZE_DOWN,
                     loc_up: tuple[int, int] = TBD_LOC_UP, loc_down: tuple[int, int] = TBD_LOC_DOWN,
                     scale: float = GAME_SCALE,
                     use_shadow: bool = True) -> None:
            super().__init__(text,
                             size_up, size_down,
                             loc_up, loc_down,
                             "assets/buttons/text_4/up.svg", "assets/buttons/text_4/down.svg",
                             scale, use_shadow)

    class Text2Button(TextButton):
        def __init__(self,
                     text: str,
                     size_up: float = TBD_SIZE_UP, size_down: float = TBD_SIZE_DOWN,
                     loc_up: tuple[int, int] = TBD_LOC_UP, loc_down: tuple[int, int] = TBD_LOC_DOWN,
                     scale: float = GAME_SCALE,
                     use_shadow: bool = True) -> None:
            super().__init__(text,
                             size_up, size_down,
                             loc_up, loc_down,
                             "assets/buttons/text_2/up.svg", "assets/buttons/text_2/down.svg",
                             scale, use_shadow=use_shadow)

    class NumberButton(TextButton):
        # noinspection PyDefaultArgument
        def __init__(self,
                     text: str,
                     size_up: float = TBD_SIZE_UP, size_down: float = TBD_SIZE_DOWN,
                     loc_up: tuple[int, int] = TBD_LOC_UP, loc_down: tuple[int, int] = TBD_LOC_DOWN,
                     scale: float = GAME_SCALE) -> None:
            super().__init__(text,
                             size_up, size_down,
                             loc_up, loc_down,
                             "assets/buttons/players_choose/up.svg", "assets/buttons/players_choose/down.svg",
                             scale)

    class StartGame(Text4Button):
        def __init__(self):
            super().__init__(text="开始游戏", loc_up=(124, 37), loc_down=(112, 34))

    class MoreGame(TextButton):
        def __init__(self):
            super().__init__(text="更多游戏",
                             loc_up=(124, 37), loc_down=(122, 37),
                             bg_up="assets/buttons/text_4/up.svg", bg_down="assets/buttons/text_4/up.svg")

    class Players1(NumberButton):
        def __init__(self):
            super().__init__("1", 65, 58, (45, 40), (40, 37))

    class Players2(NumberButton):
        def __init__(self):
            super().__init__("2", 65, 58, (45, 40), (40, 37))

    class Players3(NumberButton):
        def __init__(self):
            super().__init__("3", 65, 58, (45, 40), (40, 37))

    class PlayersOK(Text2Button):
        def __init__(self):
            super().__init__("确 定", loc_up=(95, 37), loc_down=(85, 33), use_shadow=False)

    class Return(Text2Button):
        def __init__(self):
            super().__init__("返 回", loc_up=(95, 37), loc_down=(85, 34))

    class ReturnChoose(Text4Button):
        def __init__(self):
            super().__init__("返回主页",
                             36, 32,
                             (105, 30), (95, 28),
                             scale=1.28)

    class NextLevelButton(TextButton):
        def __init__(self):
            super().__init__("下 一 关",
                             40, 36, (106, 37), (96, 33),
                             bg_up="assets/buttons/text_3/up.svg", bg_down="assets/buttons/text_3/down.svg",
                             scale=1.4)

    class RetryLevelButton(Text4Button):
        def __init__(self):
            super().__init__("再玩一次",
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
    music = GA("assets/music/music.mp3")
    jump = GA("assets/music/jump.mp3")
    eat = GA("assets/music/eat.mp3")
    die = GA("assets/music/die.mp3")


def load_empty():
    surface = pg.surface.Surface((16, 16))
    surface.fill((255, 0, 255, 255))
    return surface.convert_alpha()

def load_icon():
    image = Image.open("assets/icon.png")
    return image2surface(image.resize((64, 64)))


bg = Background()
sprites = Sprites()
buttons = Buttons()
sound = Sound()

icon = GA(custom_load_func=load_icon)
empty = GA(custom_load_func=load_empty)

ALL_ASSETS = [bg, sprites, buttons, sound]


def load_resources():
    log_func("Loading Assets...")

    def load_assets(obj: object | list):
        for name, value in inspect.getmembers(obj):
            if name.startswith("__"):  # 不能为内置类型
                continue
            if hasattr(value, "__call__"):  # 不能为函数
                continue

            if isinstance(value, GA):  # 为字符串类型
                setattr(obj, name, value.load())
            elif isinstance(value, AssetList):  # 对于每一帧执行加载
                game_asset: GA
                for i, game_asset in enumerate(value):
                    value[i] = game_asset.load()
            else:
                load_assets(value)

    global icon, empty
    icon = icon.load()
    empty = empty.load()
    for asset in ALL_ASSETS:
        load_assets(asset)
    log_func("Assets Load Done!")
