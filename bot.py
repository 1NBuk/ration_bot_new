import sqlite3
import logging
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, ContentType
from aiogram.utils.executor import start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import nest_asyncio
from func import *
import torch
from models import *

logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = "7153682251:AAHG-E4tQgL5uZV1RgUv0nEf2SVxOXniOT8"
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных
DB_PATH = "nutrition_bot.db"

def create_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Создание таблицы User
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            max_calories INTEGER DEFAULT 2000,
            max_protein INTEGER DEFAULT 100,
            max_fat INTEGER DEFAULT 70,
            max_carbs INTEGER DEFAULT 300
        )
        """)
        # Создание таблицы DailyIntake
        cursor.execute("""
CREATE TABLE IF NOT EXISTS DailyIntake (
    intake_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    calories INTEGER DEFAULT 0,
    protein INTEGER DEFAULT 0,
    fat INTEGER DEFAULT 0,
    carbs INTEGER DEFAULT 0,
    UNIQUE (user_id, date),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
)
""")

        conn.commit()
    except sqlite3.OperationalError as e:
        if 'malformed' in str(e):
            print("Database disk image is malformed. Attempting to repair...")
            conn.execute("VACUUM")  # Rebuilds the database file
            conn.commit()
    finally:
        conn.close()

create_database()

# Функции для работы с БД
def get_user_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, max_calories, max_protein, max_fat, max_carbs FROM User WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

# Состояния пользователя
class UserState(StatesGroup):
    editing_name = State()
    editing_calories = State()
    editing_protein = State()
    editing_fat = State()
    editing_carbs = State()

def update_user_data(user_id, field, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE User SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

def get_daily_intake(user_id, today):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT calories, protein, fat, carbs FROM DailyIntake WHERE user_id = ? AND date = ?",
        (user_id, today),
    )
    daily_data = cursor.fetchone()
    conn.close()
    return daily_data or (0, 0, 0, 0)

def update_daily_intake(user_id, today, calories, protein, fat, carbs):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO DailyIntake (user_id, date, calories, protein, fat, carbs)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, date) DO UPDATE SET
            calories = calories + ?,
            protein = protein + ?,
            fat = fat + ?,
            carbs = carbs + ?
        """,
        (user_id, today, calories, protein, fat, carbs, calories, protein, fat, carbs),
    )
    conn.commit()
    conn.close()

# Состояния пользователя
class PhotoState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_action = State()

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(KeyboardButton("Просмотр своего аккаунта"), KeyboardButton("Посмотреть калории за день"))
main_keyboard.row(KeyboardButton("Сколько ещё надо съесть"), KeyboardButton("Прислать фотографию"))
main_keyboard.row(KeyboardButton("Картинка с прогрессом"))

photo_action_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
photo_action_keyboard.row(KeyboardButton("Посчитать калории"), KeyboardButton("Совет"))
photo_action_keyboard.row(KeyboardButton("Назад в меню"))

# Обработчики
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if not get_user_data(user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO User (user_id, username, max_calories, max_protein, max_fat, max_carbs)
        VALUES (?, ?, 2000, 100, 70, 300)
        """, (user_id, username))
        conn.commit()
        conn.close()

    await message.reply(
        "Добро пожаловать в бота для расчёта калорий и БЖУ! Выберите действие с помощью кнопок.",
        reply_markup=main_keyboard
    )


account_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
account_keyboard.row(KeyboardButton("Просмотр аккаунта"))
account_keyboard.row(KeyboardButton("Редактирование имени"), KeyboardButton("Редактирование своего максимума калорий"))
account_keyboard.row(KeyboardButton("Редактирование своего максимума БЖУ"), KeyboardButton("Назад в меню"))

# Обработчики
@dp.message_handler(lambda message: message.text == "Просмотр своего аккаунта")
async def view_account_menu(message: types.Message):
    await message.reply("Выберите действие:", reply_markup=account_keyboard)

@dp.message_handler(lambda message: message.text == "Просмотр аккаунта")
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

@dp.message_handler(lambda message: message.text == "Редактирование имени")
async def edit_name_start(message: types.Message):
    await UserState.editing_name.set()
    await message.reply("Введите новое имя.")

@dp.message_handler(state=UserState.editing_name)
async def edit_name(message: types.Message, state: FSMContext):
    new_name = message.text
    update_user_data(message.from_user.id, "username", new_name)
    await state.finish()
    await message.reply("Изменения сохранены.", reply_markup=account_keyboard)

@dp.message_handler(lambda message: message.text == "Редактирование своего максимума калорий")
async def edit_calories_start(message: types.Message):
    await UserState.editing_calories.set()
    await message.reply("Введите новое значение калорий (допустимые значения: 500-5000).")

@dp.message_handler(state=UserState.editing_calories)
async def edit_calories(message: types.Message, state: FSMContext):
    try:
        new_calories = int(message.text)
        if 500 <= new_calories <= 5000:
            update_user_data(message.from_user.id, "max_calories", new_calories)
            await state.finish()
            await message.reply("Изменения сохранены.", reply_markup=account_keyboard)
        else:
            await message.reply("Введите значение в диапазоне 500-5000.")
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")

@dp.message_handler(lambda message: message.text == "Редактирование своего максимума БЖУ")
async def edit_bju_start(message: types.Message):
    await UserState.editing_protein.set()
    await message.reply("Введите количество белков в граммах.")

@dp.message_handler(state=UserState.editing_protein)
async def edit_protein(message: types.Message, state: FSMContext):
    try:
        protein = int(message.text)
        await state.update_data(protein=protein)
        await UserState.editing_fat.set()
        await message.reply("Введите количество жиров в граммах.")
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")

@dp.message_handler(state=UserState.editing_fat)
async def edit_fat(message: types.Message, state: FSMContext):
    try:
        fat = int(message.text)
        await state.update_data(fat=fat)
        await UserState.editing_carbs.set()
        await message.reply("Введите количество углеводов в граммах.")
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")

@dp.message_handler(state=UserState.editing_carbs)
async def edit_carbs(message: types.Message, state: FSMContext):
    try:
        carbs = int(message.text)
        user_data = await state.get_data()
        update_user_data(message.from_user.id, "max_protein", user_data["protein"])
        update_user_data(message.from_user.id, "max_fat", user_data["fat"])
        update_user_data(message.from_user.id, "max_carbs", carbs)
        await state.finish()
        await message.reply("Изменения сохранены.", reply_markup=account_keyboard)
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число.")

@dp.message_handler(lambda message: message.text == "Назад в меню")
async def back_to_main_menu(message: types.Message):
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_keyboard)


@dp.message_handler(lambda message: message.text == "Назад в меню")
async def back_to_main_menu(message: types.Message):
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_keyboard)


@dp.message_handler(lambda message: message.text == "Посмотреть калории за день")
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

@dp.message_handler(lambda message: message.text == "Сколько ещё надо съесть")
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


@dp.message_handler(lambda message: message.text == "Прислать фотографию")
async def ask_for_photo(message: types.Message):
    await PhotoState.waiting_for_photo.set()
    await message.reply("Пожалуйста, пришлите фотографию.")

@dp.message_handler(content_types=ContentType.PHOTO, state=PhotoState.waiting_for_photo)
async def receive_photo(message: types.Message, state: FSMContext):
    try:
        # Получение идентификатора файла
        file_id = message.photo[-1].file_id
        async with state.proxy() as data:
            data['file_id'] = file_id

        # Получение URL файла
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        # Обработка данных и добавление в таблицу
        user_id = message.from_user.id
        today = str(date.today())
        result = process_and_save_calories(user_id, today, file_url)

        # Уведомление пользователя о добавлении данных
        await message.reply(result)

        # Перевод состояния в ожидание действия
        await PhotoState.waiting_for_action.set()
        await message.reply("Фотография обработана. Выберите дальнейшее действие:", reply_markup=photo_action_keyboard)
    except Exception as e:
        logging.error(f"Ошибка обработки фото: {e}")
        await message.reply("Произошла ошибка при обработке изображения. Попробуйте снова.")

@dp.message_handler(lambda message: message.text == "Посчитать калории", state=PhotoState.waiting_for_action)
async def calculate_calories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file_id = data.get('file_id')

    try:
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        reply = calories(file_url)
        await message.reply(reply)
    except Exception as e:
        logging.error(f"Ошибка при расчёте калорий: {e}")
        await message.reply("Не удалось рассчитать калории. Попробуйте снова.")

@dp.message_handler(lambda message: message.text == "Совет", state=PhotoState.waiting_for_action)
async def give_advice(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file_id = data.get('file_id')

    try:
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        reply = advice(file_url)
        await message.reply(reply)
    except Exception as e:
        logging.error(f"Ошибка при генерации совета: {e}")
        await message.reply("Не удалось дать совет. Попробуйте снова.")

@dp.message_handler(lambda message: message.text == "Назад в меню", state=PhotoState.waiting_for_action)
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_keyboard)
@dp.message_handler(lambda message: message.text == "Картинка с прогрессом")
async def send_progress_image(message: types.Message):
    user_id = message.from_user.id
    today = str(date.today())

    # Получение данных пользователя и прогресса
    user_data = get_user_data(user_id)
    if not user_data:
        await message.reply("Ваш профиль не найден. Зарегистрируйтесь с помощью команды /start.")
        return

    _, _, max_calories, max_protein, max_fat, max_carbs = user_data
    daily_data = get_daily_intake(user_id, today)
    total_calories, total_protein, total_fat, total_carbs = daily_data

    # Создание изображения
    image_path = create_progress_image(
        max_calories, max_protein, max_fat, max_carbs,
        total_calories, total_protein, total_fat, total_carbs
    )

    # Отправка изображения пользователю
    with open(image_path, 'rb') as image_file:
        await bot.send_photo(message.chat.id, photo=image_file, caption="Ваш прогресс за сегодня.")


# Запуск бота
nest_asyncio.apply()

if __name__ == "__main__":
    start_polling(dp, skip_updates=True)