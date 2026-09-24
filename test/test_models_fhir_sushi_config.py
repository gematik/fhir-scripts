import unittest
from pathlib import Path

import yaml

from fhir_scripts.models.fhir.sushi_config import SushiConfig


class TestSushiConfig(unittest.TestCase):

    def test_parse_minimal(self):
        file = Path("test/data/sushi-config-minimal.yaml")

        self.assertTrue(file.exists())

        content = yaml.safe_load(file.read_text())

        SushiConfig.model_validate(content)

    def test_parse_recommended(self):
        file = Path("test/data/sushi-config-recommended.yaml")

        self.assertTrue(file.exists())

        content = yaml.safe_load(file.read_text())

        SushiConfig.model_validate(content)
