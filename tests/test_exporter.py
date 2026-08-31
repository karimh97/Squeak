import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from squeak.exporter import append_to_master, export_trial
from squeak.scorer import ObjectConfig, Scorer


class ExporterTests(unittest.TestCase):
    def make_scorer(self, objects, totals):
        scorer = Scorer([ObjectConfig(name, str(i + 1)) for i, name in enumerate(objects)])
        scorer._t0 = 100.0
        scorer._stopped = True
        scorer._accum.update(dict(zip(objects, totals)))
        scorer._bouts.update({name: 1 for name in objects})
        return scorer

    @patch("squeak.scorer.time.monotonic", return_value=110.0)
    def test_detailed_export_contains_summary_and_di(self, _monotonic):
        scorer = self.make_scorer(["Familiar", "Novel"], [3.0, 5.0])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trial.csv"
            export_trial(path, {
                "animal_id": "DEMO-001",
                "trial_name": "Test",
                "video_file": "/data/DEMO-001_Test.mp4",
            }, scorer)
            text = path.read_text()

        self.assertIn("Summary", text)
        self.assertIn("Discrimination Index", text)
        self.assertIn("(Novel - Familiar) / total", text)
        self.assertIn("0.2500", text)
        self.assertIn("/data/DEMO-001_Test.mp4", text)

    @patch("squeak.scorer.time.monotonic", return_value=110.0)
    def test_master_header_expands_without_losing_existing_rows(self, _monotonic):
        first = self.make_scorer(["Familiar", "Novel"], [3.0, 5.0])
        second = self.make_scorer(["Arm 1", "Arm 2", "Arm 3"], [1.0, 2.0, 3.0])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "master.csv"
            append_to_master(path, {"animal_id": "DEMO-001"}, first)
            append_to_master(path, {"animal_id": "DEMO-002"}, second)
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Familiar_time_s"], "3.000")
        self.assertEqual(rows[1]["Arm 3_time_s"], "3.000")
        self.assertEqual(rows[0]["Arm 3_time_s"], "")


if __name__ == "__main__":
    unittest.main()
