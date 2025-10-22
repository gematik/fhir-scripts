from pathlib import Path

from .strict_base_model import StrictBaseModel


class BuildBuiltinEpaToolsConfig(StrictBaseModel):
    cap_statements: bool = False
    openapi: bool = False
    archive_files: list[Path] = []


class BuildBuiltinConfig(StrictBaseModel):
    igtools: bool = False
    epatools: BuildBuiltinEpaToolsConfig | bool = False


class BuildConfig(StrictBaseModel):
    builtin: BuildBuiltinConfig = BuildBuiltinConfig()
