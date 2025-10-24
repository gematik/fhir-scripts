from argparse import ArgumentParser

from . import log
from .tools import epatools, igpub, igtools, publishtools, sushi

SCRIPT = "script"
TOOLS = "tools"
SUSHI = "sushi"
IGPUB = "igpub"
PYTOOLS = "pytools"
ALL = "all"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    pass


def handle(*args, **kwargs):
    modules = [epatools, igpub, igtools, publishtools, sushi]
    for module in modules:
        _update(module, *args, **kwargs)


def _update(module, *args, **kwargs):
    name = getattr(module, "__tool_name__", None) or module.__name__
    prev_version = module.version(short=True)

    # Only update if was previously installed
    if prev_version:
        log.info(f"Update {name}")

        module.update()
        log.succ(f"Updated {name}: {str(prev_version)} → {module.version(short=True)}")


__doc__ = "Update tools"
__handler__ = handle
__setup_parser__ = setup_parser
