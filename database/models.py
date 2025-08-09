from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all models."""


class Game(Base):
    """Model representing a game course."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    host_telegram_id: Mapped[int] = mapped_column(Integer)
    days_played: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_code: Mapped[str] = mapped_column(String(16), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Player(Base):
    """Model representing a registered player."""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    registration_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    name: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(100))
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False)
