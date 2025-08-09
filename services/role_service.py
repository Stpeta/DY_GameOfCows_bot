from sqlalchemy import select
from config_data.config import load_config
from database.base import AsyncSessionLocal
from database.models import Game

config = load_config()


async def get_user_role(telegram_id: int) -> str:
    """
    Возвращает одну из ролей: "host" | "player" | "guest".
    """
    # Сначала проверяем, host ли пользователь
    if telegram_id in config.tg_bot.host_ids:
        return "host"

    # Иначе — ищем в таблице participants
    async with AsyncSessionLocal() as session:
        part = await session.execute(
            select(Player).where(Participant.telegram_id == telegram_id)
        )
        part = part.scalars().first()

    if part and part.is_registered:
        return "participant"
    return "guest"
