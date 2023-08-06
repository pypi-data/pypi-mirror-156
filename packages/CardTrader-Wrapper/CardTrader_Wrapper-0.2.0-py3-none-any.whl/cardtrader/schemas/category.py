from typing import List, Union

from pydantic import BaseModel, Extra, Field, validator


class Property(BaseModel):
    name: str
    type_: str = Field(alias="type")
    property_type: str = Field(alias="type")
    possible_values: List[Union[str, bool]] = Field(default_factory=list)

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("name", "type", "property_type", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None


class Category(BaseModel):
    game_id: int
    id_: int = Field(alias="id")
    category_id: int = Field(alias="id")
    name: str
    properties: List[Property] = Field(default_factory=list)

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("name", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None
