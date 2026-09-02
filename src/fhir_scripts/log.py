import logging
import sys
from enum import StrEnum

from .helper import clean_string, strip_color

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
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    WHITE = "\033[97m"


logging.basicConfig(
    level=logging.DEBUG,
    format=f"{Colors.GRAY}%(asctime)s - %(levelname)s\t-{Colors.RESET} %(message)s",
)

OUTPUT_COLOR_CHOICES = (
    "default",
    "preserve",
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "cyan",
    "gray",
    "white",
)
_output_color = "default"


def fail(string: str):
    logging.error(f"{ERR} {string}")


def warn(string: str):
    logging.warning(f"{WARN} {string}")


def info(string: str):
    logging.info(f"{ARR} {string}")


def succ(string: str):
    logging.info(f"{CHECK} {string}")


def debug(text: str):
    logging.debug(colored(text, Colors.GRAY))


def output(text: str):
    """Write subprocess output with the configured color handling."""
    if _output_color == "preserve":
        formatted_text = text
    else:
        formatted_text = strip_color(text)
        if _output_color != "default":
            color = Colors[_output_color.upper()]
            formatted_text = f"{color}{formatted_text}{Colors.RESET}"

    logging.debug(formatted_text.rstrip("\n"))


def configure_output_color(color: str):
    if color not in OUTPUT_COLOR_CHOICES:
        raise ValueError(f"Unsupported output color: {color}")

    global _output_color
    _output_color = color


def should_preserve_output_colors() -> bool:
    """Return whether subprocess output should retain its original colors."""
    return _output_color == "preserve"


def supports_color() -> bool:
    """Check if terminal supports ANSI colors"""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colored(text: str, color: Colors) -> str:
    if supports_color():
        return f"{color}{clean_string(text)}{Colors.RESET}"
    return text
