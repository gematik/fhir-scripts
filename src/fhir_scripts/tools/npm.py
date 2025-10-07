from . import shell


def install(pkg_name: str, as_global: bool = False):
    is_installed()

    if as_global:
        cmd = f"sudo npm install -g {pkg_name}"

    else:
        cmd = f"npm install {pkg_name}"

    res = shell.run(cmd, capture_output=True)

    if res.returncode != 0:
        raise shell.CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )


def is_installed() -> None:
    """
    Checks wheater NPM is installed
    """
    try:
        shell.run("which npm", check=True, capture_output=True)

    except shell.CalledProcessError:
        raise Exception("NPM is needed but not installed")
