from pydantic import BaseModel, Field


class Condition(BaseModel):
    condition_id: int = Field(alias="conditionId")
    name: str
    abbreviation: str
    display_order: int = Field(alias="displayOrder")
