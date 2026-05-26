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
            (ig_dir / "fhirscripts.config.yaml").write_text(
                "build:\n  pipeline:\n    - sushi\n",
                "utf-8",
            )

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

    def test_pipeline_uses_ig_local_config_when_no_explicit_config(self):
        called_steps = []

        def record_sushi(*args, **kwargs):
            called_steps.append((Path.cwd().name, "sushi"))

        def record_igpub(*args, **kwargs):
            called_steps.append((Path.cwd().name, "igpub"))

        core_cfg = self.repo / "igs" / "core" / "fhirscripts.config.yaml"
        core_cfg.write_text("build:\n  pipeline:\n    - igpub\n", "utf-8")

        with patch.dict(
            build.PIPELINE_STEPS,
            {"sushi": record_sushi, "igpub": record_igpub},
            clear=False,
        ):
            with build.working_directory(self.repo):
                build.build_pipeline(config=Config(), ig=["core"], all=False)

        self.assertEqual([("core", "igpub")], called_steps)

    def test_pipeline_base_ig_runs_before_selected_ig(self):
        (self.repo / "igs" / "test").mkdir(parents=True, exist_ok=True)
        (self.repo / "igs" / "test" / "sushi-config.yaml").write_text(
            "id: test\n", "utf-8"
        )
        (self.repo / "igs" / "test" / "fhirscripts.config.yaml").write_text(
            "build:\n  pipeline:\n    - sushi\n",
            "utf-8",
        )

        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            "version: 1\nigsRoot: igs\nbaseIG:\n  - core\n  - test\n",
            "utf-8",
        )

        called_order = []

        def record_step(*args, **kwargs):
            called_order.append(Path.cwd().name)

        with patch.dict(build.PIPELINE_STEPS, {"sushi": record_step}, clear=False):
            with build.working_directory(self.repo):
                build.build_pipeline(config=Config(), ig=["rx"], all=False)

        self.assertEqual(["core", "test", "rx"], called_order)
