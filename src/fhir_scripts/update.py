import importlib
import logging
import pkgutil
from argparse import ArgumentParser

import fhir_scripts.tools

from . import log
from .config import Config
from .models.config import InstallEntry
from .version import Version


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument("--dry-run", action="store_true", help="Only simulate updating")


def update(config: Config, *args, **kwargs):
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

    # Remove modules with fixed versions
    fixed_mods = [
        mod.name
        for mod in config.install
        if isinstance(mod, InstallEntry) and mod.version
    ]
    modules = [
        mod for mod in modules if mod.__name__.rsplit(".", 1)[1] not in fixed_mods
    ]

    versions = []
    for module in modules:
        version = _update(module, *args, **kwargs)

        if version:
            versions.append(version)

    if len(versions) == 0:
        log.info("Nothing was updated")

    else:
        log.succ("The following packages where updated:")

        for name, prev, new in versions:
            logging.info(f"{name}: {prev} -> {new}")


def _update(module, dry_run: bool = False, *args, **kwargs):
    name = getattr(module, "__tool_name__", None) or module.__name__
    prev_version = module.version()

    # Only update if was previously installed
    if prev_version:
        latest_func = getattr(module, "latest_version", None)
        latest = latest_func() if latest_func else None

        if not latest or latest != prev_version:
            if dry_run:
                if latest_func := getattr(module, "latest_version", None):
                    log.info(
                        "Would update {}: {} -> {}".format(
                            name, prev_version, latest_func()
                        )
                    )

                else:
                    log.info("Would update {}: from {}".format(name, prev_version))

                return None

            else:
                module.update(Version())
                new_version = module.version()
                log.succ(f"Updated {name}: {str(prev_version)} → {new_version}")

                return name, prev_version, new_version


__doc__ = "Update tools"
__handler__ = update
__setup_parser__ = setup_parser
