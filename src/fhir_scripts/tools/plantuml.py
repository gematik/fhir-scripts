__tool_name__ = "PlantUML"

import re
from pathlib import Path

from ..version import Version
from .basic import java, shell

TEMPLATE_SCRIPTS_DIR = Path("./template/scripts")
PLANTUML_JAR = TEMPLATE_SCRIPTS_DIR / "plantuml.jar"

VERSION_REGEX = re.compile(r"PlantUML version\s+([\d\.]+)\s+")


def version(short: bool = False, *args, **kwargs) -> Version | None:
    """
    Get the installed version, returns None if not installed
    """

    try:
        res = java.run_jar(PLANTUML_JAR, "--version", check=True, log_output=False)

        # Extract the version string from output
        match = VERSION_REGEX.search(res.stdout_oneline)

        version = Version(match[1] if match else None)
        version.add_version = java.version()

        return version

    except shell.CalledProcessError:
        return None
