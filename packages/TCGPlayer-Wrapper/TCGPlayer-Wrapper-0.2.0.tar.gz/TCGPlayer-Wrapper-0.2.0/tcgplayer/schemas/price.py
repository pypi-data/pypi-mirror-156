from typing import Optional

from pydantic import BaseModel, Field


class Price(BaseModel):
    product_id: int = Field(alias="productId")
    low_price: Optional[float] = Field(alias="lowPrice", default=None)
    mid_price: Optional[float] = Field(alias="midPrice", default=None)
    high_price: Optional[float] = Field(alias="highPrice", default=None)
    market_price: Optional[float] = Field(alias="marketPrice", default=None)
    direct_low_price: Optional[float] = Field(alias="directLowPrice", default=None)
    sub_type_name: str = Field(alias="subTypeName")
