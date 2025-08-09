import secrets
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game


async def create_course(
    session: AsyncSession,
    host_id: int,
    name: str,
    description: str,
) -> Game:
    """Create a new course and persist it to the database."""
    registration_code = secrets.token_hex(4)
    course = Game(
        name=name,
        description=description,
        host_telegram_id=host_id,
        registration_code=registration_code,
        created_at=datetime.utcnow(),
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course
