from pathlib import Path

from . import shell


def run_jar(jar: Path, *args, capture_output: bool = False):
    is_installed()

    cmd = f"java -jar {str(jar)} {' '.join(args)}"

    res = shell.run(cmd, capture_output=capture_output)

    if capture_output:
        if res.returncode != 0:
            raise shell.CalledProcessError(
                res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
            )

    return res


def is_installed() -> None:
    """
    Checks if Java is installed
    """
    try:
        shell.run("which java", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise Exception("Java is needed but not installed")
