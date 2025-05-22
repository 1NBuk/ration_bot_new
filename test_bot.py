import pytest
import sqlite3
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, ANY
from aiogram import types

from bot import create_database
from config import DB_PATH
from database.db import get_user_data


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    create_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User")
    cursor.execute("INSERT OR REPLACE INTO User (user_id, username) VALUES (?, ?)", (123456, "testuser"))
    conn.commit()
    conn.close()


@pytest.mark.asyncio
async def test_view_account_menu():
    from handlers.account import view_account_menu

    message = AsyncMock()
    message.reply = AsyncMock()

    await view_account_menu(message)
    message.reply.assert_called_with("Выберите действие:", reply_markup=ANY)


@pytest.mark.asyncio
async def test_view_account():
    from handlers.account import view_account

    message = AsyncMock()
    message.from_user.id = 123456
    message.reply = AsyncMock()

    await view_account(message)
    message.reply.assert_called_with(ANY)


@pytest.mark.asyncio
async def test_daily_calories():
    from handlers.intake import daily_calories

    message = AsyncMock()
    message.from_user.id = 123456
    message.reply = AsyncMock()

    await daily_calories(message)
    message.reply.assert_called_with(ANY)


@pytest.mark.asyncio
async def test_remaining_nutrients():
    from handlers.intake import remaining_nutrients

    message = AsyncMock()
    message.from_user.id = 123456
    message.reply = AsyncMock()

    await remaining_nutrients(message)
    message.reply.assert_called_with(ANY)


@pytest.mark.asyncio
async def test_back_to_menu():
    from handlers.photo import back_to_menu
    from keyboards import main_keyboard

    message = AsyncMock()
    message.reply = AsyncMock()
    state = MagicMock()
    state.finish = AsyncMock()

    await back_to_menu(message, state)
    state.finish.assert_awaited()
    message.reply.assert_called_with("Вы вернулись в главное меню.", reply_markup=main_keyboard)
