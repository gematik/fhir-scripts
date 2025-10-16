from argparse import Namespace, _SubParsersAction
from pathlib import Path

from . import log
from .config import Config
from .exception import NoConfigException, NotInstalledException
from .tools import epatools, igpub, igtools, sushi

DEFS = "defs"
IG = "ig"
ALL = "all"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    defs_parser = subparser.add_parser(DEFS, help="Build definitions")
    defs_parser.add_argument("--only-sushi", action="store_true", help="Only run sushi")
    defs_parser.add_argument(
        "--only-req", action="store_true", help="Only process requirements"
    )

    ig_parser = subparser.add_parser(IG, help="Build IG")
    ig_parser.add_argument("--only-open-api", action="store_true", help="Only Open API")

    subparser.add_parser(ALL, help="Build everything")


def build_defs(cli_args: Namespace, *args, **kwargs):
    log.info("Building definitions")

    if not getattr(cli_args, "only_sushi", False):
        build_req(args, kwargs)

    if not getattr(cli_args, "only_req", False):
        sushi.run()

    if not getattr(cli_args, "only_req", False):
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


def build_ig(cli_args: Namespace, config: Config, *args, **kwargs):
    log.info("Building IG")

    if not getattr(cli_args, "only_open_api", False):
        igpub.run()
        log.succ("IG built successfully")

    build_openapi(config)

    igpub.qa()


def build_openapi(config: Config, *args, **kwargs):
    log.info("Updating OpenAPI")
    epatools.openapi(config.epatools)
    log.succ("OpenAPI updated successfully")


def build_all(cli_args: Namespace, config: Config, *args, **kwargs):
    build_defs(cli_args, config, args, kwargs)
    build_ig(cli_args, config, args, kwargs)


__doc__ = "Build FHIR definitions and IGs"
__handlers__ = {
    DEFS: build_defs,
    IG: build_ig,
    ALL: build_all,
}
__setup_subparser__ = setup_subparser
