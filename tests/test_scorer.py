import unittest
from unittest.mock import patch

from squeak.scorer import ObjectConfig, Scorer


class FakeClock:
    def __init__(self, value: float = 100.0):
        self.value = value

    def monotonic(self) -> float:
        return self.value


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.patcher = patch("squeak.scorer.time.monotonic", self.clock.monotonic)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_scoring_pause_and_resume_exclude_paused_time(self):
        scorer = Scorer([
            ObjectConfig("Familiar", "1"),
            ObjectConfig("Novel", "2"),
        ])
        scorer.start()

        self.clock.value = 101.0
        self.assertTrue(scorer.toggle("Familiar"))
        self.clock.value = 104.0
        self.assertFalse(scorer.toggle("Familiar"))

        self.clock.value = 105.0
        scorer.toggle("Novel")
        self.clock.value = 108.0
        scorer.pause()
        self.assertTrue(scorer.is_paused())

        self.clock.value = 110.0
        scorer.resume()
        self.clock.value = 111.0
        scorer.toggle("Novel")
        self.clock.value = 113.0
        scorer.stop()

        stats = {stat.name: stat for stat in scorer.stats()}
        self.assertAlmostEqual(stats["Familiar"].total_time, 3.0)
        self.assertEqual(stats["Familiar"].bouts, 1)
        self.assertAlmostEqual(stats["Novel"].total_time, 5.0)
        self.assertEqual(stats["Novel"].bouts, 2)
        self.assertAlmostEqual(scorer.now(), 11.0)

    def test_duration_completion_and_unknown_object(self):
        scorer = Scorer([ObjectConfig("Object A", "1")], duration=5.0)
        self.assertFalse(scorer.toggle("Object A"))
        scorer.start()
        self.assertFalse(scorer.toggle("Missing"))
        self.clock.value = 105.0
        self.assertTrue(scorer.is_complete())

    def test_stop_closes_an_active_bout(self):
        scorer = Scorer([ObjectConfig("Object A", "1")])
        scorer.start()
        self.clock.value = 102.0
        scorer.toggle("Object A")
        self.clock.value = 106.5
        scorer.stop()

        stat = scorer.stats()[0]
        self.assertAlmostEqual(stat.total_time, 4.5)
        self.assertEqual(stat.bouts, 1)
        self.assertEqual([event.event_type for event in scorer.events], ["start", "stop"])


if __name__ == "__main__":
    unittest.main()
