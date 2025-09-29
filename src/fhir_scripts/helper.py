from .exception import CancelException


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
