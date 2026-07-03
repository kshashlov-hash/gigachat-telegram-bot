import os
import sys
from pathlib import Path
import logging
from openai import AsyncOpenAI

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from utils.history import conversation_history
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    raise

_client = None
_system_prompt = None
# Читаем модель из .env, если её там нет — берем 100% бесплатную сейчас Llama 3 8B
_model_name = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct:free")


def init_gigachat(api_key: str, system_prompt_dict: dict):
    global _client, _system_prompt
    _client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    _system_prompt = system_prompt_dict


async def ask_gigachat(message, query):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        if _client is None or _system_prompt is None:
            logging.error("❌ Клиент OpenRouter или промпт не инициализированы!")
            await message.reply("❌ Ошибка инициализации ИИ-модуля.")
            return

        history = conversation_history.get_history(chat_id, user_id)

        messages = [_system_prompt]
        messages.extend(history)
        messages.append({"role": "user", "content": query})

        completion = await _client.chat.completions.create(
            model=_model_name,  # Используем динамическую модель
            messages=messages,
            extra_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Dead Pihto Bot",
            }
        )

        answer = completion.choices[0].message.content

        if not answer:
            await message.reply("🤖 Не смог сгенерировать ответ. Попробуй еще раз.")
            return

        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        # Безопасное обрезание без поломки разметки (в идеале слать кусками, но пока так)
        if len(answer) > 4000:
            answer = answer[:3900] + "\n\n...[Текст обрезан из-за лимитов Telegram]"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"❌ Ошибка в ask_openrouter: {e}", exc_info=True)
        # Временно выводим ошибку в чат для отладки
        await message.reply(f"❌ Ошибка нейросети: {str(e)}")
