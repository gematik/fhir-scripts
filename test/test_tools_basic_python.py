import unittest
from unittest.mock import patch

from fhir_scripts.tools.basic import python
from fhir_scripts.tools.basic.shell import CalledProcessError, ShellResult
from fhir_scripts.version import Version


class TestPythonInstall(unittest.TestCase):

    def test_uv_latest(self):
        python.UV_AVAILABLE = True
        python.PIPX_AVAILABLE = False

        pkg = "test"
        cmd_wanted = f"uv tool install --force {pkg}"
        called_cmd = []

        def shell_run(cmd, *args, **kwargs):
            called_cmd.append(cmd)
            res = ShellResult()
            res.returncode = 0
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            python.install(pkg, Version())

        self.assertEqual(1, len(called_cmd))
        self.assertEqual(cmd_wanted, called_cmd[0])

    def test_pipx_latest(self):
        python.UV_AVAILABLE = False
        python.PIPX_AVAILABLE = True

        pkg = "test"
        cmd_wanted = f"pipx install -f {pkg}"
        called_cmd = []

        def shell_run(cmd, *args, **kwargs):
            called_cmd.append(cmd)
            res = ShellResult()
            res.returncode = 0
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            python.install(pkg, Version())

        self.assertEqual(1, len(called_cmd))
        self.assertEqual(cmd_wanted, called_cmd[0])

    def test_uv_specific_version(self):
        python.UV_AVAILABLE = True
        python.PIPX_AVAILABLE = False

        pkg = "test"
        version = "1.2.3"
        cmd_wanted = f"uv tool install --force {pkg}=={version}"
        called_cmd = []

        def shell_run(cmd, *args, **kwargs):
            called_cmd.append(cmd)
            res = ShellResult()
            res.returncode = 0
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            python.install(pkg, Version(version))

        self.assertEqual(1, len(called_cmd))
        self.assertEqual(cmd_wanted, called_cmd[0])

    def test_pipx_specific_version(self):
        python.UV_AVAILABLE = False
        python.PIPX_AVAILABLE = True

        pkg = "test"
        version = "1.2.3"
        cmd_wanted = f"pipx install -f {pkg}=={version}"
        called_cmd = []

        def shell_run(cmd, *args, **kwargs):
            called_cmd.append(cmd)
            res = ShellResult()
            res.returncode = 0
            return res

        with patch("fhir_scripts.tools.epatools.shell.run", side_effect=shell_run):
            python.install(pkg, Version(version))

        self.assertEqual(1, len(called_cmd))
        self.assertEqual(cmd_wanted, called_cmd[0])

    def test_none_installed(self):
        python.UV_AVAILABLE = True
        python.PIPX_AVAILABLE = False

        pkg = "test"

        try:
            python.install(pkg, Version())

        except Exception:
            pass

        else:
            self.fail("Did not raise exception if no Python manager is installed")


class TestPythonVersion(unittest.TestCase):
    def test_version(self):
        version = Version("3.1.2")

        def shell_run(*args, **kwargs):
            res = ShellResult()
            res.stdout = "Python {}".format(version)
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
