"""Application entry point."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .icon import build_icon
from .main_window import MainWindow
from .theme import manager as theme_manager


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Squeak")
    app.setApplicationDisplayName("Squeak")
    app.setOrganizationName("Squeak")
    app.setStyle("Fusion")

    # Apply whichever theme the user last picked (defaults to dark).
    theme_manager().apply()

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
