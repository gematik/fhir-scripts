import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import config
from fhir_scripts.models.config import Config


class TestConfigLoad(unittest.TestCase):

    def test_exists(self):
        config_path = Path("examples/fhirscripts.config.yaml")
        self.assertTrue(config_path.exists())

        cfg = config.load(config_path)

        self.assertIsNotNone(cfg)
        self.assertIsInstance(cfg, config.Config)

    def test_not_exists(self):
        config_path = Path("examples/foo.yaml")
        self.assertFalse(config_path.exists())

        cfg = config.load(config_path)

        self.assertIsNotNone(cfg)
        self.assertIsInstance(cfg, config.Config)

        self.assertEqual(cfg, Config())

    def test_load_dot_env_reads_log_long_from_current_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_ = Path(temp_dir)
            home_dir = temp_dir_ / "home"
            home_dir.mkdir()

            current_dir = temp_dir_ / "current"
            current_dir.mkdir()
            (current_dir / ".env").write_text(
                "FHIRSCRIPTS_LONG_LOG=true\n",
                encoding="utf-8",
            )

            with patch("fhir_scripts.config.Path.cwd", return_value=current_dir):
                with patch.dict(os.environ, {}, clear=True):
                    values = config.load_dot_env()

        self.assertIn("LONG_LOG", values)
        self.assertEqual("true", values["LONG_LOG"])

    def test_load_dot_env_reads_log_long_from_home_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_ = Path(temp_dir)
            home_dir = temp_dir_ / "home"
            home_dir.mkdir()
            (home_dir / ".env").write_text(
                "FHIRSCRIPTS_LONG_LOG=true\n",
                encoding="utf-8",
            )
            current_dir = temp_dir_ / "current"
            current_dir.mkdir()

            with patch("fhir_scripts.config.Path.home", return_value=home_dir):
                with patch("fhir_scripts.config.Path.cwd", return_value=current_dir):
                    with patch.dict(os.environ, {}, clear=True):
                        values = config.load_dot_env()

        self.assertIn("LONG_LOG", values)
        self.assertEqual("true", values["LONG_LOG"])
