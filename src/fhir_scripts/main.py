import argparse
import os
import sys
from pathlib import Path

from . import build, cache, config, deploy, log, publish, update, versions
from .exception import CancelException


def main():
    parser = argparse.ArgumentParser(description="Scripts to support FHIR development")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Name and path of the config file; default `./config.yaml`",
    )
    subparsers = parser.add_subparsers(dest="cmd")

    modules = [build, cache, deploy, publish, update, versions]
    module_dict = {}
    parser_dict = {}

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
        parser_dict[cmd] = _parser

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
        cfg = config.load(args.config)

        # Get handle function for command
        module = module_dict[args.cmd]

        # Only single handler
        if func := getattr(module, "__handler__", None):
            handle = func

        # Has multiple handlers
        elif (
            (func_dict := getattr(module, "__handlers__", None))
            and (sub_cmd := getattr(args, args.cmd))
            and (func := func_dict.get(sub_cmd))
        ):
            handle = func

        # Print help if command not handled
        else:
            parser_dict[args.cmd].print_help()
            return

        # Otherwise handle the command
        handle(cli_args=args, config=cfg)

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
