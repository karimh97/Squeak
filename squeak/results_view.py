"""Results screen — KPI cards, per-object summary, CSV export."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .branding import logo_pixmap
from .exporter import append_to_master, export_trial
from .scorer import Scorer
from .theme import manager as theme_manager


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _fmt_clock(secs: float) -> str:
    secs = max(0.0, secs)
    m = int(secs // 60)
    s = int(secs % 60)
    cs = int((secs - int(secs)) * 100)
    return f"{m:02d}:{s:02d}.{cs:02d}"


class _Kpi(QFrame):
    """One KPI card."""

    def __init__(self, caption: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(8)
        self.caption_lbl = QLabel(caption.upper()); self.caption_lbl.setObjectName("Caption")
        self.value_lbl = QLabel(value); self.value_lbl.setObjectName("KpiValue")
        lay.addWidget(self.caption_lbl)
        lay.addWidget(self.value_lbl)
        lay.addStretch(1)


class ResultsView(QWidget):
    new_trial_requested = Signal()
    back_to_setup_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scorer: Optional[Scorer] = None
        self.meta: dict = {}
        self._di_value: Optional[float] = None
        self._build_ui()

    # ------------------------------------------------------------------
    # Branding / theme helpers
    # ------------------------------------------------------------------
    def _refresh_logo(self) -> None:
        px = logo_pixmap(height=28)
        if px is not None:
            self.logo_lbl.setPixmap(px)

    def _refresh_theme_btn(self) -> None:
        self.theme_btn.setText("☀" if theme_manager().is_dark() else "🌙")
        self.theme_btn.setToolTip(
            f"Switch to {'light' if theme_manager().is_dark() else 'dark'} mode"
        )

    def _refresh_di_color(self) -> None:
        p = theme_manager().palette()
        if self._di_value is None:
            self.kpi_di.value_lbl.setStyleSheet("")
            return
        di = self._di_value
        color = p.success if di > 0.05 else p.danger if di < -0.05 else p.text_2
        self.kpi_di.value_lbl.setStyleSheet(
            f"color: {color}; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;"
        )

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(22)

        # --- Brand + title ---
        brand_row = QHBoxLayout(); brand_row.setSpacing(0)
        self.logo_lbl = QLabel()
        self._refresh_logo()
        brand_row.addWidget(self.logo_lbl)
        brand_row.addStretch(1)
        self.theme_btn = QPushButton(); self.theme_btn.setObjectName("ThemeToggle")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(lambda: theme_manager().toggle())
        self._refresh_theme_btn()
        brand_row.addWidget(self.theme_btn)
        root.addLayout(brand_row)

        theme_manager().changed.connect(
            lambda _name: (self._refresh_logo(), self._refresh_theme_btn(), self._refresh_di_color())
        )

        title_block = QVBoxLayout(); title_block.setSpacing(4)
        self.title = QLabel("Trial complete"); self.title.setObjectName("H1")
        self.subtitle = QLabel(""); self.subtitle.setObjectName("Subtle")
        title_block.addWidget(self.title); title_block.addWidget(self.subtitle)
        root.addLayout(title_block)

        # --- KPI row ---
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(14)
        self.kpi_duration = _Kpi("Trial duration", "00:00.00")
        self.kpi_total = _Kpi("Total exploration", "0.00 s")
        self.kpi_di = _Kpi("Discrimination index", "—")
        kpi_row.addWidget(self.kpi_duration, 1)
        kpi_row.addWidget(self.kpi_total, 1)
        kpi_row.addWidget(self.kpi_di, 1)
        root.addLayout(kpi_row)

        # --- Table ---
        table_card = QFrame(); table_card.setObjectName("Card")
        table_lay = QVBoxLayout(table_card); table_lay.setContentsMargins(20, 16, 20, 20); table_lay.setSpacing(12)
        table_cap = QLabel("PER-OBJECT RESULTS"); table_cap.setObjectName("Caption")
        table_lay.addWidget(table_cap)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Object", "Total time (s)", "Bouts", "Mean bout (s)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("QTableWidget { border: none; }")
        self.table.setMinimumHeight(200)
        table_lay.addWidget(self.table)
        root.addWidget(table_card, 1)

        # --- Footer ---
        footer = QHBoxLayout(); footer.setSpacing(10)
        back_btn = QPushButton("← Back to setup"); back_btn.setObjectName("Ghost")
        back_btn.clicked.connect(self.back_to_setup_requested.emit)
        new_btn = QPushButton("New trial (same config)")
        new_btn.clicked.connect(self.new_trial_requested.emit)
        export_btn = QPushButton("Save CSV…")
        export_btn.clicked.connect(self._on_save_csv)
        master_btn = QPushButton("Append to master…")
        master_btn.clicked.connect(self._on_append_master)
        save_both_btn = QPushButton("Quick save (both)")
        save_both_btn.setObjectName("Primary")
        save_both_btn.setMinimumHeight(40); save_both_btn.setCursor(Qt.PointingHandCursor)
        save_both_btn.clicked.connect(self._on_quick_save)
        footer.addWidget(back_btn)
        footer.addStretch(1)
        footer.addWidget(new_btn)
        footer.addWidget(export_btn)
        footer.addWidget(master_btn)
        footer.addWidget(save_both_btn)
        root.addLayout(footer)

    # ------------------------------------------------------------------
    def load_results(self, scorer: Scorer, meta: dict) -> None:
        self.scorer = scorer
        self.meta = meta

        bits = []
        if meta.get("animal_id"): bits.append(f"Animal {meta['animal_id']}")
        if meta.get("trial_name"): bits.append(meta["trial_name"])
        if meta.get("session"): bits.append(f"Session {meta['session']}")
        if meta.get("group"): bits.append(meta["group"])
        self.subtitle.setText("  ·  ".join(bits))

        stats = scorer.stats()
        total = sum(s.total_time for s in stats)

        self.kpi_duration.value_lbl.setText(_fmt_clock(scorer.now()))
        self.kpi_total.value_lbl.setText(f"{total:.2f} s")
        self._di_value: float | None = None
        if len(stats) == 2 and total > 0:
            a, b = stats
            self._di_value = (b.total_time - a.total_time) / total
            self.kpi_di.value_lbl.setText(f"{self._di_value:+.3f}")
            self.kpi_di.caption_lbl.setText(f"DI = ({b.name.upper()} − {a.name.upper()}) / TOTAL")
        else:
            self.kpi_di.value_lbl.setText("—")
            self.kpi_di.caption_lbl.setText("DI (REQUIRES EXACTLY 2 OBJECTS)")
        self._refresh_di_color()

        self.table.setRowCount(0)
        for s in stats:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(s.name))
            self.table.setItem(r, 1, QTableWidgetItem(f"{s.total_time:.3f}"))
            self.table.setItem(r, 2, QTableWidgetItem(str(s.bouts)))
            self.table.setItem(r, 3, QTableWidgetItem(f"{s.mean_bout:.3f}"))
        # Totals row
        r = self.table.rowCount()
        self.table.insertRow(r)
        total_item = QTableWidgetItem("Total")
        f = total_item.font(); f.setBold(True); total_item.setFont(f)
        self.table.setItem(r, 0, total_item)
        tot_t = QTableWidgetItem(f"{total:.3f}"); tot_t.setFont(f)
        tot_b = QTableWidgetItem(str(sum(s.bouts for s in stats))); tot_b.setFont(f)
        self.table.setItem(r, 1, tot_t)
        self.table.setItem(r, 2, tot_b)
        self.table.setItem(r, 3, QTableWidgetItem(""))

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------
    def _suggested_filename(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bits = [self.meta.get("animal_id", ""), self.meta.get("trial_name", ""), ts]
        bits = [b for b in bits if b]
        return "_".join(bits).replace(" ", "-") + ".csv"

    def _suggested_master_name(self) -> str:
        sess = self.meta.get("session", "") or self.meta.get("group", "") or "session"
        return f"master_{sess}.csv".replace(" ", "-")

    def _on_save_csv(self) -> None:
        if self.scorer is None: return
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        default = str(DATA_DIR / self._suggested_filename())
        path, _ = QFileDialog.getSaveFileName(self, "Save trial CSV", default, "CSV (*.csv)")
        if not path: return
        try:
            export_trial(Path(path), self.meta, self.scorer)
        except OSError as e:
            QMessageBox.critical(self, "Save failed", str(e)); return
        QMessageBox.information(self, "Saved", f"Trial saved to:\n{path}")

    def _on_append_master(self) -> None:
        if self.scorer is None: return
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        default = str(DATA_DIR / self._suggested_master_name())
        path, _ = QFileDialog.getSaveFileName(
            self, "Append to / create session master CSV", default, "CSV (*.csv)"
        )
        if not path: return
        try:
            append_to_master(Path(path), self.meta, self.scorer)
        except OSError as e:
            QMessageBox.critical(self, "Save failed", str(e)); return
        QMessageBox.information(self, "Appended", f"Row added to:\n{path}")

    def _on_quick_save(self) -> None:
        if self.scorer is None: return
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        trial_path = DATA_DIR / self._suggested_filename()
        master_path = DATA_DIR / self._suggested_master_name()
        try:
            export_trial(trial_path, self.meta, self.scorer)
            append_to_master(master_path, self.meta, self.scorer)
        except OSError as e:
            QMessageBox.critical(self, "Save failed", str(e)); return
        QMessageBox.information(
            self, "Saved",
            f"Per-trial CSV:\n  {trial_path}\n\nMaster CSV:\n  {master_path}",
        )
