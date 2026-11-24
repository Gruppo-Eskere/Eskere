from pydantic import BaseModel, Field


class ImpiantoInput(BaseModel):
    id_impianto: str = Field(min_length=1, max_length=64)
    gestore: str = Field(default="", max_length=120)
    bandiera: str = Field(default="", max_length=120)
    tipo_impianto: str = Field(default="", max_length=80)
    nome: str = Field(default="", max_length=160)
    indirizzo: str = Field(default="", max_length=240)
    comune: str = Field(min_length=1, max_length=120)
    provincia: str = Field(min_length=2, max_length=8)
    latitudine: float | None = Field(default=None, ge=-90, le=90)
    longitudine: float | None = Field(default=None, ge=-180, le=180)
