import subprocess
from subprocess import CalledProcessError

from tqdm import tqdm

CalledProcessError = CalledProcessError


def run(cmd, check: bool | None = None, capture_output: bool = False):
    return subprocess.run(
        cmd,
        shell=True,
        check=check or not capture_output,
        capture_output=capture_output,
    )


def run_progress(cmd, total, prefixes, desc):
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
                stdout = ", ".join(list(proc.stdout)).replace("\n", "")
                stderr = ", ".join(list(proc.stderr)).replace("\n", "")
                raise CalledProcessError(proc.returncode, proc.args, stdout, stderr)
