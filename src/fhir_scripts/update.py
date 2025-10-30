import importlib
import pkgutil
from argparse import ArgumentParser

import fhir_scripts.tools

from . import log


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument("--dry-run", action="store_true", help="Only simulate updating")


def handle(cli_args, *args, **kwargs):
    # Get modules dynmaically
    mod_names = [
        name
        for _, name, _ in pkgutil.iter_modules(
            fhir_scripts.tools.__path__, fhir_scripts.tools.__name__ + "."
        )
    ]
    modules = [
        mod
        for mod_name in mod_names
        if (mod := importlib.import_module(mod_name)) and hasattr(mod, "update")
    ]

    for module in modules:
        _update(module, cli_args, *args, **kwargs)


def _update(module, cli_args, *args, **kwargs):
    name = getattr(module, "__tool_name__", None) or module.__name__
    prev_version = module.version(short=True)

    # Only update if was previously installed
    if prev_version:
        latest_func = getattr(module, "latest_version", None)
        latest = latest_func() if latest_func else None

        if not latest or latest != prev_version:
            if cli_args.dry_run:
                log.info(f"Would update {name}")

            else:
                module.update()
                log.succ(
                    f"Updated {name}: {str(prev_version)} → {module.version(short=True)}"
                )


__doc__ = "Update tools"
__handler__ = handle
__setup_parser__ = setup_parser
