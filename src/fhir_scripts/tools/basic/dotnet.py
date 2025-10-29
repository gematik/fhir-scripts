__tool_name__ = ".NET"

from ...helper import require_installed
from . import shell


@require_installed("dotnet", __tool_name__)
def install(pkg_name: str):

    cmd = f"dotnet tool install -g {pkg_name}"
    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


@require_installed("dotnet", __tool_name__)
def update(pkg_name: str):

    cmd = f"dotnet tool update -g {pkg_name}"
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
        res = shell.run("dotnet --version", check=True, capture_output=True)
        return res.stdout_oneline

    except shell.CalledProcessError:
        return None
