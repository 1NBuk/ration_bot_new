import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import create_database
from keyboards import main_keyboard
from handlers import account, intake, photo

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

create_database()

# Регистрация хендлеров
dp.register_message_handler(account.view_account_menu, lambda m: m.text == "Просмотр своего аккаунта")
dp.register_message_handler(account.view_account, lambda m: m.text == "Просмотр аккаунта")
dp.register_message_handler(account.edit_name_start, lambda m: m.text == "Редактирование имени")
dp.register_message_handler(account.edit_name, state=account.UserState.editing_name)

if __name__ == "__main__":
    start_polling(dp, skip_updates=True)
