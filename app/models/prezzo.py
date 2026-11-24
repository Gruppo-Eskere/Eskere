from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Prezzo(Base):
    __tablename__ = "prezzi"
    __table_args__ = (
        Index("ix_prezzi_carburante_prezzo", "carburante", "prezzo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_impianto: Mapped[int] = mapped_column(
        ForeignKey("impianti.id", ondelete="CASCADE"), index=True
    )
    carburante: Mapped[str] = mapped_column(String(60), index=True)
    prezzo: Mapped[Decimal] = mapped_column(Numeric(7, 3))
    is_self: Mapped[bool] = mapped_column(Boolean, default=True)
    data_comunicazione: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    impianto: Mapped["Impianto"] = relationship(back_populates="prices")
