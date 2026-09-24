from datetime import date as date_type
from enum import Enum

from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class SushiConfigStatus(str, Enum):
    draft = "draft"
    active = "active"
    retired = "retired"
    unknown = "unknown"


class SushiConfigPublisher(BaseModel):
    name: str
    url: AnyUrl
    email: str


class SushiConfig(BaseModel):
    # for reference see https://fshschool.org/docs/sushi/configuration/
    id: str
    canonical: AnyUrl
    name: str
    title: str | None = None
    description: str | None = None
    status: SushiConfigStatus
    license: str | None = None
    version: str
    date: date_type | None = None
    fhir_version: str = Field(
        serialization_alias="fhirVersion",
        validation_alias=AliasChoices("fhirVersion", "fhir_version"),
    )
    copyright_year: str = Field(
        serialization_alias="copyrightYear",
        validation_alias=AliasChoices("copyrightYear", "copyright_year"),
    )
    release_label: str = Field(
        serialization_alias="releaseLabel",
        validation_alias=AliasChoices("releaseLabel", "release_label"),
    )
    publisher: SushiConfigPublisher | None = None
    dependencies: dict[str, str] | None = (
        None  # last can be version, "dev", "current", "current$branchname", "latest"
    )
