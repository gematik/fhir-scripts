import argparse

from . import update


def main():
    parser = argparse.ArgumentParser(description="Scripts to support FHIR development")
    subparsers = parser.add_subparsers(dest="cmd")

    update.setup_parser(subparsers)

    args = parser.parse_args()

    handlers = {}
    update.add_handler(handlers)

    if not handlers[args.cmd](args):
        parser.print_help()
