import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts.tools import epatools


class TestEpaToolsOpenApi(unittest.TestCase):

    @patch(
        "fhir_scripts.tools.epatools.check_configured", lambda *args, **kswargs: None
    )
    @patch("fhir_scripts.tools.epatools.check_installed", lambda *args, **kswargs: None)
    @patch("fhir_scripts.tools.epatools.shell.run", lambda *args, **kswargs: None)
    @patch("fhir_scripts.tools.epatools.Path.read_text", lambda *args, **kswargs: None)
    def test_only_tool_config(self):
        files = ["openapi.json"]

        should_be_archived = [Path(f) for f in files]

        def config(*args, **kwargs):
            return {"openapi": {"capability-statement": [{"output": f} for f in files]}}

        archived_files = []

        def update_archive(archive_files: list, *args, **kwargs):
            archived_files.extend(archive_files)

        with patch("fhir_scripts.tools.epatools.yaml.safe_load", side_effect=config):
            with patch(
                "fhir_scripts.tools.epatools.Path.exists", lambda *args, **kwargs: True
            ):
                with patch(
                    "fhir_scripts.tools.epatools.update_archive",
                    side_effect=update_archive,
                ):
                    epatools.openapi()

        self.assertListEqual(archived_files, should_be_archived)
