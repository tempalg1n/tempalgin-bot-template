from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram_dialog import DialogManager
from markdown import markdown

from src.db import Database
from src.db.models import User


async def answer_getter(dialog_manager: DialogManager, **kwargs):
    content: str = dialog_manager.dialog_data.get('content')
    if content:
        dialog_manager.dialog_data['lock'] = False
        dialog_manager.dialog_data['content'] = None
        content = markdown(content)
    else:
        bot: Bot = dialog_manager.middleware_data['bot']
        await bot.send_chat_action(dialog_manager.event.from_user.id, ChatAction.TYPING)
    cost: int = dialog_manager.dialog_data.get('cost')
    if cost:
        user: User = dialog_manager.middleware_data['user_object']
        if user.balance > cost:
            user.balance -= cost
        else:
            user.balance = 0
            dialog_manager.dialog_data['no_tokens'] = True
            dialog_manager.dialog_data['lock'] = True
    error: bool = dialog_manager.dialog_data.get('error')
    prompt: str = dialog_manager.dialog_data.get('prompt')
    if error:
        content = 'ℹ️'
        dialog_manager.dialog_data['content'] = 'error'
    result: dict = {
        'content': content,
        'error': error,
        'prompt': prompt
    }
    db: Database = dialog_manager.middleware_data['db']
    await db.session.commit()
    return result
