"""Top-level window: stacked setup / scoring / results."""

from __future__ import annotations

from PySide6.QtCore import QSettings, QTimer, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

from . import __version__
from .results_view import ResultsView
from .scoring_view import ScoringView
from .setup_view import SetupView, TrialConfig
from .update_checker import (
    LATEST_RELEASE_PAGE,
    ReleaseInfo,
    UpdateChecker,
    is_newer_version,
)


class MainWindow(QMainWindow):
    def __init__(
        self,
        update_checker: UpdateChecker | None = None,
        automatic_update_checks: bool = True,
    ) -> None:
        super().__init__()
        self.setWindowTitle(f"Squeak {__version__}")
        self.resize(1320, 860)
        self.setMinimumSize(1100, 720)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.setup_view = SetupView()
        self.scoring_view = ScoringView()
        self.results_view = ResultsView()

        for w in (self.setup_view, self.scoring_view, self.results_view):
            self.stack.addWidget(w)

        self.setup_view.start_requested.connect(self._on_start_trial)
        self.scoring_view.trial_finished.connect(self._on_trial_finished)
        self.scoring_view.exit_requested.connect(self._show_setup)
        self.results_view.new_trial_requested.connect(self._on_new_trial_same_config)
        self.results_view.back_to_setup_requested.connect(self._show_setup)

        self._last_config: TrialConfig | None = None
        self._pending_update: ReleaseInfo | None = None
        self._manual_update_check = False
        self._settings = QSettings("Squeak", "Squeak")

        self.update_checker = update_checker or UpdateChecker(self)
        self.update_checker.completed.connect(self._on_update_check_completed)
        self.update_checker.failed.connect(self._on_update_check_failed)
        self._build_help_menu()

        quit_sc = QShortcut(QKeySequence.Quit, self)
        quit_sc.activated.connect(self.close)

        if automatic_update_checks:
            QTimer.singleShot(1_500, self._check_for_updates)

    def _build_help_menu(self) -> None:
        help_menu = self.menuBar().addMenu("&Help")
        self.check_updates_action = QAction("Check for Updates...", self)
        self.check_updates_action.triggered.connect(
            lambda _checked=False: self._check_for_updates(manual=True)
        )
        help_menu.addAction(self.check_updates_action)
        help_menu.addSeparator()

        about_action = QAction("About Squeak", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ------------------------------------------------------------------
    def _show_setup(self) -> None:
        self.stack.setCurrentWidget(self.setup_view)
        if self._pending_update is not None:
            release = self._pending_update
            self._pending_update = None
            QTimer.singleShot(0, lambda: self._show_update_prompt(release))

    def _on_start_trial(self, config: TrialConfig) -> None:
        self._last_config = config
        self.scoring_view.load_trial(config)
        self.stack.setCurrentWidget(self.scoring_view)

    def _on_trial_finished(self, scorer, meta: dict) -> None:
        self.results_view.load_results(scorer, meta)
        self.stack.setCurrentWidget(self.results_view)

    def _on_new_trial_same_config(self) -> None:
        if self._last_config is None:
            self._show_setup(); return
        self.scoring_view.load_trial(self._last_config)
        self.stack.setCurrentWidget(self.scoring_view)

    # ------------------------------------------------------------------
    def _check_for_updates(self, manual: bool = False) -> None:
        if not self.update_checker.check():
            if manual:
                QMessageBox.information(
                    self, "Checking for updates", "An update check is already running."
                )
            return
        self._manual_update_check = manual
        self.check_updates_action.setEnabled(False)

    def _on_update_check_completed(self, release: ReleaseInfo) -> None:
        manual = self._manual_update_check
        self._manual_update_check = False
        self.check_updates_action.setEnabled(True)

        try:
            newer = is_newer_version(release.version)
        except ValueError:
            if manual:
                QMessageBox.warning(
                    self, "Update check failed", "GitHub returned an invalid version."
                )
            return

        if not newer:
            if manual:
                QMessageBox.information(
                    self,
                    "Squeak is up to date",
                    f"You are using the latest version of Squeak ({__version__}).",
                )
            return

        skipped = str(self._settings.value("updates/skipped_version", ""))
        if not manual and skipped == release.version:
            return

        if not manual and self.stack.currentWidget() is not self.setup_view:
            self._pending_update = release
            return
        self._show_update_prompt(release)

    def _on_update_check_failed(self, message: str) -> None:
        manual = self._manual_update_check
        self._manual_update_check = False
        self.check_updates_action.setEnabled(True)
        if manual:
            QMessageBox.warning(self, "Update check failed", message)

    def _show_update_prompt(self, release: ReleaseInfo) -> None:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle("Squeak update available")
        dialog.setText(f"Squeak {release.version} is available")
        dialog.setInformativeText(
            f"You are using Squeak {__version__}. Updating is optional, so you "
            "can keep the same version for an active experiment."
        )
        if release.notes:
            dialog.setDetailedText(release.notes[:8_000])

        view_button = dialog.addButton(
            "View release", QMessageBox.ButtonRole.AcceptRole
        )
        dialog.addButton("Remind me later", QMessageBox.ButtonRole.RejectRole)
        skip_button = dialog.addButton(
            "Skip this version", QMessageBox.ButtonRole.DestructiveRole
        )
        dialog.setDefaultButton(view_button)
        dialog.exec()

        if dialog.clickedButton() is view_button:
            QDesktopServices.openUrl(QUrl(LATEST_RELEASE_PAGE))
        elif dialog.clickedButton() is skip_button:
            self._settings.setValue("updates/skipped_version", release.version)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About Squeak",
            f"Squeak {__version__}\n\n"
            "Manual scoring for rodent object exploration.\n"
            "Created by Karim Abouelnaga.",
        )
