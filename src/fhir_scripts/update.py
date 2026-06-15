import importlib
import pkgutil
from argparse import ArgumentParser
from pathlib import Path

import fhir_scripts.tools

from . import log
from .multiig import CONFIG_FILE_NAME, discover_project, working_directory


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument("--dry-run", action="store_true", help="Only simulate updating")


def update(*args, **kwargs):
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

    project = None
    cwd = Path.cwd()

    # Multi-IG root mode: update IG Publisher per IG directory.
    if (cwd / CONFIG_FILE_NAME).exists():
        project = discover_project(cwd)

    if project is None:
        for module in modules:
            _update(module, *args, **kwargs)
        return

    igpub_modules = [module for module in modules if _is_igpub_module(module)]
    other_modules = [module for module in modules if not _is_igpub_module(module)]

    for module in other_modules:
        _update(module, *args, **kwargs)

    for target_name in sorted(project.targets):
        target = project.targets[target_name]
        with working_directory(target.path):
            for module in igpub_modules:
                log.info(f"Update {module.__tool_name__} for IG '{target.name}'")
                _update(module, *args, **kwargs)


def _is_igpub_module(module) -> bool:
    return module.__name__.rsplit(".", 1)[-1] == "igpub"


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

            else:
                module.update()
                log.succ(f"Updated {name}: {str(prev_version)} → {module.version()}")


__doc__ = "Update tools"
__handler__ = update
__setup_parser__ = setup_parser
