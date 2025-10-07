import subprocess
from subprocess import CalledProcessError

from tqdm import tqdm

CalledProcessError = CalledProcessError


class ShellResult:
    def __init__(self, process):
        self.stdout = _convert_std(process.stdout)
        self.stderr = _convert_std(process.stderr)
        self.returncode = process.returncode
        self.args = process.args

    @property
    def stdout_oneline(self) -> str:
        return _oneline(self.stdout)

    @property
    def stderr_oneline(self) -> str:
        return _oneline(self.stderr)


def _convert_std(input) -> list[str]:
    if isinstance(input, bytes):
        input = input.decode("utf-8")

    return [line.strip() for line in input.strip().split("\n") if line]


def _oneline(list_: list[str]) -> str:
    return ", ".join(list_)


def run(cmd, check: bool | None = None, capture_output: bool = False):
    """
    Execute a command on the shell

    By default the output is not captured (`capture_output = False`), but if the status code is not equal to 0 an
    `CalledProcessError` is raised (`check = True`). If `capture_output` is set to `True`, `check` is automatically set
    to `False` except if stated otherwise.
    """
    res = subprocess.run(
        cmd,
        shell=True,
        check=check or not capture_output,
        capture_output=capture_output,
    )

    return ShellResult(res)


def run_progress(cmd, total, prefixes, desc):
    """
    Execute a command on shell with a progress bar

    The output is hidden but instead a progress bar shown. It also shows a progress as X out of `total`. `prefixes`
    defines a list of prefixes of lines to be counted as progress and `desc` is a string that is added as a title in
    front of the progress bar.
    """
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
                res = ShellResult(proc)
                raise CalledProcessError(
                    proc.returncode, proc.args, res.stdout_oneline, res.stderr_oneline
                )
