import json
from os import mkdir, makedirs
from os.path import isfile, join as path_join, expandvars, isdir
from shutil import rmtree

from lib.define import *

# 素材缓存路径
CACHE_PATH = path_join(expandvars("%TEMP%"), "HuoDouReloaded_Cache")


class CacheManager:
    def __init__(self):
        self.cache_path = CACHE_PATH
        self.info_fp = mk_cache("info.json")
        makedirs(self.cache_path, exist_ok=True)

        self.check_cache_info()

    def check_cache_info(self):
        try:
            if not isdir(self.cache_path):
                return
            if not isfile(self.info_fp):
                self.remove_cache()
                return
            try:
                with open(self.info_fp) as f:
                    data = json.load(f)
                    if data.get("version") != VERSION:
                        self.remove_cache()
            except (OSError, json.JSONDecodeError):
                self.remove_cache()
        finally:
            with open(self.info_fp, "w+") as f:
                json.dump({"version": VERSION}, f)

    def remove_cache(self):
        if isdir(self.cache_path):
            rmtree(self.cache_path)
            mkdir(self.cache_path)


def mk_cache(name: str, end_fix: str = None) -> str:
    return path_join(CACHE_PATH, name + (("." + end_fix) if end_fix else ""))


cache_manager = CacheManager()
