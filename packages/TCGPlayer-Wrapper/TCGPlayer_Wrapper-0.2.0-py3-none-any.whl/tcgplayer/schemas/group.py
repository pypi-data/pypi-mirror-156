from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class Group(BaseModel):
    group_id: int = Field(alias="groupId")
    name: str
    abbreviation: Optional[str] = Field(default=None)
    is_supplemental: bool = Field(alias="isSupplemental", default=False)
    published_on: date = Field(alias="publishedOn")
    modified_on: datetime = Field(alias="modifiedOn")
    category_id: int = Field(alias="categoryId")

    def __init__(self, **data):
        if "T" in (published_on := data["publishedOn"]):
            data["publishedOn"] = published_on[: published_on.index("T")]
        if "." in (modified_on := data["modifiedOn"]):
            data["modifiedOn"] = modified_on[: modified_on.rindex(".")]
        super().__init__(**data)
