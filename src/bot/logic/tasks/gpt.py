import asyncio
import io
import logging

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import Message
from aiogram_dialog import BaseDialogManager
from openai.pagination import AsyncCursorPage
from openai.types.beta.threads import Run

from src.bot.structures.enums import GPTModel, RunStatus
from src.configuration import conf
from src.gpt.client import GPT, RunResponse


logger = logging.getLogger(__name__)


async def filter_text_from_entities(bot: Bot, message: Message) -> str:
    bot_username: str = (await bot.get_me()).username
    result: str = message.text.replace(f'@{bot_username}', '').strip()
    return result


async def get_user_input(message: Message, bot: Bot):
    gpt: GPT = GPT(api_key=conf.openai.api_key, model=GPTModel.OMNI)
    if message.voice:
        await bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_VOICE)
        try:
            buffer = io.BytesIO()
            await bot.download(message.voice, destination=buffer)
            buffer.seek(0)
            buffer.name = 'voice.mp3'
            transcript: str = await gpt.translate_voice(buffer)
            buffer.close()
            text: str = transcript
        except Exception as e:
            logger.critical(f"Couldn't read user input: {e}")
    elif message.text:
        text = await filter_text_from_entities(bot=bot, message=message)
    else:
        raise ValueError('Unknown type of message')

    return text


async def get_answer(
        assistant_id: str,
        thread_id: str,
        bg_manager: BaseDialogManager,
        condition: asyncio.Condition
):
    async with condition:
        logger.info('Waiting for user input to be added in thread')
        await condition.wait()
        logger.info('Start polling thread')
        gpt: GPT = GPT(api_key=conf.openai.api_key, model=GPTModel.OMNI)
        try:
            run: Run = await gpt.create_run(thread=thread_id, assistant=assistant_id)
            response: RunResponse = await gpt.poll_run(run)
            if response.status == RunStatus.COMPLETED:
                messages: AsyncCursorPage[Message] = await gpt.get_messages(thread=thread_id)
                content: str = messages.data[0].content[0].text.value
                await bg_manager.update({"content": content, "cost": response.tokens_cost})
        except Exception as e:
            await bg_manager.update({"error": True, "error_message": e})


async def process_user_input(message: Message, bot: Bot, condition: asyncio.Condition, thread: str):
    logger.info('Start processing user input')
    gpt: GPT = GPT(api_key=conf.openai.api_key, model=GPTModel.OMNI)
    user_input: str = await get_user_input(message=message, bot=bot)
    await gpt.add_message_to_thread(
        message=user_input,
        thread=thread
    )
    async with condition:
        condition.notify()
        logger.info('User input processed')
