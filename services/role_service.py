from sqlalchemy import select

from config_data.config import load_config
from database.base import AsyncSessionLocal
from database.models import Player

config = load_config()


async def get_user_role(telegram_id: int) -> str:
    """Return one of roles: "host" | "player" | "guest"."""

    # Host users are defined in configuration
    if telegram_id in config.tg_bot.host_ids:
        return "host"

    # Otherwise, check player registrations
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == telegram_id)
        )
        player = result.scalars().first()

    if player and player.is_registered:
        return "player"
    return "guest"
