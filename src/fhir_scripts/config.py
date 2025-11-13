from pathlib import Path

import yaml

from .models.config import Config


def load(config_path: Path | None = None):
    """
    Load config

    Read values from a config file. If no `config_path` is provided or it is `None`, the default is `./config.yaml`.

    If the file does not exists, the values are initialized with defaults.
    """
    config_file = config_path or Path("./fhirscripts.config.yaml")

    # Read an existing config
    config_file_contents = (
        yaml.safe_load(config_file.read_text("utf-8")) if config_file.exists() else {}
    )

    return Config.model_validate(config_file_contents)
