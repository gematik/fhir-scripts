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
    def test_java_version_formats(self):
        cases = [
            ('java version "1.8.0_471"', "1.8.0"),
            ('java version "17.0.15" 2025-04-15 LTS', "17.0.15"),
            ('openjdk version "21" 2023-09-19', "21"),
            ('openjdk version "21.0"', "21.0"),
            ('openjdk version "21.0.8+9-LTS"', "21.0.8"),
            ('openjdk version "26-ea"', "26"),
            ('openjdk version "26.0.1-ea+5"', "26.0.1"),
            ('openjdk version "26.0.2.1+7"', "26.0.2"),
            ('openjdk "21.0.8" 2025-07-15', "21.0.8"),
            ('OPENJDK VERSION "17.0.15"', "17.0.15"),
            ('openjdk version "21.0.13.0.3_p1-r0"', "21.0.13"),
        ]

        for output, expected in cases:
            with (
                self.subTest(output=output),
                patch(
                    "fhir_scripts.tools.basic.java.shell.run",
                    return_value=_java_version_result(output),
                ),
            ):
                self.assertEqual(Version(expected), java.version())

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
        output = (
            'openjdk version "26.0.2.1" 2026-08-18\n'
            "OpenJDK Runtime Environment Homebrew (build 26.0.2.1)\n"
            "OpenJDK 64-Bit Server VM Homebrew (build 26.0.2.1, mixed mode, sharing)\n"
        )

        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result(output),
        ):
            self.assertEqual(Version("26.0.2"), java.version())

    def test_five_part_openjdk_version(self):
        output = (
            'openjdk version "21.0.13.0.3" 2026-10-24\n'
            "OpenJDK Runtime Environment Homebrew (build 21.0.13.0.3)\n"
            "OpenJDK 64-Bit Server VM Homebrew (build 21.0.13.0.3, mixed mode, sharing)\n"
        )

        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result(output),
        ):
            self.assertEqual(Version("21.0.13.0.3"), java.version())

    def test_five_part_openjdk_version_with_argument(self):
        output = (
            "Picked up JAVA_TOOL_OPTIONS: -Xms12g -Xmx16g\n"
            'openjdk version "21.0.13.0.3" 2026-10-24\n'
            "OpenJDK Runtime Environment Homebrew (build 21.0.13.0.3)\n"
            "OpenJDK 64-Bit Server VM Homebrew (build 21.0.13.0.3, mixed mode, sharing)\n"
        )

        with patch(
            "fhir_scripts.tools.basic.java.shell.run",
            return_value=_java_version_result(output),
        ):
            self.assertEqual(Version("21.0.13.0.3"), java.version())

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
