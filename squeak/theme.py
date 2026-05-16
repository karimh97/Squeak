"""Theme system: light / dark palettes plus a manager that applies QSS app-wide.

The current theme is persisted in `~/.config/squeak/theme.json` and can be
toggled at runtime — widgets that have hard-coded colors (status dots, video
placeholder, etc.) listen to `manager().changed` and refresh themselves.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


CONFIG_DIR = Path.home() / ".config" / "squeak"
THEME_PATH = CONFIG_DIR / "theme.json"


@dataclass(frozen=True)
class Palette:
    name: str
    # Surfaces
    bg: str
    surface: str
    surface_2: str
    border: str
    border_2: str
    # Text
    text: str
    text_2: str
    text_3: str
    # Brand / selector accent (chips, primary buttons, focus rings)
    accent: str
    accent_2: str           # lighter variant for hover
    accent_pressed: str
    accent_text: str        # text color that sits on top of accent
    # Semantic
    scoring: str            # color used when an object is actively being scored
    scoring_bg: str         # tinted background of an active object card
    success: str
    warning: str
    danger: str
    info: str
    # Specific surfaces
    video_bg: str
    video_border: str
    # Brand accent dot (the "." of "Squeak." — always pink, intentional)
    brand_dot: str = "#EC4899"


DARK = Palette(
    name        = "dark",
    bg          = "#0A0B0F",
    surface     = "#13151B",
    surface_2   = "#1A1D26",
    border      = "#252934",
    border_2    = "#323847",
    text        = "#F5F5F7",
    text_2      = "#9CA3AF",
    text_3      = "#6B7280",
    accent      = "#EC4899",   # pink
    accent_2    = "#F472B6",
    accent_pressed = "#D03487",
    accent_text = "#FFFFFF",
    scoring     = "#EC4899",   # pink scoring in dark mode (matches brand)
    scoring_bg  = "#2A1422",
    success     = "#34D399",
    warning     = "#FBBF24",
    danger      = "#F87171",
    info        = "#60A5FA",
    video_bg    = "#05070A",
    video_border= "#1A1D26",
)

LIGHT = Palette(
    name        = "light",
    bg          = "#F2F2F5",
    surface     = "#FFFFFF",
    surface_2   = "#F8F8FA",
    border      = "#E0E0E5",
    border_2    = "#C7C7CC",
    text        = "#0A0B0F",
    text_2      = "#5C6573",
    text_3      = "#9CA3AF",
    accent      = "#0A0B0F",   # black selector per spec
    accent_2    = "#1F2937",
    accent_pressed = "#000000",
    accent_text = "#FFFFFF",
    scoring     = "#10B981",   # green scoring in light mode per spec
    scoring_bg  = "#D1FAE5",
    success     = "#10B981",
    warning     = "#D97706",
    danger      = "#DC2626",
    info        = "#2563EB",
    video_bg    = "#1A1D26",   # dark video frame stands out on light bg
    video_border= "#D1D1D6",
)


PALETTES = {"dark": DARK, "light": LIGHT}


class ThemeManager(QObject):
    """Singleton-ish theme controller. Emits `changed(name)` after switch."""

    changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._name = self._load() or "dark"

    # --- public API ---------------------------------------------------

    def name(self) -> str:
        return self._name

    def palette(self) -> Palette:
        return PALETTES[self._name]

    def is_dark(self) -> bool:
        return self._name == "dark"

    def set_theme(self, name: str) -> None:
        if name not in PALETTES or name == self._name:
            return
        self._name = name
        self._save()
        self.apply()
        self.changed.emit(name)

    def toggle(self) -> None:
        self.set_theme("light" if self._name == "dark" else "dark")

    def apply(self) -> None:
        """Push the current palette to QApplication (QSS + base QPalette)."""
        app = QApplication.instance()
        if app is None:
            return
        from .style import build_qss
        p = self.palette()
        app.setStyleSheet(build_qss(p))
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(p.bg))
        pal.setColor(QPalette.WindowText, QColor(p.text))
        pal.setColor(QPalette.Base, QColor(p.surface))
        pal.setColor(QPalette.AlternateBase, QColor(p.surface_2))
        pal.setColor(QPalette.Text, QColor(p.text))
        pal.setColor(QPalette.Button, QColor(p.surface))
        pal.setColor(QPalette.ButtonText, QColor(p.text))
        pal.setColor(QPalette.Highlight, QColor(p.accent))
        pal.setColor(QPalette.HighlightedText, QColor(p.accent_text))
        pal.setColor(QPalette.ToolTipBase, QColor(p.surface_2))
        pal.setColor(QPalette.ToolTipText, QColor(p.text))
        pal.setColor(QPalette.PlaceholderText, QColor(p.text_2))
        pal.setColor(QPalette.Mid, QColor(p.border_2))
        app.setPalette(pal)

    # --- persistence --------------------------------------------------

    def _save(self) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            THEME_PATH.write_text(json.dumps({"theme": self._name}))
        except OSError:
            pass

    def _load(self) -> Optional[str]:
        if not THEME_PATH.exists():
            return None
        try:
            return json.loads(THEME_PATH.read_text()).get("theme")
        except (OSError, json.JSONDecodeError):
            return None


_singleton: Optional[ThemeManager] = None


def manager() -> ThemeManager:
    global _singleton
    if _singleton is None:
        _singleton = ThemeManager()
    return _singleton
