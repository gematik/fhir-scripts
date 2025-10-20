import unittest
from pathlib import Path

from fhir_scripts import config


class TestConfig(unittest.TestCase):

    def test_load_config(self):
        config_path = Path("examples/config.yaml")
        self.assertTrue(config_path.exists())

        cfg = config.load(config_path)

        self.assertIsNotNone(cfg)
        self.assertIsInstance(cfg, config.Config)
