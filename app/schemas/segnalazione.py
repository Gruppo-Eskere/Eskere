from pydantic import BaseModel, Field


class ReportInput(BaseModel):
    testo_libero: str = Field(min_length=5, max_length=2000)
