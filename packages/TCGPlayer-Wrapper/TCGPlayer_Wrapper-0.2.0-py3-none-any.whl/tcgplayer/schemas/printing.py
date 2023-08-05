from datetime import datetime

from pydantic import BaseModel, Field


class Printing(BaseModel):
    printing_id: int = Field(alias="printingId")
    name: str
    display_order: int = Field(alias="displayOrder")
    modified_on: datetime = Field(alias="modifiedOn")

    def __init__(self, **data):
        if "." in (modified_on := data["modifiedOn"]):
            data["modifiedOn"] = modified_on[: modified_on.rindex(".")]
        super().__init__(**data)
