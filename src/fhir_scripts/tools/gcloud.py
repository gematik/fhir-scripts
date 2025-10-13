import re
from pathlib import Path

from .. import helper, log
from . import shell

CMD_LIST = "gcloud projects list"
CMD_LOGIN = "gcloud auth login"
CMD_RM = "gcloud storage rm --recursive {}"
CMD_LS = "gcloud storage ls --recursive {}"
CMD_CP = "gcloud storage cp --additional-headers=Cache-Control=no-cache {} {}"
CMD_CP_R = "gcloud storage cp --additional-headers=Cache-Control=no-cache -R {} {}"

VERSION_REGEX = re.compile(r"Google\s+Cloud\s+SDK\s+([\d\.]+)\W")


def version() -> str | None:
    """
    Get the installed version, returns None if not installed
    """
    try:
        res = shell.run("gcloud -v", check=True, capture_output=True)

        # Extract the version string from output
        match = VERSION_REGEX.match(res.stdout_oneline)

        return match[1] if match else None

    except shell.CalledProcessError:
        return None


class GCloudHelper:
    def __init__(self) -> None:
        self.logged_in = False

    def login(self):
        if not self.logged_in:
            log.info("Check gcloud login")
            try:
                shell.run(CMD_LIST, check=True, capture_output=True)
                log.succ("Already logged in")

            except shell.CalledProcessError:
                # Not logged in
                try:
                    shell.run(CMD_LOGIN)
                    log.succ("Login successful")

                except Exception as e:
                    raise Exception(f"Login failed {str(e)}")

            self.logged_in = True

    def copy(self, source: Path, target: str, force=False):
        self.login()

        # Check for overwrite
        existing = self.ls(target)
        if existing:
            if not force:
                helper.confirm(
                    f"Target {target} exists. Overwrite?", "Copy aborted by user"
                )

            # Clear existing directory
            log.info("Remove existing target")

            shell.run_progress(
                CMD_RM.format(target),
                total=len(existing),
                prefixes=["Removing "],
                desc="Deleting",
            )

        # Copy data
        log.info(f"Copy to {target}")
        if source.is_dir():
            total = len(list(source.glob("**/*")))
            cmd = CMD_CP_R

        else:
            total = 1
            cmd = CMD_CP

        shell.run_progress(
            cmd.format(source.absolute(), target),
            total=total,
            prefixes=["Copying "],
            desc="Copying",
        )

    def ls(self, path: str) -> list[str]:
        res = shell.run(CMD_LS.format(path), capture_output=True)

        if res.returncode == 0:
            return res.stdout

        else:
            return []


__tool_name__ = "gCloud SDK"
