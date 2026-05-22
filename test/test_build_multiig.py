import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import build
from fhir_scripts.models.config import Config


class TestBuildPipelineMultiIg(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        for name in ["core", "rx"]:
            ig_dir = self.repo / "igs" / name
            ig_dir.mkdir(parents=True, exist_ok=True)
            (ig_dir / "sushi-config.yaml").write_text("id: test\n", "utf-8")

        self.cfg = Config.model_validate({"build": {"pipeline": ["sushi"]}})
        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_pipeline_with_single_ig(self):
        called_cwds = []

        def record_step(*args, **kwargs):
            called_cwds.append(str(Path.cwd()))

        with patch.dict(build.PIPELINE_STEPS, {"sushi": record_step}, clear=False):
            with build.working_directory(self.repo):
                build.build_pipeline(
                    config=self.cfg,
                    ig=["core"],
                    all=False,
                    cmd="build",
                )

        self.assertEqual([str((self.repo / "igs" / "core").resolve())], called_cwds)

    def test_pipeline_with_multiple_ig(self):
        called_cwds = []

        def record_step(*args, **kwargs):
            called_cwds.append(str(Path.cwd()))

        with patch.dict(build.PIPELINE_STEPS, {"sushi": record_step}, clear=False):
            with build.working_directory(self.repo):
                build.build_pipeline(
                    config=self.cfg,
                    ig=["core", "rx"],
                    all=False,
                    cmd="build",
                )

        self.assertEqual(
            [
                str((self.repo / "igs" / "core").resolve()),
                str((self.repo / "igs" / "rx").resolve()),
            ],
            called_cwds,
        )

    def test_pipeline_with_all(self):
        called_cwds = []

        def record_step(*args, **kwargs):
            called_cwds.append(str(Path.cwd()))

        with patch.dict(build.PIPELINE_STEPS, {"sushi": record_step}, clear=False):
            with build.working_directory(self.repo):
                build.build_pipeline(config=self.cfg, ig=[], all=True, cmd="build")

        self.assertEqual(
            [
                str((self.repo / "igs" / "core").resolve()),
                str((self.repo / "igs" / "rx").resolve()),
            ],
            called_cwds,
        )

    def test_pipeline_unknown_ig(self):
        with self.assertRaisesRegex(Exception, "Unknown IG name"):
            with build.working_directory(self.repo):
                build.build_pipeline(config=self.cfg, ig=["unknown"], all=False)
