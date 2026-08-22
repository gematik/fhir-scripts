import inspect
import re
from functools import wraps
from pathlib import Path

import yaml

from . import log
from .exception import CancelException, NotInstalledException
from .tools.basic import shell

COLOR_REGEX = re.compile(r"(?:\x1b|\033)\[(?:\d+;){,2}\d+m", re.IGNORECASE)


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


def confirm_with_path_modification(initial_path: str, confirm_yes: bool = False) -> str:
    """
    Prompt for confirmation with option to modify the path.
    Returns the confirmed path (either original or modified).
    """
    if confirm_yes:
        return initial_path

    current_path = initial_path

    while True:
        # Show current path and ask for confirmation
        suffix = " [Y/n]: "
        ans = input(f"Continue with path: {current_path}?" + suffix).strip().lower()

        if not ans or ans in ("y", "yes"):
            # User confirmed, return the current path
            return current_path

        if ans in ("n", "no"):
            # User declined, ask if they want to modify the path
            modify_suffix = " [Y/n]: "
            modify_ans = (
                input("Would you like to modify the path?" + modify_suffix)
                .strip()
                .lower()
            )

            if not modify_ans or modify_ans in ("y", "yes"):
                # User wants to modify, ask for new path
                new_path = input("Enter modified path: ").strip()

                if new_path:
                    current_path = new_path
                    from . import log

                    log.info(f"Deploy built IG -> {current_path}")
                    # Loop back to confirm the new path
                    continue
                else:
                    from . import log

                    log.warning("No path entered, keeping current path")
                    continue
            else:
                # User doesn't want to modify, abort
                raise CancelException("Aborted by user")
        else:
            # Invalid input, ask again
            continue


def check_installed(cmd: str, name: str):
    try:
        shell.run(f"which {cmd}", check=True, log_output=False)

    except shell.CalledProcessError:
        raise NotInstalledException(f"{name} is needed but not installed")


def require_installed(cmd: str, name: str):
    """
    Decorator that checks if `cmd` can be found

    It will be checked if `cmd` can be found on the current environment.
    Will throw an NotInstalledException if not found using `name` in the error message.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_installed(cmd, name)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_version(mod=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get module
            module = inspect.getmodule(func) if mod is None else mod

            # Get version
            version_func = getattr(module, "version", None)
            version = version_func() if version_func else None

            # Get tool name
            tool_name = getattr(module, "__tool_name__", None)

            # Only can do if both is available
            if tool_name and version:

                # Get record
                rec_file = Path.cwd() / "build-record.yaml"
                rec = (
                    yaml.safe_load(rec_file.read_text("utf-8"))
                    if rec_file.exists()
                    else {}
                )

                # Initialize version list
                if "versions" not in rec:
                    rec["versions"] = {}

                rec["versions"][tool_name] = str(version)

                # Write back record
                rec_file.write_text(yaml.safe_dump(rec), "utf-8")

                log.debug(f"Using {tool_name} version {version}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def clean_string(text: str) -> str:
    return COLOR_REGEX.sub("", text.strip())


def strip_color(text: str) -> str:
    """Remove ANSI colors without changing whitespace or line breaks."""
    return COLOR_REGEX.sub("", text)
