__version__ = "0.2.0"
__all__ = ["__version__", "get_cache_root", "get_config_root", "get_project_root"]

from pathlib import Path


def get_cache_root() -> Path:
    folder = Path.home() / ".cache" / "tcg-player-wrapper"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_config_root() -> Path:
    folder = Path.home() / ".config" / "tcg-player-wrapper"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_project_root() -> Path:
    return Path(__file__).parent.parent
