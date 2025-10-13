import re

from .basic import pipx, shell

VERSION_REGEX = re.compile(r"EPATOOLS\s\(v(\d+(?:\.\d+){,2})\b", re.IGNORECASE)
PACKAGE = "git+https://github.com/onyg/epa-tools.git"


def update():
    pipx.install(PACKAGE, as_global=True)


def version() -> str | None:
    """
    Get the installed version of epatools, returns None if not installed
    """
    try:
        res = shell.run("epatools -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return f"{match[1]} ({pipx.version()})" if match else None

    except shell.CalledProcessError:
        return None
