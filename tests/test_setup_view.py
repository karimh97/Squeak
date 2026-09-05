import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

import squeak.setup_view as setup_view


class SetupViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_selected_data_folder_is_remembered_and_emitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "last_config.json"
            selected = Path(tmp) / "lab-data"
            with patch.object(setup_view, "LAST_CONFIG_PATH", config_path):
                view = setup_view.SetupView()
                view.radio_none.setChecked(True)
                view.data_dir_edit.setText(str(selected))
                configs = []
                view.start_requested.connect(configs.append)
                view._on_start()

                restored = setup_view.SetupView()

        self.assertEqual(configs[0].data_dir, selected)
        self.assertEqual(restored.data_dir_edit.text(), str(selected))


if __name__ == "__main__":
    unittest.main()
