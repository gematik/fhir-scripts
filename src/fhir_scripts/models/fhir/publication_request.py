from enum import Enum

from pydantic import AliasChoices, AnyUrl, BaseModel, Field


class PublicationRequestMode(str, Enum):
    working = "working"
    milestone = "milestone"
    technical_correction = "technical-correction"
    withdrawal = "withdrawal"


class PublicationRequestStatus(str, Enum):
    release = "release"
    trial_use = "trial-use"
    update = "update"
    preview = "preview"
    ballot = "ballot"
    draft = "draft"
    normative_trial_use = "normative+trial-use"
    normative = "normative"
    informative = "informative"


class PublicationRequest(BaseModel):
    # for reference see https://confluence.hl7.org/spaces/FHIR/pages/144970227/IG+Publication+Request+Documentation
    package_id: str = Field(
        serialization_alias="package-id",
        validation_alias=AliasChoices("package-id", "package_id"),
    )
    version: str
    path: AnyUrl
    mode: PublicationRequestMode
    status: PublicationRequestStatus
    sequence: str
    desc: str | None = None  # optional
    descmd: str | None = None  # optional
    changes: str | None = None
    first: bool
    title: str | None = None  # only for first release
    ci_build: str | None = Field(
        serialization_alias="ci-build",
        validation_alias=AliasChoices("ci-build", "ci_build"),
        default=None,
    )  # only for first release
    registry_description: str | None = Field(
        serialization_alias="registry-description",
        validation_alias=AliasChoices("registry-description", "registry_description"),
        default=None,
    )
    registry_country: str | None = Field(
        serialization_alias="registry-country",
        validation_alias=AliasChoices("registry-country", "registry_country"),
        pattern=r"^[A-Z]{2}$",
        default=None,
    )  # only for first release
    registry_authority: str | None = Field(
        serialization_alias="registry-authority",
        validation_alias=AliasChoices("registry-authority", "registry_authority"),
        default=None,
    )  # only for first release
    category: str | None = None  # only for first release
    introduction: str | None = None  # only for first release
    replacement: AnyUrl | None = None  # only if withdrawing, optional
