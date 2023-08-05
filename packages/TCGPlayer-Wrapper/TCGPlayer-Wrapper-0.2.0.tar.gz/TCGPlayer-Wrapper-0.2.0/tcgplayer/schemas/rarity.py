from pydantic import BaseModel, Field


class Rarity(BaseModel):
    rarity_id: int = Field(alias="rarityId")
    display_text: str = Field(alias="displayText")
    db_value: str = Field(alias="dbValue")
