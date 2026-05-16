"""Loaders for the Squeak brand assets (wordmark + mouse logo)."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from .theme import manager as theme_manager

_ASSETS = Path(__file__).resolve().parent.parent / "build_assets"

# Three variants of the same artwork:
#   *_white.png — white on transparent, for the dark UI
#   *_black.png — black on transparent, for the light UI
#   *.png       — black on white, for README / papers / external embeds
LOGO_DARK_BG_PATH  = _ASSETS / "squeak_logo_white.png"
LOGO_LIGHT_BG_PATH = _ASSETS / "squeak_logo_black.png"
LOGO_SOURCE_PATH   = _ASSETS / "squeak_logo.png"

_cache: dict[tuple[str, int], QPixmap] = {}


def logo_pixmap(height: int, on_dark: Optional[bool] = None) -> Optional[QPixmap]:
    """Return the wordmark+mouse logo scaled to the given pixel height.

    `on_dark` defaults to the current theme. Cached per (variant, height).
    Returns None if the asset is missing (so callers can fall back to
    the text wordmark).
    """
    if on_dark is None:
        on_dark = theme_manager().is_dark()
    path = LOGO_DARK_BG_PATH if on_dark else LOGO_LIGHT_BG_PATH
    key = (str(path), int(height))
    if key in _cache:
        return _cache[key]
    if not path.exists():
        return None
    px = QPixmap(str(path))
    if px.isNull():
        return None
    # Use device-pixel-ratio aware scaling for crisp rendering on retina
    scaled = px.scaledToHeight(height * 2, Qt.SmoothTransformation)
    scaled.setDevicePixelRatio(2.0)
    _cache[key] = scaled
    return scaled
