from aiogram.fsm.state import StatesGroup, State
class UXForm(StatesGroup):
    business_type = State()
    audience = State()
    functions = State()
    style = State()
    confirm = State()
    GENERATE = State()

