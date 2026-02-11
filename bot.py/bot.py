import os
import asyncio
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BotCommand, Update
from langchain_gigachat.chat_models import GigaChat
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
import uvicorn

# Импорт твоей истории
from utils.history import conversation_history

# ------------------------------------------------------------
# ЗАГРУЗКА ПЕРЕМЕННЫХ
# ------------------------------------------------------------
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TOKEN")
GIGACHAT_CRED = os.getenv("GIGACHAT_API_KEY")
PORT = int(os.environ.get("PORT", 8000))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"

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
    """Загружает системный промпт из файла в папке prompts"""
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
async def on_startup(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="ask", description="❓ Задать вопрос"),
        BotCommand(command="reset", description="🔄 Сбросить историю"),
        BotCommand(command="help", description="ℹ️ Помощь"),
    ]
    await bot.set_my_commands(commands)
    print("✅ Меню команд установлено!")


dp.startup.register(on_startup)


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
    await message.answer("🧹 История диалога очищена! Я забыл всё, что мы обсуждали.")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    print("🔥 Команда /help вызвана!")
    help_text = """\
🤖 <b>dead pihto — умный ассистент от создателя milk для публичного/личного чата</b>

<b>Как использовать:</b>
• /ask <i>вопрос</i> — задать вопрос
• @DeadPIHTOaibot <i>вопрос</i> — обратиться в групповом чате
• Ответь на моё сообщение прямо в чате — я пойму контекст
• /reset — сбросить историю диалога

<b>Команды:</b>
/start — приветствие
/ask — задать вопрос
/reset — сбросить память
/help — эта справка

<b>Особенности:</b>
• Помню последние +-5 сообщений
• Не помню ничего через 30 минут (старость нерадость)
• Работаю в личке и группах, фотки пока что не умею обрабатывать

Желаю удачного пользования, мой функционал обязательно будет расти ❤️
"""
    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    query = message.text.replace("/ask", "", 1).strip()
    if not query:
        await message.answer("Напиши вопрос после /ask")
        return
    await ask_gigachat(message, query)


# ------------------------------------------------------------
# ОБРАБОТКА УПОМИНАНИЙ И ОТВЕТОВ
# ------------------------------------------------------------
@dp.message()
async def handle_mention(message: Message):
    bot_username = (await bot.me()).username
    bot_id = (await bot.me()).id
    text = message.text or message.caption or ""

    # Ответ на сообщение бота
    if message.reply_to_message and message.reply_to_message.from_user.id == bot_id:
        if text.strip():
            await ask_gigachat(message, text.strip())
        return

    # Текстовое упоминание @botname
    if f"@{bot_username}" in text:
        query = text.replace(f"@{bot_username}", "", 1).strip()
        if query:
            await ask_gigachat(message, query)
        return

    # Упоминание через entities
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = text[entity.offset:entity.offset + entity.length]
                if mention == f"@{bot_username}":
                    query = (text[:entity.offset] + text[entity.offset + entity.length:]).strip()
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
        messages = [SYSTEM_PROMPT]
        messages.extend(conversation_history.get_history(chat_id, user_id))
        messages.append({"role": "user", "content": query})

        response = giga.invoke(messages)
        answer = response.content

        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        if len(answer) > 4000:
            answer = answer[:4000] + "...\n\n(ответ обрезан из-за лимита)"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("Ошибка при запросе к GigaChat. Попробуй позже.")


# ------------------------------------------------------------
# WEBHOOK
# ------------------------------------------------------------
async def webhook(request: Request) -> Response:
    """Принимаем обновления от Telegram"""
    update = Update(**await request.json())
    await dp.feed_update(bot, update)
    return Response()


async def healthcheck(request: Request) -> PlainTextResponse:
    """Для проверки, что сервер жив"""
    return PlainTextResponse("OK")


# Создаём Starlette приложение
app = Starlette(routes=[
    Route(WEBHOOK_PATH, webhook, methods=["POST"]),
    Route("/", healthcheck, methods=["GET"]),
])


# ------------------------------------------------------------
# ЗАПУСК
# ------------------------------------------------------------
async def main():
    if not RENDER_URL:
        logging.error("RENDER_EXTERNAL_URL не задан! Бот не запустится.")
        return

    webhook_url = f"{RENDER_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url)
    logging.info(f"✅ Webhook установлен на {webhook_url}")

    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())