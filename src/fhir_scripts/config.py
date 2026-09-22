import os
from pathlib import Path

import yaml
from dotenv import dotenv_values

from .models.config import Config

ENV_PREFIX = "FHIRSCRIPTS_"


def load(config_path: Path | None = None):
    """
    Load config

    Read values from a config file. If no `config_path` is provided or it is `None`, the default is
    `./fhirscripts.config.yaml`.

    If the file does not exists, the values are initialized with defaults.
    """
    config_file = config_path or Path("./fhirscripts.config.yaml")

    # Read an existing config
    config_file_contents = (
        yaml.safe_load(config_file.read_text("utf-8")) if config_file.exists() else {}
    )

    return Config.model_validate(config_file_contents)


def load_dot_env():
    """
    Loads variables from `.env` files and environment variables. They read in the order and later read override
    provious values:

    * `.env` file in user home
    * `.env` file in current directory
    * environment variable
    """
    config = {
        **dotenv_values(Path.home() / ".env"),
        **dotenv_values(Path.cwd() / ".env"),
        **os.environ,
    }

    config = {
        k[len(ENV_PREFIX) :]: v for k, v in config.items() if k.startswith(ENV_PREFIX)
    }

    return config
