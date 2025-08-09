from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config_data.config import load_config
from lexicon.lexicon_en import LEXICON_EN

config = load_config()
HOST_IDS = config.tg_bot.host_ids

other_router = Router()


@other_router.message(CommandStart())
async def user_start(message: Message) -> None:
    if message.from_user.id in HOST_IDS:
        return
    await message.answer(LEXICON_EN["ask_registration_code"])
