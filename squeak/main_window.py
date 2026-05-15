"""Top-level window: stacked setup / scoring / results."""

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from .results_view import ResultsView
from .scoring_view import ScoringView
from .setup_view import SetupView, TrialConfig


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Squeak")
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

        quit_sc = QShortcut(QKeySequence.Quit, self)
        quit_sc.activated.connect(self.close)

    # ------------------------------------------------------------------
    def _show_setup(self) -> None:
        self.stack.setCurrentWidget(self.setup_view)

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
