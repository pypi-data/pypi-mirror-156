from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Extra, Field, validator


class Property(BaseModel):
    name: str
    type_: str = Field(alias="type")
    property_type: str = Field(alias="type")
    default_value: Optional[str] = Field(default=None)
    possible_values: List[Union[str, bool]] = Field(default_factory=list)

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("name", "type_", "property_type", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None


class Blueprint(BaseModel):
    category_id: int
    expansion_id: int
    game_id: int
    id_: int = Field(alias="id")
    blueprint_id: int = Field(alias="id")
    image_url: str
    name: str
    card_market_id: Optional[int] = Field(default=None)
    editable_properties: List[Property] = Field(default_factory=list)
    fixed_properties: Dict[str, str] = Field(default_factory=dict)
    scryfall_id: Optional[str] = Field(default=None)
    tcg_player_id: Optional[int] = Field(default=None)
    version: Optional[str] = Field(default=None)

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("image_url", "name", "scryfall_id", "version", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None
