from aiogram import Router
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Button, Cancel

from src.bot.logic.getters.start import get_data
from src.bot.middlewares.i18n_format import I18NFormat
from src.bot.structures.FSM.dialog_fsm import DialogSG

dialog = Dialog(
    Window(
        I18NFormat("hello"),
        Row(
            Button(I18NFormat("Demo-button"), id="demo"),
            Cancel(text=I18NFormat("Cancel")),
        ),
        getter=get_data,
        state=DialogSG.greeting,
    )
)

dialog_router = Router()
dialog_router.include_routers(
    dialog
)
