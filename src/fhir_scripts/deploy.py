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

    _deploy_ig(target, gcloud)

    # TODO: handle history file

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
