from argparse import _SubParsersAction

from . import log
from .tools import epatools, igpub, igtools, sushi

SCRIPT = "script"
TOOLS = "tools"
SUSHI = "sushi"
IGPUB = "igpub"
PYTOOLS = "pytools"
ALL = "all"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    subparser.add_parser(SCRIPT, help="Update this script")
    subparser.add_parser(TOOLS, help="Update FHIR tooling e.g. FSH Sushi, IG Publisher")
    subparser.add_parser(SUSHI, help="Update FSH Sushi")
    subparser.add_parser(IGPUB, help="Update IG Publisher")
    subparser.add_parser(PYTOOLS, help="Update Python tools")
    subparser.add_parser(ALL, help="Update everything")


def update_sushi(*args, **kwargs):
    log.info("Update Sushi")
    prev_version = sushi.version()
    sushi.update()
    log.succ(f"Updated Sushi: {str(prev_version)} → {sushi.version()}")


def update_igpub(*args, **kwargs):
    log.info("Update IG Publisher")
    prev_version = igpub.version()
    igpub.update()
    log.succ(f"Updated IG Publisher: {str(prev_version)} → {igpub.version()}")


def update_tools(*args, **kwargs):
    update_sushi(args, kwargs)
    update_igpub(args, kwargs)


def update_igtools(*args, **kwargs):
    log.info("Update igtools")
    prev_version = igtools.version()
    igtools.update()
    log.succ(f"Updated igtools: {str(prev_version)} → {igtools.version()}")


def update_epatools(*args, **kwargs):
    log.info("Update epatools")
    prev_version = epatools.version()
    epatools.update()
    log.succ(f"Updated epatools: {str(prev_version)} → {epatools.version()}")


def update_pytools(*args, **kwargs):
    update_igtools(args, kwargs)
    update_epatools(args, kwargs)


def update_script(*args, **kwargs):
    pass


__doc__ = "Update tools"
__handlers__ = {
    SCRIPT: update_script,
    SUSHI: update_sushi,
    IGPUB: update_igpub,
    TOOLS: update_tools,
    PYTOOLS: update_pytools,
}
__setup_subparser__ = setup_subparser
