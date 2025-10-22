__tool_name__ = "pipx"

import re

from ...helper import require_installed
from . import shell

VERSION_REGEX = re.compile(r"Python\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)


@require_installed("pipx", __tool_name__)
def install(pkg_name: str, as_global: bool = False):

    if as_global:
        cmd = f"sudo pipx install -f --global {pkg_name}"

    else:
        cmd = f"pipx install -f {pkg_name}"

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def version(short: bool = False, *args, **kwargs) -> str | None:
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
