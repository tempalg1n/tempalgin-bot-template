from aiogram.fsm.state import StatesGroup, State


class StartSG(StatesGroup):
    greeting = State()


class AssistantSG(StatesGroup):
    init = State()
    conversation = State()
