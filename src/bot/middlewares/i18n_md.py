from typing import Dict, Callable, Any, Awaitable, Union

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from src.bot.logic.dialogs.translation.i18n_format import I18N_FORMAT_KEY
from src.db.models import User


class I18nMiddleware(BaseMiddleware):
    def __init__(
            self,
            l10ns: Dict[str, FluentLocalization],
            default_lang: str,
    ):
        super().__init__()
        self.l10ns = l10ns
        self.default_lang = default_lang

    async def __call__(
            self,
            handler: Callable[
                [Union[Message, CallbackQuery], Dict[str, Any]],
                Awaitable[Any],
            ],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any],
    ) -> Any:
        # some language/locale retrieving logic
        user: User = data['user_object']
        lang = user.language_code
        if lang not in self.l10ns:
            lang = self.default_lang
        else:
            lang = self.default_lang
        if lang not in self.l10ns:
            lang = self.default_lang

        l10n = self.l10ns[lang]
        # we use fluent.runtime here, but you can create custom functions
        data[I18N_FORMAT_KEY] = l10n.format_value

        return await handler(event, data)
