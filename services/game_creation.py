import secrets
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game


async def create_game(
    session: AsyncSession,
    host_id: int,
    name: str,
    description: str,
) -> Game:
    """Create a new game and persist it to the database."""
    registration_code = secrets.token_hex(4)
    game = Game(
        name=name,
        description=description,
        host_telegram_id=host_id,
        registration_code=registration_code,
        created_at=datetime.utcnow(),
    )
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return game

