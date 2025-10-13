import re
from pathlib import Path

from .basic import dotnet, shell

VERSION_REGEX = re.compile(r"Firely Terminal\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)


def install(
    pkg: str | None = None, version: str | None = None, file: Path | None = None
):
    is_installed()

    if pkg and version:
        cmd = f"fhir install {pkg} {version}"

    elif file:
        cmd = f"fhir install {str(file)} --file"

    else:
        raise Exception("For install provide a package name AND a version or a file.")

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
        shell.run("which fhir", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise Exception(f"{__tool_name__} is needed but not installed")


def version() -> str | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("fhir -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)
        return f"{match[1]} ({dotnet.version()})" if match else None

    except shell.CalledProcessError:
        return None


def restore():
    shell.run("fhir restore")


__tool_name__ = "Firely Terminal"
