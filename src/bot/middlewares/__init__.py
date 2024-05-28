"""This package is used for middlewares."""
from src.bot.middlewares.database_md import DatabaseMiddleware
from src.bot.middlewares.register_md import RegisterCheck

middlewares = (
    DatabaseMiddleware(),
    RegisterCheck(),
)
