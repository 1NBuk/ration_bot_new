# handlers/account.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.db import get_user_data, update_user_data
from keyboards import account_keyboard, main_keyboard
from states import UserState

async def view_account_menu(message: types.Message):
    await message.reply("Выберите действие:", reply_markup=account_keyboard)

async def view_account(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    if not user_data:
        await message.reply("Ваш профиль не найден. Зарегистрируйтесь с помощью команды /start.")
        return

    _, username, max_calories, max_protein, max_fat, max_carbs = user_data
    await message.reply(
        f"Ваш профиль:\n"
        f"Имя: {username}\n"
        f"Лимит калорий: {max_calories}\n"
        f"Белки: {max_protein}, Жиры: {max_fat}, Углеводы: {max_carbs}"
    )

async def edit_name_start(message: types.Message):
    await UserState.editing_name.set()
    await message.reply("Введите новое имя.")

async def edit_name(message: types.Message, state: FSMContext):
    new_name = message.text
    update_user_data(message.from_user.id, "username", new_name)
    await state.finish()
    await message.reply("Имя изменено.", reply_markup=account_keyboard)

async def edit_calories_start(message: types.Message):
    await UserState.editing_calories.set()
    await message.reply("Введите новый лимит калорий.")

async def edit_calories(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
        update_user_data(message.from_user.id, "max_calories", value)
        await message.reply("Лимит калорий обновлён.", reply_markup=account_keyboard)
    except ValueError:
        await message.reply("Введите число.")
    await state.finish()

async def edit_protein_start(message: types.Message):
    await UserState.editing_protein.set()
    await message.reply("Введите новый лимит белков.")

async def edit_protein(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
        update_user_data(message.from_user.id, "max_protein", value)
        await message.reply("Лимит белков обновлён.", reply_markup=account_keyboard)
    except ValueError:
        await message.reply("Введите число.")
    await state.finish()

async def edit_fat_start(message: types.Message):
    await UserState.editing_fat.set()
    await message.reply("Введите новый лимит жиров.")

async def edit_fat(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
        update_user_data(message.from_user.id, "max_fat", value)
        await message.reply("Лимит жиров обновлён.", reply_markup=account_keyboard)
    except ValueError:
        await message.reply("Введите число.")
    await state.finish()

async def edit_carbs_start(message: types.Message):
    await UserState.editing_carbs.set()
    await message.reply("Введите новый лимит углеводов.")

async def edit_carbs(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
        update_user_data(message.from_user.id, "max_carbs", value)
        await message.reply("Лимит углеводов обновлён.", reply_markup=account_keyboard)
    except ValueError:
        await message.reply("Введите число.")
    await state.finish()

async def back_to_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_keyboard)
