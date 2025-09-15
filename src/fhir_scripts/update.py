from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import Callable

CMD = "update"


def setup_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(CMD, help="Update tools")

    sub_parser = parser.add_subparsers(dest=CMD)

    sub_parser.add_parser("script", help="Update this script")
    sub_parser.add_parser(
        "tools", help="Update FHIR tooling e.g. FSH Sushi, IG Publisher"
    )
    sub_parser.add_parser("sushi", help="Update FSH Sushi")
    sub_parser.add_parser("igpub", help="Update IG Publisher")
    sub_parser.add_parser("pytools", help="Update Python tools")
    sub_parser.add_parser("all", help="Update everything")


def add_handler(handlers: dict[str, Callable[[Namespace], bool]]):
    handlers[CMD] = handle


def handle(args: Namespace) -> bool:
    args
