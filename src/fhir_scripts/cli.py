from argparse import ArgumentParser, Namespace
from pathlib import Path
from types import ModuleType


def get_args(
    modules: list[ModuleType],
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

    return parser.parse_args()
