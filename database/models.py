from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all models."""


class Game(Base):
    """Model representing a game."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    host_telegram_id: Mapped[int] = mapped_column(Integer)
    days_played: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_code: Mapped[str] = mapped_column(String(16), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    degradation_coeff: Mapped[float] = mapped_column(Float, default=1.0)
    recovery_coeff: Mapped[float] = mapped_column(Float, default=1.0)


class Player(Base):
    """Model representing a registered player."""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    registration_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    name: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(100))
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[int] = mapped_column(Integer, default=0)


class PlayerMove(Base):
    """Daily player moves (grazing hours and earned coins)."""

    __tablename__ = "player_moves"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    day_number: Mapped[int] = mapped_column(Integer)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    hours: Mapped[int] = mapped_column(Integer)
    coins: Mapped[int] = mapped_column(Integer, default=0)


class FieldState(Base):
    """Field level history for each day."""

    __tablename__ = "field_states"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    day_number: Mapped[int] = mapped_column(Integer)
    field_level: Mapped[float] = mapped_column(Float)
    degradation_coeff: Mapped[float] = mapped_column(Float)
    recovery_coeff: Mapped[float] = mapped_column(Float)
