import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication

from squeak.video_source import VideoSource


class FakeCapture:
    def __init__(self):
        self.released = False

    def isOpened(self):
        return True

    def get(self, _property):
        return 25.0

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


if __name__ == "__main__":
    unittest.main()
