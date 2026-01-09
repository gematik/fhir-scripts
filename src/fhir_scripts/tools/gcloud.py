__tool_name__ = "gCloud SDK"

import re
from functools import wraps
from pathlib import Path

from .. import helper, log
from ..helper import require_installed
from ..types import Url
from ..version import Version
from .basic import shell

CMD_LIST = "gcloud projects list"
CMD_LOGIN = "gcloud auth login"
CMD_LS = "gcloud storage ls {}"
CMD_CP = "gcloud storage cp --additional-headers=Cache-Control=no-cache {} {}"
CMD_RSYNC = (
    "gcloud storage rsync {} {} --recursive --delete-unmatched-destination-objects"
)

VERSION_REGEX = re.compile(r"Google\s+Cloud\s+SDK\s+(\d+(?:\.\d+){,2})\b")

_logged_in = False


def logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _logged_in
        if not _logged_in:
            log.info("Check gcloud login")
            try:
                shell.run(CMD_LIST, check=True, log_output=False)
                log.succ("Already logged in")

            except shell.CalledProcessError:
                # Not logged in
                try:
                    shell.run(CMD_LOGIN)
                    log.succ("Login successful")

                except Exception as e:
                    raise Exception(f"Login failed {str(e)}")

            _logged_in = True
        return func(*args, **kwargs)

    return wrapper


def version(*args, **kwargs) -> Version | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("gcloud -v", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return Version(match[1] if match else None)

    except shell.CalledProcessError:
        return None


def latest_version(*args, **kwargs) -> Version | None:
    return Version()


@require_installed("gcloud", __tool_name__)
@logged_in
def copy(source: Path | Url, target: Url, force=False):
    # Check for overwrite
    existing = ls(target)
    if existing:
        if not force:
            helper.confirm(
                f"Target {target} exists. Overwrite?", "Copy aborted by user"
            )

    _rsync(source, target)


@require_installed("gcloud", __tool_name__)
@logged_in
def _rsync(source: Path | Url, target: Url):

    log.info(f"Copy {str(source)} to {target}")

    source = source.absolute() if isinstance(source, Path) else source

    if source.is_dir():
        total = len(
            list(source.glob("**/*") if isinstance(source, Path) else ls(source))
        )
        shell.run_progress(
            CMD_RSYNC.format(source, target),
            total=total,
            prefixes=["Copying "],
            desc="Syncing",
        )

    else:
        shell.run(CMD_CP.format(source, target), check=True, log_output=False)


@require_installed("gcloud", __tool_name__)
@logged_in
def ls(path: Url) -> list[str]:
    # Try interpret `path` as directory
    try:
        path_dir = path / "**" if not path.endswith("/**") else path
        res = shell.run(CMD_LS.format(path_dir), check=False, log_output=False)
        return res.stdout

    except shell.CalledProcessError:
        # If this fails it might be a single file
        try:
            res = shell.run(CMD_LS.format(path), check=False, log_output=False)
            return res.stdout

        except shell.CalledProcessError:
            return []
