import os
import asyncio
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from langchain_gigachat.chat_models import GigaChat
import http.server
import socketserver
from threading import Thread
from utils.mat import contains_bad_words, get_bad_word_reaction, get_swear

# Импорт твоей истории
from utils.history import conversation_history

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
    except FileNotFoundError:
        content = "Ты — полезный ассистент. Отвечай кратко и по делу."
        logging.warning(f"Промпт {prompt_name} не найден, использую запасной")
    return {"role": "system", "content": content}


SYSTEM_PROMPT = load_system_prompt("default.txt")


# ------------------------------------------------------------
# МЕНЮ КОМАНД
# ------------------------------------------------------------
async def set_commands():
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="ask", description="❓ Задать вопрос"),
        BotCommand(command="reset", description="🔄 Сбросить историю"),
        BotCommand(command="help", description="ℹ️ Помощь"),
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
• /ask вопрос — задать вопрос
• @DeadPIHTOaibot вопрос — обратиться в группе
• Ответь на моё сообщение — я пойму контекст
• /reset — сбросить историю
• /help — эта справка
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
@dp.message()
async def handle_bad_words(message: Message):
    """Реагирует на мат ТОЛЬКО если это ответ на сообщение бота"""
    text = message.text or message.caption or ""
    bot_id = (await bot.me()).id

    # Проверяем: это ответ на сообщение бота И есть мат
    if (message.reply_to_message and
            message.reply_to_message.from_user.id == bot_id and
            contains_bad_words(text)):
        reaction = get_bad_word_reaction()
        await message.reply(reaction)
        print(f"⚠️ Мат в ответе от {message.from_user.first_name}: {text[:50]}...")
        return  # мат обработан — выходим

    # Если это не мат в ответ боту — передаем дальше
    await handle_mention(message)

@dp.message()
async def handle_mention(message: Message):
    bot_username = (await bot.me()).username
    bot_id = (await bot.me()).id
    text = message.text or ""

    # 1. Ответ на сообщение бота
    if message.reply_to_message and message.reply_to_message.from_user.id == bot_id:
        if text.strip():
            await ask_gigachat(message, text.strip())
        return

    # 2. Упоминание @botname
    if f"@{bot_username}" in text:
        query = text.replace(f"@{bot_username}", "", 1).strip()
        if query:
            await ask_gigachat(message, query)
        return


# ------------------------------------------------------------
# ОСНОВНАЯ ФУНКЦИЯ ЗАПРОСА К GIGACHAT
# ------------------------------------------------------------
async def ask_gigachat(message: Message, query: str):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await bot.send_chat_action(chat_id, "typing")

    try:
        # Собираем сообщения
        messages = [SYSTEM_PROMPT]
        messages.extend(conversation_history.get_history(chat_id, user_id))
        messages.append({"role": "user", "content": query})

        # Запрос к GigaChat
        response = giga.invoke(messages)
        answer = response.content

        # 🔥 ДОБАВЛЯЕМ ПСЕВДО-МАТ С ВЕРОЯТНОСТЬЮ 25%
        swear = get_swear(probability=0.55)  # 7% шанс
        if swear:
            answer = f"{swear} {answer}"

        # Сохраняем в историю
        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        # Обрезаем длинные ответы
        if len(answer) > 4000:
            answer = answer[:4000] + "...\n\n(ответ обрезан из-за лимита)"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("❌ Ошибка при запросе. Попробуй позже.")


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

    await bot.delete_webhook(drop_pending_updates=True)

    await set_commands()

    print("🚀 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
