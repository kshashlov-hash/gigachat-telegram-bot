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
_model_name = os.getenv("OPENROUTER_MODEL", "gemini-2.5-flash")


def init_gigachat(api_key: str, system_prompt_dict: dict):
    global _client, _system_prompt
    _client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key
    )
    _system_prompt = system_prompt_dict


async def ask_gigachat(message, query: str, image_base64: str = None):
    """
    Основная функция запроса к ИИ. Умеет принимать текст и опциональное фото в base64.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        if _client is None or _system_prompt is None:
            logging.error("❌ Клиент ИИ не инициализирован!")
            await message.reply("❌ Ошибка инициализации ИИ-модуля.")
            return

        # Получаем историю (текстовую)
        history = conversation_history.get_history(chat_id, user_id)

        messages = [_system_prompt]
        messages.extend(history)

        # Формируем контент для текущего сообщения
        if image_base64:
            # Если есть фото, структура контента становится массивом
            current_content = [
                {"type": "text", "text": query or "Что на этой картинке?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        else:
            # Если фото нет — обычная строка текста
            current_content = query

        messages.append({"role": "user", "content": current_content})

        completion = await _client.chat.completions.create(
            model=_model_name,
            messages=messages,
            extra_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Dead Pihto Bot",
            }
        )

        answer = completion.choices[0].message.content

        if not answer:
            await message.reply("🤖 Не смог разобрать запрос. Попробуй еще раз.")
            return

        # В историю сохраняем только текст, чтобы не раздувать БД картинками
        conversation_history.add_message(chat_id, user_id, "user", query or "[Отправлено фото]")
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        if len(answer) > 4000:
            answer = answer[:3900] + "\n\n...[Текст обрезан из-за лимитов Telegram]"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"❌ Ошибка в ask_gigachat: {e}", exc_info=True)
        await message.reply(f"❌ Ошибка нейросети: {str(e)}")