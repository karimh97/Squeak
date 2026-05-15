"""Loaders for the Squeak brand assets (wordmark + mouse logo)."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

_ASSETS = Path(__file__).resolve().parent.parent / "build_assets"

LOGO_DARK_BG_PATH = _ASSETS / "squeak_logo_white.png"   # white on transparent — for dark UI
LOGO_LIGHT_BG_PATH = _ASSETS / "squeak_logo.png"        # black on white — for README, papers

_cache: dict[tuple[str, int], QPixmap] = {}


def logo_pixmap(height: int, on_dark: bool = True) -> Optional[QPixmap]:
    """Return the wordmark+mouse logo scaled to the given pixel height.

    Cached per (variant, height). Returns None if the asset is missing
    (so callers can fall back to the text wordmark).
    """
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
