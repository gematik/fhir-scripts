import unittest
from unittest.mock import patch

from fhir_scripts.tools.basic import python
from fhir_scripts.tools.basic.shell import CalledProcessError, ShellResult


class TestPythonInstall(unittest.TestCase):

    def test_uv_installed(self):
        python.UV_AVAILABLE = True
        python.PIPX_AVAILABLE = False

        pkg = "test"
        cmd_wanted = "uv tool install --force {}".format(pkg)
        called_cmd = []

        def shell_run(cmd, *args, **kwargs):
            called_cmd.append(cmd)
            res = ShellResult()
            res.returncode = 0
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            python.install(pkg)

        self.assertEqual(1, len(called_cmd))
        self.assertEqual(cmd_wanted, called_cmd[0])

    def test_pipx_installed(self):
        python.UV_AVAILABLE = False
        python.PIPX_AVAILABLE = True

        pkg = "test"
        cmd_wanted = "pipx install -f {}".format(pkg)
        called_cmd = []

        def shell_run(cmd, *args, **kwargs):
            called_cmd.append(cmd)
            res = ShellResult()
            res.returncode = 0
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            python.install(pkg)

        self.assertEqual(1, len(called_cmd))
        self.assertEqual(cmd_wanted, called_cmd[0])

    def test_none_installed(self):
        python.UV_AVAILABLE = True
        python.PIPX_AVAILABLE = False

        pkg = "test"

        try:
            python.install(pkg)

        except Exception:
            pass

        else:
            self.fail("Did not raise exception if no Python manager is installed")


class TestPythonVersion(unittest.TestCase):
    def test_version(self):
        version = "3.1.2"

        def shell_run(*args, **kwargs):
            res = ShellResult()
            res.stdout = ["Python {}".format(version)]
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            output = python.version()

            self.assertEqual(version, output)

    def test_not_installed(self):
        def shell_run(cmd, *args, **kwargs):
            raise CalledProcessError(1, cmd)

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            output = python.version()

            self.assertEqual(None, output)
