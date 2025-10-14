import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from .. import log
from ..config import EpaToolsArchiveConfig, EpaToolsConfig
from ..exception import NoConfigException, NotInstalledException
from .basic import pipx, shell

VERSION_REGEX = re.compile(r"EPATOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/onyg/epa-tools.git"


def merge_capabilities():
    """
    Merge CapabilityStatements
    """
    is_installed()
    is_configured()

    log.info("Merge CapabilityStatements")
    shell.run("epatools merge", capture_output=True)
    log.succ("CapabilityStatements merged successfully")


def openapi(config: EpaToolsConfig | None):
    """
    Build the Open APIs
    """
    is_installed()
    is_configured()

    if config is None:
        raise Exception("Missing config for epatools")

    log.info("Build Open APIs")
    shell.run("epatools openapi", capture_output=True)
    log.succ("Open APIs built successfully")
    update_archive(config.archive)


def update_archive(config: EpaToolsArchiveConfig):
    archive = Path("./output/full-ig.zip")

    if not archive.exists():
        raise Exception("Archive does not exists: " + str(archive))

    log.info("Update IG archive")
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Extract existing archive
        with ZipFile(archive, "r") as zip_ref:
            zip_ref.extractall(tmp_path)

        # Add new content files from config
        for content_file in config.content_files:
            content_path = Path("./output") / content_file
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


def is_installed() -> None:
    """
    Checks if installed
    """
    try:
        shell.run("which epatools", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise NotInstalledException(f"{__tool_name__} is needed but not installed")


def is_configured() -> None:
    """
    Checks if project is configured for tool"
    """
    config = Path("./epatools.yaml")

    if not config.exists():
        raise NoConfigException(f"{__tool_name__} not configured for project")


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


__tool_name__ = "epatools"
