import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import cache
from fhir_scripts.multiig import working_directory


class TestCacheMultiIg(unittest.TestCase):

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

    def test_cache_rebuild_with_all_runs_per_ig(self):
        calls = []

        def install_deps(*args, **kwargs):
            calls.append(Path.cwd().name)

        with patch("fhir_scripts.cache.fhir_pkg_tool.is_installed", lambda: True):
            with patch(
                "fhir_scripts.cache.fhir_pkg_tool.install_deps",
                side_effect=install_deps,
            ):
                with working_directory(self.repo):
                    cache.cache_rebuild_fhir_cache(
                        ig=[],
                        all=True,
                        new=True,
                        no_clear=True,
                    )

        self.assertEqual(["core", "rx"], calls)

    def test_clear_build_caches_with_explicit_igs(self):
        for name in ["core", "rx"]:
            for rel in ["input-cache/schemas", "input-cache/txcache", "temp", "template"]:
                path = self.repo / "igs" / name / rel
                path.mkdir(parents=True, exist_ok=True)

        with working_directory(self.repo):
            cache.clear_build_caches(ig=["core", "rx"], all=False)

        for name in ["core", "rx"]:
            self.assertFalse((self.repo / "igs" / name / "input-cache/schemas").exists())
            self.assertFalse((self.repo / "igs" / name / "input-cache/txcache").exists())
            self.assertFalse((self.repo / "igs" / name / "temp").exists())
            self.assertFalse((self.repo / "igs" / name / "template").exists())
