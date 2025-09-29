import argparse
import os
from pathlib import Path
import sys

import yaml

from . import deploy, log, update
from .config import Config
from .exception import CancelException


def main():
    parser = argparse.ArgumentParser(description="Scripts to support FHIR development")
    subparsers = parser.add_subparsers(dest="cmd")

    deploy.setup_parser(subparsers)
    update.setup_parser(subparsers)

    args = parser.parse_args()

    handlers = {}
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

    except BaseException as e:
        log.fail(f"Error: {e}")
        sys.exit(os.EX_DATAERR)

    sys.exit(os.EX_OK)
