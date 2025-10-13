import json
from pathlib import Path

import yaml

from .. import log
from . import java, shell

DOWNLOAD_URL = (
    "https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar"
)
INPUT_CACHE_DIR = Path("./input-cache")
PUBLISHER_JAR = INPUT_CACHE_DIR / "publisher.jar"


def run():
    is_installed()
    log.info("Run IG Publisher")

    sushi_config = yaml.safe_load(Path("./sushi-config.yaml").read_text("utf-8"))

    publish_url = sushi_config["canonical"] + "/" + sushi_config["version"]
    try:
        args = ["-no-sushi", "-ig .", f"-publish {publish_url}"]
        java.run_jar(PUBLISHER_JAR, *args)
        log.succ("IG Publisher run successful")

    except shell.CalledProcessError:
        raise Exception("IG Publisher run failed")


def is_installed() -> None:
    """
    Checks if installed
    """
    if not PUBLISHER_JAR.exists():
        raise Exception(f"{__tool_name__} is needed but not installed")


def qa():
    qa_file = Path("./output/qa.json")
    if not qa_file.exists():
        raise Exception("IG not built")

    qa = json.loads(qa_file.read_text("utf-8"))

    result = []
    if (errs := qa["errs"]) > 0:
        result.append(f"{log.ERR} {errs}")

    if (warn := qa["warnings"]) > 0:
        result.append(f"{log.WARN} {warn}")

    if (info := qa["hints"]) > 0:
        result.append(f"{log.INFO} {info}")

    if len(result) == 0:
        result.append(f"{log.CHECK} Everything looks fine")

    log.info(f"QA result: {', '.join(result)}")


def update():
    if not INPUT_CACHE_DIR.exists():
        INPUT_CACHE_DIR.mkdir(parents=True)

    shell.run(
        f'curl -L "{DOWNLOAD_URL}" -o "{PUBLISHER_JAR}"',
        check=True,
        capture_output=True,
    )


def version() -> str | None:
    """
    Get the installed version of IG Publisher, returns None if not installed
    """

    try:
        res = java.run_jar(PUBLISHER_JAR, "-v", capture_output=True)

        return res.stdout_oneline if res.stdout_oneline else None

    except shell.CalledProcessError:
        return None


__tool_name__ = "IG Publisher"
