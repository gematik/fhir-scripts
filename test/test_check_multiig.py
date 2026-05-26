import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import check
from fhir_scripts.multiig import working_directory


class TestCheckMultiIg(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            "version: 1\nigsRoot: igs\n",
            "utf-8",
        )

        for name in ["core", "rx"]:
            (self.repo / "igs" / name).mkdir(parents=True, exist_ok=True)

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_check_with_explicit_igs(self):
        called = []

        def run_check(workdir: Path, release: bool):
            called.append((workdir.name, release))

        with patch("fhir_scripts.check._check_project", side_effect=run_check):
            with working_directory(self.repo):
                check.check(workdir=None, release=False, ig=["core", "rx"], all=False)

        self.assertEqual([("core", False), ("rx", False)], called)

    def test_check_with_all(self):
        called = []

        def run_check(workdir: Path, release: bool):
            called.append((workdir.name, release))

        with patch("fhir_scripts.check._check_project", side_effect=run_check):
            with working_directory(self.repo):
                check.check(workdir=None, release=True, ig=[], all=True)

        self.assertEqual([("core", True), ("rx", True)], called)

    def test_check_workdir_conflicts_with_ig(self):
        with self.assertRaisesRegex(Exception, "cannot be combined"):
            with working_directory(self.repo):
                check.check(
                    workdir=self.repo / "igs" / "core",
                    release=False,
                    ig=["core"],
                    all=False,
                )
