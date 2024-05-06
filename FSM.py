from aiogram.fsm.state import State, StatesGroup


class FSM(StatesGroup):
    find_user = State()
    question_1 = State()
    question_2 = State()
    final_question = State()