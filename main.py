import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from database.base import init_db
from handlers.handlers_other import other_router
from handlers.handlers_player import player_router
from handlers.handlers_host import host_router

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Инициализируем базу данных
    await init_db()

    # Регистрируем роутеры в диспетчере
    dp.include_router(host_router)
    dp.include_router(player_router)
    dp.include_router(other_router)

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("Bot started successfully.")
