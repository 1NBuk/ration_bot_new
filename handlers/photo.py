# handlers/photo.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import photo_action_keyboard, main_keyboard
from states import PhotoState
from func import process_and_save_calories, calories, advice
from datetime import date

async def ask_for_photo(message: types.Message):
    await PhotoState.waiting_for_photo.set()
    await message.reply("Пожалуйста, пришлите фотографию.")

async def receive_photo(message: types.Message, state: FSMContext, bot, BOT_TOKEN):
    file_id = message.photo[-1].file_id
    async with state.proxy() as data:
        data['file_id'] = file_id
    file_info = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    user_id = message.from_user.id
    today = str(date.today())
    result = process_and_save_calories(user_id, today, file_url)
    await message.reply(result)
    await PhotoState.waiting_for_action.set()
    await message.reply("Фотография обработана. Выберите дальнейшее действие:", reply_markup=photo_action_keyboard)

async def calculate_calories(message: types.Message, state: FSMContext, bot, BOT_TOKEN):
    async with state.proxy() as data:
        file_id = data.get('file_id')
    file_info = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    reply = calories(file_url)
    await message.reply(reply)

async def give_advice(message: types.Message, state: FSMContext, bot, BOT_TOKEN):
    async with state.proxy() as data:
        file_id = data.get('file_id')
    file_info = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    reply = advice(file_url)
    await message.reply(reply)

async def back_to_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_keyboard)
