from pydantic import BaseModel, ConfigDict, Field


class TestData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    password: str | None = None
    phone: str | None = None


class Requirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: str = Field(min_length=1)
    test_data: TestData | None = None


class BusinessChecklist(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project: dict[str, str]
    requirements: list[Requirement] = Field(min_length=1)