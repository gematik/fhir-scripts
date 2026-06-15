import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fhir_scripts import update
from fhir_scripts.multiig import working_directory


class TestUpdateMultiIg(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            "version: 1\nigsRoot: igs\n",
            "utf-8",
        )

        for name in ["core", "rx"]:
            ig_dir = self.repo / "igs" / name
            ig_dir.mkdir(parents=True, exist_ok=True)

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_update_runs_igpub_per_ig_in_multiig_root(self):
        igpub_calls = []
        other_calls = []

        igpub_module = SimpleNamespace(
            __name__="fhir_scripts.tools.igpub",
            __tool_name__="IG Publisher",
            version=lambda *args, **kwargs: "1.0.0",
            latest_version=lambda *args, **kwargs: None,
            update=lambda *args, **kwargs: igpub_calls.append(Path.cwd().name),
        )
        sushi_module = SimpleNamespace(
            __name__="fhir_scripts.tools.sushi",
            __tool_name__="sushi",
            version=lambda *args, **kwargs: "1.0.0",
            latest_version=lambda *args, **kwargs: None,
            update=lambda *args, **kwargs: other_calls.append(Path.cwd().name),
        )

        modules = {
            "fhir_scripts.tools.igpub": igpub_module,
            "fhir_scripts.tools.sushi": sushi_module,
        }

        with patch(
            "fhir_scripts.update.pkgutil.iter_modules",
            lambda *args, **kwargs: [
                (None, "fhir_scripts.tools.igpub", None),
                (None, "fhir_scripts.tools.sushi", None),
            ],
        ):
            with patch(
                "fhir_scripts.update.importlib.import_module",
                side_effect=lambda mod_name: modules[mod_name],
            ):
                with working_directory(self.repo):
                    update.update()

        self.assertEqual(["core", "rx"], igpub_calls)
        self.assertEqual([self.repo.name], other_calls)
