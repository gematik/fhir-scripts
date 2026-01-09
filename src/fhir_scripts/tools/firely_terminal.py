__tool_name__ = "Firely Terminal"

import re
from pathlib import Path

from ..helper import require_installed
from ..version import Version
from .basic import dotnet, shell

VERSION_REGEX = re.compile(r"Firely Terminal\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)

PACKAGE = "firely.terminal"


@require_installed("fhir", __tool_name__)
def install(
    pkg: str | None = None, version: str | None = None, file: Path | None = None
):
    if pkg and version:
        cmd = f"fhir install {pkg} {version}"

    elif file:
        cmd = f"fhir install {str(file)} --file"

    else:
        raise Exception("For install provide a package name AND a version or a file.")

    res = shell.run(cmd)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def update(install: bool = False, *args, **kwargs):
    if install:
        dotnet.install(PACKAGE)

    else:
        # Disable for now as this appears to cause problems
        # dotnet.update(PACKAGE)
        pass


def version(short: bool = False, *args, **kwargs) -> Version:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("fhir -v", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        version = Version(match[1] if match else None)
        version.add_version = dotnet.version()

        return version

    except shell.CalledProcessError:
        return Version()


@require_installed("fhir", __tool_name__)
def restore():
    shell.run("fhir restore")
