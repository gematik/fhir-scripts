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
    defs_parser.add_argument(
        "--req", action="store_true", help="Also process requirements"
    )
    defs_parser.add_argument(
        "--only-req", action="store_true", help="Only process requirements"
    )
    defs_parser.add_argument(
        "--cap", action="store_true", help="Also merge CapabilityStatements"
    )
    defs_parser.add_argument(
        "--only-cap", action="store_true", help="Only merge CapabilityStatements"
    )

    ig_parser = subparser.add_parser(IG, help="Build IG")
    ig_parser.add_argument("--oapi", action="store_true", help="Also build OpenAPI")
    ig_parser.add_argument(
        "--only-oapi", action="store_true", help="Only build OpenAPI"
    )

    all_parser = subparser.add_parser(ALL, help="Build everything")
    all_parser.add_argument(
        "--req", action="store_true", help="Also process requirements"
    )
    all_parser.add_argument(
        "--cap", action="store_true", help="Also merge CapabilityStatements"
    )
    all_parser.add_argument("--oapi", action="store_true", help="Also build OpenAPI")


def build_defs(cli_args: Namespace, config: Config, *args, **kwargs):
    log.info("Building definitions")

    defs_config = config.build.steps.definitions
    only_cap = getattr(cli_args, "only_cap", False)
    only_req = getattr(cli_args, "only_req", False)

    if defs_config.requirements or ((cli_args.req or only_req) and not only_cap):
        build_req(args, kwargs)

    if not only_req and not only_cap:
        sushi.run()

    if defs_config.cap_statements or ((cli_args.cap or only_cap) and not only_req):
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

    ig_config = config.build.steps.ig
    only_oapi = getattr(cli_args, "only_oapi", False)

    if not only_oapi:
        igpub.run()
        log.succ("IG built successfully")

    if ig_config.openapi or only_oapi or cli_args.oapi:
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
