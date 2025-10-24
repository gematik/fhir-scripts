__tool_name__ = "epatools"

import re
from functools import wraps
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import yaml

from .. import log
from ..exception import NoConfigException
from ..models.build_config import BuildBuiltinEpaToolsConfig

# try:
#     importlib.metadata.version("epatools")
#     EPATOOLS_PACKAGE_AVAILABLE = True
# except importlib.metadata.PackageNotFoundError:
EPATOOLS_PACKAGE_AVAILABLE = False

config_file = Path("./epatools.yaml")


def is_configured(func):
    """
    Checks if project is configured for tool"
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not config_file.exists():
            raise NoConfigException(f"{__tool_name__} not configured for project")

        return func(*args, **kwargs)

    return wrapper


###
# Use the module
###
if EPATOOLS_PACKAGE_AVAILABLE:
    # Disable for now as the module does not provide a stable interface
    pass

    # from epatools.common import DEFAULT_CONFIG
    # from epatools.merger import Merger
    # from epatools.oaconverter import OpenApiConverter

    # @is_configured
    # def merge_capabilities():
    #     """
    #     Merge CapabilityStatements
    #     """
    #     log.info("Merge CapabilityStatements")

    #     try:
    #         merger = Merger(config_file=DEFAULT_CONFIG).load()
    #         merger.merge()

    #     except Exception as e:
    #         raise Exception("Failed to merge CapabilityStatements: " + str(e))

    #     log.succ("CapabilityStatements merged successfully")

    # @is_configured
    # def openapi(config: EpaToolsConfig | bool | None):
    #     """
    #     Build the Open APIs
    #     """
    #     if config is None:
    #         raise Exception("Missing config for epatools")

    #     log.info("Build Open APIs")

    #     try:
    #         converter = OpenApiConverter(config_file=DEFAULT_CONFIG).load()
    #         converter.convert()

    #     # Get the generated API files from the tool config
    #     tool_config = yaml.safe_load(config_file.read_text("utf-8"))
    #     output_dir = Path("./output")
    #     api_files = [
    #         file
    #         for item in tool_config["openapi"]["capability-statement"]
    #         if (file := Path(item["output"])) and (output_dir / file).exists()
    #     ]

    #     # Archive the API files
    #     update_archive(api_files)

    # def update():
    #     pass

    # def version(short: bool = False, *args, **kwargs) -> str | None:
    #     """
    #     Get the installed version
    #     """
    #     return importlib.metadata.version("epatools")


###
# Use the command line
###
else:
    from ..helper import require_installed
    from .basic import pipx, shell

    VERSION_REGEX = re.compile(r"EPATOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
    PACKAGE = "git+https://github.com/onyg/epa-tools.git"

    @is_configured
    @require_installed("epatools", __tool_name__)
    def merge_capabilities():
        """
        Merge CapabilityStatements
        """
        log.info("Merge CapabilityStatements")
        shell.run("epatools merge", capture_output=True)
        log.succ("CapabilityStatements merged successfully")

    @is_configured
    @require_installed("epatools", __tool_name__)
    def openapi(*args, **kwargs):
        """
        Build the Open APIs
        """

        log.info("Build Open APIs")
        shell.run("epatools openapi", capture_output=True)
        log.succ("Open APIs built successfully")

        # Get the generated API files from the tool config
        tool_config = yaml.safe_load(config_file.read_text("utf-8"))
        output_dir = Path("./output")
        api_files = [
            file
            for item in tool_config["openapi"]["capability-statement"]
            if (file := Path(item["output"])) and (output_dir / file).exists()
        ]

        # Archive the API files
        update_archive(api_files)

    def update():
        pipx.install(PACKAGE, as_global=True)

    def version(short: bool = False, *args, **kwargs) -> str | None:
        """
        Get the installed version of epatools, returns None if not installed
        """
        try:
            res = shell.run("epatools -v", check=True, capture_output=True)

            # Extract the version string from output
            match = VERSION_REGEX.match(res.stdout_oneline)

            if short:
                return match[1] if match else None

            else:
                return f"{match[1]} ({pipx.version()})" if match else None

        except shell.CalledProcessError:
            return None


def update_archive(archive_files: list[Path], output_dir: Path | None = None):
    archive = Path("./output/full-ig.zip")

    if output_dir is None:
        output_dir = Path("./output")

    if not archive.exists():
        raise Exception("Archive does not exists: " + str(archive))

    log.info("Update IG archive")
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Extract existing archive
        with ZipFile(archive, "r") as zip_ref:
            zip_ref.extractall(tmp_path)

        # Add new content files from config
        for content_file in archive_files:
            content_path = output_dir / content_file
            if content_path.exists():
                # Copy to temp directory
                log.info(f"Adding or replacing '{content_file}' in '{archive}'")
                dest = tmp_path / "site" / content_file.name
                dest.write_bytes(content_path.read_bytes())

        # Create new archive
        with ZipFile(archive, "w", ZIP_DEFLATED) as zip_ref:
            for file_path in tmp_path.rglob("*"):
                if file_path.is_file():
                    zip_ref.write(file_path, file_path.relative_to(tmp_path))

    log.succ(f"IG archive updated successfully: {str(archive)}")
