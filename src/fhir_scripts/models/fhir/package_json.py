from pydantic import AliasChoices, BaseModel, Field


class PackageJson(BaseModel):
    version: str
    fhir_versions: list[str] = Field(
        serialization_alias="fhirVersions",
        validation_alias=AliasChoices("fhirVersions", "fhir_versions"),
        default=[],
    )
    dependencies: dict[str, str] = {}
    name: str
