import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "chats.db"

def init_chats_db():
    """Создаёт таблицу для хранения ID чатов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            chat_type TEXT,
            title TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_chat(chat_id: int, chat_type: str, title: str = None):
    """Сохраняет или обновляет информацию о чате"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chats (chat_id, chat_type, title, last_active)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(chat_id) DO UPDATE SET
            last_active = CURRENT_TIMESTAMP,
            title = COALESCE(EXCLUDED.title, title),
            chat_type = EXCLUDED.chat_type
    """, (chat_id, chat_type, title))
    conn.commit()
    conn.close()

def get_all_chats():
    """Возвращает список всех сохранённых чатов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, chat_type, title FROM chats ORDER BY last_active DESC")
    chats = cursor.fetchall()
    conn.close()
    return chats

# Инициализация при импорте
init_chats_db()