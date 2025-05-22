# handlers/intake.py
from aiogram import types
from database.db import get_daily_intake, get_user_data
from datetime import date

async def daily_calories(message: types.Message):
    user_id = message.from_user.id
    today = str(date.today())
    daily_data = get_daily_intake(user_id, today)
    total_calories, total_protein, total_fat, total_carbs = daily_data
    await message.reply(
        f"Ваши данные за сегодня:\n"
        f"Калории: {total_calories}\n"
        f"Белки: {total_protein}, Жиры: {total_fat}, Углеводы: {total_carbs}"
    )

async def remaining_nutrients(message: types.Message):
    user_id = message.from_user.id
    today = str(date.today())
    user_data = get_user_data(user_id)
    if not user_data:
        await message.reply("Ваш профиль не найден. Зарегистрируйтесь с помощью команды /start.")
        return
    _, _, max_calories, max_protein, max_fat, max_carbs = user_data
    daily_data = get_daily_intake(user_id, today)
    total_calories, total_protein, total_fat, total_carbs = daily_data
    await message.reply(
        f"Остаток до лимита:\n"
        f"Калории: {max_calories - total_calories}\n"
        f"Белки: {max_protein - total_protein}, Жиры: {max_fat - total_fat}, Углеводы: {max_carbs - total_carbs}"
    )
