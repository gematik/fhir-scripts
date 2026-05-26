import json
import shutil
from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path

from . import log
from .multiig import IGTarget, select_targets, working_directory
from .tools import fhir_pkg_tool, firely_terminal
from .tools.basic import npm

# Commands
PKG = "package"
BUILD = "build"

# Arguments
PKG_DIR = "--package-dir"
NO_CLEAR = "--no-clear"
NEW = "--new"
LEGACY = "--legacy"

FHIR_REGISTRY = "https://packages.simplifier.net"


def setup_subparser(
    parser: ArgumentParser, subparser: _SubParsersAction, *args, **kwarsg
):
    target_args_parser = ArgumentParser(add_help=False)
    target_args_parser.add_argument(
        "--ig",
        action="extend",
        nargs="+",
        default=[],
        help="Target IG name(s), e.g. '--ig core rx' or '--ig core --ig rx'",
    )
    target_args_parser.add_argument(
        "--all",
        action="store_true",
        help="Run for all IGs in a multi-IG repository",
    )

    pkg_parser = subparser.add_parser(
        PKG,
        help="Clear and rebuild the FHIR package cache",
        parents=[target_args_parser],
    )
    pkg_parser.add_argument(
        PKG_DIR, type=Path, default=None, help="Local directory with packages archives"
    )
    pkg_parser.add_argument(
        NO_CLEAR,
        action="store_true",
        help="Do no clear the FHIR cache before restoring",
    )

    group = pkg_parser.add_mutually_exclusive_group()
    group.add_argument(
        NEW,
        action="store_true",
        help="Use the new WIP implementation of a package manager",
    )
    group.add_argument(
        LEGACY, action="store_true", help="Old implementation using Firely Terminal"
    )

    subparser.add_parser(
        BUILD,
        help="Clear all build related cache directories",
        parents=[target_args_parser],
    )


def cache_rebuild_fhir_cache(
    package_dir: Path | None = None,
    no_clear: bool = False,
    new: bool = False,
    legacy: bool = False,
    ig: list[str] | None = None,
    all: bool = False,
    *args,
    **kwargs,
):

    for target in _selected_targets(ig=ig, all=all):
        with working_directory(target.path):
            log.info(f"Rebuild package cache for IG '{target.name}'")
            _cache_rebuild_fhir_cache_once(
                package_dir=package_dir,
                no_clear=no_clear,
                new=new,
                legacy=legacy,
            )
            log.succ(f"Package cache rebuilt for IG '{target.name}'")


def _cache_rebuild_fhir_cache_once(
    package_dir: Path | None = None,
    no_clear: bool = False,
    new: bool = False,
    legacy: bool = False,
):

    # Set default to "legacy" at the moment
    if not new and not legacy:
        legacy = True

    if not fhir_pkg_tool.is_installed() and not legacy:
        legacy = True
        log.warn(
            "{} not installed, fall back to {}".format(
                fhir_pkg_tool.__tool_name__, firely_terminal.__tool_name__
            )
        )

    if legacy:
        # TODO: Get dependencies from sushi config
        # Can include some "meta" packages that cannot be downloaded from the registry
        # sushi_config = Path("./sushi-config.yaml")

        # if not sushi_config.exists():
        #     raise Exception("Not in project root; no `sushi-config.yaml` found")

        # sushi_config_def = yaml.safe_load(sushi_config.read_text(encoding="utf-8"))
        # dependencies = sushi_config_def.get("dependencies", {})

        # Get dependencies from package.json
        package_json = Path("./package.json")

        if not package_json.exists():
            raise Exception("Not in project root; no `package.json` found")

        packge_json_def = json.loads(package_json.read_text(encoding="utf-8"))
        dependencies = packge_json_def.get("dependencies", {})

        pkg_json = Path("./package.json")
        pkg_json_bak = Path("./package.bak.json")

        if not no_clear:
            # Remove all previous packages
            fhir_cache = Path.home() / ".fhir/packages"

            if fhir_cache.exists():
                log.info("Remove all previous packages")
                for item in fhir_cache.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                log.succ("Removed all packages")

        if package_dir is not None:

            # Create package dir if it does not exist
            if not package_dir.exists():
                package_dir.mkdir(parents=True)

            log.info(
                f"Using package directory '{package_dir}' to restore package cache"
            )

            try:
                # Handle each dependency
                for pkg, version in dependencies.items():
                    ###
                    # Get local file
                    ###

                    # Check if any of the possible namings of the package file already exists
                    found = False

                    # Check the naming for official packages
                    pkg_file = package_dir / f"{pkg}-{version}.tgz"
                    if pkg_file.exists():
                        found = True
                        log.info(f"Cache hit for {pkg}@{version}")

                    else:
                        pkg_file = package_dir / f"{pkg}_{version}.tgz"

                        # Check naming for own build packages
                        if pkg_file.exists():
                            found = True
                            log.info(f"Cache hit for {pkg}@{version}")

                        # No file was found, so it needs to be downloaded
                        if not found:
                            log.info(f"Cache miss for {pkg}@{version}")
                            npm.download(pkg, version, package_dir, FHIR_REGISTRY)
                            log.succ(f"Downloaded {pkg}@{version}")
                            pkg_file = package_dir / f"{pkg}-{version}.tgz"

                    ###
                    # Install
                    ###

                    # Backup old `package.json` and remove original one
                    pkg_json_bak.write_bytes(pkg_json.read_bytes())
                    pkg_json.write_text("{}", "utf-8")

                    # Install from package file
                    log.info(f"Install {pkg}@{version}")
                    firely_terminal.install(file=pkg_file)
                    log.succ(f"Installed {pkg}@{version} successfully")

                    # Restore `package.json`
                    pkg_json.write_bytes(pkg_json_bak.read_bytes())
                    pkg_json_bak.unlink()

            except Exception as e:
                # Restore backup of `package.json` if it exists before rethrowing the exception
                if pkg_json_bak.exists():
                    pkg_json.write_bytes(pkg_json_bak.read_bytes())
                    pkg_json_bak.unlink()

                raise e

        log.info("Restore cache")
        firely_terminal.restore()
        log.succ("Restore successful")

    else:
        if not no_clear:
            # Remove all previous packages
            fhir_cache = Path.home() / ".fhir/packages"

            if fhir_cache.exists():
                log.info("Remove all previous packages")
                for item in fhir_cache.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                log.succ("Removed all packages")

        log.info("Restore cache")
        fhir_pkg_tool.install_deps()
        log.succ("Restore successful")


def clear_build_caches(
    ig: list[str] | None = None, all: bool = False, *args, **kwargs
):
    for target in _selected_targets(ig=ig, all=all):
        with working_directory(target.path):
            log.info(f"Clear build caches for IG '{target.name}'")
            for p in [
                "./input-cache/schemas",
                "./input-cache/txcache",
                "./temp",
                "./template",
            ]:
                if (path := Path(p)).exists():
                    shutil.rmtree(path)
                    log.succ("Removed {}".format(str(path)))
            log.succ(f"Cleared build caches successfully for IG '{target.name}'")


def _selected_targets(ig: list[str] | None, all: bool):
    targets = select_targets(ig=ig, select_all=all)
    if len(targets) == 0:
        return [IGTarget(name="current", path=Path.cwd())]

    return targets


__doc__ = "Handle caches"
__handlers__ = {PKG: cache_rebuild_fhir_cache, BUILD: clear_build_caches}
__setup_subparser__ = setup_subparser
