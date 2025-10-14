import re
from pathlib import Path

from .. import log
from ..exception import NoConfigException, NotInstalledException
from .basic import pipx, shell

VERSION_REGEX = re.compile(r"IGTOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/onyg/req-tooling.git"


def process():
    """
    Process requirements
    """
    is_configured()
    is_installed()

    log.info("Processing requirements")
    shell.run("igtools process", capture_output=True)
    log.succ("Requirements processed")


def release_notes(output_dir: Path | str):
    """
    Update release notes
    """
    is_configured()
    is_installed()

    log.info("Updating release-notes")
    shell.run(f"igtools ig-release-notes {str(output_dir)}", capture_output=True)
    log.succ("Release-notes updated")


def export(output_dir: Path | str):
    """
    Exports requirements
    """
    is_configured()
    is_installed()

    log.info("Export requirements")
    shell.run(f"igtools export {str(output_dir)}", capture_output=True)
    log.succ("Requirements exported successfully")


def is_installed() -> None:
    """
    Checks if installed
    """
    try:
        shell.run("which igtools", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise NotInstalledException(f"{__tool_name__} is needed but not installed")


def is_configured() -> None:
    """
    Checks if project is configured for tool"
    """
    config = Path("./.igtools/config.yaml")

    if not config.exists():
        raise NoConfigException(f"{__tool_name__} not configured for project")


def update():
    pipx.install(PACKAGE, as_global=True)


def version() -> str | None:
    """
    Get the installed version of igtools, returns None if not installed
    """
    try:
        res = shell.run("igtools -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return f"{match[1]} ({pipx.version()})" if match else None

    except shell.CalledProcessError:
        return None


__tool_name__ = "igtools"
