import os
import sys
from pathlib import Path
import logging
from openai import AsyncOpenAI

# Жёстко добавляем путь к корню проекта (гарантированно)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Импорт твоей истории сообщений
try:
    from utils.history import conversation_history
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    raise

# Единые экземпляры для OpenRouter
_client = None
_system_prompt = None


def init_gigachat(api_key: str, system_prompt_dict: dict):
    """
    Инициализируем асинхронный клиент OpenRouter.
    Имя функции оставляем прежним, чтобы не ломать импорты в основном файле.
    """
    global _client, _system_prompt
    _client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    _system_prompt = system_prompt_dict


async def ask_gigachat(message, query):
    """
    Основная функция запроса к Llama 3.1 70B Free через OpenRouter
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        if _client is None:
            logging.error("❌ Клиент OpenRouter не инициализирован!")
            await message.reply("❌ Ошибка: Клиент ИИ не инициализирован.")
            return

        if _system_prompt is None:
            logging.error("❌ _system_prompt не инициализирован!")
            await message.reply("❌ Ошибка: системный промпт не загружен.")
            return

        # Получаем историю сообщений из твоей БД/модуля истории
        history = conversation_history.get_history(chat_id, user_id)

        # Собираем пачку сообщений для OpenRouter
        messages = [_system_prompt]
        messages.extend(history)
        messages.append({"role": "user", "content": query})

        # Асинхронный запрос к актуальной бесплатной модели
        completion = await _client.chat.completions.create(
            model="qwen/qwen-2.5-coder-32b-instruct:free",  # <-- Меняем здесь
            messages=messages,
            extra_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Dead Pihto Bot",
            }
        )

        # Вытаскиваем чистый ответ
        answer = completion.choices[0].message.content

        # Сохраняем в твою историю
        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        # Твой ограничитель на длину сообщения в Telegram
        if len(answer) > 4000:
            answer = answer[:4000] + "..."

        await message.reply(answer)

    except Exception as e:
        logging.error(f"❌ Ошибка в ask_openrouter: {e}", exc_info=True)
        await message.reply("❌ Ошибка при запросе к нейросети.")