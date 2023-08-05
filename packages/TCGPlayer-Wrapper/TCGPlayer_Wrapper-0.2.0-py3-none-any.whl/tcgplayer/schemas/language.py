from pydantic import BaseModel, Field


class Language(BaseModel):
    language_id: int = Field(alias="languageId")
    name: str
    abbreviation: str = Field(alias="abbr")
