import json
from os.path import isfile
from typing import Any, Callable


class Config:
    play_sound: bool = False
    use_cache: bool = False

    def __init__(self):
        self.cfg_fp = "data/config.json"
        self.load()
        self.config_callbacks: dict[str, list[Callable]] = {}

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

    def save(self):
        print("保存游戏配置")
        data = {key: getattr(self, key) for key in self.load_config_keys()}
        data_content = json.dumps(data)
        with open(self.cfg_fp, "w") as f:
            f.write(data_content)

    def load_config_keys(self) -> list[str]:
        return list(self.__annotations__.keys())


gm_config = Config()
