import re

from ...exception import NotInstalledException
from . import shell

VERSION_REGEX = re.compile(r"Python\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)


def install(pkg_name: str, as_global: bool = False):
    is_installed()

    if as_global:
        cmd = f"sudo pipx install --global {pkg_name}"

    else:
        cmd = f"pipx install {pkg_name}"

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def is_installed() -> None:
    """
    Checks if installed
    """
    try:
        shell.run("which pipx", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise NotInstalledException(f"{__tool_name__} is needed but not installed")


def version() -> str | None:
    """
    Get the installed version of FSH Sushi, returns None if sushi is not installed
    """
    try:
        res = shell.run("python3 --version", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return match[1] if match else None

    except shell.CalledProcessError:
        return None


__tool_name__ = "pipx"
