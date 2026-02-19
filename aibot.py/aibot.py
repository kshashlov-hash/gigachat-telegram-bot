import os
import asyncio
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from langchain_gigachat.chat_models import GigaChat
import http.server
import socketserver
from threading import Thread
from utils.mat import contains_bad_words, get_bad_word_reaction, get_swear
from rank_system.database import ensure_owner_rank
from utils.gigachat_client import init_gigachat, ask_gigachat
from utils.chats_db import save_chat
# Импорт твоей истории
from utils.history import conversation_history

from rank_system.rank_handler import router as rank_router


# ------------------------------------------------------------
# ЗАГРУЗКА ПЕРЕМЕННЫХ
# ------------------------------------------------------------
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TOKEN")
GIGACHAT_CRED = os.getenv("GIGACHAT_API_KEY")

# ------------------------------------------------------------
# ИНИЦИАЛИЗАЦИЯ
# ------------------------------------------------------------
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
# Сначала создаем объект GigaChat
giga = GigaChat(
    credentials=GIGACHAT_CRED,
    verify_ssl_certs=False,
    model="GigaChat",
    temperature=0.7,
    max_tokens=1000,
    scope="GIGACHAT_API_PERS"
)

# И ТОЛЬКО ТЕПЕРЬ передаем их в dp
dp['giga'] = giga

# Теперь подключаем роутер (он увидит данные из dp)
print("⚙️ Попытка подключения rank_router...")
dp.include_router(rank_router)
# ...

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
        content = "Ты — полезный ассистент."
    return {"role": "system", "content": content}

# Используй СВОЮ функцию, а не импортированную load_prompt
SYSTEM_PROMPT = load_system_prompt("default.txt")

# ------------------------------------------------------------
# МЕНЮ КОМАНД
# ------------------------------------------------------------
async def set_commands():
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="ask", description="❓ Задать вопрос"),
        BotCommand(command="reset", description="🔄 Сбросить историю"),
        BotCommand(command="help", description="ℹ️ Общая справка"),
        BotCommand(command="askrank", description="🎓 Вопрос для ранга"),
        BotCommand(command="myrank", description="📊 Мой ранг"),
        BotCommand(command="exam", description="📝 Начать экзамен"),
        BotCommand(command="exam_cancel", description="🚫 Отменить экзамен"),
        BotCommand(command="rank_help", description="📖 О ранговой системе"),
    ]
    await bot.set_my_commands(commands)
    print("✅ Меню команд установлено!")



# ------------------------------------------------------------
# КОМАНДЫ БОТА
# ------------------------------------------------------------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Я бот от создателя milk. Упомяни меня @DeadPIHTOaibot или напиши /ask вопрос")


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    conversation_history.clear_history(chat_id, user_id)
    await message.answer("🧹 История диалога очищена!")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """\
🤖 <b>Dead Pihto — умный ассистент</b>

<b>👀Как использовать:</b>
• /start — приветствие бота
• /ask вопрос — задать вопрос (НЕ учитывается в ранговую систему)
• @DeadPIHTOaibot вопрос — обратиться в группе
• Ответь на моё сообщение — я пойму контекст
• /reset — сбросить историю
• /help — эта справка

📈 Система рангов (ТОЛЬКО для общего чата):
• /askrank вопрос — задать вопрос, который учитывается в ранговой системе
• /myrank — показать текущий ранг и статистику
• /exam — начать экзамен для повышения ранга (если доступно)
• /exam_cancel — прервать текущий экзамен

Приятного пользования 💥
Создатель: milk @thesunissad
"""
    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    query = message.text.replace("/ask", "", 1).strip()
    if not query:
        await message.answer("Напиши свой вопрос после команды /ask")
        return
    await ask_gigachat(message, query)


# ------------------------------------------------------------
# ОБРАБОТКА УПОМИНАНИЙ И ОТВЕТОВ
# ------------------------------------------------------------
# В aibot.py

@dp.message(~F.text.startswith("/"))
async def global_message_handler(message: Message):
    if message.chat.type != "private":
        title = message.chat.title or "Без названия"
        save_chat(message.chat.id, message.chat.type, title)
    text = message.text or message.caption or ""
    bot_id = (await bot.me()).id
    bot_username = (await bot.me()).username

    # 1. Сначала логируем для отладки
    print(f"📥 ТЕКСТ: '{text[:30]}...' | chat_id={message.chat.id}")

    # 2. Логика мата (только если это ответ на сообщение бота)
    if message.reply_to_message and message.reply_to_message.from_user.id == bot_id:
        if contains_bad_words(text):
            reaction = get_bad_word_reaction()
            await message.reply(reaction)
            print(f"⚠️ Мат обработан.")
            return

        # Если это просто текстовый ответ боту без мата — отвечаем через GigaChat
        if text.strip():
            await ask_gigachat(message, text.strip())
            return

    # 3. Логика упоминания @botname
    if f"@{bot_username}" in text:
        query = text.replace(f"@{bot_username}", "", 1).strip()
        if query:
            await ask_gigachat(message, query)
        return



# ------------------------------------------------------------
# ОСНОВНАЯ ФУНКЦИЯ ЗАПРОСА К GIGACHAT
# ------------------------------------------------------------


def run_health_server():
    """Минимальный HTTP-сервер для Render и UptimeRobot"""
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler

    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Bot is running')

    with socketserver.TCPServer(("0.0.0.0", port), HealthHandler) as httpd:
        print(f"✅ Health server running on port {port}")
        httpd.serve_forever()

# ------------------------------------------------------------
# ЗАПУСК (ТОЛЬКО POLLING, РАБОТАЕТ ЛОКАЛЬНО)
# ------------------------------------------------------------
async def main():
    # Запускаем HTTP-сервер для Render и UptimeRobot
    Thread(target=run_health_server, daemon=True).start()

    await asyncio.sleep(2)

    ensure_owner_rank()
    await bot.delete_webhook(drop_pending_updates=True)

    await set_commands()
    init_gigachat(giga, SYSTEM_PROMPT)
    print("🚀 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot, giga=giga, sys_prompt=SYSTEM_PROMPT)


if __name__ == "__main__":
    asyncio.run(main())
