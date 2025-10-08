from argparse import Namespace, _SubParsersAction
from typing import Callable

from . import log
from .tools import igpub, sushi

CMD = "update"

SCRIPT = "script"
TOOLS = "tools"
SUSHI = "sushi"
IGPUB = "igpub"
PYTOOLS = "pytools"
ALL = "all"


def setup_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(CMD, help="Update tools")

    sub_parser = parser.add_subparsers(dest=CMD)

    sub_parser.add_parser(SCRIPT, help="Update this script")
    sub_parser.add_parser(
        TOOLS, help="Update FHIR tooling e.g. FSH Sushi, IG Publisher"
    )
    sub_parser.add_parser(SUSHI, help="Update FSH Sushi")
    sub_parser.add_parser(IGPUB, help="Update IG Publisher")
    sub_parser.add_parser(PYTOOLS, help="Update Python tools")
    sub_parser.add_parser(ALL, help="Update everything")


def add_handler(handlers: dict[str, Callable[[Namespace], bool]]):
    handlers[CMD] = handle


def handle(cli_args: Namespace, *arsg, **kwargs) -> bool:
    upd_funcs = {SCRIPT: update_script, SUSHI: update_sushi, IGPUB: update_igpub}

    func = upd_funcs.get(getattr(cli_args, CMD), None)

    if func is None:
        return False

    func()
    return True


def update_sushi():
    log.info("Update Sushi")
    prev_version = sushi.version()
    sushi.update()
    log.succ(f"Updated Sushi: {str(prev_version)} → {sushi.version()}")


def update_igpub():
    log.info("Update IG Publisher")
    prev_version = igpub.version()
    igpub.update()
    log.succ(f"Updated IG Publisher: {str(prev_version)} → {igpub.version()}")


def update_script():
    pass
