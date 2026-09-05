import unittest
from unittest.mock import patch

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

from squeak import __version__
from squeak.main_window import MainWindow
from squeak.update_checker import ReleaseInfo


class FakeUpdateChecker(QObject):
    completed = Signal(object)
    failed = Signal(str)

    def check(self):
        return True


class FakeSettings:
    def __init__(self, skipped_version=""):
        self.skipped_version = skipped_version

    def value(self, _key, default=""):
        return self.skipped_version or default

    def setValue(self, _key, value):
        self.skipped_version = value


class MainWindowUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.checker = FakeUpdateChecker()
        self.window = MainWindow(
            update_checker=self.checker, automatic_update_checks=False
        )
        self.window._settings = FakeSettings()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    @staticmethod
    def newer_release():
        return ReleaseInfo(
            version="9.0.0",
            tag_name="v9.0.0",
            title="Squeak v9.0.0",
            notes="Test release",
        )

    def test_automatic_prompt_waits_until_scoring_is_left(self):
        self.window.stack.setCurrentWidget(self.window.scoring_view)

        with patch.object(self.window, "_show_update_prompt") as show_prompt:
            self.window._on_update_check_completed(self.newer_release())

        show_prompt.assert_not_called()
        self.assertEqual(self.window._pending_update.version, "9.0.0")

    def test_skipped_version_does_not_prompt_automatically(self):
        self.window._settings = FakeSettings(skipped_version="9.0.0")

        with patch.object(self.window, "_show_update_prompt") as show_prompt:
            self.window._on_update_check_completed(self.newer_release())

        show_prompt.assert_not_called()

    def test_manual_check_reports_when_current(self):
        release = ReleaseInfo(
            version=__version__,
            tag_name=f"v{__version__}",
            title=f"Squeak v{__version__}",
            notes="",
        )
        self.window._manual_update_check = True

        with patch.object(QMessageBox, "information") as information:
            self.window._on_update_check_completed(release)

        information.assert_called_once()


if __name__ == "__main__":
    unittest.main()
