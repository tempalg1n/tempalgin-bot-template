import asyncio
from typing import Any

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, BaseDialogManager
from openai.types.beta import Thread

from src.bot.logic.tasks.gpt import get_answer, process_user_input
from src.bot.structures.FSM.dialog_fsm import AssistantSG
from src.configuration import conf
from src.db import Database
from src.db.models import User
from src.gpt.client import GPT


async def resolve_user_state(manager: DialogManager):
    if manager.current_context().state == AssistantSG.init:
        await manager.switch_to(AssistantSG.conversation)


async def start_designer_thread_text_handler(
        message: Message, widget: Any, manager: DialogManager, **kwargs
):
    user: User = manager.middleware_data['user']
    if user.balance <= 0:
        await message.reply('Похоже, у вас не хватает токенов 🤷‍♂️')
        # await manager.start(PaymentSG.choose_amount, mode=StartMode.RESET_STACK)
        return
    db: Database = manager.middleware_data['db']
    gpt: GPT = manager.middleware_data['gpt']
    bot: Bot = manager.middleware_data['bot']
    assistant: str = conf.openai.tekla_assistant
    manager.dialog_data['assistant'] = assistant
    thread: Thread = await gpt.create_thread()
    manager.dialog_data['thread'] = thread.id
    await db.thread.new(
        thread_id=thread.id,
        user=user
    )
    bg_manager: BaseDialogManager = manager.bg(load=True)
    manager.dialog_data['lock'] = True
    condition: asyncio.Condition = asyncio.Condition()
    asyncio.gather(
        get_answer(
            assistant_id=assistant,
            thread_id=thread.id,
            bg_manager=bg_manager,
            condition=condition
        ),
        process_user_input(
            message=message,
            bot=bot,
            condition=condition,
            thread=thread.id
        )
    )
    await manager.next()
    await bot.send_chat_action(manager.event.from_user.id, ChatAction.TYPING)


async def user_text_handler(
        message: Message, widget: Any, manager: DialogManager, **kwargs
):
    bot: Bot = manager.middleware_data['bot']
    manager.dialog_data['prompt'] = None
    assistant_id: str = manager.dialog_data.get('assistant') or manager.start_data['assistant']
    thread_id: str = manager.dialog_data.get('thread') or manager.start_data['thread']
    lock: bool = bool(manager.dialog_data.get('lock'))

    if lock:
        no_tokens: bool = bool(manager.dialog_data.get('no_tokens'))
        if no_tokens:
            await message.reply('Похоже, у вас не хватает токенов 🤷‍♂️')
            return
        await message.reply('⏳ Подождите, пока бот обработает ваш ответ')
        return

    # await resolve_user_state(manager)
    bg_manager: BaseDialogManager = manager.bg(load=True)
    manager.dialog_data['lock'] = True
    await bot.send_chat_action(manager.event.from_user.id, ChatAction.TYPING)
    condition: asyncio.Condition = asyncio.Condition()
    asyncio.gather(
        get_answer(
            assistant_id=assistant_id,
            thread_id=thread_id,
            bg_manager=bg_manager,
            condition=condition
        ),
        process_user_input(
            message=message,
            bot=bot,
            condition=condition,
            thread=thread_id
        )
    )
