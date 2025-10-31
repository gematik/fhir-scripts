import os
import sys
from argparse import ArgumentParser
from types import ModuleType

from . import cli, config, log
from .exception import CancelException


def main():
    module_dict: dict[str, ModuleType] = {}
    parser_dict: dict[str, ArgumentParser] = {}

    args = cli.get_args(module_dict, parser_dict)

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

        # Unpack the cli arguments
        cli_args = vars(args)
        del cli_args["config"]

        # Otherwise handle the command
        handle(config=cfg, **cli_args)

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
