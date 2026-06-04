from .strict_base_model import StrictBaseModel


class MultiIGEntryConfig(StrictBaseModel):
    path: str


class MultiIGConfig(StrictBaseModel):
    version: int = 1
    igsRoot: str = "igs"
    igs: dict[str, MultiIGEntryConfig] | None = None
