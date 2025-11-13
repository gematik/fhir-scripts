import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts.models.config import Config
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

        def tool_config(*args, **kwargs):
            return {"openapi": {"capability-statement": [{"output": f} for f in files]}}

        archived_files = []

        def update_archive(archive_files: list, *args, **kwargs):
            archived_files.extend(archive_files)

        config = Config()
        with patch(
            "fhir_scripts.tools.epatools.yaml.safe_load", side_effect=tool_config
        ):
            with patch(
                "fhir_scripts.tools.epatools.Path.exists", lambda *args, **kwargs: True
            ):
                with patch(
                    "fhir_scripts.tools.epatools.update_archive",
                    side_effect=update_archive,
                ):
                    epatools.openapi(config=config)

        self.assertListEqual(archived_files, should_be_archived)

    @patch(
        "fhir_scripts.tools.epatools.check_configured", lambda *args, **kswargs: None
    )
    @patch("fhir_scripts.tools.epatools.check_installed", lambda *args, **kswargs: None)
    @patch("fhir_scripts.tools.epatools.shell.run", lambda *args, **kswargs: None)
    @patch("fhir_scripts.tools.epatools.Path.read_text", lambda *args, **kswargs: None)
    def test_also_script_config(self):
        files = ["openapi.json"]
        files_add = ["openapi.add.json"]

        should_be_archived = [Path(f) for f in files + files_add]

        def tool_config(*args, **kwargs):
            return {"openapi": {"capability-statement": [{"output": f} for f in files]}}

        archived_files = []

        def update_archive(archive_files: list, *args, **kwargs):
            archived_files.extend(archive_files)

        config_data = {
            "build": {"args": {"openapi": {"additional_archive": files_add}}}
        }
        config = Config.model_validate(config_data)
        with patch(
            "fhir_scripts.tools.epatools.yaml.safe_load", side_effect=tool_config
        ):
            with patch(
                "fhir_scripts.tools.epatools.Path.exists", lambda *args, **kwargs: True
            ):
                with patch(
                    "fhir_scripts.tools.epatools.update_archive",
                    side_effect=update_archive,
                ):
                    epatools.openapi(config=config)

        self.assertListEqual(archived_files, should_be_archived)
