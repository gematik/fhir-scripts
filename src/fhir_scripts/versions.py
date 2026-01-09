from argparse import ArgumentParser

from . import log, tools

TARGET_BASE_DIR = "ig/fhir"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument(
        "--outdated", action="store_true", help="List outdated versions"
    )
    pass


def versions(outdated: bool = False, *args, **kwargs) -> bool:
    up_to_date = True
    for name, module in tools.__dict__.items():
        if not name.startswith("__") and (
            version_func := getattr(module, "version", None)
        ):
            try:
                tool_name = getattr(module, "__tool_name__", None) or name
                version = version_func()

                if outdated:
                    if latest_func := getattr(module, "latest_version", None):
                        latest = latest_func() if latest_func else None

                        if latest is not None and latest != version:
                            log.info("{}: {} < {}".format(tool_name, version, latest))
                            up_to_date = False

                    else:
                        log.warn(
                            "{} is missing latest version information".format(tool_name)
                        )

                elif version is not None:
                    log.info("{}: {}".format(tool_name, version.long))

            except Exception as e:
                raise Exception(
                    "Error occured during processing version of {}".format(tool_name), e
                )

    if outdated and up_to_date:
        log.succ("Everything up-to-date")
        return True

    return True


__doc__ = "Version information of all tools"
__handler__ = versions
__setup_parser__ = setup_parser
