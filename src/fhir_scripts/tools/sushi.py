import re

from .. import log
from . import npm, shell

VERSION_REGEX = re.compile(r"SUSHI\sv([\d\.]+)\s", re.IGNORECASE)


def run():
    log.info("Run sushi")
    try:
        shell.run("sushi build .")
        log.succ("Sushi run successful")

    except shell.CalledProcessError:
        raise Exception("Sushi run failed")


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

        return match[1] if match else None

    except shell.CalledProcessError:
        return None


__tool_name__ = "FSH Sushi"
