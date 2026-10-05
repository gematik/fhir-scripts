import json
import re
from argparse import ArgumentParser
from collections import deque
from pathlib import Path

import yaml
from pydantic import AnyUrl

from . import log
from .error import ProjectCheckError, ProjectSetupError
from .models.fhir.package_json import PackageJson
from .models.fhir.publication_request import (
    PublicationRequest,
    PublicationRequestStatus,
)
from .models.fhir.sushi_config import SushiConfig, SushiConfigStatus

PUB_REQUEST_NAME = "publication-request.json"
SUSHI_CONFIG_NAME = "sushi-config.yaml"
PACKAGE_JSON_NAME = "package.json"

VERSION_REGEX = re.compile(r"(?:\/|\s|^)(\d+(?:\.\d+){2}(?:-[a-z\.\d]+)?)(?:\s|$)")


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument(
        "--workdir", type=Path, default=Path.cwd(), help="Working directory"
    )
    parser.add_argument(
        "--release", action="store_true", help="Perform extra checks for release"
    )


def check(workdir: Path, release: bool, *args, **kwargs):
    errors = 0
    warnings = 0

    # Define the file names
    pub_request_file = workdir / PUB_REQUEST_NAME
    sushi_config_file = workdir / SUSHI_CONFIG_NAME
    package_json_file = workdir / PACKAGE_JSON_NAME

    # Read the content of the files
    pub_request = (
        PublicationRequest.model_validate(
            json.loads(pub_request_file.read_text("utf-8"))
        )
        if pub_request_file.exists()
        else None
    )

    sushi_config = (
        SushiConfig.model_validate(yaml.safe_load(sushi_config_file.read_text("utf-8")))
        if sushi_config_file.exists()
        else None
    )
    package_json = (
        PackageJson.model_validate(json.loads(package_json_file.read_text("utf-8")))
        if package_json_file.exists()
        else None
    )

    # Check all files exist
    if pub_request is None or sushi_config is None or package_json is None:
        raise ProjectSetupError(
            "Project malformed: publication request, sushi config or package JSON missing"
        )

    # Check versions equal
    err, warn = _check_versions(
        pub_request.version,
        pub_request.desc,
        pub_request.path,
        sushi_config.version,
        package_json.version,
        **kwargs,
    )
    errors += err
    warnings += warn

    # Check versions of dependencies
    err, warn = _check_deps(
        sushi_config.dependencies,
        package_json.dependencies,
    )
    errors += err
    warnings += warn

    # Check versions of transistive dependencies
    err, warn = _check_transitive_deps(sushi_config.dependencies, **kwargs)
    errors += err
    warnings += warn

    # Check definitions
    err, warn = _check_def_versions(
        defs_dir=workdir / "fsh-generated" / "resources", **kwargs
    )
    errors += err
    warnings += warn

    # Make release specific checks
    if release:
        err, warn = _check_release(
            pub_request.status,
            sushi_config.status,
            sushi_config.release_label,
        )
        errors += err
        warnings += warn

    if errors > 0 or warnings > 0:
        log.fail(f"Checks failed: {log.ERR}{errors}, {log.WARN}{warnings}")
        raise ProjectCheckError("Checks failed")

    else:
        log.succ("Checks successful")


def _check_versions(
    pub_request_version: str,
    pub_request_desc: str | None,
    pub_request_path: AnyUrl,
    sushi_config_version: str,
    package_json_version: str,
    **kwargs,
):
    errors = 0
    warnings = 0

    log.info("checking versions")

    # Publication Request == Sushi Config
    if (
        pub_request_version != sushi_config_version
        or sushi_config_version != package_json_version
    ):
        errors += 1

        log.fail(
            f"IG versions not match: Publication Request {pub_request_version}, Sushi Config {sushi_config_version}, "
            f"Package JSON {package_json_version}"
        )

    # Version in path of Sushi Config
    if (path_version := _get_version(str(pub_request_path))) != sushi_config_version:
        errors += 1

        log.fail(
            "Version in PublicationRequest 'path' does not match 'version' in sushi config: "
            f"{path_version} != {sushi_config_version}"
        )

    # Version in description in Sushi Config
    if (desc_version := _get_version(pub_request_desc)) != sushi_config_version:
        errors += 1

        log.fail(
            f"Version in description does not match version in sushi config: {desc_version} != {sushi_config_version}"
        )

    return errors, warnings


def _check_deps(
    sushi_config_deps: dict[str, str],
    package_json_deps: dict[str, str],
    **kwargs,
):
    errors = 0
    warnings = 0

    log.info("check dependencies")

    pkg_deps = set(package_json_deps)
    sushi_deps = set(sushi_config_deps)
    ignore_deps = {"hl7.fhir.r4.core"}

    if not_sushi := pkg_deps - sushi_deps - ignore_deps:
        warnings += 1

        log.warn(f"Missing dependencies in Sushi Config: {', '.join(not_sushi)}")

    if not_pkg := sushi_deps - pkg_deps - ignore_deps:
        warnings += 1

        log.warn(f"Missing dependencies in Package JSON: {', '.join(not_pkg)}")

    for entry in pkg_deps & sushi_deps:
        if (pkg_version := package_json_deps.get(entry)) != (
            sushi_version := sushi_config_deps.get(entry)
        ):
            errors += 1

            log.fail(
                f"Dependency {entry} version does not match: Sushi Config {sushi_version}, Package JSON {pkg_version}"
            )

    return errors, warnings


def _check_transitive_deps(
    sushi_config_deps: dict[str, str], pkg_dir: Path | None = None, **kwargs
):
    fhir_pkg_dir = pkg_dir or (Path.home() / ".fhir" / "packages")

    err = 0
    warn = 0

    log.info("check transitive dependencies")

    dep_versions: dict[str, list[str]] = {}

    to_process = deque(sushi_config_deps.items())
    while len(to_process) > 0:
        pkg, version = to_process.popleft()

        if pkg not in dep_versions:
            dep_versions[pkg] = []

        if version not in dep_versions[pkg]:
            dep_versions[pkg].append(version)

        pkg_json = fhir_pkg_dir / f"{pkg}#{version}" / "package" / "package.json"

        if not pkg_json.exists():
            log.warn(f"Cannot check package {pkg}#{version}: not installed")
            warn += 1
            continue

        pkg_content = PackageJson.model_validate(json.loads(pkg_json.read_text()))
        pkg_deps = pkg_content.dependencies

        to_process += deque(pkg_deps.items())

    for pkg, versions in dep_versions.items():
        if len(versions) > 1:
            log.warn(
                f"Different transitive versions of package {pkg}: {', '.join(versions)}"
            )
            warn += 1

    return err, warn


def _check_def_versions(defs_dir: Path, **kwargs):
    err = 0
    warn = 0

    log.info("check versions in definition")

    # Generate list of versions and associated dates
    version_dates: dict[str, list[str]] = {}
    for f in defs_dir.glob("**/*.json"):
        content = json.loads(f.read_text())
        version = content.get("version")
        date = content.get("date")

        if isinstance(version, list):
            continue

        if version is None:
            continue

        if version not in version_dates:
            version_dates[version] = []

        if date not in version_dates[version]:
            version_dates[version].append(date)

    log.debug(f"Versions in definitions: {', '.join(version_dates.keys())}")

    for version, dates in version_dates.items():
        if len(dates) != 1:
            log.fail(f"Different dates for version {version}: {', '.join(dates)}")
            err += 1

    return err, warn


def _check_release(
    pub_request_status: PublicationRequestStatus,
    sushi_config_status: SushiConfigStatus,
    sushi_config_release_label: str,
    **kwargs,
):
    errors = 0
    warnings = 0

    log.info("check release configuration")

    if (status := sushi_config_status) != "active":
        errors += 1

        log.fail(f'Status in Sushi Config is "{status.name}", but should be "active"')

    if (label := sushi_config_release_label) != "release":
        errors += 1

        log.fail(f'Release label in Sushi Config is "{label}", but should be "release"')

    if (status := pub_request_status) != "release":
        errors += 1

        log.fail(
            f'Status in Publication Request is "{status.name}", but should be "release"'
        )

    return errors, warnings


def _get_version(value: str | None) -> str | None:
    if value is None:
        return None

    match = VERSION_REGEX.search(value)
    return match[1] if match else None


__doc__ = "Check consistencies"
__handler__ = check
__setup_subparser__ = setup_parser
