import unittest
from io import StringIO
from unittest.mock import patch

from fhir_scripts import log
from fhir_scripts.tools.basic import shell


class TestShellRun(unittest.TestCase):

    def tearDown(self):
        log.configure_output_color("default")

    def test_uses_terminal_default_color_and_preserves_layout(self):
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            shell.run("printf '\\033[32m  formatted output\\033[0m\\n\\n'")

        self.assertEqual(stdout.getvalue(), "  formatted output\n\n")

    def test_can_preserve_subprocess_colors(self):
        log.configure_output_color("preserve")
        subprocess_output = "\033[32mformatted output\033[0m\n"

        with patch("sys.stdout", new_callable=StringIO) as stdout:
            shell.run("printf '\\033[32mformatted output\\033[0m\\n'")

        self.assertEqual(stdout.getvalue(), subprocess_output)

    def test_can_override_subprocess_color(self):
        for color_name in log.OUTPUT_COLOR_CHOICES[2:]:
            with self.subTest(color=color_name):
                log.configure_output_color(color_name)

                with patch("sys.stdout", new_callable=StringIO) as stdout:
                    shell.run("printf '\\033[32mformatted output\\033[0m\\n'")

                color = log.Colors[color_name.upper()]
                self.assertEqual(
                    stdout.getvalue(),
                    f"{color}formatted output\n{log.Colors.RESET}",
                )

    def test_does_not_log_subprocess_output_when_disabled(self):
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            result = shell.run("printf 'output\\n'", log_output=False)

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(result.stdout, ["output"])
