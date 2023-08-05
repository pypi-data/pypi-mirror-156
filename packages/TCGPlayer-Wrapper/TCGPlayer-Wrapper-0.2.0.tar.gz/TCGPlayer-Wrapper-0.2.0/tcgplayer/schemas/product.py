from datetime import datetime

from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: int = Field(alias="productId")
    name: str
    clean_name: str = Field(alias="cleanName")
    image_url: str = Field(alias="imageUrl")
    category_id: int = Field(alias="categoryId")
    group_id: int = Field(alias="groupId")
    url: str
    modified_on: datetime = Field(alias="modifiedOn")

    def __init__(self, **data):
        if "." in (modified_on := data["modifiedOn"]):
            data["modifiedOn"] = modified_on[: modified_on.rindex(".")]
        super().__init__(**data)
