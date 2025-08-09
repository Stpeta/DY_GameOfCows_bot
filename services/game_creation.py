import secrets
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game, FieldState


async def create_game(
    session: AsyncSession,
    host_id: int,
    name: str,
    description: str,
    degradation_coeff: float,
    recovery_coeff: float,
) -> Game:
    """Create a new game and persist it to the database."""
    registration_code = secrets.token_hex(4)
    game = Game(
        name=name,
        description=description,
        host_telegram_id=host_id,
        registration_code=registration_code,
        created_at=datetime.utcnow(),
        degradation_coeff=degradation_coeff,
        recovery_coeff=recovery_coeff,
        days_played=0,
    )
    session.add(game)
    await session.commit()
    await session.refresh(game)
    session.add(
        FieldState(
            game_id=game.id,
            day_number=0,
            field_level=100.0,
            degradation_coeff=degradation_coeff,
            recovery_coeff=recovery_coeff,
        )
    )
    await session.commit()
    return game

