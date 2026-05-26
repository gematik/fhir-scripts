from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path

from . import log
from .multiig import IGTarget, select_targets, working_directory
from .tools import publishtools

PROJECT = "project"
IG_REGISTRY = "ig-registry"


def setup_subparser(
    parser: ArgumentParser, subparser: _SubParsersAction, *args, **kwarsg
):
    project_parser = subparser.add_parser(PROJECT, help="Publish the current project")
    project_parser.add_argument(
        "--ig",
        action="extend",
        nargs="+",
        default=[],
        help=(
            "Target IG name(s), e.g. 'fhirscripts publish project --ig core rx "
            "--ig-registry ../fhir-ig-registry' or '--ig core --ig rx'"
        ),
    )
    project_parser.add_argument(
        "--all",
        action="store_true",
        help="Run for all IGs, e.g. 'fhirscripts publish project --all --ig-registry ...'",
    )
    project_parser.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="Path of the project to publish",
    )
    project_parser.add_argument(
        "--ig-registry",
        type=Path,
        required=True,
        help="Directory that contains the IG registry related files",
    )

    registry_parser = subparser.add_parser(IG_REGISTRY, help="Publish the IG registry")

    registry_parser.add_argument(
        "--ig-registry",
        type=Path,
        required=True,
        help="Directory that contains the IG registry related files",
    )


def publish_project(
    project_dir: Path | None,
    ig_registry: Path,
    ig: list[str] | None = None,
    all: bool = False,
    *args,
    **kwargs,
):
    targets = select_targets(ig=ig, select_all=all)
    if len(targets) == 0:
        targets = [IGTarget(name="current", path=Path.cwd())]

    for target in targets:
        with working_directory(target.path):
            selected_project_dir = project_dir or Path.cwd()
            log.info(
                f"Publish project '{selected_project_dir}' using IG registry '{ig_registry}'"
            )
            publishtools.publish(selected_project_dir, ig_registry)
            log.succ(f"Project published for IG '{target.name}'")


def publish_igregistry(ig_registry: Path, *args, **kwargs):
    log.info(f"Publish IG registry '{ig_registry}'")
    publishtools.render_list(ig_registry)
    log.succ("IG registry published")


__doc__ = "Publish a project or IG registry"
__handlers__ = {PROJECT: publish_project, IG_REGISTRY: publish_igregistry}
__setup_subparser__ = setup_subparser
