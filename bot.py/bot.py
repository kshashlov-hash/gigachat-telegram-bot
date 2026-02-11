import os
import asyncio
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BotCommand  # ← BotCommand сюда
from langchain_gigachat.chat_models import GigaChat

from utils.history import conversation_history


def load_system_prompt(prompt_name: str = "default.txt.txt") -> dict:
    """Загружает системный промпт из файла в папке prompts"""
    prompt_path = Path("prompts") / prompt_name

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except FileNotFoundError:
        # Если файл не найден — используем запасной вариант
        content = "Ты — полезный ассистент. Отвечай кратко и по делу."
        logging.warning(f"Промпт {prompt_name} не найден, использую запасной")

    return {
        "role": "system",
        "content": content
    }

# Загружаем переменные окружения
load_dotenv()

# Настройки
TELEGRAM_TOKEN = os.getenv("TOKEN")
GIGACHAT_CRED = os.getenv("GIGACHAT_API_KEY")

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

giga = GigaChat(
    credentials=GIGACHAT_CRED,
    verify_ssl_certs=False,
    model="GigaChat",
    temperature=0.7,  # 0.1 — строго по фактам, 1.0 — креативно
    max_tokens=1000,   # Максимальная длина ответа
    scope="GIGACHAT_API_PERS"  # или CORP, если есть
)

async def on_startup(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="ask", description="❓ Задать вопрос"),
        BotCommand(command="reset", description="🔄 Сбросить историю"),
        BotCommand(command="help", description="ℹ️ Помощь"),
    ]
    await bot.set_my_commands(commands)
    print("✅ Меню команд установлено!")

async def main():
    dp.startup.register(on_startup)  # регистрируем функцию при старте
    await dp.start_polling(bot)

logging.basicConfig(level=logging.INFO)
# Логирование (чтобы видеть ошибки)


def load_system_prompt(prompt_name: str = "default.txt.txt") -> dict:
    """Загружает системный промпт из файла в папке prompts"""
    prompt_path = Path("prompts") / prompt_name

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except FileNotFoundError:
        content = "Ты — полезный ассистент. Отвечай кратко и по делу."
        logging.warning(f"Промпт {prompt_name} не найден, использую запасной")

    return {
        "role": "system",
        "content": content
    }


# Загружаем системный промпт
SYSTEM_PROMPT = load_system_prompt("default.txt")

# ------------------------------------------------------------
# 2. ХРАНИЛИЩЕ ИСТОРИИ ДИАЛОГОВ


# Приветствие /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Я бот от создателя milk. Упомяни меня @DeadPIHTOaibot или напиши /ask вопрос")


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Очищаем историю для этого пользователя
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



# Команда /ask
@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    # Берём текст после команды
    query = message.text.replace("/ask", "", 1).strip()
    if not query:
        await message.answer("Напиши вопрос после /ask")
        return

    await ask_gigachat(message, query)


# Реакция на упоминание бота в группе
@dp.message()
async def handle_mention(message: Message):
    bot_username = (await bot.me()).username
    bot_id = (await bot.me()).id
    text = message.text or message.caption or ""
    # ВРЕМЕННО: просто эхо для теста
    if f"@{bot_username}" in text:
        query = text.replace(f"@{bot_username}", "", 1).strip()
        await message.reply(f"Ты написал: {query}")
        return

    # --------------------------------------------------------
    # СЛУЧАЙ 1: Ответ на сообщение бота (reply)
    # --------------------------------------------------------
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        # Это ответ на сообщение бота — берём текст как запрос
        if text.strip():
            await ask_gigachat(message, text.strip())
            return

    # --------------------------------------------------------
    # СЛУЧАЙ 2: Текстовое упоминание @botname
    # --------------------------------------------------------
    if f"@{bot_username}" in text:
        query = text.replace(f"@{bot_username}", "", 1).strip()
        if query:
            await ask_gigachat(message, query)
        return

    # --------------------------------------------------------
    # СЛУЧАЙ 3: Упоминание через entities
    # --------------------------------------------------------
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = text[entity.offset:entity.offset + entity.length]
                if mention == f"@{bot_username}":
                    query = (text[:entity.offset] + text[entity.offset + entity.length:]).strip()
                    if query:
                        await ask_gigachat(message, query)
                    return


async def ask_gigachat(message: Message, query: str):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Отправляем "печатает..."
    await bot.send_chat_action(chat_id, "typing")

    try:
        # --- СОБИРАЕМ СООБЩЕНИЯ ДЛЯ GIGACHAT ---
        messages = []

        # 1. Системный промпт
        messages.append(SYSTEM_PROMPT)

        # 2. ИСТОРИЯ ДИАЛОГА (вот это добавили)
        history = conversation_history.get_history(chat_id, user_id)
        messages.extend(history)

        # 3. Текущий запрос
        messages.append({
            "role": "user",
            "content": query
        })

        # --- ОТПРАВЛЯЕМ В GIGACHAT ---
        response = giga.invoke(messages)
        answer = response.content

        # --- СОХРАНЯЕМ В ИСТОРИЮ (и это добавили) ---
        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        # --- ОТПРАВЛЯЕМ ОТВЕТ ---
        if len(answer) > 4000:
            answer = answer[:4000] + "...\n\n(ответ обрезан из-за лимита)"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("Ошибка при запросе к GigaChat. Попробуй позже.")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())