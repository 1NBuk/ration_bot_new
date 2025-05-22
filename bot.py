import logging
import nest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import create_database

# Логирование
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание БД
create_database()

# Подключение обработчиков
from handlers import account, intake, photo
account.register(dp)
intake.register(dp)
photo.register(dp)

# Запуск
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
