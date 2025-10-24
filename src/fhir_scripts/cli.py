import importlib
import pkgutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from types import ModuleType

import fhir_scripts


def get_args(
    module_dict: dict[str, ModuleType],
    parser_dict: dict[str, ArgumentParser],
) -> Namespace:

    parser = ArgumentParser(description="Scripts to support FHIR development")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Name and path of the config file; default `./config.yaml`",
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
            setup_subparser(subparser=sub_parser)

        else:
            raise Exception(
                f"No setup function for parser or subparser defined for '{module.__name__}'"
            )

    return parser.parse_args()
