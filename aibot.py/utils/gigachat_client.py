import os
import sys
from pathlib import Path

# Жёстко добавляем путь к корню проекта (гарантированно)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # gigachat_client.py → utils/ → корень
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Пробуем импортировать, если не получается — выводим диагностику
try:
    from utils.history import conversation_history
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    print(f"🔍 Текущий файл: {current_file}")
    print(f"🔍 Корень проекта: {project_root}")
    print(f"🔍 sys.path: {sys.path}")
    raise

import logging

# Единый экземпляр
_giga = None
_system_prompt = None

def init_gigachat(giga_instance, system_prompt_dict):
    global _giga, _system_prompt
    _giga = giga_instance
    _system_prompt = system_prompt_dict

async def ask_gigachat(message, query):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        if _giga is None:
            logging.error("❌ _giga не инициализирован!")
            await message.reply("❌ Ошибка: GigaChat не инициализирован.")
            return

        if _system_prompt is None:
            logging.error("❌ _system_prompt не инициализирован!")
            await message.reply("❌ Ошибка: системный промпт не загружен.")
            return

        history = conversation_history.get_history(chat_id, user_id)

        messages = [_system_prompt]
        messages.extend(history)
        messages.append({"role": "user", "content": query})

        response = _giga.invoke(messages)
        answer = response.content

        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        if len(answer) > 4000:
            answer = answer[:4000] + "..."

        await message.reply(answer)

    except Exception as e:
        logging.error(f"❌ Ошибка в ask_gigachat: {e}", exc_info=True)
        await message.reply("❌ Ошибка при запросе.")