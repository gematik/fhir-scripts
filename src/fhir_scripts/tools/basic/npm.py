__tool_name__ = "npm"

from pathlib import Path

from ...helper import require_installed
from . import shell


@require_installed("npm", __tool_name__)
def install(pkg_name: str, as_global: bool = False):

    if as_global:
        cmd = f"sudo npm install -g {pkg_name}"

    else:
        cmd = f"npm install {pkg_name}"

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("npm -v", check=True, capture_output=True)
        version = res.stdout_oneline

        res = shell.run("node -v", check=True, capture_output=True)
        sdk_version = res.stdout_oneline.lstrip("v")

        return f"{version} [{sdk_version}]"

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

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )
