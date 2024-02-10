import logging
import sys
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import settings
from app.handlers.yd_loader import register_handlers_yd_loader
from app.handlers.common import register_handlers_common


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/cancel", description="Отменить текущее действие"),
        BotCommand(command="/start", description="Начать по новой")
    ]
    await bot.set_my_commands(commands)
async def main():
    # Настройка логирования в stdout
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=settings.TG_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_yd_loader(dp, bot)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())

