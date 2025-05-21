import pytest
import sqlite3
import asyncio
import time
from unittest.mock import patch, AsyncMock
from aiogram import types

from bot import create_database, DB_PATH


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
@patch("bot.dp")
@patch("bot.get_user_data")
async def test_start_command(mock_get_user_data, mock_dp):
    mock_get_user_data.return_value = (123456, "testuser")

    message = types.Message(
        message_id=1,
        date=int(time.time()),  # <-- Unix timestamp
        chat=types.Chat(id=123456, type="private"),
        from_user=types.User(id=123456, is_bot=False, first_name="TestUser"),
        text="/start"
    )
    update = types.Update(message=message)

    mock_dp.feed_update = AsyncMock(return_value=None)
    await mock_dp.feed_update(update)

    user_data = mock_get_user_data(123456)
    assert user_data is not None
    assert user_data[1] == "testuser"


@pytest.mark.asyncio
@patch("bot.dp")
async def test_view_account_menu(mock_dp):
    message = types.Message(
        message_id=2,
        date=int(time.time()),
        chat=types.Chat(id=123456, type="private"),
        from_user=types.User(id=123456, is_bot=False, first_name="TestUser"),
        text="Просмотр своего аккаунта"
    )
    update = types.Update(message=message)

    mock_dp.feed_update = AsyncMock(return_value=None)
    await mock_dp.feed_update(update)


@pytest.mark.asyncio
@patch("bot.dp")
@patch("bot.get_user_data")
async def test_edit_name_and_save(mock_get_user_data, mock_dp):
    from aiogram.dispatcher import FSMContext

    mock_state = AsyncMock()
    mock_state.set_state = AsyncMock()

    mock_dp.current_state = AsyncMock(return_value=mock_state)

    message = types.Message(
        message_id=3,
        date=int(time.time()),
        chat=types.Chat(id=123456, type="private"),
        from_user=types.User(id=123456, is_bot=False, first_name="TestUser"),
        text="NewName"
    )
    update = types.Update(message=message)

    mock_dp.feed_update = AsyncMock(return_value=None)
    await mock_dp.feed_update(update)

    mock_get_user_data.return_value = (123456, "NewName")

    user_data = mock_get_user_data(123456)
    assert user_data[1] == "NewName"


@pytest.mark.asyncio
@patch("bot.dp")
async def test_daily_calories(mock_dp):
    message = types.Message(
        message_id=4,
        date=int(time.time()),
        chat=types.Chat(id=123456, type="private"),
        from_user=types.User(id=123456, is_bot=False, first_name="TestUser"),
        text="Посмотреть калории за день"
    )
    update = types.Update(message=message)

    mock_dp.feed_update = AsyncMock(return_value=None)
    await mock_dp.feed_update(update)


@pytest.mark.asyncio
@patch("bot.dp")
async def test_remaining_nutrients(mock_dp):
    message = types.Message(
        message_id=5,
        date=int(time.time()),
        chat=types.Chat(id=123456, type="private"),
        from_user=types.User(id=123456, is_bot=False, first_name="TestUser"),
        text="Сколько ещё надо съесть"
    )
    update = types.Update(message=message)

    mock_dp.feed_update = AsyncMock(return_value=None)
    await mock_dp.feed_update(update)
