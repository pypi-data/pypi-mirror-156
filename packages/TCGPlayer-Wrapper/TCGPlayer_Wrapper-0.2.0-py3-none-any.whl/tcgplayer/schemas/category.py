from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    category_id: int = Field(alias="categoryId")
    name: str
    modified_on: datetime = Field(alias="modifiedOn")
    display_name: str = Field(alias="displayName")
    seo_category_name: str = Field(alias="seoCategoryName")
    sealed_label: Optional[str] = Field(alias="sealedLabel", default=None)
    non_sealed_label: Optional[str] = Field(alias="nonSealedLabel", default=None)
    condition_guide_url: str = Field(alias="conditionGuideUrl")
    is_scannable: bool = Field(alias="isScannable", default=False)
    popularity: int
    is_direct: bool = Field(alias="isDirect", default=False)

    def __init__(self, **data):
        if "." in (modified_on := data["modifiedOn"]):
            data["modifiedOn"] = modified_on[: modified_on.rindex(".")]
        super().__init__(**data)
