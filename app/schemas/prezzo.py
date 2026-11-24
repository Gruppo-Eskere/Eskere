from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriceInput(BaseModel):
    id_impianto: str = Field(min_length=1, max_length=64)
    carburante: str = Field(min_length=1, max_length=60)
    prezzo: Decimal = Field(gt=0, le=10, decimal_places=3)
    is_self: bool = True
    data_comunicazione: datetime | None = None

    @field_validator("carburante")
    @classmethod
    def normalize_fuel(cls, value: str) -> str:
        return value.strip()


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    carburante: str
    prezzo: Decimal
    is_self: bool
    data_comunicazione: datetime
