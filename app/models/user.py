from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, Enum):
    AUTOMOBILISTA = "automobilista"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(80))
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[UserRole] = mapped_column(default=UserRole.AUTOMOBILISTA)

    reports: Mapped[list["Segnalazione"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Preferito"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
