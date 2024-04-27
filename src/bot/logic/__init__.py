"""This package is used for a bot logic implementation."""
from src.bot.logic.dialogs.start.dialog import dialog_router
from src.bot.logic.handlers.help import help_router
from src.bot.logic.handlers.start import start_router

routers = (
    start_router,
    help_router,
    dialog_router
)
