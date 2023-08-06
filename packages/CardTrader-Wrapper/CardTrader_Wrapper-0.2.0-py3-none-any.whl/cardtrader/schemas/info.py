from pydantic import BaseModel, Extra, Field, validator


class Info(BaseModel):
    id_: int = Field(alias="id")
    info_id: int = Field(alias="id")
    name: str
    shared_secret: str

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    @validator("name", "shared_secret", pre=True, check_fields=False)
    def remove_blank_strings(cls, value: str):
        if value:
            return value
        return None
