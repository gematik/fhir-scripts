__tool_name__ = "epatools"

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import yaml

from .. import log
from ..exception import NoConfigException
from ..helper import check_installed
from ..models.config import Config
from .basic import python, shell

VERSION_REGEX = re.compile(r"EPATOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/onyg/epa-tools.git"

config_file = Path("./epatools.yaml")


def check_configured():
    if not config_file.exists():
        raise NoConfigException(f"{__tool_name__} not configured for project")


def merge_capabilities():
    """
    Merge CapabilityStatements
    """

    check_configured()
    check_installed("epatools", __tool_name__)
    log.info("Merge CapabilityStatements")
    shell.run("epatools merge", check=True)
    log.succ("CapabilityStatements merged successfully")


def openapi(config: Config, *args, **kwargs):
    """
    Build the Open APIs
    """
    check_configured()
    check_installed("epatools", __tool_name__)

    log.info("Build Open APIs")
    shell.run("epatools openapi", check=True)
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
    update_archive(api_files + config.build.args.openapi.additional_archive)


def update(*args, **kwargs):
    python.install(PACKAGE, as_global=True)


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version of epatools, returns None if not installed
    """
    try:
        res = shell.run("epatools -v", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        if short:
            return match[1] if match else None

        else:
            return f"{match[1]} ({python.version()})" if match else None

    except shell.CalledProcessError:
        return None


def latest_version(*args, **kwargs) -> str | None:
    return python.latest_version_number(PACKAGE)


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
