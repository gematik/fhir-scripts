import json
import shutil
from argparse import _SubParsersAction
from pathlib import Path

from . import log
from .tools import firely_terminal
from .tools.basic import npm

PKG = "package"
BUILD = "build"
PKG_DIR = "--package-dir"
NO_CLEAR = "--no-clear"

FHIR_REGISTRY = "https://packages.simplifier.net"


def setup_subparser(subparser: _SubParsersAction, *args, **kwarsg):
    pkg_parser = subparser.add_parser(
        PKG, help="Clear and rebuild the FHIR package cache"
    )
    pkg_parser.add_argument(
        PKG_DIR, type=Path, default=None, help="Local directory with packages archives"
    )
    pkg_parser.add_argument(
        NO_CLEAR,
        action="store_true",
        help="Do no clear the FHIR cache before restoring",
    )

    subparser.add_parser(BUILD, help="Clear all build related cache directories")


def cache_rebuild_fhir_cache(
    package_dir: Path | None = None, no_clear: bool = False, *args, **kwargs
):
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

        log.info(f"Using package directory '{package_dir}' to restore package cache")

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
                pkg_json.unlink()

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


def clear_build_caches(*args, **kwargs):
    log.info("Clear build caches")
    for p in ["./input-cache/schemas", "./input-cache/txcache", "./temp", "./template"]:
        if (path := Path(p)).exists():
            shutil.rmtree(path)
            log.succ("Removed {}".format(str(path)))
    log.succ("Cleared build caches successfully")


__doc__ = "Handle caches"
__handlers__ = {PKG: cache_rebuild_fhir_cache, BUILD: clear_build_caches}
__setup_subparser__ = setup_subparser
