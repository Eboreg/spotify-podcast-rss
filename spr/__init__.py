from spr.config import Config
from spr.engine import SPR


__version__ = "0.3.0"
VERSION = tuple(map(int, __version__.split(".")))

__all__ = ["SPR", "Config"]
