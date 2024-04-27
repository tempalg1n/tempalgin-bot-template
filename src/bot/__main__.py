"""This file represent startup bot logic."""
import asyncio
import logging

from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram_dialog import setup_dialogs

from redis.asyncio.client import Redis
from src.bot.dispatcher import get_dispatcher, get_redis_storage, make_i18n_middleware
from src.bot.middlewares.database_md import DatabaseMiddleware
from src.bot.middlewares.i18n_md import I18nMiddleware
from src.bot.middlewares.register_md import RegisterCheck
from src.bot.structures.data_structure import TransferData
from src.configuration import conf
from src.db.database import create_async_engine

COMMANDS = {
    'profile': 'My account',
    'help': 'Get additional info',
}


def register_middlewares(dp) -> None:
    i18n_middleware: I18nMiddleware = make_i18n_middleware()

    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)

    dp.callback_query.outer_middleware(DatabaseMiddleware())
    dp.message.outer_middleware(DatabaseMiddleware())

    dp.callback_query.outer_middleware(RegisterCheck())
    dp.message.outer_middleware(RegisterCheck())


async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
    description in COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)


async def start_bot():
    """This function will start bot with polling mode."""
    bot = Bot(token=conf.bot.token)
    storage = get_redis_storage(
        redis=Redis(
            db=conf.redis.db,
            host=conf.redis.host,
            password=conf.redis.passwd,
            username=conf.redis.username,
            port=conf.redis.port,
        )
    )
    dp = get_dispatcher(storage=MemoryStorage())

    register_middlewares(dp)
    setup_dialogs(dp)

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        **TransferData(
            engine=create_async_engine(url=conf.db.build_connection_str())
        )
    )


if __name__ == '__main__':
    logging.basicConfig(level=conf.logging_level)
    asyncio.run(start_bot())
