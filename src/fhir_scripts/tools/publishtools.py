__tool_name__ = "publishtools"

import re
from pathlib import Path

from .. import log
from ..helper import require_installed
from .basic import python, shell

VERSION_REGEX = re.compile(r"IGTOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/gematik/publish-tools.git"


@require_installed("publishtools", __tool_name__)
def publish(project_dir: Path, ig_registry: Path):
    """
    Publish project
    """
    log.info("Publish project")
    shell.run(
        f"publishtools publish --project-dir {str(project_dir)} --ig-registry {str(ig_registry)}",
    )
    log.succ("Project published successfully")


@require_installed("publishtools", __tool_name__)
def render_list(ig_registry: Path):
    """
    Render the IG overview list
    """
    log.info("Render IG overview list")
    shell.run(f"publishtools render-list --ig-registry {str(ig_registry)}")
    log.succ("IG overview rendered successfully")


def update(*args, **kwargs):
    python.install(PACKAGE, as_global=True)


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version of igtools, returns None if not installed
    """
    try:
        res = shell.run("publishtools version", check=True, log_output=False)
        version = res.stdout_oneline

        if short:
            return version if version else None

        else:
            return f"{version} ({python.version()})" if version else None

    except shell.CalledProcessError:
        return None


def latest_version(*args, **kwargs) -> str | None:
    return python.latest_version_number(PACKAGE)
