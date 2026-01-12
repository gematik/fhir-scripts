__tool_name__ = "FSH Sushi"

import re

from .. import log
from ..helper import require_installed
from ..version import Version
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


def version(short: bool = False, *args, **kwargs) -> Version | None:
    """
    Get the installed version of FSH Sushi, returns None if sushi is not installed
    """
    try:
        res = shell.run("sushi -v", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.search(res.stdout_oneline)

        version = Version(match[1] if match else None)
        version.add_version = npm.version()

        return version

    except shell.CalledProcessError:
        return None


def latest_version(*args, **kwargs) -> Version | None:
    return github.latest_version_number(REPO_URL)
