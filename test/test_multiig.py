import tempfile
import unittest
from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch

import yaml

from fhir_scripts import build, deploy, publish
from fhir_scripts.multiig import SelectionError, select_targets, working_directory


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


class TestParserSupport(unittest.TestCase):

    def test_build_parser_ig_options(self):
        parser = ArgumentParser()
        subparser = parser.add_subparsers(dest="build")
        build.setup_subparser(parser, subparser)

        args = parser.parse_args(["pipeline", "--ig", "core", "rx"])
        self.assertEqual(["core", "rx"], args.ig)
        self.assertFalse(args.all)

    def test_publish_parser_ig_options(self):
        parser = ArgumentParser()
        subparser = parser.add_subparsers(dest="publish")
        publish.setup_subparser(parser, subparser)

        args = parser.parse_args(["project", "--ig-registry", "./registry", "--all"])
        self.assertEqual([], args.ig)
        self.assertTrue(args.all)

    def test_deploy_parser_ig_options(self):
        parser = ArgumentParser()
        deploy.setup_parser(parser)

        args = parser.parse_args(["dev", "--ig", "rx"])
        self.assertEqual(["rx"], args.ig)
        self.assertFalse(args.all)


class TestPublishMultiIg(unittest.TestCase):

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
            (ig_dir / "sushi-config.yaml").write_text("id: test\n", "utf-8")

        (self.repo / "project").mkdir(parents=True, exist_ok=True)

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_publish_relative_project_dir_is_resolved_from_invocation_cwd(self):
        calls = []

        def publish_stub(project_dir: Path, ig_registry: Path):
            calls.append((project_dir.resolve(), ig_registry, Path.cwd().name))

        with patch("fhir_scripts.publish.publishtools.publish", side_effect=publish_stub):
            with working_directory(self.repo):
                publish.publish_project(
                    project_dir=Path("project"),
                    ig_registry=Path("/tmp/ig-registry"),
                    ig=[],
                    all=True,
                )

        expected_project_dir = (self.repo / "project").resolve()
        self.assertEqual(
            [
                (expected_project_dir, Path("/tmp/ig-registry"), "core"),
                (expected_project_dir, Path("/tmp/ig-registry"), "rx"),
            ],
            calls,
        )
