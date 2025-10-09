from argparse import _SubParsersAction

from . import log
from .tools import igpub, sushi

DEFS = "defs"
IG = "ig"
ALL = "all"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    subparser.add_parser(DEFS, help="Build definitions")
    subparser.add_parser(IG, help="Build IG")
    subparser.add_parser(ALL, help="Build everything")


def build_defs(*args, **kwargs):
    log.info("Building definitions")
    sushi.run()
    log.succ("Definitions built successfully")


def build_ig(*args, **kwargs):
    log.info("Building IG")
    igpub.run()
    igpub.qa()
    log.succ("IG built successfully")


def build_all(*args, **kwargs):
    build_defs()
    build_ig()


__doc__ = "Build FHIR definitions and IGs"
__handlers__ = {DEFS: build_defs, IG: build_ig, ALL: build_all}
__setup_subparser__ = setup_subparser
