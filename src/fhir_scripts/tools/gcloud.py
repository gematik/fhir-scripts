import subprocess
from pathlib import Path
from subprocess import CalledProcessError

from tqdm import tqdm

from .. import log

CMD_LIST = "gcloud projects list"
CMD_LOGIN = "gcloud auth login"
CMD_RM = "gcloud storage rm --recursive {}"
CMD_LS = "gcloud storage ls --recursive {}"
CMD_CP = "gcloud storage cp --additional-headers=Cache-Control=no-cache {} {}"
CMD_CP_R = "gcloud storage cp --additional-headers=Cache-Control=no-cache -R {} {}"


class GCloudHelper:
    def __init__(self) -> None:
        self.logged_in = False

    def login(self):
        if not self.logged_in:
            log.info("Check gcloud login")
            try:
                subprocess.run(CMD_LIST, shell=True, check=True, capture_output=True)
                log.succ("Already logged in")

            except CalledProcessError:
                # Not logged in
                try:
                    subprocess.run(CMD_LOGIN, shell=True, check=True)
                    log.succ("Login successful")

                except Exception as e:
                    raise Exception("Login failed", e)

            self.logged_in = True

    def copy(self, source: Path, target: str, force=False):
        self.login()

        # Check for overwrite
        existing = self.ls(target)
        if existing and not force:
            if not _confirm(f"Target {target} exists. Overwrite?"):
                log.warn("Copy aborted by user")
                return

            # Clear existing directory
            log.info("Remove existing target")

            _execute_progress(
                CMD_RM.format(target),
                total=len(existing),
                prefixes=["Removing "],
                desc="Deleting",
            )

        # Copy data
        log.info(f"Copy to {target}")
        if source.is_dir():
            total = len(list(source.glob("**/*")))

            # Copy recursive
            _execute_progress(
                CMD_CP_R.format(source.absolute(), target),
                total=total,
                prefixes=["Copying "],
                desc="Copying",
            )

        else:
            _execute_progress(
                CMD_CP.format(source.absolute(), target),
                total=1,
                prefixes=["Copying "],
                desc="Copying",
            )

    def ls(self, path: str) -> list[str]:
        res = subprocess.run(CMD_LS.format(path), shell=True, capture_output=True)

        if res.returncode == 0:
            return res.stdout.decode("utf-8").split()

        else:
            return []


def _confirm(prompt: str, default: bool = False) -> bool:
    """
    Prompt for yes/no confirmation.
    default=False -> [y/N]
    default=True  -> [Y/n]
    Non-TTY (e.g. piped / CI) returns default automatically.
    """

    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        ans = input(prompt + suffix).strip().lower()
        if not ans:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False


def _execute_progress(cmd, total, prefixes, desc):
    with subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as proc:
        with tqdm(
            total=total, unit="obj", desc=desc, disable=False, dynamic_ncols=True
        ) as bar:
            for line in proc.stdout:
                line = line.rstrip()
                for pref in prefixes:
                    if line.startswith(pref):
                        bar.update(1)
                        break  # avoid double count if multiple prefixes match
            proc.wait()

            # If we had an estimated total that was too large/small, normalize so bar shows 100%.
            if bar.total is None or bar.n != bar.total:
                bar.total = bar.n
                bar.refresh()

            if proc.returncode != 0:
                raise CalledProcessError(proc.returncode, proc.args)
