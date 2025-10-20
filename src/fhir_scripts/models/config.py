from pathlib import Path

from pydantic import BaseModel


class BuildStepDefsConfig(BaseModel):
    requirements: bool = False
    cap_statements: bool = False


class BuildStepIgConfig(BaseModel):
    openapi: bool = False


class BuildStepConfig(BaseModel):
    definitions: BuildStepDefsConfig = BuildStepDefsConfig()
    ig: BuildStepIgConfig = BuildStepIgConfig()


class BuildConfig(BaseModel):
    steps: BuildStepConfig = BuildStepConfig()


class DeployConfig(BaseModel):
    env: dict[str, str]
    path: str | None = None


class EpaToolsArchiveConfig(BaseModel):
    content_files: list[Path]


class EpaToolsConfig(BaseModel):
    archive: EpaToolsArchiveConfig


class Config(BaseModel):
    deploy: DeployConfig | None = None
    epatools: EpaToolsConfig | None = None
    build: BuildConfig = BuildConfig()
