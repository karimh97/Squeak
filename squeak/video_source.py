"""Thin wrapper around cv2.VideoCapture that emits QImages via Qt signals."""

import cv2
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QImage


class VideoSource(QObject):
    frame_ready = Signal(QImage)
    error = Signal(str)
    ended = Signal()

    def __init__(self, source, parent=None):
        super().__init__(parent)
        # source: int (camera index), str (file path), or None (disabled)
        self.source = source
        self.is_file = isinstance(source, str)
        self.cap: cv2.VideoCapture | None = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_frame)

    def start(self, fallback_fps: float = 30.0) -> bool:
        if self.source is None:
            return False
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            self.error.emit(f"Could not open video source: {self.source}")
            self.cap = None
            return False
        if self.is_file:
            fps = self.cap.get(cv2.CAP_PROP_FPS) or fallback_fps
        else:
            fps = fallback_fps
        interval = max(10, int(1000 / fps))
        self.timer.start(interval)
        return True

    def stop(self) -> None:
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def _read_frame(self) -> None:
        if self.cap is None:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.ended.emit()
            self.stop()
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        # .copy() because the underlying numpy buffer is reused by cv2
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.frame_ready.emit(img)
