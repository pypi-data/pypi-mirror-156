from pydantic import BaseModel, Extra, Field, validator


class Expansion(BaseModel):
    code: str
    game_id: int
    id_: int = Field(alias="id")
    expansion_id: int = Field(alias="id")
    name: str

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("code", "name", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None
