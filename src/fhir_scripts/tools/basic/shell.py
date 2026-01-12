import re
import subprocess
from subprocess import CalledProcessError

from tqdm import tqdm

from ... import helper, log

CalledProcessError = CalledProcessError

COLOR_FORMATTING = re.compile(r"(?:\x1b|\\e)\[\d+(?:;\d+)?m")


class ShellResult:
    def __init__(self, process=None):
        self._stdout: list[str] = []
        self._stderr: list[str] = []

        if process is not None:
            self.stdout = process.stdout
            self.stderr = process.stderr

        self.returncode = process.returncode if process else 0
        self.args = process.args if process else []

    @property
    def stdout(self) -> list[str]:
        return self._stdout

    @stdout.setter
    def stdout(self, value):
        self._stdout = _convert_std(value) if value else []

    @property
    def stdout_oneline(self) -> str:
        return _oneline(self.stdout)

    @property
    def stderr(self) -> list[str]:
        return self._stderr

    @stderr.setter
    def stderr(self, value):
        self._stderr = _convert_std(value) if value else []

    @property
    def stderr_oneline(self) -> str:
        return _oneline(self.stderr)


def _convert_std(input) -> list[str]:
    if input is None:
        return []

    if isinstance(input, bytes):
        input = input.decode("utf-8")

    return [
        COLOR_FORMATTING.sub("", line.strip())
        for line in input.strip().split("\n")
        if line
    ]


def _oneline(list_: list[str]) -> str:
    return " ".join(list_)


def run(cmd, check: bool = False, log_output: bool = True):
    """
    Execute a command on the shell

    By default the return code is not check (`check = False`), but if set to true and the return code is not equal to 0 an
    `CalledProcessError` is raised. If `log_output` is set to `True` (default), the output of the command is printed on the command line.
    """

    res = ShellResult()
    with subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as proc:
        for line in proc.stdout:
            line = helper.clean_string(line)
            res.stdout.append(line)

            if log_output:
                log.debug(line)

        proc.wait()

        res.stderr = proc.stderr
        res.args = proc.args
        res.returncode = proc.returncode

    if check and res.returncode != 0:
        raise CalledProcessError(
            res.returncode, res.args, res.stdout_oneline, res.stderr_oneline
        )

    return res


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
