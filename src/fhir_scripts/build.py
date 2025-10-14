from argparse import _SubParsersAction
from pathlib import Path

from . import log
from .exception import NoConfigException, NotInstalledException
from .tools import igpub, igtools, sushi

DEFS = "defs"
REQ = "req"
IG = "ig"
ALL = "all"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    subparser.add_parser(DEFS, help="Build definitions")
    subparser.add_parser(REQ, help="Process requirements")
    subparser.add_parser(IG, help="Build IG")
    subparser.add_parser(ALL, help="Build everything")


def build_defs(*args, **kwargs):
    log.info("Building definitions")
    build_req(args, kwargs)
    sushi.run()
    log.succ("Definitions built successfully")


def build_req(*args, **kwargs):
    log.info("Process requirements")
    # Try to run igtools
    try:
        output_dir = Path("input/data")
        igtools.process()
        igtools.release_notes(output_dir)
        igtools.export(output_dir)

    except NoConfigException or NotInstalledException:
        log.warn("igtools not configured or installed, skipping")

    log.succ("Requirements processed successfully")


def build_ig(*args, **kwargs):
    log.info("Building IG")
    igpub.run()
    igpub.qa()
    log.succ("IG built successfully")


def build_all(*args, **kwargs):
    build_defs()
    build_ig()


__doc__ = "Build FHIR definitions and IGs"
__handlers__ = {DEFS: build_defs, REQ: build_req, IG: build_ig, ALL: build_all}
__setup_subparser__ = setup_subparser
