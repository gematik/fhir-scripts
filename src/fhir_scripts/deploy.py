import json
from argparse import ArgumentParser
from pathlib import Path

from . import log
from .helper import confirm
from .models.config import Config, DeployConfig
from .tools import gcloud

TARGET_BASE_DIR = "ig/fhir"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument("environment", help="Name of the environment")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm all prompts with 'yes'"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all", action="store_true", help="Deploy everything (IG and history)"
    )
    group.add_argument("--only-ig", action="store_true", help="Deploy the IG")
    group.add_argument("--only-history", action="store_true", help="Deploy IG history")
    group.add_argument(
        "--ig-registry", action="store_true", help="Deploy IG registry entries"
    )


def deploy(
    config: Config,
    environment: str,
    ig_registry: bool = False,
    all: bool = False,
    only_ig: bool = False,
    only_history: bool = False,
    yes: bool = False,
    *args,
    **kwargs,
) -> bool:
    deploy_config = config.deploy
    if deploy_config is None:
        raise Exception("deploy configuration missing")

    if ig_registry:
        # Build target URL
        target = _target_path(deploy_config, environment)
        _deploy_ig_registry(target, confirm_yes=yes)

    else:
        # Build target URL
        target = _target_path(deploy_config, environment, needs_project=True)

        if all:
            _deploy_ig(target, confirm_yes=yes)
            _deploy_history(target, confirm_yes=yes)

        elif only_ig:
            _deploy_ig(target, confirm_yes=yes)

        elif only_history:
            _deploy_history(target, confirm_yes=yes)

        else:
            _deploy_ig(target, confirm_yes=yes)

    return True


def _deploy_ig_registry(target, confirm_yes: bool = False):
    reg_dir = Path("./")

    log.info(f"Deploy IG registry files to {target}")
    confirm("Continue?", "Aborted by user", confirm_yes=confirm_yes, default=True)

    deploy_files = ["index.html", "package-feed.xml"]
    for file in deploy_files:

        file = reg_dir / file
        if not file.exists():
            raise Exception(f"Source '{file.absolute()}' does not exist")

        target_file = target + "/" + file.name
        gcloud.copy(source=file, target=target_file, force=True)

    log.succ("Deployed IG registry files")


def _target_path(
    deploy_cfg: DeployConfig, env_name: str, needs_project: bool = False
) -> str:
    env = deploy_cfg.env.get(env_name)

    if env is None:
        raise Exception(f"Environment '{env_name}' not defined in config")

    path_parts: list[str]
    if deploy_cfg.path is not None:
        path_parts = [env, deploy_cfg.path]

    elif project := _project_name(needs_project):
        path_parts = [env, TARGET_BASE_DIR, project]

    else:
        if needs_project:
            raise Exception(
                "Path needs to include a project name, none found in built IG or config"
            )

        path_parts = [env, TARGET_BASE_DIR]

    return "gs://" + "/".join([p.strip("/") for p in path_parts])


def _deploy_ig(target: str, confirm_yes: bool = False):
    output_dir = Path("./output")

    # Get built version
    igs = list(output_dir.glob("ImplementationGuide*.json"))
    if len(igs) != 1:
        raise Exception("Built IG not found")

    ig = json.loads(igs[0].read_text(encoding="utf-8"))
    version = ig["version"]

    # Copy IG
    target_versioned = f"{target}/{version}"
    log.info(f"Deploy built IG to {target_versioned}")
    confirm("Continue?", "Aborted by user", confirm_yes=confirm_yes, default=True)
    gcloud.copy(source=output_dir, target=target_versioned, force=confirm_yes)

    log.succ("Deployed IG")


def _deploy_history(target, confirm_yes: bool = False):
    publish_dir = Path("./publish") / _project_name(needs_project=True)

    history_file_name = "index.html"
    history_file = publish_dir / history_file_name
    if not history_file.exists():
        raise Exception(f"History does not exist: {history_file} not found")

    # Copy history
    target_history = target + "/" + history_file_name
    log.info(f"Deploy history file to {target_history}")
    gcloud.copy(source=history_file, target=target_history, force=True)

    log.succ("Deployed history file")


def _project_name(needs_project: bool = True) -> str | None:
    """
    Extract the project name from a IG Canonical URL
    """
    output_dir = Path("./output")

    # Get project name
    igs = list(output_dir.glob("ImplementationGuide*.json"))
    if len(igs) != 1:
        if needs_project:
            raise Exception("Built IG not found")

        else:
            return None

    ig = json.loads(igs[0].read_text(encoding="utf-8"))
    return ig["url"].rsplit("/", 3)[1]


__doc__ = "Deploy IG"
__handler__ = deploy
__setup_parser__ = setup_parser
