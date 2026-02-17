import sqlite3
from datetime import date
import os

DB_PATH = "rank_data.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            rank TEXT DEFAULT 'Five',
            questions_asked INTEGER DEFAULT 0,
            last_question_date TEXT,
            questions_today INTEGER DEFAULT 0
        )
    """)
    # Таблица экзаменов (чтобы знать, сдал ли уже для этого ранга)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            user_id INTEGER,
            target_rank TEXT,
            passed BOOLEAN DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            last_attempt_date TEXT,
            PRIMARY KEY (user_id, target_rank)
        )
    """)
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name, rank, questions_asked, questions_today)
        VALUES (?, ?, ?, 'Five', 0, 0)
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()


def increment_question_count(user_id):
    today = str(date.today())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Получаем текущие данные
    cursor.execute("SELECT questions_asked, last_question_date, questions_today FROM users WHERE user_id = ?",
                   (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return 0
    total_q, last_date, today_q = result

    # Сбрасываем счетчик сегодняшних вопросов, если день новый
    if last_date != today:
        today_q = 0

    # Увеличиваем счетчики
    total_q += 1
    today_q += 1

    cursor.execute("""
        UPDATE users 
        SET questions_asked = ?, last_question_date = ?, questions_today = ?
        WHERE user_id = ?
    """, (total_q, today, today_q, user_id))
    conn.commit()
    conn.close()
    return total_q


def get_user_rank_and_counts(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rank, questions_asked, questions_today FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"rank": result[0], "total": result[1], "today": result[2]}
    return None


def update_user_rank(user_id, new_rank):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET rank = ? WHERE user_id = ?", (new_rank, user_id))
    conn.commit()
    conn.close()


# --- Экзамены ---
def get_exam_status(user_id, target_rank):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT passed, attempts FROM exams WHERE user_id = ? AND target_rank = ?", (user_id, target_rank))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"passed": result[0], "attempts": result[1]}
    return {"passed": 0, "attempts": 0}


def update_exam_attempt(user_id, target_rank, passed=False):
    today = str(date.today())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Проверяем, есть ли запись
    cursor.execute("SELECT attempts FROM exams WHERE user_id = ? AND target_rank = ?", (user_id, target_rank))
    result = cursor.fetchone()
    if result:
        attempts = result[0] + 1
        cursor.execute("""
            UPDATE exams 
            SET attempts = ?, last_attempt_date = ?, passed = ?
            WHERE user_id = ? AND target_rank = ?
        """, (attempts, today, passed, user_id, target_rank))
    else:
        cursor.execute("""
            INSERT INTO exams (user_id, target_rank, passed, attempts, last_attempt_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, target_rank, passed, 1, today))
    conn.commit()
    conn.close()


# Инициализация
init_db()