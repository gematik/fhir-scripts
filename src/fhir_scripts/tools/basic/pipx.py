__tool_name__ = "pipx"

import re
import tomllib

import requests

from ...helper import require_installed
from . import shell

VERSION_REGEX = re.compile(r"Python\s+(\d+(?:\.\d+){,2})\b", re.IGNORECASE)


@require_installed("pipx", __tool_name__)
def install(pkg_name: str, as_global: bool = False):

    if as_global:
        cmd = f"sudo pipx install -f --global {pkg_name}"

    else:
        cmd = f"pipx install -f {pkg_name}"

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def latest_version_number(url: str) -> str | None:
    url_raw = url.lstrip("git+").rstrip(".git") + "/raw/main/"

    pyproject_url = url_raw + "pyproject.toml"
    content = requests.get(pyproject_url)
    pyproject = tomllib.loads(content.text)

    # Try to get the information from the pyproject file
    if version := pyproject.get("project", {}).get("version"):
        return version

    # Try for poetry
    if version := pyproject.get("tool", {}).get("poetry", {}).get("version"):
        return version

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
                for l in content.split("\n")
                if "=" in l and (split := l.split("=")) and len(split) == 2
            }

            version = attrs.get(attr)

            if version is not None:
                return version

    # Else nothing was found
    return None


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version of FSH Sushi, returns None if sushi is not installed
    """
    try:
        res = shell.run("python3 --version", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return match[1] if match else None

    except shell.CalledProcessError:
        return None
