from argparse import ArgumentParser

from . import log, tools

TARGET_BASE_DIR = "ig/fhir"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument(
        "--outdated", action="store_true", help="List outdated versions"
    )
    pass


def versions(outdated: bool = False, *args, **kwargs) -> bool:
    versions = {}
    for name, module in tools.__dict__.items():
        if not name.startswith("__") and (
            version_func := getattr(module, "version", None)
        ):
            tool_name = getattr(module, "__tool_name__", None) or name

            if outdated:
                latest_func = getattr(module, "latest_version", None)
                latest = latest_func() if latest_func else None

                if (
                    latest is not None
                    and (version := version_func(short=True))
                    and latest != version
                ):
                    versions[tool_name] = (version, latest)

            else:
                versions[tool_name] = version_func(), None

    if outdated and len(versions) == 0:
        log.succ("Everything up-to-date")
        return True

    for name, (version, latest) in sorted(versions.items(), key=lambda x: x[0].lower()):
        if latest is not None:
            log.info(f"{name}: {version} < {latest}")

        else:
            log.info(f"{name}: {version}")

    return True


__doc__ = "Version information of all tools"
__handler__ = versions
__setup_parser__ = setup_parser
