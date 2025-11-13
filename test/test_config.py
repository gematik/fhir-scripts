import unittest
from pathlib import Path

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
