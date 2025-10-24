import importlib
import pkgutil
from argparse import ArgumentParser

import fhir_scripts.tools

from . import log

TOOL_MODULES = {}


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    global TOOL_MODULES

    # Get modules dynmaically
    mod_names = [
        name
        for _, name, _ in pkgutil.iter_modules(
            fhir_scripts.tools.__path__, fhir_scripts.tools.__name__ + "."
        )
    ]
    TOOL_MODULES = {
        mod_name.rsplit(".")[-1]: mod
        for mod_name in mod_names
        if (mod := importlib.import_module(mod_name)) and hasattr(mod, "update")
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
