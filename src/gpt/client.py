import asyncio
import logging
from dataclasses import dataclass
from typing import Union, BinaryIO

import httpx

from openai import AsyncOpenAI, NotGiven, AsyncStream, BadRequestError
from openai.pagination import AsyncCursorPage
from openai.types import ImagesResponse
from openai.types.audio import Transcription
from openai.types.beta import Assistant, Thread, AssistantStreamEvent
from openai.types.beta.threads import Message, Run

from src.bot.structures.enums import GPTModel, DALLeResolutions, DALLeQuality, RunStatus
from src.configuration import conf
from src.db.models.thread import ThreadModel

logger = logging.getLogger(__name__)


@dataclass
class RunResponse:
    status: RunStatus
    tokens_cost: int = 0
    content: str = None


class GPT:
    model: GPTModel
    client: AsyncOpenAI

    def __init__(
            self,
            api_key: str,
            model: GPTModel,
            use_proxy: bool = conf.debug
    ):
        self.model = model
        self.api_key = api_key
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=120 if use_proxy else NotGiven,
            http_client=httpx.AsyncClient(
                proxies=conf.proxy.build_proxy_payload()
            ) if use_proxy else None
        )

    @staticmethod
    def _get_thread_id(thread: Union[Thread, ThreadModel, str]):
        if isinstance(thread, Thread):
            thread_id: str = thread.id
        elif isinstance(thread, ThreadModel):
            thread_id = thread.thread_id
        elif isinstance(thread, str):
            thread_id = thread
        else:
            raise ValueError(f"Can't get thread id from {thread}")
        return thread_id

    async def _create_assistant(
            self,
            name: str,
            description: str,
            instructions: str,
            model: GPTModel = GPTModel.OMNI,
            tools: list = None,
    ) -> Assistant | None:
        assistant: Assistant = (
            await self.client.beta.assistants.create(
                name=name,
                description=description,
                model=model,
                instructions=instructions,
                tools=tools,
            )
        )
        logger.info(
            f'Assistant {assistant.id} was successfully created.'
        )
        return assistant

    async def _update_assistant(
            self,
            assistant_id: str,
            name: str,
            description: str,
            instructions: str,
            model: GPTModel = GPTModel.OMNI,
            tools: list = None,
    ) -> Assistant | None:
        assistant: Assistant = (
            await self.client.beta.assistants.update(
                name=name,
                description=description,
                model=model,
                instructions=instructions,
                tools=tools if tools else [],
                assistant_id=assistant_id
            )
        )
        logger.info(
            f'Assistant {assistant.id} was successfully updated.'
        )
        return assistant

    async def create_thread(self):
        thread: Thread = await self.client.beta.threads.create()
        logger.info(f'Thread {thread.id} was successfully created.')
        return thread

    async def add_message_to_thread(
            self,
            thread: Union[Thread, ThreadModel, str],
            message: str,
    ) -> None:
        thread_id: str = self._get_thread_id(thread)
        await self.client.beta.threads.messages.create(
            thread_id=thread_id, role='user', content=message
        )
        logger.info(f'Message added to thread {thread_id}')

    async def create_run_and_stream(
            self,
            thread: Union[Thread, ThreadModel, str],
            assistant: Union[Assistant, str],
    ) -> AsyncStream[AssistantStreamEvent]:
        thread_id: str = self._get_thread_id(thread)
        assistant_id: str = assistant.id if isinstance(assistant, Assistant) else assistant
        stream: AsyncStream[AssistantStreamEvent] = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            stream=True
        )
        return stream

    async def create_run(
            self,
            thread: Union[Thread, ThreadModel, str],
            assistant: Union[Assistant, str],
    ) -> Run:
        thread_id: str = self._get_thread_id(thread)
        assistant_id: str = assistant.id if isinstance(assistant, Assistant) else assistant
        run: Run = await self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        return run

    @staticmethod
    async def poll_run(
            run: Run,
    ) -> RunResponse:
        logger.info('Start polling run')
        attempt = 1
        while True:
            if run.status == RunStatus.COMPLETED:
                response = RunResponse(tokens_cost=run.usage.total_tokens, status=RunStatus.COMPLETED)
                logger.info(f'Run completed with status {run.status}')
                return response
            elif run.status in [RunStatus.REQUIRES_ACTION]:
                response = RunResponse(status=RunStatus.REQUIRES_ACTION)
                logger.info(f'Run completed with status {run.status}')
                return response
            elif run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS]:
                await asyncio.sleep(2)
                attempt += 1
                logger.info(f"Run still {run.status}, attempt {attempt}")
            else:
                raise Exception('Some error occurred while processing run polling')

    async def get_messages(
            self,
            thread: Union[Thread, ThreadModel, str]
    ) -> AsyncCursorPage[Message]:
        thread_id: str = self._get_thread_id(thread)
        messages: AsyncCursorPage[
            Message
        ] = await self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        logger.info('Messages was retrieved successfully.')
        return messages

    async def submit_tools_output(
            self, thread_id: str, run_id: str, tool_call_id: str, output: str
    ) -> Run:
        logger.info(f'Submitting tools output... Output: {output}')
        run: Run = await self.client.beta.threads.runs.submit_tool_outputs(
            run_id=run_id,
            thread_id=thread_id,
            tool_outputs=[{'tool_call_id': tool_call_id, 'output': output}],
        )
        return run

    async def generate_image(
            self,
            prompt: str,
            size: DALLeResolutions = DALLeResolutions.SQUARE1024,
            quality: DALLeQuality = DALLeQuality.STANDARD,
    ):
        try:
            response: ImagesResponse = await self.client.images.generate(
                prompt=prompt, size=size, model='dall-e-3', quality=quality
            )
            return response
        except BadRequestError as br:
            return {
                "error": True,
                "error_message": f'Code: {br.code}. Message: {br.message}',
            }

    async def translate_voice(self, voice: BinaryIO):
        transcript: Transcription = (
            await self.client.audio.transcriptions.create(
                file=voice, model='whisper-1', response_format='text'
            )
        )
        return transcript
