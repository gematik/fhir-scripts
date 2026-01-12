import os
from pathlib import Path

from .. import log
from ..exception import NotInstalledException
from ..version import Version
from .basic import github, java, shell

JAR_NAME = "fhir-pkg-tool.jar"
REPO_URL = "https://github.com/Gefyra/fhir-pkg-tool"
DOWNLOAD_URL = REPO_URL + "/releases/latest/download/" + JAR_NAME
JAR_DIR = (Path(home) if (home := os.environ.get("HOME")) else Path()) / "fhir-pkg-tool"
JAR = JAR_DIR / JAR_NAME


def install_deps():
    java.require_min_version(Version("21"))
    ensure_installed()

    log.info("Run {}".format(__tool_name__))

    sushi_config = Path("./sushi-config.yaml")
    if not sushi_config.exists():
        raise Exception("{} missing".format(sushi_config))

    try:
        args = ["--sushi-deps-file {}".format(sushi_config)]
        java.run_jar(JAR, check=True, *args)
        log.succ("{} run successful".format(__tool_name__))

    except shell.CalledProcessError:
        raise Exception("{} run failed".format(__tool_name__))


def is_installed():
    """
    Checks if installed
    """
    return JAR.exists()


def ensure_installed():
    if not is_installed():
        raise NotInstalledException(f"{__tool_name__} is needed but not installed")


def update(*args, **kwargs):
    java.require_min_version(Version("21"))

    if not JAR_DIR.exists():
        JAR_DIR.mkdir(parents=True)

    shell.run(f'curl -L "{DOWNLOAD_URL}" -o "{JAR}"', check=True)


def version(short: bool = False, *args, **kwargs) -> Version | None:
    """
    Get the installed version, returns None if not installed
    """

    # Currently there is no way to detect the version
    if is_installed():
        return Version()

    else:
        return None


def latest_version(*args, **kwargs) -> Version | None:
    return github.latest_version_number(REPO_URL)


__tool_name__ = "FHIR Package Snapshot Tool"
