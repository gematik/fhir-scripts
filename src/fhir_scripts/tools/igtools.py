__tool_name__ = "igtools"

import re
from functools import wraps
from pathlib import Path

from .. import log
from ..exception import NoConfigException

# Check if igtools package is installed
# try:
#     importlib.metadata.version("igtools")
#     IGTOOLS_PACKAGE_AVAILABLE = True
# except importlib.metadata.PackageNotFoundError:
IGTOOLS_PACKAGE_AVAILABLE = False


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


###
# Use the module
###
if IGTOOLS_PACKAGE_AVAILABLE:
    # Disable for now as the module does not provide a stable interface
    pass

    # from igtools.config import CONFIG_DEFAULT_DIR, CONFIG_FILE, Config
    # from igtools.specifications import (
    #     Processor,
    #     ReleaseNoteManager,
    #     RequirementExporter,
    # )

    # DEFAULT_EXPORT_FORMAT = "JSON"
    # DEFAULT_EXPORT_VERSION = "current"

    # config = Path(CONFIG_DEFAULT_DIR) / CONFIG_FILE

    # @is_configured
    # def process():
    #     """
    #     Process requirements
    #     """
    #     log.info("Processing requirements")

    #     try:
    #         config = Config()
    #         config.load()
    #         processor = Processor(config=config)
    #         processor.process()

    #     except Exception as e:
    #         raise Exception("Failed to process requirements: " + str(e))

    #     log.succ("Requirements processed")

    # @is_configured
    # def release_notes(output_dir: Path | str):
    #     """
    #     Update release notes
    #     """
    #     log.info("Updating release-notes")

    #     try:
    #         config = Config()
    #         config.load()

    #         release_note_manager = ReleaseNoteManager(config=config)
    #         release_note_manager.generate(output=output_dir)

    #     except Exception as e:
    #         raise Exception("Failed to update release-notes: " + str(e))

    #     log.succ("Release-notes updated")

    # @is_configured
    # def export(output_dir: Path | str):
    #     """
    #     Exports requirements
    #     """
    #     log.info("Export requirements")

    #     try:
    #         config = Config()
    #         config.load()
    #         filename = RequirementExporter.generate_filename(
    #             format=DEFAULT_EXPORT_FORMAT, version=DEFAULT_EXPORT_VERSION
    #         )
    #         exporter = RequirementExporter(
    #             config=config,
    #             format=DEFAULT_EXPORT_FORMAT,
    #             filename=filename,
    #             version=DEFAULT_EXPORT_VERSION,
    #         )
    #         exporter.export(output=output_dir)

    #     except Exception as e:
    #         raise Exception("Failed to export requirements: " + str(e))

    #     log.succ("Requirements exported successfully")

    # def update():
    #     pass

    # def version(short: bool = False, *args, **kwargs) -> str | None:
    #     """
    #     Get the installed version
    #     """
    #     return importlib.metadata.version("igtools")


###
# Use the command line
###
else:
    from ..helper import require_installed
    from .basic import pipx, shell

    VERSION_REGEX = re.compile(r"IGTOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
    PACKAGE = "git+https://github.com/onyg/req-tooling.git"

    config = Path("./.igtools/config.yaml")

    @is_configured
    @require_installed("igtools", __tool_name__)
    def process():
        """
        Process requirements
        """
        log.info("Processing requirements")
        shell.run("igtools process", capture_output=True)
        log.succ("Requirements processed")

    @is_configured
    @require_installed("igtools", __tool_name__)
    def release_notes(output_dir: Path | str):
        """
        Update release notes
        """
        log.info("Updating release-notes")
        shell.run(f"igtools ig-release-notes {str(output_dir)}", capture_output=True)
        log.succ("Release-notes updated")

    @is_configured
    @require_installed("igtools", __tool_name__)
    def export(output_dir: Path | str):
        """
        Exports requirements
        """
        log.info("Export requirements")
        shell.run(f"igtools export {str(output_dir)}", capture_output=True)
        log.succ("Requirements exported successfully")

    def update():
        pipx.install(PACKAGE, as_global=True)

    def version(short: bool = False, *args, **kwargs) -> str | None:
        """
        Get the installed version of igtools, returns None if not installed
        """
        try:
            res = shell.run("igtools -v", check=True, capture_output=True)

            # Extract the version string from output
            match = VERSION_REGEX.match(res.stdout_oneline)

            if short:
                return match[1] if match else None

            else:
                return f"{match[1]} ({pipx.version()})" if match else None

        except shell.CalledProcessError:
            return None
