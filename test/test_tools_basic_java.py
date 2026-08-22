import unittest
from unittest.mock import patch

from fhir_scripts.tools.basic import java
from fhir_scripts.tools.basic.shell import CalledProcessError, ShellResult
from fhir_scripts.version import Version


def _java_version_result(output: str) -> ShellResult:
    res = ShellResult()
    res.returncode = 0
    res.stdout = output
    return res


class TestJavaVersion(unittest.TestCase):
    def test_three_part_openjdk_version(self):
        output = (
            'openjdk version "17.0.15" 2025-04-15\n'
            "OpenJDK Runtime Environment Temurin-17.0.15+6 (build 17.0.15+6-LTS)\n"
        )

        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result(output),
        ):
            self.assertEqual(Version("17.0.15"), java.version())

    def test_four_part_openjdk_version(self):
        # Homebrew and recent Temurin builds report JEP 223's optional PATCH
        # component, e.g. 26.0.2.1. The previous regex accepted at most three
        # numeric parts and treated those JDKs as not installed.
        output = (
            'openjdk version "26.0.2.1" 2026-08-18\n'
            "OpenJDK Runtime Environment Homebrew (build 26.0.2.1)\n"
            "OpenJDK 64-Bit Server VM Homebrew (build 26.0.2.1, mixed mode, sharing)\n"
        )

        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result(output),
        ):
            self.assertEqual(Version("26.0.2.1"), java.version())

    def test_four_part_version_satisfies_java_17_minimum(self):
        output = 'openjdk version "26.0.2.1" 2026-08-18\n'

        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result(output),
        ):
            self.assertTrue(java.has_min_version(Version("17")))

    def test_unparseable_version_is_unknown(self):
        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result("not a java version banner"),
        ):
            self.assertTrue(java.version().unknown)

    def test_not_installed(self):
        def shell_run(cmd, *args, **kwargs):
            raise CalledProcessError(1, cmd)

        with patch("fhir_scripts.tools.basic.java.shell.run", side_effect=shell_run):
            self.assertIsNone(java.version())
