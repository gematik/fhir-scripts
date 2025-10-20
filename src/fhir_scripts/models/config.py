from pathlib import Path

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BuildStepDefsConfig(StrictBaseModel):
    requirements: bool = False
    cap_statements: bool = False


class BuildStepIgConfig(StrictBaseModel):
    openapi: bool = False


class BuildStepConfig(StrictBaseModel):
    definitions: BuildStepDefsConfig = BuildStepDefsConfig()
    ig: BuildStepIgConfig = BuildStepIgConfig()


class BuildConfig(StrictBaseModel):
    steps: BuildStepConfig = BuildStepConfig()


class DeployConfig(StrictBaseModel):
    env: dict[str, str]
    path: str | None = None


class EpaToolsArchiveConfig(StrictBaseModel):
    content_files: list[Path]


class EpaToolsConfig(StrictBaseModel):
    archive: EpaToolsArchiveConfig


class Config(StrictBaseModel):
    deploy: DeployConfig | None = None
    epatools: EpaToolsConfig | None = None
    build: BuildConfig = BuildConfig()
