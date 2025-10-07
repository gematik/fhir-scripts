import argparse
import os
import sys
from pathlib import Path

import yaml

from . import build, deploy, log, update
from .config import Config
from .exception import CancelException


def main():
    parser = argparse.ArgumentParser(description="Scripts to support FHIR development")
    subparsers = parser.add_subparsers(dest="cmd")

    build.setup_parser(subparsers)
    deploy.setup_parser(subparsers)
    update.setup_parser(subparsers)

    args = parser.parse_args()

    handlers = {}
    build.add_handler(handlers)
    deploy.add_handler(handlers)
    update.add_handler(handlers)

    try:
        config_file = Path("./config.yaml")
        config = Config.model_validate(
            yaml.safe_load(config_file.read_text(encoding="utf-8"))
        )

        if not handlers[args.cmd](args, config):
            parser.print_help()

    except CancelException as e:
        log.warn(str(e))
        sys.exit(-1)

    except Exception as e:
        if stdout := getattr(e, "stdout", None):
            log.info(stdout)

        if stderr := getattr(e, "stderr", None):
            log.fail(stderr)

        log.fail(f"Error: {str(e)}")
        sys.exit(os.EX_DATAERR)

    sys.exit(os.EX_OK)
