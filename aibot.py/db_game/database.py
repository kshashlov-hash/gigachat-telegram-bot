import sqlite3
import os
from pathlib import Path

# Привязываем путь к базе данных к директории этого файла
# Если database.py лежит в db_game/, то подняться на уровень выше (корневой)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "rank_data.db"

def init_db():
    # Используем str(DB_PATH), так как sqlite3 любит строки, а не объекты Path
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Оставляем простую таблицу пользователей (для истории и рассылок)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    """)

    # Таблица для рекордов Змейки
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snake_leaderboard (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            score INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def create_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()


# Функции для Змейки
def update_snake_score(user_id, username, first_name, new_score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM snake_leaderboard WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("""
            INSERT INTO snake_leaderboard (user_id, username, first_name, score) 
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, new_score))
        updated = True
    elif new_score > result[0]:
        cursor.execute("UPDATE snake_leaderboard SET score = ?, username = ?, first_name = ? WHERE user_id = ?",
                       (new_score, username, first_name, user_id))
        updated = True
    else:
        updated = False
    conn.commit()
    conn.close()
    return updated


def get_snake_top(limit=15):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, username, score FROM snake_leaderboard ORDER BY score DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


init_db()