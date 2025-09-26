from pydantic import BaseModel


class DeployConfig(BaseModel):
    env: dict[str, str]
    path: str


class Config(BaseModel):
    deploy: DeployConfig
