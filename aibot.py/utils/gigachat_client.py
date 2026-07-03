import os
import sys
import logging
from pathlib import Path
from google import genai
from google.genai import types as genai_types

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
_system_instruction = None
# Используем рабочую лошадку с лимитом 1500 запросов в день
_model_name = "gemini-1.5-flash"


def init_gigachat(api_key: str, system_prompt_dict: dict):
    global _client, _system_instruction
    # Инициализируем официальный клиент Google
    _client = genai.Client(api_key=api_key)
    # Вытаскиваем чистый текст системного промпта
    _system_instruction = system_prompt_dict.get("content", "Ты — полезный ИИ-ассистент.")


async def ask_gigachat(message, query: str, image_base64: str = None):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        if _client is None:
            logging.error("❌ Клиент Gemini не инициализирован!")
            await message.reply("❌ Ошибка инициализации ИИ-модуля.")
            return

        # Получаем историю (текст)
        history = conversation_history.get_history(chat_id, user_id)

        # Переводим историю в формат Google Gemini
        contents = []
        for h in history:
            role = "user" if h["role"] == "user" else "model"
            contents.append(genai_types.Content(
                role=role,
                parts=[genai_types.Part.from_text(text=h["content"])]
            ))

        # Собираем текущий запрос
        current_parts = []

        # Если прилетело фото, добавляем его через байты
        if image_base64:
            import base64
            image_data = base64.b64decode(image_base64)
            current_parts.append(genai_types.Part.from_bytes(
                data=image_data,
                mime_type="image/jpeg"
            ))

        current_parts.append(genai_types.Part.from_text(text=query or "Что на этой картинке?"))

        contents.append(genai_types.Content(role="user", parts=current_parts))

        # Запрос к Gemini API (вызов синхронный, но в потоке httpx под капотом ок)
        response = _client.models.generate_content(
            model=_model_name,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                system_instruction=_system_instruction,
                temperature=0.7
            )
        )

        answer = response.text

        if not answer:
            await message.reply("🤖 Не смог разобрать запрос. Попробуй еще раз.")
            return

        # Пишем в историю
        conversation_history.add_message(chat_id, user_id, "user", query or "[Отправлено фото]")
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        if len(answer) > 4000:
            answer = answer[:3900] + "\n\n...[Текст обрезан из-за лимитов Telegram]"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"❌ Ошибка в ask_gemini: {e}", exc_info=True)
        await message.reply(f"❌ Ошибка нейросети: {str(e)}")