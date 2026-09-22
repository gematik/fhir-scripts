import os
import unittest
from unittest.mock import patch

from fhir_scripts import log
from fhir_scripts.tools.basic import shell


class TestShellRun(unittest.TestCase):

    def tearDown(self):
        log.configure_output_color("default")

    def test_uses_terminal_default_color_and_preserves_layout(self):
        with patch("fhir_scripts.log.logging.debug") as debug:
            shell.run("printf '\\033[32m  formatted output\\033[0m\\n\\n'")

        self.assertEqual(debug.call_args_list[1].args[0], "  formatted output")

    def test_can_preserve_subprocess_colors(self):
        log.configure_output_color("preserve")
        subprocess_output = "\033[32mformatted output\033[0m"

        with patch("fhir_scripts.log.logging.debug") as debug:
            shell.run("printf '\\033[32mformatted output\\033[0m\\n'")

        self.assertEqual(debug.call_args_list[1].args[0], subprocess_output)

    def test_requests_colors_from_subprocess_when_preserving(self):
        log.configure_output_color("preserve")
        subprocess_output = "\033[32mformatted output\033[0m"
        command = (
            'test "$FORCE_COLOR" = "1" '
            '&& test -z "${NO_COLOR:-}" '
            "&& printf '\\033[32mformatted output\\033[0m\\n'"
        )

        with patch.dict(os.environ, {"NO_COLOR": "1"}, clear=True):
            with patch("fhir_scripts.log.logging.debug") as debug:
                result = shell.run(command)

        self.assertEqual(debug.call_args_list[1].args[0], subprocess_output)
        self.assertEqual(result.stdout, ["formatted output"])

    def test_can_override_subprocess_color(self):
        for color_name in log.OUTPUT_COLOR_CHOICES[2:]:
            with self.subTest(color=color_name):
                log.configure_output_color(color_name)

                with patch("fhir_scripts.log.logging.debug") as debug:
                    shell.run("printf '\\033[32mformatted output\\033[0m\\n'")

                color = log.Colors[color_name.upper()]
                self.assertEqual(
                    debug.call_args_list[1].args[0],
                    f"{color}formatted output\n{log.Colors.RESET}",
                )

    def test_does_not_log_subprocess_output_when_disabled(self):
        with patch("fhir_scripts.log.logging.debug") as debug:
            result = shell.run("printf 'output\\n'", log_output=False)

        self.assertFalse(debug.called)
        self.assertEqual(result.stdout, ["output"])
