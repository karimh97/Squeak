"""Squeak visual theme. Dark with a pink accent, Linear/Vercel-style rhythm."""

# Palette
BG          = "#0A0B0F"
SURFACE     = "#13151B"
SURFACE_2   = "#1A1D26"
BORDER      = "#252934"
BORDER_2    = "#323847"
TEXT        = "#F5F5F7"
TEXT_2      = "#9CA3AF"
TEXT_3      = "#6B7280"
ACCENT      = "#EC4899"       # Squeak pink
ACCENT_2    = "#F472B6"
ACCENT_BG   = "#2A1422"
SUCCESS     = "#34D399"
WARNING     = "#FBBF24"
DANGER      = "#F87171"
INFO        = "#60A5FA"


QSS = f"""
* {{
    font-family: -apple-system, "SF Pro Text", "Inter", "Segoe UI", Roboto, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QWidget {{
    background-color: {BG};
}}

/* ---- Typography ---- */

QLabel#Brand {{
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: {TEXT};
}}
QLabel#BrandDot {{
    color: {ACCENT};
    font-size: 28px;
    font-weight: 700;
}}

QLabel#H1 {{
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: {TEXT};
}}

QLabel#H2 {{
    font-size: 16px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel#Subtle {{
    color: {TEXT_2};
    font-size: 12px;
}}

QLabel#Caption {{
    color: {TEXT_3};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
}}

QLabel#FieldLabel {{
    color: {TEXT_2};
    font-size: 12px;
    font-weight: 500;
}}

/* ---- Cards ---- */

QFrame#Card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QFrame#ObjectCard {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-left: 3px solid {BORDER};
    border-radius: 12px;
}}

QFrame#ObjectCard[active="true"] {{
    background-color: {ACCENT_BG};
    border: 1px solid {ACCENT};
    border-left: 3px solid {ACCENT};
}}

QLabel#ObjectName {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel#ObjectTime {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 30px;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: {TEXT};
}}

QLabel#ObjectMeta {{
    color: {TEXT_2};
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.3px;
}}

QLabel#Clock {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 54px;
    font-weight: 600;
    letter-spacing: -1.5px;
    color: {TEXT};
}}

QLabel#ClockBig {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 108px;
    font-weight: 700;
    letter-spacing: -4px;
    color: {TEXT};
}}

QLabel#ObjectNameBig {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel#ObjectTimeBig {{
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 56px;
    font-weight: 700;
    letter-spacing: -1.5px;
    color: {TEXT};
}}

QLabel#ObjectMetaBig {{
    color: {TEXT_2};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.6px;
}}

QLabel#HotkeyBig {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER_2};
    border-bottom: 2px solid {BORDER_2};
    border-radius: 8px;
    padding: 4px 12px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 14px;
    font-weight: 600;
    color: {TEXT};
    min-width: 24px;
}}

QLabel#KpiValue {{
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: {TEXT};
}}

/* ---- Hotkey keycap ---- */

QLabel#Hotkey {{
    background-color: {SURFACE_2};
    border: 1px solid {BORDER_2};
    border-bottom: 2px solid {BORDER_2};
    border-radius: 6px;
    padding: 2px 8px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 11px;
    font-weight: 600;
    color: {TEXT};
    min-width: 16px;
}}

/* ---- Status indicator ---- */

QLabel#StatusText {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
    color: {TEXT_2};
}}
QLabel#StatusText[state="recording"] {{ color: {DANGER}; }}
QLabel#StatusText[state="paused"]    {{ color: {WARNING}; }}
QLabel#StatusText[state="done"]      {{ color: {INFO}; }}
QLabel#StatusText[state="ready"]     {{ color: {TEXT_2}; }}

/* ---- Buttons ---- */

QPushButton {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 16px;
    color: {TEXT};
    font-weight: 500;
}}
QPushButton:hover    {{ background-color: {SURFACE_2}; border-color: {BORDER_2}; }}
QPushButton:pressed  {{ background-color: {BG}; }}
QPushButton:disabled {{ color: {TEXT_3}; background-color: {SURFACE}; }}

QPushButton#Primary {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
    color: white;
    font-weight: 600;
}}
QPushButton#Primary:hover   {{ background-color: {ACCENT_2}; border-color: {ACCENT_2}; }}
QPushButton#Primary:pressed {{ background-color: #D03487; }}
QPushButton#Primary:disabled{{ background-color: {SURFACE}; color: {TEXT_3}; border-color: {BORDER}; }}

QPushButton#Danger {{
    background-color: transparent;
    border: 1px solid {DANGER};
    color: {DANGER};
    font-weight: 600;
}}
QPushButton#Danger:hover    {{ background-color: rgba(248, 113, 113, 30); }}
QPushButton#Danger:disabled {{ color: {TEXT_3}; border-color: {BORDER}; }}

QPushButton#Ghost {{
    background-color: transparent;
    border: 1px solid transparent;
    color: {TEXT_2};
}}
QPushButton#Ghost:hover {{
    background-color: {SURFACE};
    color: {TEXT};
}}

QPushButton#Chip {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 6px 14px;
    color: {TEXT_2};
    font-weight: 500;
    font-size: 12px;
}}
QPushButton#Chip:hover {{
    border-color: {BORDER_2};
    color: {TEXT};
}}
QPushButton#Chip[selected="true"] {{
    background-color: {ACCENT};
    border-color: {ACCENT};
    color: white;
}}

QPushButton#IconBtn {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 8px;
    color: {TEXT_2};
    min-width: 24px;
}}
QPushButton#IconBtn:hover {{ color: {TEXT}; border-color: {BORDER_2}; }}

/* ---- Inputs ---- */

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: {ACCENT};
    selection-color: white;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
}}
QLineEdit:disabled, QSpinBox:disabled {{
    color: {TEXT_3};
    background-color: {SURFACE};
}}

QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_2};
    border-radius: 8px;
    selection-background-color: {ACCENT};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    width: 18px;
    border-left: 1px solid {BORDER};
    background: transparent;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {SURFACE_2};
}}

/* ---- Tables ---- */

QTableWidget, QTableView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BORDER};
    selection-background-color: {ACCENT};
    selection-color: white;
}}
QTableWidget::item, QTableView::item {{ padding: 8px 10px; }}
QHeaderView::section {{
    background-color: {SURFACE_2};
    color: {TEXT_2};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
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
    background: {BORDER_2};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_3}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

/* ---- Plain text ---- */

QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    font-family: "SF Mono", "JetBrains Mono", "Menlo", monospace;
    font-size: 12px;
    color: {TEXT_2};
    padding: 8px;
}}

/* ---- Misc ---- */

QRadioButton, QCheckBox {{ spacing: 8px; color: {TEXT}; }}

QToolTip {{
    background-color: {SURFACE_2};
    color: {TEXT};
    border: 1px solid {BORDER_2};
    border-radius: 6px;
    padding: 4px 8px;
}}

QMenu {{
    background-color: {SURFACE};
    border: 1px solid {BORDER_2};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{ padding: 6px 16px; border-radius: 4px; }}
QMenu::item:selected {{ background-color: {ACCENT}; color: white; }}
"""
