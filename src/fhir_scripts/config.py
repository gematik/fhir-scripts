from pathlib import Path

from pydantic import BaseModel


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
