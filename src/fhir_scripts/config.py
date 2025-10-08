from pydantic import BaseModel


class DeployConfig(BaseModel):
    env: dict[str, str]
    path: str | None = None


class Config(BaseModel):
    deploy: DeployConfig | None = None
