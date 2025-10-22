from .strict_base_model import StrictBaseModel


class BuildBuiltinEpaToolsConfig(StrictBaseModel):
    cap_statements: bool = False
    openapi: bool = False


class BuildBuiltinConfig(StrictBaseModel):
    igtools: bool = False
    epatools: BuildBuiltinEpaToolsConfig | bool = False


class BuildConfig(StrictBaseModel):
    builtin: BuildBuiltinConfig = BuildBuiltinConfig()
