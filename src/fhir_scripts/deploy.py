from argparse import Namespace, _SubParsersAction
from pathlib import Path
from typing import Callable
import json
from . import log

from .config import Config
from .tools.gcloud import GCloudHelper

CMD = "deploy"


def setup_parser(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(CMD, help="Deploy IG")
    parser.add_argument("environment", help="Name of the environment")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Deploy everything (IG and history)")
    group.add_argument("--only-ig", action="store_true", help="Deploy the IG")
    group.add_argument("--only-history", action="store_true", help="Deploy IG history")


def add_handler(handlers: dict[str, Callable[[Namespace], bool]]):
    handlers[CMD] = handle


def handle(cli_args: Namespace, config: Config, *args, **kwargs) -> bool:
    gcloud = GCloudHelper()

    deploy_cfg = config.deploy
    env = deploy_cfg.env.get(cli_args.environment)

    if env is None:
        raise Exception(f"Environment '{cli_args.environment}' not defined in config")

    # Build URLs
    target = f"gs://{env.rstrip("/")}/{deploy_cfg.path.strip("/")}"

    # Login if necessary
    gcloud.login()

    # TODO: add arguments to deploy --all, --only-ig or --only-history, default should be --only-ig

    if cli_args.all:
        _deploy_ig(target, gcloud)
        _deploy_history(target, gcloud)

    elif cli_args.only_ig:
        _deploy_ig(target, gcloud)

    elif cli_args.only_history:
        _deploy_history(target, gcloud)

    else:
        _deploy_ig(target, gcloud)

    return True

def _deploy_ig(target: str, gcloud: GCloudHelper):
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
    gcloud.copy(source=output_dir, target=target_versioned)

    log.succ("Deployed IG")

def _deploy_history(target, gcloud:GCloudHelper):
    output_dir = Path("./output")

    # Get project name
    igs = list(output_dir.glob("ImplementationGuide*.json"))
    if len(igs) != 1:
        raise Exception("Built IG not found")

    ig = json.loads(igs[0].read_text(encoding="utf-8"))
    project = _project_name(ig["url"])

    publish_dir = Path("./publish/" + project)

    history_file_name = "index.html"
    history_file = publish_dir / history_file_name
    if not history_file.exists():
        raise Exception(f"history does not exist: {history_file} not found")

    # Copy history
    target_history = target + "/" + history_file_name
    log.info(f"Deploy history file to {target_history}")
    gcloud.copy(source=history_file, target=target_history, force=True)

    log.succ("Deployed history file")

def _project_name(url:str)-> str:
    """
    Extract the project name from a IG Canonical URL
    """
    return url.rsplit("/",3)[1]
