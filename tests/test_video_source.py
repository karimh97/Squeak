import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QCoreApplication

from squeak.video_source import VideoSource


class FakeCapture:
    def __init__(self):
        self.released = False

    def isOpened(self):
        return True

    def get(self, _property):
        return 25.0

    def read(self):
        return True, np.zeros((48, 64, 3), dtype=np.uint8)

    def release(self):
        self.released = True


class FakeWriter:
    def __init__(self):
        self.frames = []
        self.released = False

    def isOpened(self):
        return True

    def write(self, frame):
        self.frames.append(frame.copy())

    def release(self):
        self.released = True


class VideoSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def test_file_playback_pauses_and_resumes_without_reopening(self):
        capture = FakeCapture()
        with patch("squeak.video_source.cv2.VideoCapture", return_value=capture) as factory:
            source = VideoSource("demo.mp4")
            self.assertTrue(source.start())
            self.assertTrue(source.timer.isActive())
            self.assertEqual(source.timer.interval(), 40)

            source.pause()
            self.assertFalse(source.timer.isActive())
            self.assertFalse(capture.released)

            source.resume()
            self.assertTrue(source.timer.isActive())
            self.assertEqual(factory.call_count, 1)

            source.stop()
            self.assertFalse(source.timer.isActive())
            self.assertTrue(capture.released)
            self.assertIsNone(source.cap)

    def test_live_camera_recording_writes_frames_and_finalizes(self):
        capture = FakeCapture()
        writer = FakeWriter()
        with tempfile.TemporaryDirectory() as tmp, \
             patch("squeak.video_source.cv2.VideoCapture", return_value=capture), \
             patch("squeak.video_source.cv2.VideoWriter", return_value=writer), \
             patch("squeak.video_source.cv2.VideoWriter_fourcc", return_value=1234):
            source = VideoSource(0)
            self.assertTrue(source.start())
            source.timer.stop()
            source._read_frame()

            requested = Path(tmp) / "trial.mp4"
            self.assertTrue(source.start_recording(requested))
            self.assertTrue(source.is_recording())
            source._read_frame()
            completed = source.stop_recording()

        self.assertEqual(completed, requested)
        self.assertEqual(len(writer.frames), 1)
        self.assertTrue(writer.released)

    def test_prerecorded_file_cannot_be_recorded_as_camera_input(self):
        capture = FakeCapture()
        with tempfile.TemporaryDirectory() as tmp, \
             patch("squeak.video_source.cv2.VideoCapture", return_value=capture):
            source = VideoSource("input.mp4")
            self.assertTrue(source.start())
            self.assertFalse(source.start_recording(Path(tmp) / "copy.mp4"))
            self.assertFalse(source.is_recording())


if __name__ == "__main__":
    unittest.main()
