import sqlite3
from config import DB_PATH

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, max_calories, max_protein, max_fat, max_carbs FROM User WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

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
