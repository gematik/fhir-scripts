ERR = "❌"
CHECK = "✅"
INFO = "ℹ️"

# These need an additional space after the symbol as they omit one
WARN = "⚠️ "
ARR = "➡️ "


def fail(string: str):
    print(f"{ERR} {string}")


def warn(string: str):
    print(f"{WARN} {string}")


def info(string: str):
    print(f"{ARR} {string}")


def succ(string: str):
    print(f"{CHECK} {string}")
