import importlib
import os
import pkgutil
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from types import ModuleType

import fhir_scripts

from . import config, log
from .exception import CancelException
from .helper import log_version
from .tools import fhirscripts
from .tools.basic.shell import CalledProcessError


def get_args(
    module_dict: dict[str, ModuleType],
    parser_dict: dict[str, ArgumentParser],
) -> Namespace:

    parser = ArgumentParser(description="Scripts to support FHIR development")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Name and path of the config file; default `./fhirscripts.config.yaml`",
    )
    parser.add_argument(
        "--output-color",
        choices=log.OUTPUT_COLOR_CHOICES,
        default="default",
        help=(
            "Color handling for subprocess output: use the terminal default, "
            "preserve tool colors, or apply a named color (default: default)"
        ),
    )
    subparsers = parser.add_subparsers(dest="cmd")

    # Get modules dynmaically
    mod_names = [
        name
        for _, name, _ in pkgutil.iter_modules(
            fhir_scripts.__path__, fhir_scripts.__name__ + "."
        )
    ]
    modules = [
        mod
        for mod_name in mod_names
        if (mod := importlib.import_module(mod_name))
        and hasattr(mod, "__doc__")
        and (hasattr(mod, "__handler__") or hasattr(mod, "__handlers__"))
    ]

    for module in modules:
        cmd = module.__name__.split(".")[-1]
        desc = module.__doc__

        module_dict[cmd] = module

        # Setup parser
        _parser = subparsers.add_parser(cmd, help=desc)
        parser_dict[cmd] = _parser

        if setup_parser := getattr(module, "__setup_parser__", None):
            setup_parser(parser=_parser)

        elif setup_subparser := getattr(module, "__setup_subparser__", None):
            sub_parser = _parser.add_subparsers(dest=cmd)
            setup_subparser(parser=_parser, subparser=sub_parser)

        else:
            raise Exception(
                f"No setup function for parser or subparser defined for '{module.__name__}'"
            )

    args = parser.parse_args()

    if args.cmd is None:
        parser.print_help()
        exit(0)

    return args


@log_version(fhirscripts)
def cli():
    module_dict: dict[str, ModuleType] = {}
    parser_dict: dict[str, ArgumentParser] = {}

    args = get_args(module_dict, parser_dict)
    log.configure_output_color(args.output_color)

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
        del cli_args["output_color"]

        # Otherwise handle the command
        handle(config=cfg, **cli_args)

    except CancelException as e:
        log.warn(str(e))
        sys.exit(-1)

    except CalledProcessError as e:
        for line in e.output.splitlines():
            log.debug(line)

        for line in e.stderr.splitlines():
            log.debug(line)

        log.fail(f"Error: {str(e)}")
        sys.exit(os.EX_DATAERR)

    except Exception as e:
        log.fail(f"Error: {str(e)}")
        sys.exit(os.EX_DATAERR)

    sys.exit(os.EX_OK)
