from argparse import _SubParsersAction

from . import log
from .tools import epatools, igpub, igtools, publishtools, sushi

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


def _update(module, *args, **kwargs):
    name = getattr(module, "__tool_name__", None) or module.__name__
    log.info(f"Update {name}")

    prev_version = module.version(short=True)
    module.update()
    log.succ(f"Updated {name}: {str(prev_version)} → {module.version(short=True)}")


def update_sushi(*args, **kwargs):
    _update(sushi, *args, **kwargs)


def update_igpub(*args, **kwargs):
    _update(igpub, *args, **kwargs)


def update_tools(*args, **kwargs):
    update_sushi(*args, **kwargs)
    update_igpub(*args, **kwargs)


def update_igtools(*args, **kwargs):
    _update(igtools, *args, **kwargs)


def update_epatools(*args, **kwargs):
    _update(epatools, *args, **kwargs)


def update_publishtools(*args, **kwargs):
    _update(publishtools, *args, **kwargs)


def update_pytools(*args, **kwargs):
    update_igtools(*args, **kwargs)
    update_epatools(*args, **kwargs)
    update_publishtools(*args, **kwargs)


def update_script(*args, **kwargs):
    pass


def update_everything(*args, **kwargs):
    update_script(*args, **kwargs)
    update_pytools(*args, **kwargs)
    update_tools(*args, **kwargs)


__doc__ = "Update tools"
__handlers__ = {
    SCRIPT: update_script,
    SUSHI: update_sushi,
    IGPUB: update_igpub,
    TOOLS: update_tools,
    PYTOOLS: update_pytools,
    ALL: update_everything,
}
__setup_subparser__ = setup_subparser
