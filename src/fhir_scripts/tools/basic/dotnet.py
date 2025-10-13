from . import shell


def version() -> str | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("dotnet --version", check=True, capture_output=True)
        return res.stdout_oneline

    except shell.CalledProcessError:
        return None
