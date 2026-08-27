"""Trial setup screen — Squeak branding, template chips, modern card sections."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .branding import logo_pixmap
from .scorer import ObjectConfig
from .theme import manager as theme_manager


class CameraSelector(QWidget):
    """Pick a camera by detected name, or fall back to a manual index.

    Uses QMediaDevices to list connected cameras with friendly names
    ('FaceTime HD Camera', 'Logitech C920', …) and listens for plug /
    unplug events to refresh the list automatically.

    The index returned by `value()` is the position in the live device
    list, which (on the platforms Qt supports) matches the index
    OpenCV's VideoCapture uses on the same backend. The "Use index"
    toggle is an escape hatch when that mapping is wrong.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TransparentWidget")

        self._media = QMediaDevices(self)
        self._media.videoInputsChanged.connect(self._refresh)

        self.combo = QComboBox()
        self.combo.setMinimumWidth(220)

        self.spin = QSpinBox()
        self.spin.setRange(0, 10)
        self.spin.setFixedWidth(80)
        self.spin.setSuffix("")
        self.spin.hide()

        self.toggle = QPushButton("Use index")
        self.toggle.setObjectName("Ghost")
        self.toggle.setCursor(Qt.PointingHandCursor)
        self.toggle.setToolTip("Switch to manual camera index if the dropdown doesn't show what you want.")
        self.toggle.clicked.connect(self._toggle_mode)

        self.hint = QLabel("")
        self.hint.setObjectName("Subtle")
        self.hint.setWordWrap(True)
        self.hint.hide()

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self.combo, 1)
        row.addWidget(self.spin, 0)
        row.addWidget(self.toggle, 0)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)
        outer.addLayout(row)
        outer.addWidget(self.hint)

        self._manual = False
        self._refresh()

    # --- public API ---------------------------------------------------

    def value(self) -> int:
        """Return the cv2.VideoCapture index to open."""
        if self._manual:
            return int(self.spin.value())
        idx = self.combo.currentData()
        return int(idx) if idx is not None else 0

    def display_name(self) -> str:
        if self._manual:
            return f"Camera {self.spin.value()}"
        return self.combo.currentText() or "Camera 0"

    def is_manual(self) -> bool:
        return self._manual

    def set_state(self, manual: bool, index: int, name: str = "") -> None:
        self._set_manual(manual)
        if manual:
            self.spin.setValue(max(0, min(10, int(index))))
            return
        # Try to restore by name first, then fall back to index
        if name:
            i = self.combo.findText(name)
            if i >= 0:
                self.combo.setCurrentIndex(i)
                return
        if 0 <= index < self.combo.count():
            self.combo.setCurrentIndex(index)

    # --- internals ----------------------------------------------------

    def _refresh(self) -> None:
        previous = self.combo.currentText()
        self.combo.clear()
        devices = QMediaDevices.videoInputs()
        if not devices:
            self.combo.addItem("No cameras detected", -1)
            self.combo.setEnabled(False)
            self.hint.setText(
                "No cameras detected. If you have one plugged in, "
                "check Camera access in System Settings → Privacy & Security."
            )
            self.hint.show()
        else:
            self.combo.setEnabled(True)
            for i, dev in enumerate(devices):
                self.combo.addItem(dev.description(), i)
            self.hint.hide()
            if previous:
                i = self.combo.findText(previous)
                if i >= 0:
                    self.combo.setCurrentIndex(i)

    def _toggle_mode(self) -> None:
        self._set_manual(not self._manual)

    def _set_manual(self, manual: bool) -> None:
        self._manual = manual
        self.combo.setVisible(not manual)
        self.spin.setVisible(manual)
        self.toggle.setText("Use detected camera" if manual else "Use index")
        if manual:
            self.hint.hide()
        else:
            # Re-show hint only if we still have no devices
            if self.combo.count() == 1 and self.combo.itemData(0) == -1:
                self.hint.show()


PRESETS = {
    "Custom": None,
    "Sample": {
        "trial_name": "Sample",
        "minutes": 5, "seconds": 0,
        "open_ended": False,
        "objects": [("Object A", "1"), ("Object B", "2")],
    },
    "Reactivation": {
        "trial_name": "Reactivation",
        "minutes": 3, "seconds": 0,
        "open_ended": False,
        "objects": [("Object", "1")],
    },
    "Test": {
        "trial_name": "Test",
        "minutes": 10, "seconds": 0,
        "open_ended": False,
        "objects": [("Familiar", "1"), ("Novel", "2")],
    },
    "Y-maze": {
        "trial_name": "Y-maze",
        "minutes": 5, "seconds": 0,
        "open_ended": False,
        "objects": [("Arm 1", "1"), ("Arm 2", "2"), ("Arm 3", "3")],
    },
}

CONFIG_DIR = Path.home() / ".config" / "squeak"
LAST_CONFIG_PATH = CONFIG_DIR / "last_config.json"


@dataclass
class TrialConfig:
    animal_id: str
    group: str
    session: str
    experimenter: str
    trial_name: str
    duration_s: Optional[float]
    video_source: object        # int (cam index), str (file path), or None
    objects: list[ObjectConfig] = field(default_factory=list)


# ---------------------------------------------------------------------- helpers

def _section(title: str, body: QWidget) -> QFrame:
    """A quiet, captioned setup panel."""
    body.setObjectName("SectionBody")
    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(20, 20, 20, 20)
    lay.setSpacing(16)
    title_row = QHBoxLayout()
    title_row.setSpacing(8)
    marker = QLabel()
    marker.setObjectName("SectionMarker")
    marker.setFixedSize(3, 12)
    cap = QLabel(title.upper())
    cap.setObjectName("Caption")
    title_row.addWidget(marker)
    title_row.addWidget(cap)
    title_row.addStretch(1)
    lay.addLayout(title_row)
    lay.addWidget(body)
    return card


class ObjectRow(QWidget):
    """One editable object: [name] [key] [×]."""

    deleted = Signal(QWidget)

    def __init__(self, name: str = "", hotkey: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("TransparentWidget")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Object label (e.g. Novel)")
        self.key_edit = QLineEdit(hotkey)
        self.key_edit.setPlaceholderText("key")
        self.key_edit.setMaxLength(1)
        self.key_edit.setFixedWidth(56)
        self.key_edit.setAlignment(Qt.AlignCenter)

        del_btn = QPushButton("×")
        del_btn.setObjectName("IconBtn")
        del_btn.setFixedWidth(34)
        del_btn.setToolTip("Remove object")
        del_btn.clicked.connect(lambda: self.deleted.emit(self))

        row.addWidget(self.name_edit, 1)
        row.addWidget(self.key_edit, 0)
        row.addWidget(del_btn, 0)

    def values(self) -> tuple[str, str]:
        return self.name_edit.text().strip(), self.key_edit.text().strip()


# ---------------------------------------------------------------------- view

class SetupView(QWidget):
    start_requested = Signal(TrialConfig)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chip_buttons: list[QPushButton] = []
        self._object_rows: list[ObjectRow] = []
        self._build_ui()
        self._load_last_config()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(22)

        # --- Brand header (logo image + theme toggle) ---
        brand_row = QHBoxLayout()
        brand_row.setSpacing(0)
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
            lambda _name: (self._refresh_logo(), self._refresh_theme_btn())
        )

        subtitle = QLabel("Manual scoring for rodent object exploration")
        subtitle.setObjectName("Subtle")
        root.addWidget(subtitle)
        root.addSpacing(6)

        # --- Template chips ---
        chips_card = QFrame(); chips_card.setObjectName("Card")
        chips_lay = QVBoxLayout(chips_card)
        chips_lay.setContentsMargins(20, 16, 20, 16)
        chips_lay.setSpacing(10)
        chips_title = QHBoxLayout(); chips_title.setSpacing(8)
        chips_marker = QLabel(); chips_marker.setObjectName("SectionMarker")
        chips_marker.setFixedSize(3, 12)
        chips_cap = QLabel("TEMPLATE"); chips_cap.setObjectName("Caption")
        chips_title.addWidget(chips_marker)
        chips_title.addWidget(chips_cap)
        chips_title.addStretch(1)
        chips_lay.addLayout(chips_title)
        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        for name in PRESETS.keys():
            btn = QPushButton(name)
            btn.setObjectName("Chip")
            btn.setProperty("selected", False)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, n=name: self._select_template(n))
            self._chip_buttons.append(btn)
            chip_row.addWidget(btn)
        chip_row.addStretch(1)
        chips_lay.addLayout(chip_row)
        root.addWidget(chips_card)

        # --- Body: two columns ---
        body = QHBoxLayout()
        body.setSpacing(20)
        root.addLayout(body)
        left = QVBoxLayout(); left.setSpacing(20)
        right = QVBoxLayout(); right.setSpacing(20)
        body.addLayout(left, 1)
        body.addLayout(right, 1)

        # Animal & trial info
        meta_body = QWidget()
        meta_form = QFormLayout(meta_body)
        meta_form.setContentsMargins(0, 0, 0, 0)
        meta_form.setSpacing(10)
        meta_form.setLabelAlignment(Qt.AlignLeft)
        meta_form.setFormAlignment(Qt.AlignTop)
        self.animal_id = QLineEdit(); self.animal_id.setPlaceholderText("e.g. M001")
        self.group = QLineEdit(); self.group.setPlaceholderText("e.g. WT, knockout, vehicle")
        self.session = QLineEdit(); self.session.setPlaceholderText("e.g. Day 1")
        self.experimenter = QLineEdit(); self.experimenter.setPlaceholderText("Your initials")
        self.trial_name = QLineEdit("Sample")
        for label, w in [
            ("Animal ID", self.animal_id),
            ("Group / condition", self.group),
            ("Session", self.session),
            ("Experimenter", self.experimenter),
            ("Trial name", self.trial_name),
        ]:
            lbl = QLabel(label); lbl.setObjectName("FieldLabel")
            meta_form.addRow(lbl, w)
        left.addWidget(_section("Animal & trial info", meta_body))

        # Duration
        dur_body = QWidget()
        dur_lay = QVBoxLayout(dur_body); dur_lay.setContentsMargins(0, 0, 0, 0); dur_lay.setSpacing(12)
        dur_row = QHBoxLayout(); dur_row.setSpacing(10)
        self.minutes_spin = QSpinBox(); self.minutes_spin.setRange(0, 240); self.minutes_spin.setValue(5)
        self.minutes_spin.setSuffix(" min"); self.minutes_spin.setFixedWidth(100)
        self.seconds_spin = QSpinBox(); self.seconds_spin.setRange(0, 59); self.seconds_spin.setValue(0)
        self.seconds_spin.setSuffix(" s"); self.seconds_spin.setFixedWidth(80)
        dur_row.addWidget(self.minutes_spin)
        dur_row.addWidget(self.seconds_spin)
        dur_row.addStretch(1)
        self.open_ended_check = QCheckBox("Open-ended (no auto-stop)")
        self.open_ended_check.toggled.connect(self._toggle_duration_inputs)
        dur_lay.addLayout(dur_row)
        dur_lay.addWidget(self.open_ended_check)
        left.addWidget(_section("Trial duration", dur_body))
        left.addStretch(1)

        # Video source
        vid_body = QWidget()
        vid_lay = QVBoxLayout(vid_body); vid_lay.setContentsMargins(0, 0, 0, 0); vid_lay.setSpacing(10)
        self.radio_webcam = QRadioButton("Webcam"); self.radio_webcam.setChecked(True)
        self.radio_file = QRadioButton("Video file")
        self.radio_none = QRadioButton("No video (live observation)")
        self.radio_webcam.toggled.connect(self._update_video_inputs)
        self.radio_file.toggled.connect(self._update_video_inputs)

        cam_row = QHBoxLayout()
        cam_lbl = QLabel("Camera"); cam_lbl.setObjectName("FieldLabel")
        cam_row.addSpacing(24); cam_row.addWidget(cam_lbl)
        self.cam_selector = CameraSelector()
        cam_row.addWidget(self.cam_selector, 1)

        file_row = QHBoxLayout()
        file_row.addSpacing(24)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Path to .mp4 / .mov / .avi …")
        browse_btn = QPushButton("Browse…"); browse_btn.clicked.connect(self._browse_video)
        file_row.addWidget(self.file_path_edit, 1)
        file_row.addWidget(browse_btn)

        vid_lay.addWidget(self.radio_webcam)
        vid_lay.addLayout(cam_row)
        vid_lay.addWidget(self.radio_file)
        vid_lay.addLayout(file_row)
        vid_lay.addWidget(self.radio_none)
        right.addWidget(_section("Video source", vid_body))

        # Objects
        obj_body = QWidget()
        obj_lay = QVBoxLayout(obj_body); obj_lay.setContentsMargins(0, 0, 0, 0); obj_lay.setSpacing(10)
        # column header row
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        h1 = QLabel("OBJECT LABEL"); h1.setObjectName("Caption")
        h2 = QLabel("KEY"); h2.setObjectName("Caption"); h2.setFixedWidth(56); h2.setAlignment(Qt.AlignCenter)
        head.addWidget(h1, 1); head.addWidget(h2, 0); head.addSpacing(34)
        obj_lay.addLayout(head)
        self._objects_layout = QVBoxLayout()
        self._objects_layout.setSpacing(8)
        obj_lay.addLayout(self._objects_layout)
        add_btn = QPushButton("+  Add object")
        add_btn.setObjectName("Ghost")
        add_btn.clicked.connect(lambda: self._add_object_row("", ""))
        obj_lay.addWidget(add_btn, 0, Qt.AlignLeft)
        hint = QLabel("During the trial, press the object's key to start a bout; press it again to stop.")
        hint.setObjectName("Subtle"); hint.setWordWrap(True)
        obj_lay.addWidget(hint)
        right.addWidget(_section("Objects to score", obj_body), 1)

        # --- Footer ---
        footer = QHBoxLayout()
        footer.addStretch(1)
        self.start_btn = QPushButton("Start trial  ▶")
        self.start_btn.setObjectName("Primary")
        self.start_btn.setMinimumHeight(42)
        self.start_btn.setMinimumWidth(180)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start)
        footer.addWidget(self.start_btn)
        root.addLayout(footer)

        # Initial state
        self._update_video_inputs()
        self._add_object_row("Object A", "1")
        self._add_object_row("Object B", "2")
        self._mark_chip("Custom")

    # ------------------------------------------------------------------
    # Branding / theme
    # ------------------------------------------------------------------
    def _refresh_logo(self) -> None:
        px = logo_pixmap(height=84)
        if px is not None:
            self.logo_lbl.setPixmap(px)

    def _refresh_theme_btn(self) -> None:
        self.theme_btn.setText("☀" if theme_manager().is_dark() else "🌙")
        self.theme_btn.setToolTip(
            f"Switch to {'light' if theme_manager().is_dark() else 'dark'} mode"
        )

    # ------------------------------------------------------------------
    # Template chips
    # ------------------------------------------------------------------
    def _mark_chip(self, name: str) -> None:
        for btn in self._chip_buttons:
            sel = btn.text() == name
            btn.setProperty("selected", sel)
            btn.style().unpolish(btn); btn.style().polish(btn)

    def _select_template(self, name: str) -> None:
        self._mark_chip(name)
        preset = PRESETS.get(name)
        if preset is None:
            return
        self.trial_name.setText(preset["trial_name"])
        self.minutes_spin.setValue(preset["minutes"])
        self.seconds_spin.setValue(preset["seconds"])
        self.open_ended_check.setChecked(preset.get("open_ended", False))
        self._clear_object_rows()
        for label, key in preset["objects"]:
            self._add_object_row(label, key)

    # ------------------------------------------------------------------
    # Object rows
    # ------------------------------------------------------------------
    def _add_object_row(self, name: str, hotkey: str) -> None:
        row = ObjectRow(name, hotkey)
        row.deleted.connect(self._remove_row)
        self._object_rows.append(row)
        self._objects_layout.addWidget(row)

    def _remove_row(self, row: ObjectRow) -> None:
        if len(self._object_rows) <= 1:
            return  # always leave at least one
        if row in self._object_rows:
            self._object_rows.remove(row)
        row.setParent(None)
        row.deleteLater()

    def _clear_object_rows(self) -> None:
        for r in self._object_rows:
            r.setParent(None); r.deleteLater()
        self._object_rows.clear()

    def _collect_objects(self) -> list[ObjectConfig]:
        out: list[ObjectConfig] = []
        for r in self._object_rows:
            name, key = r.values()
            if not name or not key:
                continue
            out.append(ObjectConfig(name=name, hotkey=key))
        return out

    # ------------------------------------------------------------------
    # Video source
    # ------------------------------------------------------------------
    def _update_video_inputs(self) -> None:
        on_cam = self.radio_webcam.isChecked()
        on_file = self.radio_file.isChecked()
        self.cam_selector.setEnabled(on_cam)
        self.file_path_edit.setEnabled(on_file)

    def _browse_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select video file", str(Path.home()),
            "Video files (*.mp4 *.mov *.avi *.mkv *.m4v);;All files (*)"
        )
        if path:
            self.file_path_edit.setText(path)
            self.radio_file.setChecked(True)

    def _toggle_duration_inputs(self, open_ended: bool) -> None:
        self.minutes_spin.setEnabled(not open_ended)
        self.seconds_spin.setEnabled(not open_ended)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _current_config_dict(self) -> dict:
        return {
            "animal_id": self.animal_id.text(),
            "group": self.group.text(),
            "session": self.session.text(),
            "experimenter": self.experimenter.text(),
            "trial_name": self.trial_name.text(),
            "minutes": self.minutes_spin.value(),
            "seconds": self.seconds_spin.value(),
            "open_ended": self.open_ended_check.isChecked(),
            "video_kind": ("webcam" if self.radio_webcam.isChecked()
                           else "file" if self.radio_file.isChecked() else "none"),
            "cam_mode": "index" if self.cam_selector.is_manual() else "named",
            "cam_index": self.cam_selector.value(),
            "cam_name": "" if self.cam_selector.is_manual() else self.cam_selector.display_name(),
            "file_path": self.file_path_edit.text(),
            "objects": [(o.name, o.hotkey) for o in self._collect_objects()],
        }

    def _save_last_config(self) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            LAST_CONFIG_PATH.write_text(json.dumps(self._current_config_dict(), indent=2))
        except OSError:
            pass

    def _load_last_config(self) -> None:
        if not LAST_CONFIG_PATH.exists():
            return
        try:
            data = json.loads(LAST_CONFIG_PATH.read_text())
        except (OSError, json.JSONDecodeError):
            return
        self.animal_id.setText(data.get("animal_id", ""))
        self.group.setText(data.get("group", ""))
        self.session.setText(data.get("session", ""))
        self.experimenter.setText(data.get("experimenter", ""))
        self.trial_name.setText(data.get("trial_name", "Sample"))
        self.minutes_spin.setValue(int(data.get("minutes", 5)))
        self.seconds_spin.setValue(int(data.get("seconds", 0)))
        self.open_ended_check.setChecked(bool(data.get("open_ended", False)))
        vk = data.get("video_kind", "webcam")
        if vk == "file": self.radio_file.setChecked(True)
        elif vk == "none": self.radio_none.setChecked(True)
        else: self.radio_webcam.setChecked(True)
        self.cam_selector.set_state(
            manual=(data.get("cam_mode") == "index"),
            index=int(data.get("cam_index", 0)),
            name=data.get("cam_name", ""),
        )
        self.file_path_edit.setText(data.get("file_path", ""))
        objs = data.get("objects")
        if objs:
            self._clear_object_rows()
            for label, key in objs:
                self._add_object_row(label, key)

    # ------------------------------------------------------------------
    def _on_start(self) -> None:
        objects = self._collect_objects()
        if not objects:
            QMessageBox.warning(self, "Missing objects",
                                "Add at least one object with a label and a key.")
            return
        keys = [o.hotkey.lower() for o in objects]
        if len(set(keys)) != len(keys):
            QMessageBox.warning(self, "Duplicate keys", "Each object needs a unique key.")
            return

        if self.radio_webcam.isChecked():
            source = self.cam_selector.value()
        elif self.radio_file.isChecked():
            p = self.file_path_edit.text().strip()
            if not p:
                QMessageBox.warning(self, "Missing file",
                                    "Pick a video file or choose another source.")
                return
            source = p
        else:
            source = None

        if self.open_ended_check.isChecked():
            duration: Optional[float] = None
        else:
            duration = self.minutes_spin.value() * 60 + self.seconds_spin.value()
            if duration <= 0:
                QMessageBox.warning(self, "Invalid duration",
                                    "Set a duration greater than 0, or check Open-ended.")
                return

        cfg = TrialConfig(
            animal_id=self.animal_id.text().strip(),
            group=self.group.text().strip(),
            session=self.session.text().strip(),
            experimenter=self.experimenter.text().strip(),
            trial_name=self.trial_name.text().strip() or "Trial",
            duration_s=duration,
            video_source=source,
            objects=objects,
        )
        self._save_last_config()
        self.start_requested.emit(cfg)
