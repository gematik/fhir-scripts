import tempfile
import unittest
from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import multiig


class TestMultiIgMode(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            "version: 1\nigsRoot: igs\n",
            "utf-8",
        )

        for name in ["core", "rx", "test"]:
            ig_dir = self.repo / "igs" / name
            ig_dir.mkdir(parents=True, exist_ok=True)
            (ig_dir / "sushi-config.yaml").write_text("id: test\n", "utf-8")

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_parser_options(self):
        parser = ArgumentParser()
        multiig.setup_parser(parser)

        args = parser.parse_args(["--ig", "core", "--ig", "rx", "build", "pipeline"])
        self.assertEqual(["core", "rx"], args.ig)
        self.assertFalse(args.all)
        self.assertEqual(["build", "pipeline"], args.command)

    def test_multiig_runs_all_by_default(self):
        calls = []

        class Proc:
            returncode = 0

        def fake_run(cmd, cwd, check):
            calls.append((cmd, Path(cwd).name, check))
            return Proc()

        with patch("fhir_scripts.multiig.subprocess.run", side_effect=fake_run):
            with multiig.working_directory(self.repo):
                multiig.handle_multiig(command=["build", "pipeline"])

        self.assertEqual(["core", "rx", "test"], [entry[1] for entry in calls])

    def test_multiig_runs_requested_order(self):
        calls = []

        class Proc:
            returncode = 0

        def fake_run(cmd, cwd, check):
            calls.append(Path(cwd).name)
            return Proc()

        with patch("fhir_scripts.multiig.subprocess.run", side_effect=fake_run):
            with multiig.working_directory(self.repo):
                multiig.handle_multiig(
                    command=["build", "pipeline"],
                    ig=["rx", "core"],
                )

        self.assertEqual(["rx", "core"], calls)

    def test_nested_multiig_is_rejected(self):
        with self.assertRaisesRegex(Exception, "Nested multi-IG mode"):
            with multiig.working_directory(self.repo):
                multiig.handle_multiig(command=["multiig", "build", "pipeline"])

    def test_failed_subcommand_reports_failed_igs(self):
        class ProcOk:
            returncode = 0

        class ProcFail:
            returncode = 1

        def fake_run(cmd, cwd, check):
            if Path(cwd).name == "rx":
                return ProcFail()
            return ProcOk()

        with patch("fhir_scripts.multiig.subprocess.run", side_effect=fake_run):
            with self.assertRaisesRegex(
                Exception,
                r"multiig execution failed for IG\(s\): rx",
            ):
                with multiig.working_directory(self.repo):
                    multiig.handle_multiig(command=["build", "pipeline"])

    def test_forwarded_command_keeps_inner_options(self):
        calls = []

        class Proc:
            returncode = 0

        def fake_run(cmd, cwd, check):
            calls.append(cmd)
            return Proc()

        with patch("fhir_scripts.multiig.subprocess.run", side_effect=fake_run):
            with multiig.working_directory(self.repo):
                multiig.handle_multiig(
                    command=["build", "pipeline", "--update", "--ig", "rx"],
                    ig=["core"],
                )

        forwarded = calls[0][-5:]
        self.assertEqual(["build", "pipeline", "--update", "--ig", "rx"], forwarded)
