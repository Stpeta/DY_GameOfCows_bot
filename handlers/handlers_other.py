from aiogram import Router
from aiogram.types import Message

other_router = Router()


@other_router.message()
async def other_message(message: Message):
    await message.answer('Unknown command.')
