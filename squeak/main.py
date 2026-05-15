"""Application entry point."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from .icon import build_icon
from .main_window import MainWindow
from .style import BG, BORDER_2, SURFACE, SURFACE_2, TEXT, TEXT_2, QSS, ACCENT


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Squeak")
    app.setApplicationDisplayName("Squeak")
    app.setOrganizationName("Squeak")
    app.setStyle("Fusion")

    # Base palette — keeps non-QSS-styled widgets (dialogs, menus) in theme.
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(BG))
    pal.setColor(QPalette.WindowText, QColor(TEXT))
    pal.setColor(QPalette.Base, QColor(BG))
    pal.setColor(QPalette.AlternateBase, QColor(SURFACE))
    pal.setColor(QPalette.Text, QColor(TEXT))
    pal.setColor(QPalette.Button, QColor(SURFACE))
    pal.setColor(QPalette.ButtonText, QColor(TEXT))
    pal.setColor(QPalette.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.ToolTipBase, QColor(SURFACE_2))
    pal.setColor(QPalette.ToolTipText, QColor(TEXT))
    pal.setColor(QPalette.PlaceholderText, QColor(TEXT_2))
    pal.setColor(QPalette.Mid, QColor(BORDER_2))
    app.setPalette(pal)
    app.setStyleSheet(QSS)

    # Prefer .icns / .png from build_assets if present, otherwise paint at runtime
    repo_root = Path(__file__).resolve().parent.parent
    icns = repo_root / "build_assets" / "icon.icns"
    png  = repo_root / "build_assets" / "icon.png"
    if icns.exists():
        app.setWindowIcon(QIcon(str(icns)))
    elif png.exists():
        app.setWindowIcon(QIcon(str(png)))
    else:
        app.setWindowIcon(build_icon(512))

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
