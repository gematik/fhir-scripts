from argparse import Namespace, _SubParsersAction
from pathlib import Path

from . import log
from .exception import NoConfigException, NotInstalledException
from .models.config import Config
from .tools import epatools, igpub, igtools, sushi

DEFS = "defs"
IG = "ig"
ALL = "all"
PIPELINE = "pipeline"


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

    subparser.add_parser(PIPELINE, help="Build IG")


def build_defs(cli_args: Namespace, config: Config, *args, **kwargs):
    log.info("Building definitions")

    epatools_config = config.build.builtin.epatools
    igtools_config = config.build.builtin.igtools

    only_cap = getattr(cli_args, "only_cap", False)
    only_req = getattr(cli_args, "only_req", False)

    enable_requirements = (igtools_config or cli_args.req or only_req) and not only_cap
    enable_sushi = not only_req and not only_cap
    enable_cap_statements = (
        (isinstance(epatools_config, bool) and epatools_config)
        or epatools_config.cap_statements  # type: ignore
        or ((cli_args.cap or only_cap))
        and not only_req
    )

    if enable_requirements:
        build_req(*args, **kwargs)

    if enable_sushi:
        build_sushi(*args, **kwargs)

    if enable_cap_statements:
        build_cap(*args, **kwargs)

    log.succ("Definitions built successfully")


def build_sushi(*args, **kwargs):
    sushi.run()


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

    epatools_config = config.build.builtin.epatools
    only_oapi = getattr(cli_args, "only_oapi", False)

    enable_igpub = not only_oapi
    enable_openapi = (
        (isinstance(epatools_config, bool) and epatools_config)
        or epatools_config.cap_statements  # type: ignore
        or only_oapi
        or cli_args.oapi
    )

    if enable_igpub:
        build_igpub(*args, **kwargs)

    if enable_openapi:
        build_openapi(config)

    log.succ("IG built successfully")
    igpub.qa()


def build_igpub(*args, **kwargs):
    igpub.run()


def build_openapi(*args, **kwargs):
    log.info("Updating OpenAPI")
    epatools.openapi(*args, **kwargs)
    log.succ("OpenAPI updated successfully")


def build_all(cli_args: Namespace, config: Config, *args, **kwargs):
    build_defs(cli_args, config, *args, **kwargs)
    build_ig(cli_args, config, *args, **kwargs)


def _step_name(any) -> str:
    return any if isinstance(any, str) else list(any.model_dump().keys())[0]


PIPELINE_STEPS = {
    "requirements": build_req,
    "sushi": build_sushi,
    "cap_statements": build_cap,
    "igpub": build_igpub,
    "openapi": build_openapi,
}


def build_pipeline(config: Config, *args, **kwargs):
    pipeline = config.build.pipeline

    invalid_steps = [
        step_name
        for step in pipeline
        if not isinstance(step, str)
        if (step_name := _step_name(step)) and step_name not in PIPELINE_STEPS
    ]

    if invalid_steps:
        raise Exception(
            f"Pipeline configuration contains invalid step(s): {", ".join(invalid_steps)}"
        )

    for step in pipeline:
        step_name = _step_name(step)

        log.info(f"Processing step '{step_name}'")
        PIPELINE_STEPS[step_name](config, *args, **kwargs)
        pass


__doc__ = "Build FHIR definitions and IGs"
__handlers__ = {
    DEFS: build_defs,
    IG: build_ig,
    ALL: build_all,
    PIPELINE: build_pipeline,
}
__setup_subparser__ = setup_subparser
