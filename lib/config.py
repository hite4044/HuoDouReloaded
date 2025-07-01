import json
from os.path import isfile
from typing import Any, Callable


class Config:
    play_sound: bool = False
    use_cache: bool = True
    sim: bool = False
    sim_player_fps: bool = False
    sim_bomb_fps: bool = False

    def __init__(self):
        self.cfg_fp = "data/config.json"
        self.config_callbacks: dict[str, list[Callable]] = {}
        self.load()

    def set_config(self, key: str, value: Any):
        setattr(self, key, value)
        if key in self.config_callbacks:
            for callback in self.config_callbacks[key]:
                callback(value)
        self.save()

    def reg_config_callback(self, key: str, func: Callable):
        self.config_callbacks.setdefault(key, []).append(func)

    def load(self):
        if not isfile(self.cfg_fp):
            return
        with open(self.cfg_fp, "r") as f:
            self.__dict__.update(json.load(f))
        if not self.sim:
            self.sim_player_fps = False

    def save(self):
        print("Save Game Config")
        data = {key: getattr(self, key) for key in self.load_config_keys()}
        data_content = json.dumps(data)
        with open(self.cfg_fp, "w") as f:
            f.write(data_content)

    def load_config_keys(self) -> list[str]:
        return list(self.__annotations__.keys())


gm_config = Config()
