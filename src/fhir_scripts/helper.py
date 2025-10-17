from functools import wraps

from .exception import CancelException, NotInstalledException
from .tools.basic import shell


def confirm(prompt: str, log_no: str, confirm_yes: bool = False, default: bool = False):
    """
    Prompt for yes/no confirmation.
    default=False -> [y/N]
    default=True  -> [Y/n]

    Continues if 'y' or 'yes', raises CancelException if 'n' or 'no'.
    """

    if confirm_yes:
        return

    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        ans = input(prompt + suffix).strip().lower()
        if not ans:
            if not default:
                raise CancelException(log_no)

            return

        if ans in ("y", "yes"):
            return

        if ans in ("n", "no"):
            raise CancelException(log_no)


def require_installed(cmd: str, name: str):
    """
    Decorator that checks if `cmd` can be found

    It will be checked if `cmd` can be found on the current environment.
    Will throw an NotInstalledException if not found using `name` in the error message.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                shell.run(f"which {cmd}", check=True, capture_output=True)

            except shell.CalledProcessError:
                raise NotInstalledException(f"{name} is needed but not installed")

            return func(*args, **kwargs)

        return wrapper

    return decorator
