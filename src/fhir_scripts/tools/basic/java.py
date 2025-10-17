__tool_name__ = "Java"

import re
from pathlib import Path

from ...helper import require_installed
from . import shell

VERSION_REGEX = re.compile(r"\w*jdk\w*\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)

require_installed = require_installed("java", __tool_name__)


@require_installed
def run_jar(jar: Path, *args, capture_output: bool = False):

    cmd = f"java -jar {str(jar)} {' '.join(args)}"

    res = shell.run(cmd, capture_output=capture_output)

    if capture_output:
        if res.returncode != 0:
            raise shell.CalledProcessError(
                res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
            )

    return res


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("java --version", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)
        return match[1] if match else None

    except shell.CalledProcessError:
        return None
