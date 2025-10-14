from argparse import ArgumentParser, Namespace

from . import log, tools
from .config import Config

TARGET_BASE_DIR = "ig/fhir"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    pass


def handle(cli_args: Namespace, config: Config, *args, **kwargs) -> bool:
    versions = {}
    for name, module in tools.__dict__.items():
        if (
            not name.startswith("__")
            and (version_func := getattr(module, "version", None))
            and (version := version_func())
        ):
            tool_name = getattr(module, "__tool_name__", None) or name
            versions[tool_name] = version

    for name, version in sorted(versions.items(), key=lambda x: x[0].lower()):
        log.info(f"{name}: {version}")

    return True


__doc__ = "Version information of all tools"
__handler__ = handle
__setup_parser__ = setup_parser
