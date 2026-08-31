"""QSS builder. Takes a Palette and returns a full stylesheet string.

All theme-dependent colours flow through the Palette so that switching
between light and dark is just `app.setStyleSheet(build_qss(palette))`.
Compatibility aliases at the bottom (ACCENT, DANGER, …) resolve to the
*currently active* palette so old call sites keep working until they
are migrated.
"""

from .theme import DARK, Palette, manager


def build_qss(p: Palette) -> str:
    return f"""
* {{
    font-family: -apple-system, "SF Pro Text", "Inter", "Segoe UI", Roboto, sans-serif;
    font-size: 13px;
    color: {p.text};
}}

QMainWindow, QWidget {{
    background-color: {p.bg};
}}

QLabel, QRadioButton, QCheckBox {{
    background-color: transparent;
}}

QWidget#SectionBody, QWidget#TransparentWidget {{
    background-color: transparent;
}}

/* ---- Typography ---- */

QLabel#Brand {{
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: {p.text};
}}
QLabel#BrandDot {{
    color: {p.brand_dot};
    font-size: 28px;
    font-weight: 700;
}}

QLabel#H1 {{
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: {p.text};
}}

QLabel#H2 {{
    font-size: 16px;
    font-weight: 600;
    color: {p.text};
}}

QLabel#Subtle {{
    color: {p.text_2};
    font-size: 12px;
}}

QLabel#Caption {{
    color: {p.text_3};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
}}

QLabel#FieldLabel {{
    color: {p.text_2};
    font-size: 12px;
    font-weight: 500;
}}

/* ---- Cards ---- */

QFrame#Card {{
    background-color: {p.surface};
    border: none;
    border-radius: 8px;
}}

QLabel#SectionMarker {{
    background-color: {p.accent};
    border: none;
    border-radius: 1px;
}}

QFrame#ObjectCard {{
    background-color: {p.surface};
    border: 1px solid {p.border};
    border-left: 3px solid {p.border};
    border-radius: 8px;
}}

QFrame#ObjectCard[active="true"] {{
    background-color: {p.scoring_bg};
    border: 1px solid {p.scoring};
    border-left: 3px solid {p.scoring};
}}

QLabel#ObjectName {{
    font-size: 14px;
    font-weight: 600;
    color: {p.text};
}}

QLabel#ObjectTime {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 30px;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: {p.text};
}}

QLabel#ObjectMeta {{
    color: {p.text_2};
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.3px;
}}

QLabel#Clock {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 54px;
    font-weight: 600;
    letter-spacing: -1.5px;
    color: {p.text};
}}

QLabel#ClockBig {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 108px;
    font-weight: 700;
    letter-spacing: -4px;
    color: {p.text};
}}

QLabel#ObjectNameBig {{
    font-size: 18px;
    font-weight: 600;
    color: {p.text};
}}

QLabel#ObjectTimeBig {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 56px;
    font-weight: 700;
    letter-spacing: -1.5px;
    color: {p.text};
}}

QLabel#ObjectMetaBig {{
    color: {p.text_2};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.6px;
}}

QLabel#HotkeyBig {{
    background-color: {p.surface_2};
    border: 1px solid {p.border_2};
    border-bottom: 2px solid {p.border_2};
    border-radius: 8px;
    padding: 4px 12px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 14px;
    font-weight: 600;
    color: {p.text};
    min-width: 24px;
}}

QLabel#KpiValue {{
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: {p.text};
}}

/* ---- Hotkey keycap ---- */

QLabel#Hotkey {{
    background-color: {p.surface_2};
    border: 1px solid {p.border_2};
    border-bottom: 2px solid {p.border_2};
    border-radius: 6px;
    padding: 2px 8px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 11px;
    font-weight: 600;
    color: {p.text};
    min-width: 16px;
}}

/* ---- Status indicator ---- */

QLabel#StatusText {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
    color: {p.text_2};
}}
QLabel#StatusText[state="recording"] {{ color: {p.danger}; }}
QLabel#StatusText[state="paused"]    {{ color: {p.warning}; }}
QLabel#StatusText[state="done"]      {{ color: {p.info}; }}
QLabel#StatusText[state="ready"]     {{ color: {p.text_2}; }}

QLabel#RecordingBadge {{
    background-color: transparent;
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 5px 9px;
    color: {p.text_2};
    font-size: 10px;
    font-weight: 700;
}}
QLabel#RecordingBadge[state="recording"] {{
    color: {p.danger};
    border-color: {p.danger};
}}
QLabel#RecordingBadge[state="starting"] {{ color: {p.warning}; }}
QLabel#RecordingBadge[state="saved"] {{ color: {p.success}; border-color: {p.success}; }}
QLabel#RecordingBadge[state="error"] {{ color: {p.danger}; border-color: {p.danger}; }}

/* ---- Video placeholder ---- */

QLabel#VideoLabel {{
    background-color: {p.video_bg};
    border-radius: 14px;
    border: 1px solid {p.video_border};
    color: {p.text_3};
}}

/* ---- Buttons ---- */

QPushButton {{
    background-color: {p.surface};
    border: 1px solid {p.border};
    border-radius: 8px;
    padding: 9px 16px;
    color: {p.text};
    font-weight: 500;
}}
QPushButton:hover    {{ background-color: {p.surface_2}; border-color: {p.border_2}; }}
QPushButton:pressed  {{ background-color: {p.bg}; }}
QPushButton:disabled {{ color: {p.text_3}; background-color: {p.surface}; }}

QPushButton#Primary {{
    background-color: {p.accent};
    border: 1px solid {p.accent};
    color: {p.accent_text};
    font-weight: 600;
}}
QPushButton#Primary:hover   {{ background-color: {p.accent_2}; border-color: {p.accent_2}; }}
QPushButton#Primary:pressed {{ background-color: {p.accent_pressed}; }}
QPushButton#Primary:disabled{{ background-color: {p.surface}; color: {p.text_3}; border-color: {p.border}; }}

QPushButton#Danger {{
    background-color: transparent;
    border: 1px solid {p.danger};
    color: {p.danger};
    font-weight: 600;
}}
QPushButton#Danger:hover    {{ background-color: rgba(248, 113, 113, 30); }}
QPushButton#Danger:disabled {{ color: {p.text_3}; border-color: {p.border}; }}

QPushButton#Ghost {{
    background-color: transparent;
    border: 1px solid transparent;
    color: {p.text_2};
}}
QPushButton#Ghost:hover {{
    background-color: {p.surface};
    color: {p.text};
}}

QPushButton#Chip {{
    background-color: transparent;
    border: 1px solid {p.border};
    border-radius: 16px;
    padding: 6px 14px;
    color: {p.text_2};
    font-weight: 500;
    font-size: 12px;
}}
QPushButton#Chip:hover {{
    border-color: {p.border_2};
    color: {p.text};
}}
QPushButton#Chip[selected="true"] {{
    background-color: {p.accent};
    border-color: {p.accent};
    color: {p.accent_text};
}}

QPushButton#IconBtn {{
    background-color: transparent;
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 4px 8px;
    color: {p.text_2};
    min-width: 24px;
}}
QPushButton#IconBtn:hover {{ color: {p.text}; border-color: {p.border_2}; }}

QPushButton#ThemeToggle {{
    background-color: transparent;
    border: 1px solid {p.border};
    border-radius: 14px;
    padding: 4px 10px;
    color: {p.text_2};
    font-size: 14px;
    min-width: 24px;
}}
QPushButton#ThemeToggle:hover {{
    background-color: {p.surface};
    color: {p.text};
    border-color: {p.border_2};
}}

/* ---- Inputs ---- */

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {p.surface_2};
    border: 1px solid {p.border};
    border-radius: 6px;
    padding: 8px 10px;
    selection-background-color: {p.accent};
    selection-color: {p.accent_text};
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {p.accent};
}}
QLineEdit:disabled, QSpinBox:disabled {{
    color: {p.text_3};
    background-color: {p.bg};
}}

QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {p.surface};
    border: 1px solid {p.border_2};
    border-radius: 8px;
    selection-background-color: {p.accent};
    selection-color: {p.accent_text};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    width: 18px;
    border-left: 1px solid {p.border};
    background: transparent;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {p.surface_2};
}}

/* ---- Tables ---- */

QTableWidget, QTableView {{
    background-color: {p.surface};
    border: 1px solid {p.border};
    border-radius: 10px;
    gridline-color: {p.border};
    selection-background-color: {p.accent};
    selection-color: {p.accent_text};
}}
QTableWidget::item, QTableView::item {{ padding: 8px 10px; }}
QHeaderView::section {{
    background-color: {p.surface_2};
    color: {p.text_2};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {p.border};
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.4px;
}}

/* ---- Scrollbars ---- */

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {p.border_2};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {p.text_3}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

QScrollArea#ObjectScroll {{
    background-color: transparent;
    border: none;
}}

/* ---- Plain text ---- */

QPlainTextEdit, QTextEdit {{
    background-color: {p.surface};
    border: 1px solid {p.border};
    border-radius: 10px;
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 12px;
    color: {p.text_2};
    padding: 8px;
}}

/* ---- Misc ---- */

QRadioButton, QCheckBox {{ spacing: 8px; color: {p.text}; }}

QToolTip {{
    background-color: {p.surface_2};
    color: {p.text};
    border: 1px solid {p.border_2};
    border-radius: 6px;
    padding: 4px 8px;
}}

QMenu {{
    background-color: {p.surface};
    border: 1px solid {p.border_2};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{ padding: 6px 16px; border-radius: 4px; }}
QMenu::item:selected {{ background-color: {p.accent}; color: {p.accent_text}; }}
"""


# ----------------------------------------------------------------------
# Backwards-compatible color constants — resolve to the currently active
# palette. Kept so existing imports (`from .style import ACCENT, …`) keep
# working without forcing every caller to be rewritten.
# ----------------------------------------------------------------------

def _p():
    try:
        return manager().palette()
    except Exception:
        return DARK


def __getattr__(name: str):
    aliases = {
        "ACCENT":      lambda p: p.accent,
        "ACCENT_2":    lambda p: p.accent_2,
        "ACCENT_BG":   lambda p: p.scoring_bg,
        "BG":          lambda p: p.bg,
        "SURFACE":     lambda p: p.surface,
        "SURFACE_2":   lambda p: p.surface_2,
        "BORDER":      lambda p: p.border,
        "BORDER_2":    lambda p: p.border_2,
        "TEXT":        lambda p: p.text,
        "TEXT_2":      lambda p: p.text_2,
        "TEXT_3":      lambda p: p.text_3,
        "SUCCESS":     lambda p: p.success,
        "WARNING":     lambda p: p.warning,
        "DANGER":      lambda p: p.danger,
        "INFO":        lambda p: p.info,
        "SCORING":     lambda p: p.scoring,
    }
    if name in aliases:
        return aliases[name](_p())
    if name == "QSS":
        return build_qss(_p())
    raise AttributeError(name)
