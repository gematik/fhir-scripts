import re
from pathlib import Path

from ...exception import NotInstalledException
from . import shell

VERSION_REGEX = re.compile(r"\w*jdk\w*\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)


def run_jar(jar: Path, *args, capture_output: bool = False):
    is_installed()

    cmd = f"java -jar {str(jar)} {' '.join(args)}"

    res = shell.run(cmd, capture_output=capture_output)

    if capture_output:
        if res.returncode != 0:
            raise shell.CalledProcessError(
                res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
            )

    return res


def version() -> str | None:
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


def is_installed() -> None:
    """
    Checks if Java is installed
    """
    try:
        shell.run("which java", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise NotInstalledException("Java is needed but not installed")
