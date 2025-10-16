import os
from argparse import Namespace, _SubParsersAction
from pathlib import Path

from . import log
from .tools import publishtools

PROJECT = "project"
IG_REGISTRY = "ig-registry"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    project_parser = subparser.add_parser(PROJECT, help="Publish the current project")
    project_parser.add_argument(
        "--project-dir",
        type=Path,
        default=os.getcwd(),
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


def publish_project(cli_args: Namespace, *args, **kwargs):
    log.info(
        f"Publish project '{cli_args.project_dir}' using IG registry '{cli_args.ig_registry}'"
    )
    publishtools.publish(cli_args.project_dir, cli_args.ig_registry)
    log.succ("Project published")


def publish_igregistry(cli_args: Namespace, *args, **kwargs):
    log.info(f"Publish IG registry '{cli_args.ig_registry}'")
    publishtools.render_list(cli_args.ig_registry)
    log.succ("IG registry published")


__doc__ = "Publish a project or IG registry"
__handlers__ = {PROJECT: publish_project, IG_REGISTRY: publish_igregistry}
__setup_subparser__ = setup_subparser
