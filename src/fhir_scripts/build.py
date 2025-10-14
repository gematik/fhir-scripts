from argparse import _SubParsersAction
from pathlib import Path

from . import log
from .config import Config
from .exception import NoConfigException, NotInstalledException
from .tools import epatools, igpub, igtools, sushi

DEFS = "defs"
REQ = "req"
IG = "ig"
OPEN_API = "openapi"
ALL = "all"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    subparser.add_parser(DEFS, help="Build definitions")
    subparser.add_parser(REQ, help="Process requirements")
    subparser.add_parser(IG, help="Build IG")
    subparser.add_parser(OPEN_API, help="Update OpenAPI")
    subparser.add_parser(ALL, help="Build everything")


def build_defs(*args, **kwargs):
    log.info("Building definitions")
    build_req(args, kwargs)
    sushi.run()
    build_cap()
    log.succ("Definitions built successfully")


def build_req(*args, **kwargs):
    log.info("Process requirements")
    # Try to run igtools
    try:
        output_dir = Path("input/data")
        igtools.process()
        igtools.release_notes(output_dir)
        igtools.export(output_dir)

    except (NoConfigException, NotInstalledException) as e:
        log.warn(f"epa not configured or installed, skipping: {str(e)}")

    log.succ("Requirements processed successfully")


def build_cap(*args, **kwargs):
    """
    Build CapabilityStatements
    """
    try:
        epatools.merge_capabilities()

    except (NoConfigException, NotInstalledException) as e:
        log.warn(f"epatools not configured or installed, skipping: {str(e)}")


def build_ig(config: Config, *args, **kwargs):
    log.info("Building IG")
    igpub.run()
    log.succ("IG built successfully")
    build_openapi(config)
    igpub.qa()


def build_openapi(config: Config, *args, **kwargs):
    log.info("Updating OpenAPI")
    epatools.openapi(config.epatools)
    log.succ("OpenAPI updated successfully")


def build_all(config: Config, *args, **kwargs):
    build_defs(config, args, kwargs)
    build_ig(config, args, kwargs)


__doc__ = "Build FHIR definitions and IGs"
__handlers__ = {
    DEFS: build_defs,
    REQ: build_req,
    IG: build_ig,
    OPEN_API: build_openapi,
    ALL: build_all,
}
__setup_subparser__ = setup_subparser
