import json
import unittest
from pathlib import Path

from fhir_scripts.models.fhir.publication_request import PublicationRequest


class TestPublicationRequest(unittest.TestCase):

    def test_parse_minimal(self):
        file = Path("test/data/publication-request-minimal.json")

        self.assertTrue(file.exists())

        content = json.loads(file.read_text())

        PublicationRequest.model_validate(content)

    def test_parse_maximal(self):
        file = Path("test/data/publication-request-maximal.json")

        self.assertTrue(file.exists())

        content = json.loads(file.read_text())

        PublicationRequest.model_validate(content)
