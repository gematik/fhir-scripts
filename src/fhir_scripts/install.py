import importlib
import pkgutil
from argparse import ArgumentParser
from pathlib import Path

import fhir_scripts.tools

from . import config as config_loader, log
from .config import Config
from .multiig import CONFIG_FILE_NAME, discover_project, working_directory

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

    parser.add_argument(
        "--config-file",
        action="store_true",
        help="Install tools defined from config file",
    )

    for name, mod in TOOL_MODULES.items():
        parser.add_argument(
            f"--{name.replace("_", "-")}",
            action="store_true",
            help=f"Install {mod.__tool_name__}",
        )


def install(
    config: Config,
    config_file: bool = False,
    config_path: Path | None = None,
    *args,
    **kwargs,
):
    # '--config-file': install the tools listed in the config's install section.
    if config_file:
        _install_tools(config.install)
        return

    # Explicit tool flags (e.g. '--igpub --sushi'): install only those tools.
    explicit_tools = [tool for tool, v in kwargs.items() if isinstance(v, bool) and v]
    if explicit_tools:
        _install_tools(explicit_tools)
        return

    # No flags given.  In a multi-IG root (detected by the presence of the
    # multi-IG config file) install tools from each IG's own config.
    if config_path is None:
        cwd = Path.cwd()
        if (cwd / CONFIG_FILE_NAME).exists():
            project = discover_project(cwd)
            if project is not None:
                log.info(
                    "Detected multi-IG repository, installing tools from each IG config"
                )
                for target in sorted(project.targets.values(), key=lambda t: t.name):
                    with working_directory(target.path):
                        target_config = config_loader.load(
                            Path("./fhirscripts.config.yaml")
                        )
                        log.info(f"Install tooling for IG '{target.name}'")
                        _install_tools(target_config.install)
                return

    # Single-IG fallback: use the tools defined in the loaded config.
    _install_tools(config.install)


def _install_tools(install_tools: list[str]):

    # Get the module for each tool
    modules = []
    for tool in install_tools:
        if (mod := TOOL_MODULES.get(tool, None)) and hasattr(mod, "update"):
            modules.append(mod)

        else:
            log.warn(f"Tool '{tool}' does not exist")

    if len(modules) == 0:
        log.warn("Nothing to install")

    for module in modules:
        # Skip if already installed
        if module.version() is not None:
            log.warn(f"{module.__tool_name__} already installed, skipping")
            continue

        log.info(f"Install {module.__tool_name__}")
        module.update(install=True)
        log.succ(f"Installed {module.__tool_name__} ({module.version(short=True)})")


__doc__ = "Update tools"
__handler__ = install
__setup_parser__ = setup_parser
