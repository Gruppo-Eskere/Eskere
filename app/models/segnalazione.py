from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReportStatus(str, Enum):
    PENDING = "in_attesa"
    APPROVED = "approvata"
    REJECTED = "rifiutata"


class Segnalazione(Base):
    __tablename__ = "segnalazioni"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_impianto: Mapped[int] = mapped_column(
        ForeignKey("impianti.id", ondelete="CASCADE"), index=True
    )
    id_utente: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    testo_libero: Mapped[str] = mapped_column(Text)
    stato: Mapped[ReportStatus] = mapped_column(default=ReportStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    impianto: Mapped["Impianto"] = relationship(back_populates="reports")
    user: Mapped["User"] = relationship(back_populates="reports")
