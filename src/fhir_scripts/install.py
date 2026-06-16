import importlib
import pkgutil
from argparse import ArgumentParser

import fhir_scripts.tools

from . import log
from .config import Config
from .models.config import InstallEntry
from .version import Version

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


def install(config: Config, config_file: bool = False, *args, **kwargs):
    # If '--config-file' argument, get list of tools to install from the config file 'install' section
    if config_file:
        install_tools = config.install

    # Else get them from arguments
    else:
        install_tools = [
            tool for tool, v in kwargs.items() if isinstance(v, bool) and v
        ]

    # Get the module for each tool
    module_configs = []
    for tool in install_tools:

        if isinstance(tool, InstallEntry):
            name = tool.name
            version = Version(tool.version)

        else:
            name = tool
            version = Version(None)

        if (mod := TOOL_MODULES.get(name)) and hasattr(mod, "update"):
            module_configs.append((mod, version))

        else:
            log.warn(f"Tool '{name}' does not exist")

    if len(module_configs) == 0:
        log.warn("Nothing to install")

    for module, version in module_configs:

        # Version dependend install
        if not version.unknown:

            # Skip if version already installed
            if (
                installed_version := module.version()
            ) is not None and installed_version == version:
                log.warn(
                    f"{module.__tool_name__} already installed in version {version}, skipping"
                )
                continue

        else:

            # Skip if already installed
            if module.version() is not None:
                log.warn(f"{module.__tool_name__} already installed, skipping")
                continue

        log.info(f"Install {module.__tool_name__}")
        module.update(install=True, version=version)
        log.succ(f"Installed {module.__tool_name__} ({module.version(short=True)})")


__doc__ = "Update tools"
__handler__ = install
__setup_parser__ = setup_parser
