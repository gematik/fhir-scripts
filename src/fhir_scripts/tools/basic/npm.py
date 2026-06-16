__tool_name__ = "npm"

from pathlib import Path

from ...helper import require_installed
from ...version import Version
from . import shell


@require_installed("npm", __tool_name__)
def install(pkg_name: str, version: Version, as_global: bool = False):

    pkg = pkg_name if version.unknown else f"{pkg_name}@{version}"

    flags = []
    sudo = False

    if as_global:
        flags.append("-g")
        sudo = True

    cmd = f"npm install {' '.join(flags)} {pkg}"

    # Run as sudo if needed
    if sudo:
        cmd = "sudo " + cmd

    res = shell.run(cmd)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def version(*args, **kwargs) -> Version | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("npm -v", check=True, log_output=False)
        version = Version(res.stdout_oneline)

        res = shell.run("node -v", check=True, log_output=False)
        version.add_version = Version(res.stdout_oneline.lstrip("v"))

        return version

    except shell.CalledProcessError:
        return None


@require_installed("npm", __tool_name__)
def download(
    pkg_name: str, version: str, target_dir: Path, registry: str | None = None
):
    """
    Download a package from a NPM registry

    If `registry` is provided it used instead of the default NPM one.
    """

    if not target_dir.exists():
        target_dir.mkdir(parents=True)

    if registry:
        cmd = f"npm --registry {registry} pack --pack-destination {target_dir} {pkg_name}@{version}"

    else:
        cmd = f"npm pack --pack-destination {target_dir} {pkg_name}@{version}"

    res = shell.run(cmd)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )
