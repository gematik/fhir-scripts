__tool_name__ = "Java"

import re
from pathlib import Path

from ...exception import PrerequisiteFailed
from ...helper import require_installed
from ...version import Version
from . import shell

VERSION_REGEX = re.compile(
    r"\w*jdk\w*\s+version\s+\"(\d+(?:\.\d+){,2})\"", re.IGNORECASE
)


@require_installed("java", __tool_name__)
def run_jar(jar: Path, *args, check: bool = False, log_output: bool = True):

    cmd = f"java -jar {str(jar)} {' '.join(args)}"

    res = shell.run(cmd, check=check, log_output=log_output)
    return res


def require_min_version(min: Version):
    if not has_min_version(min):
        raise PrerequisiteFailed(
            "{} version {} required, but only {} installed".format(
                __tool_name__, min, version()
            )
        )


def has_min_version(min: Version):
    return (v := version()) and min >= v


def version(*args, **kwargs) -> Version | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("java -version", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.search(res.stdout_oneline)
        return Version(match[1] if match else None)

    except shell.CalledProcessError:
        return None
