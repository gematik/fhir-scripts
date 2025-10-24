from argparse import ArgumentParser
from types import ModuleType

from . import log, tools

TOOL_MODULES = {}


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    global TOOL_MODULES
    TOOL_MODULES = {
        k: v
        for k, v in tools.__dict__.items()
        if isinstance(v, ModuleType) and hasattr(v, "update")
    }

    for name, mod in TOOL_MODULES.items():
        parser.add_argument(
            f"--{name}", action="store_true", help=f"Install {mod.__tool_name__}"
        )


def handle(cli_args, *args, **kwargs):
    install_tools = [
        mod
        for k, v in cli_args.__dict__.items()
        if isinstance(v, bool)
        and v
        and (mod := TOOL_MODULES.get(k, None))
        and hasattr(mod, "update")
    ]
    for module in install_tools:
        log.info(f"Install {module.__tool_name__}")
        module.update()
        log.succ(f"Installed {module.__tool_name__} ({module.version(short=True)})")


__doc__ = "Update tools"
__handler__ = handle
__setup_parser__ = setup_parser
