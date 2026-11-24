from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Impianto(Base):
    __tablename__ = "impianti"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_impianto: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    gestore: Mapped[str] = mapped_column(String(120), default="")
    bandiera: Mapped[str] = mapped_column(String(120), default="", index=True)
    tipo_impianto: Mapped[str] = mapped_column(String(80), default="")
    nome: Mapped[str] = mapped_column(String(160), default="")
    indirizzo: Mapped[str] = mapped_column(String(240), default="")
    comune: Mapped[str] = mapped_column(String(120), index=True)
    provincia: Mapped[str] = mapped_column(String(8), index=True)
    latitudine: Mapped[float | None] = mapped_column()
    longitudine: Mapped[float | None] = mapped_column()

    prices: Mapped[list["Prezzo"]] = relationship(
        back_populates="impianto", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Segnalazione"]] = relationship(
        back_populates="impianto", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Preferito"]] = relationship(
        back_populates="impianto", cascade="all, delete-orphan"
    )


class Preferito(Base):
    __tablename__ = "preferiti"
    __table_args__ = (UniqueConstraint("id_utente", "id_impianto"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    id_utente: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    id_impianto: Mapped[int] = mapped_column(
        ForeignKey("impianti.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(back_populates="favorites")
    impianto: Mapped["Impianto"] = relationship(back_populates="favorites")
