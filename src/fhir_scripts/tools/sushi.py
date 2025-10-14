import re

from .. import log
from ..exception import NotInstalledException
from .basic import npm, shell

VERSION_REGEX = re.compile(r"SUSHI\sv(\d+(?:\.\d+){,2})\b", re.IGNORECASE)


def run():
    is_installed()
    log.info("Run sushi")
    try:
        shell.run("sushi build .")
        log.succ("Sushi run successful")

    except shell.CalledProcessError:
        raise Exception("Sushi run failed")


def is_installed() -> None:
    """
    Checks if installed
    """
    try:
        shell.run("which sushi", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise NotInstalledException("sushi is needed but not installed")


def update():
    npm.install("fsh-sushi", as_global=True)


def version() -> str | None:
    """
    Get the installed version of FSH Sushi, returns None if sushi is not installed
    """
    try:
        res = shell.run("sushi -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return f"{match[1]} ({npm.version()})" if match else None

    except shell.CalledProcessError:
        return None


__tool_name__ = "FSH Sushi"
