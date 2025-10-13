import re

from .basic import pipx, shell

VERSION_REGEX = re.compile(r"IGTOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/onyg/req-tooling.git"


def is_installed() -> None:
    """
    Checks if installed
    """
    try:
        shell.run("which igtools", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise Exception(f"{__tool_name__} is needed but not installed")


def update():
    pipx.install(PACKAGE, as_global=True)


def version() -> str | None:
    """
    Get the installed version of igtools, returns None if not installed
    """
    try:
        res = shell.run("igtools -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return f"{match[1]} ({pipx.version()})" if match else None

    except shell.CalledProcessError:
        return None


__tool_name__ = "igtools"
