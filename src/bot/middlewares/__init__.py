"""This package is used for middlewares."""
from src.bot.middlewares.chat_type_md import ChatTypeMiddleware
from src.bot.middlewares.database_md import DatabaseMiddleware
from src.bot.middlewares.register_md import RegisterCheck

middlewares = (
    DatabaseMiddleware(),
    RegisterCheck(),
    ChatTypeMiddleware()
)
