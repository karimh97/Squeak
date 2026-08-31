"""OpenCV video capture with Qt preview signals and optional camera recording."""

import math
from pathlib import Path
from typing import Optional

import cv2
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QImage


class VideoSource(QObject):
    frame_ready = Signal(QImage)
    error = Signal(str)
    ended = Signal()
    recording_started = Signal(str)
    recording_error = Signal(str)
    recording_stopped = Signal(str)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        # source: int (camera index), str (file path), or None (disabled)
        self.source = source
        self.is_file = isinstance(source, str)
        self.cap: cv2.VideoCapture | None = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_frame)
        self._interval_ms = 33
        self._paused = False
        self._last_frame = None
        self._record_requested = False
        self._recording_path: Optional[Path] = None
        self._writer: Optional[cv2.VideoWriter] = None

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
        self._interval_ms = max(10, int(1000 / fps))
        self._paused = False
        self.timer.start(self._interval_ms)
        return True

    def pause(self) -> None:
        """Pause file playback without losing the current frame position."""
        if not self.is_file or self.cap is None or self._paused:
            return
        self.timer.stop()
        self._paused = True

    def resume(self) -> None:
        """Resume file playback from the frame where it was paused."""
        if not self.is_file or self.cap is None or not self._paused:
            return
        self._paused = False
        self.timer.start(self._interval_ms)

    def stop(self) -> None:
        self.timer.stop()
        self._paused = False
        self.stop_recording()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    @property
    def recording_path(self) -> Optional[Path]:
        return self._recording_path

    def is_recording(self) -> bool:
        return self._writer is not None

    def start_recording(self, path: Path, fallback_fps: float = 30.0) -> bool:
        """Arm recording for a live camera.

        The writer opens from the latest camera frame so its dimensions always
        match the actual stream. If no frame has arrived yet, opening is
        deferred until the next frame. Returns False only when recording cannot
        be armed at all; codec/open failures are reported through
        ``recording_error`` without stopping the scoring trial.
        """
        if self.is_file or self.cap is None or not self.cap.isOpened():
            self.recording_error.emit("Camera recording is unavailable.")
            return False
        self.stop_recording()
        path = Path(path).with_suffix(".mp4")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.recording_error.emit(f"Could not create the video folder: {exc}")
            return False
        self._recording_path = path
        self._record_requested = True
        if self._last_frame is not None:
            return self._open_writer(self._last_frame, fallback_fps)
        return True

    def stop_recording(self) -> Optional[Path]:
        """Finalize the current recording and return its actual path."""
        was_requested = self._record_requested
        self._record_requested = False
        had_writer = self._writer is not None
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        path = self._recording_path
        if had_writer and path is not None:
            self.recording_stopped.emit(str(path))
            return path
        if was_requested:
            self._recording_path = None
            self.recording_error.emit("No camera frames were available to save.")
        return None

    def _open_writer(self, frame, fallback_fps: float) -> bool:
        if not self._record_requested or self._recording_path is None:
            return False
        height, width = frame.shape[:2]
        fps = float(self.cap.get(cv2.CAP_PROP_FPS)) if self.cap is not None else 0.0
        if not math.isfinite(fps) or fps < 1.0 or fps > 240.0:
            fps = fallback_fps

        candidates = [
            (self._recording_path.with_suffix(".mp4"), "mp4v"),
            (self._recording_path.with_suffix(".avi"), "MJPG"),
        ]
        for path, codec in candidates:
            writer = cv2.VideoWriter(
                str(path), cv2.VideoWriter_fourcc(*codec), fps, (width, height)
            )
            if writer.isOpened():
                self._writer = writer
                self._recording_path = path
                self.recording_started.emit(str(path))
                return True
            writer.release()

        self._record_requested = False
        self._recording_path = None
        self.recording_error.emit(
            "The camera is working, but Squeak could not create an MP4 or AVI recording."
        )
        return False

    def _read_frame(self) -> None:
        if self.cap is None:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.ended.emit()
            self.stop()
            return
        self._last_frame = frame.copy()
        if self._record_requested:
            if self._writer is None and not self._open_writer(frame, 30.0):
                pass
            if self._writer is not None:
                self._writer.write(frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        # .copy() because the underlying numpy buffer is reused by cv2
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.frame_ready.emit(img)
