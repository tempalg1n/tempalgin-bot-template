from aiogram import Router
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Button, Cancel

from src.bot.logic.dialogs.start.getter import get_data
from src.bot.structures.FSM.dialog_fsm import DialogSG
from src.bot.utils.translation.i18n_format import I18NFormat

dialog = Dialog(
    Window(
        I18NFormat("Hello-user"),
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
