from .build_config import BuildConfig
from .strict_base_model import StrictBaseModel


class DeployConfig(StrictBaseModel):
    env: dict[str, str]
    path: str | None = None


class Config(StrictBaseModel):
    deploy: DeployConfig | None = None
    build: BuildConfig = BuildConfig()
