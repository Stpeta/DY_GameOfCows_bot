from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot) -> None:
    commands = [
        BotCommand(command='/start', description='Start bot'),
        BotCommand(command='/newgame', description='Create new game'),
        BotCommand(command='/join', description='Join a game'),
    ]
    await bot.set_my_commands(commands)
