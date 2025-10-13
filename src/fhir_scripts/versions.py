from argparse import ArgumentParser, Namespace

from . import log, tools
from .config import Config

TARGET_BASE_DIR = "ig/fhir"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    pass


def handle(cli_args: Namespace, config: Config, *args, **kwargs) -> bool:
    for name, module in tools.__dict__.items():
        if (
            not name.startswith("__")
            and (version_func := getattr(module, "version", None))
            and (version := version_func())
        ):
            log.info(f"{name}: {version}")

    return True


__doc__ = "Version information of all tools"
__handler__ = handle
__setup_parser__ = setup_parser
