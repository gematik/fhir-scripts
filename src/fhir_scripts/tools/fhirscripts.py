__tool_name__ = "fhirscripts"

import importlib.metadata

from ..version import Version
from .basic import python

PACKAGE = "git+https://github.com/gematik/fhir-scripts.git"


def update(version: Version, *args, **kwargs):
    python.install(PACKAGE, version, as_global=True)


def version(short: bool = False, *args, **kwargs) -> Version:
    """
    Get the installed version
    """
    return Version(importlib.metadata.version("fhir_scripts"))


def latest_version(*args, **kwargs) -> Version | None:
    return python.latest_version_number(PACKAGE)
