import argparse
import os
import sys
from pathlib import Path

import yaml

from . import build, cache, deploy, log, update
from .config import Config
from .exception import CancelException


def main():
    parser = argparse.ArgumentParser(description="Scripts to support FHIR development")
    subparsers = parser.add_subparsers(dest="cmd")

    modules = [build, cache, deploy, update]
    module_dict = {}

    for module in modules:
        if not getattr(module, "__doc__", None) or (
            not getattr(module, "__handlers__", None)
            and not getattr(module, "__handler__", None)
        ):
            raise Exception(
                f"Module '{module.__name__}' does not provide all needed attributes"
            )

        cmd = module.__name__.split(".")[-1]
        desc = module.__doc__

        module_dict[cmd] = module

        # Setup parser
        _parser = subparsers.add_parser(cmd, help=desc)

        if setup_parser := getattr(module, "__setup_parser__", None):
            setup_parser(parser=_parser)

        elif setup_subparser := getattr(module, "__setup_subparser__", None):
            sub_parser = _parser.add_subparsers(dest=module.__name__.split(".")[-1])
            setup_subparser(subparser=sub_parser)

        else:
            raise Exception(
                f"No setup function for parser or subparser defined for '{module.__name__}'"
            )

    args = parser.parse_args()

    try:
        # Read config; initialize with default values if not found
        config_file = Path("./config.yaml")
        if config_file.exists():
            config_file_contents = yaml.safe_load(
                config_file.read_text(encoding="utf-8")
            )
        else:
            config_file_contents = {}
        config = Config.model_validate(config_file_contents)

        # Get handle function for command
        module = module_dict[args.cmd]

        # Only single handler
        if func := getattr(module, "__handler__", None):
            handle = func

        # Has multiple handlers
        elif func_dict := getattr(module, "__handlers__", None):
            handle = func_dict[getattr(args, args.cmd)]

        else:
            raise Exception("No handler defined")

        # Print help if command not handled
        if handle is None:
            parser.print_help()
            return

        # Otherwise handle the command
        handle(cli_args=args, config=config)

    except CancelException as e:
        log.warn(str(e))
        sys.exit(-1)

    except Exception as e:
        if stdout := getattr(e, "stdout", None):
            log.info(stdout)

        if stderr := getattr(e, "stderr", None):
            log.fail(stderr)

        log.fail(f"Error: {str(e)}")
        sys.exit(os.EX_DATAERR)

    sys.exit(os.EX_OK)
