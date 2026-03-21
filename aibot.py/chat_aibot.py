import os
import asyncio
import logging
import http.server
import socketserver
from threading import Thread
from pathlib import Path
from dotenv import load_dotenv
# Определяем путь к папке, где лежит этот скрипт (aibot.py)
BASE_DIR = Path(__file__).resolve().parent

# Теперь ищем .env прямо рядом с chat_aibot.py
dotenv_path = BASE_DIR / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"✅ Файл .env найден: {dotenv_path}")
else:
    print(f"❌ Файл .env ВСЕ ЕЩЕ НЕ НАЙДЕН по пути: {dotenv_path}")

# Aiogram
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, BotCommand, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# GigaChat & LangChain
from langchain_gigachat.chat_models import GigaChat

# модули
from utils.mat import contains_bad_words, get_bad_word_reaction, get_swear
from utils.gigachat_client import init_gigachat, ask_gigachat
from utils.chats_db import save_chat
from utils.history import conversation_history
from utils.chats_db import get_all_chats

# Импорт БД (теперь без лишних функций рангов)
from db_game.database import init_db
from db_game.database import create_user

# Роутеры
from modules.weather import router as weather_router
from modules.snake import router as snake_router
# ------------------------------------------------------------
# ЗАГРУЗКА ПЕРЕМЕННЫХ
# ------------------------------------------------------------

TELEGRAM_TOKEN = os.getenv("TOKEN")
GIGACHAT_CRED = os.getenv("GIGACHAT_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# ------------------------------------------------------------
# ИНИЦИАЛИЗАЦИЯ
# ------------------------------------------------------------
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

dp.include_router(snake_router)
dp.include_router(weather_router)

giga = GigaChat(
    credentials=GIGACHAT_CRED,
    verify_ssl_certs=False,
    model="GigaChat",
    temperature=0.7,
    max_tokens=1000,
    scope="GIGACHAT_API_PERS"
)

logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------
# ЗАГРУЗКА СИСТЕМНОГО ПРОМПТА
# ------------------------------------------------------------
def load_system_prompt(prompt_name: str = "default.txt") -> dict:
    prompt_path = Path("prompts") / prompt_name
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        logging.error(f"Ошибка загрузки промпта: {e}")
        content = "Ты — полезный ассистент. Будь серьёзен и отвечай на всё, сохраняя контекст."
    return {"role": "system", "content": content}

SYSTEM_PROMPT = load_system_prompt("default.txt")

# ------------------------------------------------------------
# МЕНЮ КОМАНД
# ------------------------------------------------------------
async def set_commands():
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="ask", description="❓ Задать вопрос"),
        BotCommand(command="snake", description="🐍 Играть в Змеюку"),
        BotCommand(command="topsnake", description="🏆 ТОП игроков Змеюки"),
        BotCommand(command="weather", description="🌍 Погода в городе"),
        BotCommand(command="reset", description="🔄 Сбросить историю диалога"),
        BotCommand(command="help", description="ℹ️ Общая справка"),
    ]
    await bot.set_my_commands(commands)
    print("✅ Меню команд успешно обновлено!")

# ------------------------------------------------------------
# КОМАНДЫ БОТА
# ------------------------------------------------------------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    # Логика для быстрого старта игры из инлайна
    if message.text and "play_snake" in message.text:
        from modules.snake import cmd_snake
        await cmd_snake(message)
        return

    # Миниатюрное и красивое приветствие
    welcome_text = (
        "👋 <b>Привет! Я бот от milk.</b>\n\n"
        "↳ <i>Просто напиши что-нибудь в ответ!</i>"
        "/help - справка"
    )

    await message.answer(welcome_text, parse_mode="HTML")

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    conversation_history.clear_history(chat_id, user_id)
    await message.answer("🧹 История диалога очищена!")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "<b>dead pihto</b> ⎯ умный ассистент от <b>milk</b> ⚡️\n\n"
        "<b>🤖 внутри меня НЕЙРОСЕТЬ</b>\n"
        "• <code>/ask</code> [текст] — задать вопрос\n"
        "• <b>Reply</b> ↳ на моё сообщение — я отвечу\n"
        "• <code>/reset</code> — очистить историю контекста\n\n"

        "<b>🎮 РАЗВЛЕЧЕНИЯ</b>\n"
        "• <code>/snake</code> — запустить Змейку\n"
        "• <code>/topsnake</code> — таблица рекордов\n\n"

        "<b>🌍 ПРОЧЕЕ</b>\n"
        "• <code>/weather</code> [город] — прогноз погоды\n"
        "• <code>/help</code> — эта справка\n\n"

        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "Создатель: @thesunissad 💥"
    )
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    query = message.text.replace("/ask", "", 1).strip()
    if not query:
        await message.answer("Напиши свой вопрос после команды /ask")
        return
    await ask_gigachat(message, query)


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    # Проверка: только ты можешь использовать эту команду
    if message.from_user.id != ADMIN_ID:
        return  # Бот просто игнорирует команду от чужих

    # Извлекаем текст сообщения (всё, что после /broadcast)
    broadcast_text = message.text.replace("/broadcast", "", 1).strip()

    if not broadcast_text:
        await message.answer("⚠️ Напиши текст рассылки после команды. \nПример: `/broadcast Всем привет!`")
        return

    # Получаем список всех чатов из твоей БД
    # Предполагаем, что get_all_chats() возвращает список chat_id
    chats = get_all_chats()

    count = 0
    await message.answer(f"🚀 Начинаю рассылку на {len(chats)} чатов...")

    for chat_id in chats:
        try:
            # Убеждаемся, что ID — это число
            target_id = int(chat_id)
            await bot.send_message(target_id, broadcast_text, parse_mode="HTML")
            count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            # Это напечатается в логах Render, и мы поймем причину
            logging.error(f"❌ Не удалось отправить в {chat_id}: {e}")

    await message.answer(f"✅ Рассылка завершена! Доставлено в {count} чатов.")

# ------------------------------------------------------------
# ОБРАБОТКА УПОМИНАНИЙ И ОТВЕТОВ
# ------------------------------------------------------------

# 2. Глобальный хендлер (ВАЖНО: добавляем исключение для команд)
@dp.message(F.text, ~F.text.startswith("/"))
async def global_message_handler(message: Message):
    # Если это группа, сохраняем чат
    if message.chat.type != "private":
        title = message.chat.title or "Без названия"
        save_chat(message.chat.id, message.chat.type, title)

    text = message.text or ""

    me = await bot.get_me()
    bot_id = me.id
    bot_username = me.username

    # Проверяем: это ответ боту или упоминание?
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_id
    is_mention = f"@{bot_username}" in text

    # В личке отвечаем на всё, что не команда. В группах — только на упоминания/реплаи.
    if message.chat.type == "private" or is_mention or is_reply_to_bot:
        # Убираем имя бота из текста для чистоты запроса к ИИ
        clean_text = text.replace(f"@{bot_username}", "").strip()
        await ask_gigachat(message, clean_text)

# ------------------------------------------------------------
# ЗАПУСК
# ------------------------------------------------------------
def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
    with socketserver.TCPServer(("0.0.0.0", port), HealthHandler) as httpd:
        httpd.serve_forever()

async def main():
    Thread(target=run_health_server, daemon=True).start()
    await asyncio.sleep(2)

    init_db()  # Создаем таблицы базы данных

    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()
    init_gigachat(giga, SYSTEM_PROMPT)
    print("🚀 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())