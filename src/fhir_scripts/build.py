from argparse import Namespace, _SubParsersAction
from typing import Callable

from . import log
from .tools import igpub, sushi

CMD = "build"

DEFS = "defs"
IG = "ig"
ALL = "all"


def setup_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(CMD, help="Update tools")

    sub_parser = parser.add_subparsers(dest=CMD)

    sub_parser.add_parser(DEFS, help="Build definitions")
    sub_parser.add_parser(IG, help="Build IG")
    sub_parser.add_parser(ALL, help="Build everything")


def add_handler(handlers: dict[str, Callable[[Namespace], bool]]):
    handlers[CMD] = handle


def handle(cli_args: Namespace, *arsg, **kwargs) -> bool:
    upd_funcs = {DEFS: build_defs, IG: build_ig, ALL: build_all}

    func = upd_funcs.get(getattr(cli_args, CMD), None)

    if func is None:
        return False

    func()
    return True


def build_defs():
    log.info("Building definitions")
    sushi.run()
    log.succ("Definitions built successfully")


def build_ig():
    log.info("Building IG")
    igpub.run()
    igpub.qa()
    log.succ("IG built successfully")


def build_all():
    build_defs()
    build_ig()
