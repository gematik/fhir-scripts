__tool_name__ = "igtools"

import re
from functools import wraps
from pathlib import Path

from .. import log
from ..exception import NoConfigException
from ..helper import log_version, require_installed
from ..version import Version
from .basic import python, shell

VERSION_REGEX = re.compile(r"REQTOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/gematik/fhir-igtools.git"

config = Path("./.igtools/config.yaml")


def is_configured(func):
    """
    Checks if project is configured for tool"
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not config.exists():
            raise NoConfigException(f"{__tool_name__} not configured for project")

        return func(*args, **kwargs)

    return wrapper


@is_configured
@require_installed("reqtools", __tool_name__)
@log_version()
@log_version(python)
def process():
    """
    Process requirements
    """
    log.info("Processing requirements")
    shell.run("reqtools process")
    log.succ("Requirements processed")


@is_configured
@require_installed("reqtools", __tool_name__)
@log_version()
@log_version(python)
def release_notes(output_dir: Path | str):
    """
    Update release notes
    """
    log.info("Updating release-notes")
    shell.run(f"reqtools ig-release-notes {str(output_dir)}")
    log.succ("Release-notes updated")


@is_configured
@require_installed("reqtools", __tool_name__)
@log_version()
@log_version(python)
def export(output_dir: Path | str):
    """
    Exports requirements
    """
    log.info("Export requirements")
    shell.run(f"reqtools export {str(output_dir)}")
    log.succ("Requirements exported successfully")


def update(*args, **kwargs):
    python.install(PACKAGE, as_global=True)


def version(short: bool = False, *args, **kwargs) -> Version | None:
    """
    Get the installed version of reqtools, returns None if not installed
    """
    try:
        res = shell.run("reqtools -v", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.search(res.stdout_oneline)

        version = Version(match[1] if match else None)
        version.add_version = python.version()

        return version

    except shell.CalledProcessError:
        return None


def latest_version(*args, **kwargs) -> Version | None:
    return python.latest_version_number(PACKAGE)
