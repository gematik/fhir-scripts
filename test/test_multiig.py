import tempfile
import unittest
from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch

import yaml

from fhir_scripts.multiig import SelectionError, select_targets


class TestMultiIgSelection(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        for name in ["core", "rx", "test"]:
            ig_dir = self.repo / "igs" / name
            ig_dir.mkdir(parents=True, exist_ok=True)
            (ig_dir / "sushi-config.yaml").write_text("id: test\n", "utf-8")

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_priority_explicit_ig_over_all(self):
        res = select_targets(
            ig=["rx"],
            select_all=True,
            cwd=self.repo / "igs" / "core",
        )

        self.assertEqual(["rx"], [entry.name for entry in res])

    def test_select_all(self):
        res = select_targets(ig=[], select_all=True, cwd=self.repo)
        self.assertEqual(["core", "rx", "test"], [entry.name for entry in res])

    def test_auto_detect_from_cwd(self):
        res = select_targets(ig=[], select_all=False, cwd=self.repo / "igs" / "rx")
        self.assertEqual(["rx"], [entry.name for entry in res])

    def test_error_on_ambiguous_root_without_ig(self):
        with self.assertRaisesRegex(SelectionError, "Unable to determine"):
            select_targets(ig=[], select_all=False, cwd=self.repo)

    def test_error_for_unknown_ig(self):
        with self.assertRaisesRegex(SelectionError, r"Unknown IG name\(s\): foo"):
            select_targets(ig=["foo"], select_all=False, cwd=self.repo)

    def test_optional_config_file_allows_aliases(self):
        config = {
            "version": 1,
            "igsRoot": "igs",
            "igs": {
                "core": {"path": "igs/core"},
                "rx": {"path": "igs/rx"},
                "erp-chrg": {"path": "igs/core"},
            },
        }
        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            yaml.safe_dump(config),
            "utf-8",
        )

        res = select_targets(ig=["erp-chrg"], select_all=False, cwd=self.repo)
        self.assertEqual(["erp-chrg"], [entry.name for entry in res])

    def test_optional_config_with_only_root_auto_matches_folder_name(self):
        config = {
            "version": 1,
            "igsRoot": "igs",
        }
        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            yaml.safe_dump(config),
            "utf-8",
        )

        res = select_targets(ig=["test"], select_all=False, cwd=self.repo)
        self.assertEqual(["test"], [entry.name for entry in res])
