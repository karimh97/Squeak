import unittest
from pathlib import Path
from types import SimpleNamespace

from squeak import __version__
from squeak.scoring_view import ScoringView


class ReleaseMetadataTests(unittest.TestCase):
    def test_trial_metadata_includes_app_version(self):
        config = SimpleNamespace(
            animal_id="M001",
            group="control",
            session="day-1",
            experimenter="KA",
            trial_name="Test",
            data_dir=Path("/tmp/squeak-data"),
        )
        view = SimpleNamespace(config=config, recording_path=None)

        meta = ScoringView._build_meta(view)

        self.assertEqual(meta["squeak_version"], __version__)


if __name__ == "__main__":
    unittest.main()
