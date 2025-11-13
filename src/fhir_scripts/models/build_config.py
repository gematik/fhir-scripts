from pathlib import Path

from .strict_base_model import StrictBaseModel


class BuildBuiltinEpaToolsConfig(StrictBaseModel):
    cap_statements: bool = False
    openapi: bool = False


class BuildBuiltinConfig(StrictBaseModel):
    igtools: bool = False
    epatools: BuildBuiltinEpaToolsConfig | bool = False


class BuildPipelineShellStep(StrictBaseModel):
    shell: str


class BuildArgsOpenApi(StrictBaseModel):
    additional_archive: list[Path] = []


class BuildArgsConfig(StrictBaseModel):
    openapi: BuildArgsOpenApi = BuildArgsOpenApi()


class BuildConfig(StrictBaseModel):
    builtin: BuildBuiltinConfig = BuildBuiltinConfig()
    pipeline: list[str | BuildPipelineShellStep] = []
    args: BuildArgsConfig = BuildArgsConfig()
