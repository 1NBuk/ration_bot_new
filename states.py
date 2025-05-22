from aiogram.dispatcher.filters.state import State, StatesGroup

class UserState(StatesGroup):
    editing_name = State()
    editing_calories = State()
    editing_protein = State()
    editing_fat = State()
    editing_carbs = State()

class PhotoState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_action = State()
