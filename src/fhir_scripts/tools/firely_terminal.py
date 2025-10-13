from pathlib import Path

from . import shell


def install(
    pkg: str | None = None, version: str | None = None, file: Path | None = None
):
    if pkg and version:
        cmd = f"fhir install {pkg} {version}"

    elif file:
        cmd = f"fhir install {str(file)} --file"

    else:
        raise Exception("For install provide a package name AND a version or a file.")

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def restore():
    shell.run("fhir restore")


__tool_name__ = "Firely Terminal"
