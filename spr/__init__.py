try:
    from spr.config import Config
    from spr.engine import SPR
except ImportError:
    pass

__version__ = "0.4.0"
VERSION = tuple(map(int, __version__.split(".")))

__all__ = ["SPR", "Config"]
