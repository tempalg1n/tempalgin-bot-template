from aiogram.fsm.state import StatesGroup, State


class DialogSG(StatesGroup):
    greeting = State()
