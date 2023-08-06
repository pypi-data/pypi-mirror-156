from typing import Dict, Optional, Union

from pydantic import BaseModel, Extra, Field, validator


class Price(BaseModel):
    cents: int
    currency: str
    currency_symbol: str
    formatted: str

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("currency", "currency_symbol", "formatted", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None


class Expansion(BaseModel):
    code: str
    id_: int = Field(alias="id")
    expansion_id: int = Field(alias="id")
    name: str = Field(alias="name_en")

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("code", "name", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None


class User(BaseModel):
    can_sell_sealed_with_ct_zero: bool
    can_sell_via_hub: bool
    country_code: str
    id_: int = Field(alias="id")
    user_id: int = Field(alias="id")
    too_many_request_for_cancel_as_seller: bool
    user_type: str
    username: str
    max_sellable_in24h_quantity: Optional[int] = Field(default=None)

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("country_code", "user_type", "username", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None


class Product(BaseModel):
    blueprint_id: int
    bundle_size: int
    expansion: Expansion
    id_: int = Field(alias="id")
    product_id: int = Field(alias="id")
    name: str = Field(alias="name_en")
    on_vacation: bool
    price: Price
    price_cents: int
    price_currency: str
    quantity: int
    seller: User = Field(alias="user")
    description: Optional[str] = Field(default=None)
    graded: Optional[bool] = Field(default=None)
    layered_price_cents: Optional[int] = Field(default=None)
    properties: Dict[str, Optional[Union[str, bool]]] = Field(
        alias="properties_hash", default_factory=dict
    )
    tag: Optional[str] = Field(default=None)

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("name", "price_currency", "description", "tag", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None
