from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format
from sulguk import SULGUK_PARSE_MODE

from src.bot.structures.FSM.dialog_fsm import AssistantSG
from src.bot.utils.translation.i18n_format import I18NFormat

assistant_init_window = Window(
    I18NFormat('Tekla-init-window'),
    MessageInput(start_designer_thread_text_handler, content_types=[ContentType.TEXT, ContentType.VOICE]),
    state=AssistantSG.init,
    parse_mode=SULGUK_PARSE_MODE,
)

conversation_window = Window(
    Format('{content}', when='content'),
    I18NFormat('Error', when='error'),
    I18NFormat('Wait', when=~F['content']),
    MessageInput(
        user_text_handler,
        content_types=[ContentType.TEXT, ContentType.VOICE],
    ),
    getter=answer_getter,
    state=AssistantSG.conversation,
    parse_mode=SULGUK_PARSE_MODE,
)