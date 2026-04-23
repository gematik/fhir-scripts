import json
import re
from argparse import ArgumentParser
from pathlib import Path

import yaml

from . import log

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
        json.loads(pub_request_file.read_text("utf-8"))
        if pub_request_file.exists()
        else None
    )
    sushi_config = (
        yaml.safe_load(sushi_config_file.read_text("utf-8"))
        if sushi_config_file.exists()
        else None
    )
    package_json = (
        json.loads(package_json_file.read_text("utf-8"))
        if package_json_file.exists()
        else None
    )

    # Check all files exist
    if pub_request is None or sushi_config is None or package_json is None:
        raise Exception(
            "Project malformed: publication request, sushi config or package JSON missing"
        )

    args = {
        "pub_request": pub_request,
        "sushi_config": sushi_config,
        "package_json": package_json,
        "defs_dir": workdir / "fsh-generated" / "resources",
    }

    # Check versions equal
    err, warn = _check_versions(**args)
    errors += err
    warnings += warn

    # Check versions of dependencies
    err, warn = _check_deps(**args)
    errors += err
    warnings += warn

    # Check definitions
    err, warn = _check_def_versions(**args)
    errors += err
    warnings += warn

    # Make release specific checks
    if release:
        err, warn = _check_release(**args)
        errors += err
        warnings += warn

    if errors > 0 or warnings > 0:
        log.fail(f"Checks failed: {log.ERR}{errors}, {log.WARN}{warnings}")
        raise Exception("Checks failed")

    else:
        log.succ("Checks successful")


def _check_versions(
    pub_request: dict, sushi_config: dict, package_json: dict, **kwargs
):
    errors = 0
    warnings = 0

    pub_request_version = pub_request.get("version")
    sushi_config_version = sushi_config.get("version")
    package_json_version = package_json.get("version")

    # Publication Request == Sushi Config
    if (
        pub_request_version == sushi_config_version
        and sushi_config_version == package_json_version
    ):
        log.succ(f"All IG versions match: {pub_request_version}")

    else:
        errors += 1

        log.fail(
            f"IG versions not match: Publication Request {pub_request_version}, Sushi Config {sushi_config_version}, Package JSON {package_json_version}"
        )

    # Version in path of Sushi Config
    if (path_version := _get_version(pub_request, "path")) == sushi_config_version:
        log.succ("Version in path in publication request matches")

    else:
        errors += 1

        log.fail(
            "Version in path does not match version in sushi config: {} != {}".format(
                path_version, sushi_config_version
            )
        )

    # Version in description in Sushi Config
    if (desc_version := _get_version(pub_request, "desc")) == sushi_config_version:
        log.succ("Version in description in publication request matches")

    else:
        errors += 1

        log.fail(
            "Version in description does not match version in sushi config: {} != {}".format(
                desc_version, sushi_config_version
            )
        )

    return errors, warnings


def _check_deps(pub_request: dict, sushi_config: dict, package_json: dict, **kwargs):
    errors = 0
    warnings = 0

    package_json_deps = package_json.get("dependencies", {})
    sushi_config_deps = sushi_config.get("dependencies", {})

    pkg_deps = set(package_json_deps)
    sushi_deps = set(sushi_config_deps)
    ignore_deps = set(["hl7.fhir.r4.core"])

    if not_sushi := pkg_deps - sushi_deps - ignore_deps:
        warnings += 1

        log.warn(
            "Missing dependencies in Sushi Config: {}".format(", ".join(not_sushi))
        )

    if not_pkg := sushi_deps - pkg_deps - ignore_deps:
        warnings += 1

        log.warn("Missing dependencies in Package JSON: {}".format(", ".join(not_pkg)))

    for entry in pkg_deps & sushi_deps:
        if (pkg_version := package_json_deps.get(entry)) != (
            sushi_version := sushi_config_deps.get(entry)
        ):
            errors += 1

            log.fail(
                "Dependency {} version does not match: Sushi Config {}, Package JSON {}".format(
                    entry, sushi_version, pkg_version
                )
            )

        else:
            log.succ(
                "Dependency {} version does match: {}".format(entry, sushi_version)
            )

    return errors, warnings


def _check_def_versions(defs_dir: Path, **kwargs):
    err = 0
    warn = 0

    # Generate list of versions and associated dates
    version_dates: dict[str, list[str]] = {}
    for f in defs_dir.glob("**/*.json"):
        content = json.loads(f.read_text())
        version = content.get("version")
        date = content.get("date")

        if version is None:
            continue

        if version not in version_dates:
            version_dates[version] = []

        if date not in version_dates[version]:
            version_dates[version].append(date)

    log.info(f"Versions in definitions: {', '.join(version_dates.keys())}")

    for version, dates in version_dates.items():
        if len(dates) == 1:
            log.succ(f"Version {version} has consistent dates")

        else:
            log.fail(f"Different dates for version {version}: {', '.join(dates)}")
            err += 1

    return err, warn


def _check_release(pub_request: dict, sushi_config: dict, **kwargs):
    errors = 0
    warnings = 0

    if (status := sushi_config.get("status")) != "active":
        errors += 1

        log.fail(
            'Status in Sushi Config is "{}", but should be "active"'.format(status)
        )
    else:
        log.succ('Status in Sushi Config is "active"')

    if (status := sushi_config.get("releaseLabel")) != "release":
        errors += 1

        log.fail(
            'Release label in Sushi Config is "{}", but should be "release"'.format(
                status
            )
        )
    else:
        log.succ('Release label in Sushi Config is "release"')

    if (status := pub_request.get("status")) != "release":
        errors += 1

        log.fail(
            'Status in Publication Request is "{}", but should be "release"'.format(
                status
            )
        )
    else:
        log.succ('Status in Publication Request is "release"')

    return errors, warnings


def _get_version(value: str | dict[str, str], key: str | None = None) -> str | None:
    if isinstance(value, dict):
        if key is None:
            return None

        value = value.get(key, "")

    match = VERSION_REGEX.search(value)
    return match[1] if match else None


__doc__ = "Check consistencies"
__handler__ = check
__setup_subparser__ = setup_parser
