__tool_name__ = "pipx"

import re
import tomllib

import requests

from ...helper import NotInstalledException, check_installed
from ...version import Version
from . import shell

VERSION_REGEX = re.compile(r"Python\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
VERSION_FILE_REGEX = re.compile(
    r"(?:Version\()?['\"]?([\d\.]+)['\"]?\)?", re.IGNORECASE
)

try:
    check_installed("uv", __tool_name__)
    UV_AVAILABLE = True

except NotInstalledException:
    UV_AVAILABLE = False

try:
    check_installed("pipx", __tool_name__)
    PIPX_AVAILABLE = True

except NotInstalledException:
    PIPX_AVAILABLE = False


def install(pkg_name: str, as_global: bool = False):
    if UV_AVAILABLE:
        cmd = "uv tool install --force {}"

    elif PIPX_AVAILABLE:
        if as_global:
            cmd = "sudo pipx install -f --global {}"

        else:
            cmd = "pipx install -f {}"

    else:
        raise Exception("No Python manager installed")

    res = shell.run(cmd.format(pkg_name))

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def latest_version_number(url: str) -> Version | None:
    url_raw = url.removeprefix("git+").removesuffix(".git") + "/raw/main/"

    pyproject_url = url_raw + "pyproject.toml"
    content = requests.get(pyproject_url)
    pyproject = tomllib.loads(content.text)

    # Try to get the information from the pyproject file
    if version := pyproject.get("project", {}).get("version"):
        return Version(version)

    # Try for poetry
    if version := pyproject.get("tool", {}).get("poetry", {}).get("version"):
        return Version(version)

    # Try dynamic version for setuptools
    if "version" in pyproject.get("project", {}).get("dynamic", []) and (
        version_loc := pyproject.get("tool", {})
        .get("setuptools", {})
        .get("dynamic", {})
        .get("version")
    ):
        if attr := version_loc.get("attr"):
            file, attr = attr.rsplit(".", 1)
            file = file.replace(".", "/") + ".py"
            version_url = url_raw + "src/" + file

            content = requests.get(version_url).text

            attrs = {
                split[0].strip().strip("'"): split[1].strip().strip("'")
                for line in content.split("\n")
                if "=" in line and (split := line.split("=")) and len(split) == 2
            }

            version = attrs.get(attr)

            if version is not None:
                match = VERSION_FILE_REGEX.match(version)
                return Version(match[1]) if match else Version(version)

    # Else nothing was found
    return None


def version(*args, **kwargs) -> Version | None:
    """
    Get the installed version of FSH Sushi, returns None if sushi is not installed
    """
    try:
        res = shell.run("python3 --version", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return Version(match[1]) if match else None

    except shell.CalledProcessError:
        return None
