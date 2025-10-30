__tool_name__ = "FSH Sushi"

import re

from .. import log
from ..helper import require_installed
from .basic import github, npm, shell

VERSION_REGEX = re.compile(r"SUSHI\sv(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
REPO_URL = "https://github.com/FHIR/sushi"


@require_installed("sushi", __tool_name__)
def run():
    log.info("Run sushi")
    try:
        shell.run("sushi build .")
        log.succ("Sushi run successful")

    except shell.CalledProcessError:
        raise Exception("Sushi run failed")


def update(*args, **kwargs):
    npm.install("fsh-sushi", as_global=True)


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version of FSH Sushi, returns None if sushi is not installed
    """
    try:
        res = shell.run("sushi -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        if short:
            return match[1] if match else None

        else:
            return f"{match[1]} ({npm.version()})" if match else None

    except shell.CalledProcessError:
        return None


def latest_version(*args, **kwargs) -> str | None:
    return github.latest_version_number(REPO_URL)
