import sys
from enum import StrEnum

from .helper import clean_string

ERR = "❌"
CHECK = "✅"
INFO = "ℹ️"

# These need an additional space after the symbol as they omit one
WARN = "⚠️ "
ARR = "➡️ "


class Colors(StrEnum):
    """ANSI color codes"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    # SGR 2 (faint): the terminal dims its own foreground color instead of
    # us picking a shade, so this stays readable on light and dark themes
    DIM = "\033[2m"


def fail(string: str):
    print(f"{ERR} {string}")


def warn(string: str):
    print(f"{WARN} {string}")


def info(string: str):
    print(f"{ARR} {string}")


def succ(string: str):
    print(f"{CHECK} {string}")


def debug(text: str):
    # Carries the streamed stdout/stderr of spawned build tools, so it must
    # never be a fixed color -- see Colors.DIM
    print(colored(text, Colors.DIM))


def supports_color() -> bool:
    """Check if terminal supports ANSI colors"""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colored(text: str, color: Colors) -> str:
    if supports_color():
        return f"{color}{clean_string(text)}{Colors.RESET}"
    return text
