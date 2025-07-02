from lib.config import gm_config
from lib.perf import Counter

timer = Counter()  # 库导入计时器
timer.start("lib", "all")
from time import perf_counter
import ctypes
from ctypes import windll
from engine.sprite_manager import SpritesManager

from os import getcwd, environ
from os.path import join

environ["PATH"] += ";" + join(getcwd(), "base_library")
from lib.public_data import public, sprites, layer_updates
from sprites.visual_logger import VisualLogger
from engine import resource as rs
from engine.asset_parser import *
from lib.define import *

pg.init()
screen = pg.display.set_mode((1050, 750))
public.screen = screen

logger = VisualLogger()
players_count = 1
left_player = 1
level = "None"
sound = False
pg.display.set_caption("火柴人吃豆豆2")
timer.end_start("lib", "res")  # 资源加载计时
public.set_log_fuc(logger.log)
rs.load_resources()
timer.end("res")  # 资源加载计时器
public.set_log_fuc(print)
pg.display.set_icon(rs.icon)
buffer = ctypes.create_unicode_buffer("Adobe Flash Player 34")
t_hwnd = windll.user32.FindWindowW(None, ctypes.byref(buffer))
windll.user32.SetWindowPos(t_hwnd, None, 357, 131 - 20, 1050 + 16, 750 + 59, 0x0004)
windll.user32.SetWindowPos(pg.display.get_wm_info()["window"], None, 357, 131, 0, 0, 0x0001 | 0x0004)
timer.start("spr_create")  # 元素创建计时器
logger.log("Creating Sprites...")
sm = SpritesManager()
public.sprites_manager = sm
logger.log("Sprites Creating Done!")
timer.end("spr_create")  # 元素创建计时器
timer.end("all")

logger.log("Game Loading Over!")
logger.log(f"Library Load Use: {timer.endT('lib')}")
logger.log(f"Resource Loading Use: {timer.endT('res')}")
logger.log(f"Sprites Create Use: {timer.endT('spr_create')}")
logger.log(f"Game Launch Use: {timer.endT('all')}")

logger.finish()
logger.render_now()
public.move_target = sm.lose_cover_title
clock = pg.time.Clock()
pg.key.stop_text_input()
st = perf_counter()

while True:
    _events = pg.event.get()
    for _event in _events:
        if _event.type == pg.QUIT:
            break
        elif _event.type == pg.KEYDOWN:
            if _event.key == pg.K_UP and public.move_target:
                public.move_target.target(0, -1)
            elif _event.key == pg.K_DOWN and public.move_target:
                public.move_target.target(0, 1)
            elif _event.key == pg.K_RIGHT and public.move_target:
                public.move_target.target(1, 0)
            elif _event.key == pg.K_LEFT and public.move_target:
                public.move_target.target(-1, 0)
            elif _event.key == pg.K_KP_PLUS and public.move_target:
                sm.send_event(EVENT_REQ_CLONE)
            elif _event.key == pg.K_KP0:
                sm.send_event(EVENT_REQ_LEVEL_SAVE)
            elif _event.key == pg.K_r:
                sm.send_event(EVENT_REQ_RELOAD_LEVEL)
            elif _event.key == pg.K_DELETE and public.move_target:
                sm.send_event(EVENT_REQ_DELETE)
            elif _event.key == pg.K_KP_ENTER and public.move_target:
                print(public.move_target.loc)
            elif _event.key == pg.K_p:
                sm.send_event(EVENT_LEVEL_END, LEVEL_END_WIN)
            elif _event.key == pg.K_t:
                sm.send_event(EVENT_SWITCH_HT_MODE)
            elif _event.key == pg.K_l:
                print("FPS:", round(clock.get_fps(), 2))
        elif _event.type == pg.MOUSEBUTTONDOWN:
            if _event.button == pg.BUTTON_RIGHT:
                mouse_pos = pg.mouse.get_pos()
                for sprite in public.sprite_list:
                    if sprite.show and sprite.rect.collidepoint(mouse_pos):
                        public.move_target = sprite
                        break
                print(f"Select Sprite: {public.move_target.__class__.__name__}")
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
                    time = (perf_counter() - timer) * 1000
                    if time > 0.01:
                        updates[time] = _sprite.__class__.__name__
                else:
                    _sprite.update()
        if SHOW_PERF and perf_counter() - st > 1:
            if SPRITE_PERF:
                print("-" * 50)
                _times = sorted(updates.keys())
                for time in _times[:min(20, len(_times))]:
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
gm_config.save()
