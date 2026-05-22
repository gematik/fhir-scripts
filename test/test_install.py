import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import install as install_module
from fhir_scripts.models.config import Config
from fhir_scripts.multiig import working_directory


class TestInstallMultiIg(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            "version: 1\nigsRoot: igs\n",
            "utf-8",
        )

        for name, tools in {
            "core": ["tool_a"],
            "rx": ["tool_b"],
        }.items():
            ig_dir = self.repo / "igs" / name
            ig_dir.mkdir(parents=True, exist_ok=True)
            install_lines = "\n".join([f"  - {tool}" for tool in tools])
            (ig_dir / "fhirscripts.config.yaml").write_text(
                f"install:\n{install_lines}\n",
                "utf-8",
            )

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_install_without_flags_uses_all_ig_configs(self):
        calls = []

        class ToolA:
            __tool_name__ = "tool-a"

            @staticmethod
            def version(*args, **kwargs):
                return None

            @staticmethod
            def update(*args, **kwargs):
                calls.append((Path.cwd().name, "tool_a"))

        class ToolB:
            __tool_name__ = "tool-b"

            @staticmethod
            def version(*args, **kwargs):
                return None

            @staticmethod
            def update(*args, **kwargs):
                calls.append((Path.cwd().name, "tool_b"))

        with patch.dict(
            install_module.TOOL_MODULES,
            {"tool_a": ToolA, "tool_b": ToolB},
            clear=True,
        ):
            with working_directory(self.repo):
                install_module.install(
                    config=Config(),
                    config_file=False,
                    config_path=None,
                )

        self.assertEqual([("core", "tool_a"), ("rx", "tool_b")], calls)
