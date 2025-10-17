__tool_name__ = "publishtools"

import importlib.metadata
import re
from pathlib import Path

from .. import log

# Check if igtools package is installed
try:
    importlib.metadata.version("publish_tools")
    PUBLISHTOOLS_PACKAGE_AVAILABLE = True
except importlib.metadata.PackageNotFoundError:
    PUBLISHTOOLS_PACKAGE_AVAILABLE = False


###
# Use the module
###
if PUBLISHTOOLS_PACKAGE_AVAILABLE:
    from publish_tools import ig, render

    def publish(project_dir: Path, ig_registry: Path):
        """
        Publish project
        """
        log.info("Publish project")
        ig.publish(project_dir, ig_registry)
        log.succ("Project published successfully")

    def render_list(ig_registry: Path):
        """
        Render the IG overview list
        """
        log.info("Render IG overview list")
        render.render_ig_list(ig_registry)
        log.succ("IG overview rendered successfully")

    def update():
        pass

    def version(short: bool = False, *args, **kwargs) -> str | None:
        """
        Get the installed version
        """
        return importlib.metadata.version("publish_tools")


###
# Use the command line
###
else:
    from ..helper import require_installed
    from .basic import pipx, shell

    VERSION_REGEX = re.compile(r"IGTOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
    PACKAGE = "git+https://github.com/gematik/publish-tools.git"

    require_installed = require_installed("publishtools", __tool_name__)

    @require_installed
    def publish(project_dir: Path, ig_registry: Path):
        """
        Publish project
        """
        log.info("Publish project")
        shell.run(
            f"publishtools publish --project-dir {str(project_dir)} --ig-registry {str(ig_registry)}",
            capture_output=True,
        )
        log.succ("Project published successfully")

    @require_installed
    def render_list(ig_registry: Path):
        """
        Render the IG overview list
        """
        log.info("Render IG overview list")
        shell.run(
            f"publishtools render-list --ig-registry {str(ig_registry)}",
            capture_output=True,
        )
        log.succ("IG overview rendered successfully")

    def update():
        pipx.install(PACKAGE, as_global=True)

    def version(short: bool = False, *args, **kwargs) -> str | None:
        """
        Get the installed version of igtools, returns None if not installed
        """
        try:
            res = shell.run("publishtools version", check=True, capture_output=True)
            version = res.stdout_oneline

            if short:
                return version if version else None

            else:
                return f"{version} ({pipx.version()})" if version else None

        except shell.CalledProcessError:
            return None
