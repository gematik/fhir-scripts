__tool_name__ = "fhirscripts"

import importlib.metadata

from .basic import python

PACKAGE = "git+https://github.com/gematik/fhir-scripts.git"


def update(*args, **kwargs):
    python.install(PACKAGE, as_global=True)


def version(short: bool = False, *args, **kwargs) -> str | None:
    """
    Get the installed version
    """
    return importlib.metadata.version("fhir_scripts")


def latest_version(*args, **kwargs) -> str | None:
    return python.latest_version_number(PACKAGE)
