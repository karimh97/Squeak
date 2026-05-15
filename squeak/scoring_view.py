"""Live scoring screen — two layouts (video-on-left vs. no-video centered),
animated recording dot, refined cards."""

from typing import Optional

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QImage,
    QKeySequence,
    QPainter,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .branding import logo_pixmap
from .scorer import Scorer
from .setup_view import TrialConfig
from .style import ACCENT, DANGER, INFO, TEXT_2, WARNING
from .video_source import VideoSource


def _fmt_clock(secs: float) -> str:
    secs = max(0.0, secs)
    m = int(secs // 60)
    s = int(secs % 60)
    cs = int((secs - int(secs)) * 100)
    return f"{m:02d}:{s:02d}.{cs:02d}"


def _fmt_short(secs: float) -> str:
    secs = max(0.0, secs)
    m = int(secs // 60)
    s = secs - m * 60
    return f"{m:02d}:{s:05.2f}"


def _grid_cols(n: int) -> int:
    """Number of columns to lay out N object cards in a grid."""
    if n <= 1: return 1
    if n <= 3: return n          # 1 row for 1-3
    if n <= 4: return 2          # 2x2 for 4
    if n <= 6: return 3          # 2x3 for 5-6
    return 4                     # 4 cols for 7+


# ---------------------------------------------------------------------- widgets

class StatusDot(QWidget):
    """8px circle, pulses when recording, colored by state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._color = QColor(TEXT_2)
        self._alpha = 1.0
        self._pulse: Optional[QPropertyAnimation] = None

    def _get_alpha(self) -> float: return self._alpha
    def _set_alpha(self, v: float) -> None:
        self._alpha = v
        self.update()
    alpha = Property(float, _get_alpha, _set_alpha)

    def set_state(self, state: str) -> None:
        colors = {
            "ready":     QColor(TEXT_2),
            "recording": QColor(DANGER),
            "paused":    QColor(WARNING),
            "done":      QColor(INFO),
        }
        self._color = colors.get(state, QColor(TEXT_2))
        if state == "recording":
            self._start_pulse()
        else:
            self._stop_pulse()
            self._alpha = 1.0
            self.update()

    def _start_pulse(self) -> None:
        if self._pulse is not None:
            return
        anim = QPropertyAnimation(self, b"alpha")
        anim.setDuration(900)
        anim.setStartValue(0.35)
        anim.setEndValue(1.0)
        anim.setLoopCount(-1)
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.start()
        self._pulse = anim

    def _stop_pulse(self) -> None:
        if self._pulse is not None:
            self._pulse.stop()
            self._pulse = None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(self._color); c.setAlphaF(self._alpha)
        p.setBrush(c); p.setPen(Qt.NoPen)
        p.drawEllipse(2, 2, 8, 8)


class ObjectCard(QFrame):
    def __init__(self, name: str, hotkey: str, large: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("ObjectCard")
        self.setProperty("active", "false")
        self.name = name

        lay = QVBoxLayout(self)
        if large:
            lay.setContentsMargins(28, 22, 28, 22)
            lay.setSpacing(10)
        else:
            lay.setContentsMargins(18, 14, 18, 14)
            lay.setSpacing(6)

        top = QHBoxLayout(); top.setSpacing(8)
        name_lbl = QLabel(name)
        name_lbl.setObjectName("ObjectNameBig" if large else "ObjectName")
        key_lbl = QLabel(hotkey.upper())
        key_lbl.setObjectName("HotkeyBig" if large else "Hotkey")
        top.addWidget(name_lbl, 1)
        top.addWidget(key_lbl, 0, Qt.AlignRight)
        lay.addLayout(top)

        self.time_lbl = QLabel("00:00.00")
        self.time_lbl.setObjectName("ObjectTimeBig" if large else "ObjectTime")
        lay.addWidget(self.time_lbl)

        self.meta_lbl = QLabel("0 BOUTS")
        self.meta_lbl.setObjectName("ObjectMetaBig" if large else "ObjectMeta")
        lay.addWidget(self.meta_lbl)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self); self.style().polish(self)

    def update_values(self, secs: float, bouts: int) -> None:
        self.time_lbl.setText(_fmt_short(secs))
        self.meta_lbl.setText(f"{bouts} BOUT" + ("S" if bouts != 1 else ""))


class VideoLabel(QLabel):
    """Scales its pixmap to fit, preserving aspect ratio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(480, 320)
        self.setStyleSheet(
            "background-color: #05070A; border-radius: 14px; "
            "border: 1px solid #1A1D26; color: #6B7280;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._src: Optional[QPixmap] = None

    def set_placeholder(self, text: str) -> None:
        # QLabel.setText() implicitly clears any pixmap, so do this last.
        self._src = None
        self.setText(text)

    def set_image(self, img: QImage) -> None:
        self._src = QPixmap.fromImage(img)
        self._redraw()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._redraw()

    def _redraw(self) -> None:
        if self._src is None: return
        scaled = self._src.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled)


# ---------------------------------------------------------------------- view

class ScoringView(QWidget):
    trial_finished = Signal(object, dict)
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scorer: Optional[Scorer] = None
        self.video: Optional[VideoSource] = None
        self.config: Optional[TrialConfig] = None
        self.object_cards: dict[str, ObjectCard] = {}
        self._shortcuts: list[QShortcut] = []
        self._has_video_mode: Optional[bool] = None

        # Body-mode-specific widget refs (reassigned on mode change)
        self.video_label: Optional[VideoLabel] = None
        self.clock_lbl: Optional[QLabel] = None
        self.clock_caption: Optional[QLabel] = None
        self.objects_container = None       # QVBoxLayout or QGridLayout
        self.start_btn: Optional[QPushButton] = None
        self.pause_btn: Optional[QPushButton] = None
        self.stop_btn: Optional[QPushButton] = None

        # Outer skeleton
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(28, 22, 28, 22)
        self.root.setSpacing(18)

        self.header_widget = self._build_header()
        self.root.addWidget(self.header_widget)

        self.body_widget = QWidget()        # placeholder; replaced by _build_body
        self.root.addWidget(self.body_widget, 1)

        self.log_card = self._build_log()
        self.root.addWidget(self.log_card)

        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(50)
        self.tick_timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------
    # Persistent widgets (built once)
    # ------------------------------------------------------------------
    def _build_header(self) -> QWidget:
        w = QWidget()
        header = QHBoxLayout(w)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(14)

        brand_row = QHBoxLayout(); brand_row.setSpacing(0)
        logo_px = logo_pixmap(height=28, on_dark=True)
        if logo_px is not None:
            logo_lbl = QLabel()
            logo_lbl.setPixmap(logo_px)
            brand_row.addWidget(logo_lbl)
        else:
            brand = QLabel("Squeak"); brand.setStyleSheet("font-size: 15px; font-weight: 700;")
            dot = QLabel("."); dot.setStyleSheet(f"color: {ACCENT}; font-size: 15px; font-weight: 700;")
            brand_row.addWidget(brand); brand_row.addWidget(dot)
        header.addLayout(brand_row)
        header.addSpacing(20)

        title_block = QVBoxLayout(); title_block.setSpacing(2)
        self.title_lbl = QLabel("Trial"); self.title_lbl.setObjectName("H1")
        self.subtitle_lbl = QLabel(""); self.subtitle_lbl.setObjectName("Subtle")
        title_block.addWidget(self.title_lbl)
        title_block.addWidget(self.subtitle_lbl)
        header.addLayout(title_block, 1)

        status_box = QHBoxLayout(); status_box.setSpacing(6)
        self.status_dot = StatusDot()
        self.status_text = QLabel("READY"); self.status_text.setObjectName("StatusText")
        self.status_text.setProperty("state", "ready")
        status_box.addWidget(self.status_dot)
        status_box.addWidget(self.status_text)
        header.addLayout(status_box)
        header.addSpacing(12)

        self.exit_btn = QPushButton("Back"); self.exit_btn.setObjectName("Ghost")
        self.exit_btn.clicked.connect(self._on_exit)
        header.addWidget(self.exit_btn)
        return w

    def _build_log(self) -> QFrame:
        card = QFrame(); card.setObjectName("Card")
        lay = QVBoxLayout(card); lay.setContentsMargins(18, 14, 18, 14); lay.setSpacing(8)
        cap = QLabel("EVENT LOG"); cap.setObjectName("Caption")
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(110)
        lay.addWidget(cap)
        lay.addWidget(self.log_view)
        return card

    # ------------------------------------------------------------------
    # Body — two modes
    # ------------------------------------------------------------------
    def _swap_body(self, new_body: QWidget) -> None:
        old = self.body_widget
        self.root.replaceWidget(old, new_body)
        old.setParent(None); old.deleteLater()
        self.body_widget = new_body

    def _make_controls(self, large: bool) -> QHBoxLayout:
        ctrl = QHBoxLayout(); ctrl.setSpacing(12)
        self.start_btn = QPushButton("Start  ▶"); self.start_btn.setObjectName("Primary")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop"); self.stop_btn.setObjectName("Danger")
        h = 52 if large else 40
        for b in (self.start_btn, self.pause_btn, self.stop_btn):
            b.setMinimumHeight(h)
            b.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        if large:
            self.start_btn.setMinimumWidth(180)
            self.pause_btn.setMinimumWidth(140)
            self.stop_btn.setMinimumWidth(140)
            ctrl.addStretch(1)
            ctrl.addWidget(self.start_btn)
            ctrl.addWidget(self.pause_btn)
            ctrl.addWidget(self.stop_btn)
            ctrl.addStretch(1)
        else:
            ctrl.addWidget(self.start_btn, 1)
            ctrl.addWidget(self.pause_btn, 1)
            ctrl.addWidget(self.stop_btn, 1)
        return ctrl

    def _build_video_body(self) -> QWidget:
        body = QWidget()
        outer = QHBoxLayout(body)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(20)

        self.video_label = VideoLabel()
        outer.addWidget(self.video_label, 1)

        sidebar = QWidget()
        sidebar.setFixedWidth(360)
        sb = QVBoxLayout(sidebar); sb.setContentsMargins(0, 0, 0, 0); sb.setSpacing(14)

        clock_card = QFrame(); clock_card.setObjectName("Card")
        cl = QVBoxLayout(clock_card); cl.setContentsMargins(22, 18, 22, 18); cl.setSpacing(6)
        self.clock_caption = QLabel("TRIAL TIME"); self.clock_caption.setObjectName("Caption")
        self.clock_lbl = QLabel("00:00.00"); self.clock_lbl.setObjectName("Clock")
        self.clock_lbl.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.clock_caption)
        cl.addWidget(self.clock_lbl)
        sb.addWidget(clock_card)

        self.objects_container = QVBoxLayout()
        self.objects_container.setSpacing(10)
        sb.addLayout(self.objects_container)
        sb.addStretch(1)
        sb.addLayout(self._make_controls(large=False))

        outer.addWidget(sidebar, 0)
        return body

    def _build_no_video_body(self) -> QWidget:
        body = QWidget()
        outer = QVBoxLayout(body)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(20)

        # Big centered clock
        clock_card = QFrame(); clock_card.setObjectName("Card")
        cl = QVBoxLayout(clock_card); cl.setContentsMargins(40, 32, 40, 36); cl.setSpacing(10)
        self.clock_caption = QLabel("TRIAL TIME"); self.clock_caption.setObjectName("Caption")
        self.clock_caption.setAlignment(Qt.AlignCenter)
        self.clock_lbl = QLabel("00:00.00"); self.clock_lbl.setObjectName("ClockBig")
        self.clock_lbl.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.clock_caption)
        cl.addWidget(self.clock_lbl)
        outer.addWidget(clock_card, 0)

        # Object cards card (grid inside)
        objs_card = QFrame(); objs_card.setObjectName("Card")
        objs_lay = QVBoxLayout(objs_card); objs_lay.setContentsMargins(28, 24, 28, 28); objs_lay.setSpacing(14)
        objs_cap = QLabel("OBJECTS"); objs_cap.setObjectName("Caption")
        objs_lay.addWidget(objs_cap, 0, Qt.AlignLeft)
        self.objects_container = QGridLayout()
        self.objects_container.setSpacing(16)
        objs_lay.addLayout(self.objects_container)
        outer.addWidget(objs_card, 1)

        # Controls
        outer.addLayout(self._make_controls(large=True))

        # In no-video mode there is no live video panel
        self.video_label = None
        return body

    # ------------------------------------------------------------------
    # Trial lifecycle
    # ------------------------------------------------------------------
    def load_trial(self, config: TrialConfig) -> None:
        self.config = config
        self.scorer = Scorer(objects=config.objects, duration=config.duration_s)

        has_video = config.video_source is not None
        if has_video != self._has_video_mode:
            new_body = self._build_video_body() if has_video else self._build_no_video_body()
            self._swap_body(new_body)
            self._has_video_mode = has_video

        # Header text
        self.title_lbl.setText(config.trial_name)
        bits = []
        if config.animal_id: bits.append(f"Animal {config.animal_id}")
        if config.group: bits.append(config.group)
        if config.session: bits.append(f"Session {config.session}")
        self.subtitle_lbl.setText("  ·  ".join(bits))

        # Clock caption + initial value
        if config.duration_s:
            self.clock_caption.setText(f"REMAINING · OF {_fmt_clock(config.duration_s)}")
        else:
            self.clock_caption.setText("TRIAL TIME · OPEN-ENDED")
        self.clock_lbl.setText(_fmt_clock(config.duration_s or 0))

        # Rebuild object cards
        self._clear_object_cards()
        n = len(config.objects)
        large = not has_video
        cols = _grid_cols(n) if isinstance(self.objects_container, QGridLayout) else 1
        for i, obj in enumerate(config.objects):
            card = ObjectCard(obj.name, obj.hotkey, large=large)
            if isinstance(self.objects_container, QGridLayout):
                r, c = divmod(i, cols)
                self.objects_container.addWidget(card, r, c)
            else:
                self.objects_container.addWidget(card)
            self.object_cards[obj.name] = card

        # Shortcuts
        for sc in self._shortcuts:
            sc.setParent(None)
        self._shortcuts = []
        for obj in config.objects:
            sc = QShortcut(QKeySequence(obj.hotkey), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(lambda n=obj.name: self._on_toggle_object(n))
            self._shortcuts.append(sc)
        sp = QShortcut(QKeySequence(Qt.Key_Space), self)
        sp.setContext(Qt.ApplicationShortcut)
        sp.activated.connect(self._on_pause_clicked)
        self._shortcuts.append(sp)

        # Video init
        if self.video is not None:
            self.video.stop(); self.video.deleteLater(); self.video = None
        if has_video and self.video_label is not None:
            self.video = VideoSource(config.video_source, parent=self)
            self.video.frame_ready.connect(self.video_label.set_image)
            self.video.error.connect(self._on_video_error)
            self.video.ended.connect(lambda: self.video_label.set_placeholder("Video ended"))
            if not self.video.start():
                self.video_label.set_placeholder("Could not open video source")

        # Reset controls
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.stop_btn.setEnabled(False)
        self._set_status("ready", "READY")
        self.log_view.clear()
        for card in self.object_cards.values():
            card.set_active(False); card.update_values(0, 0)

    def _clear_object_cards(self) -> None:
        # Remove all widgets from objects_container regardless of layout type
        if self.objects_container is None: return
        while self.objects_container.count():
            item = self.objects_container.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        self.object_cards.clear()

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------
    def _on_start_clicked(self) -> None:
        if self.scorer is None: return
        self.scorer.start()
        self.tick_timer.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self._set_status("recording", "RECORDING")
        self._append_log(0.0, "trial", "start")

    def _on_pause_clicked(self) -> None:
        if self.scorer is None or not self.scorer.is_started() or self.scorer.is_stopped():
            return
        if self.scorer.is_paused():
            self.scorer.resume()
            self.pause_btn.setText("Pause")
            self._set_status("recording", "RECORDING")
            self._append_log(self.scorer.now(), "trial", "resume")
        else:
            self.scorer.pause()
            self.pause_btn.setText("Resume")
            self._set_status("paused", "PAUSED")
            self._append_log(self.scorer.now(), "trial", "pause")
            for card in self.object_cards.values():
                card.set_active(False)

    def _on_stop_clicked(self) -> None:
        if self.scorer is None or not self.scorer.is_started(): return
        ret = QMessageBox.question(
            self, "Stop trial?", "End this trial now and view results?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
        )
        if ret != QMessageBox.Yes: return
        self._finish_trial(manual=True)

    def _on_toggle_object(self, name: str) -> None:
        if self.scorer is None or not self.scorer.is_started(): return
        if self.scorer.is_paused() or self.scorer.is_stopped(): return
        now_active = self.scorer.toggle(name)
        card = self.object_cards.get(name)
        if card: card.set_active(now_active)
        self._append_log(self.scorer.now(), name, "start" if now_active else "stop")

    # ------------------------------------------------------------------
    def _tick(self) -> None:
        if self.scorer is None: return
        t = self.scorer.now()
        if self.config and self.config.duration_s:
            remaining = max(0.0, self.config.duration_s - t)
            self.clock_lbl.setText(_fmt_clock(remaining))
        else:
            self.clock_lbl.setText(_fmt_clock(t))
        for name, card in self.object_cards.items():
            card.update_values(self.scorer.time_for(name), self.scorer.bouts_for(name))
        if self.scorer.is_complete() and not self.scorer.is_stopped():
            self._finish_trial(manual=False)

    # ------------------------------------------------------------------
    def _finish_trial(self, manual: bool) -> None:
        if self.scorer is None: return
        self.scorer.stop()
        self.tick_timer.stop()
        if self.video is not None: self.video.stop()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self._set_status("done", "DONE")
        self._append_log(self.scorer.now(), "trial", "stop" if manual else "auto-stop")
        meta = self._build_meta()
        self.trial_finished.emit(self.scorer, meta)

    def _build_meta(self) -> dict:
        c = self.config
        return {
            "animal_id": c.animal_id if c else "",
            "group": c.group if c else "",
            "session": c.session if c else "",
            "experimenter": c.experimenter if c else "",
            "trial_name": c.trial_name if c else "",
        }

    # ------------------------------------------------------------------
    def _set_status(self, state: str, text: str) -> None:
        self.status_text.setText(text)
        self.status_text.setProperty("state", state)
        self.status_text.style().unpolish(self.status_text)
        self.status_text.style().polish(self.status_text)
        self.status_dot.set_state(state)

    def _append_log(self, t: float, name: str, ev: str) -> None:
        self.log_view.appendPlainText(f"{t:7.2f}s   {name:<16} {ev}")

    def _on_video_error(self, msg: str) -> None:
        if self.video_label is not None:
            self.video_label.set_placeholder(msg)

    def _on_exit(self) -> None:
        if self.scorer is not None and self.scorer.is_started() and not self.scorer.is_stopped():
            ret = QMessageBox.question(
                self, "Discard trial?", "A trial is in progress. Leave without saving?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if ret != QMessageBox.Yes: return
            self.scorer.stop()
        self.tick_timer.stop()
        if self.video is not None: self.video.stop()
        self.exit_requested.emit()
