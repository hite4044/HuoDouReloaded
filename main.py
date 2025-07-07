from os import getcwd, environ
from os.path import join

environ["PATH"] += ";" + join(getcwd(), "base_library")
# noinspection PyUnresolvedReferences
import engine.game
