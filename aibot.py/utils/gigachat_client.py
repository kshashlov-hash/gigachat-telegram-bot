import os
import sys
from pathlib import Path

# Жёстко добавляем путь к корню проекта
current_dir = Path(__file__).resolve().parent  # папка utils
project_root = current_dir.parent  # корень проекта

# Добавляем путь к папке utils
utils_path = current_dir
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# Теперь импортируем напрямую
from history import conversation_history
import logging

# Единый экземпляр (будет инициализирован из main)
_giga = None
_system_prompt = None

def init_gigachat(giga_instance, system_prompt_dict):
    """Вызывается из aibot.py после создания giga и SYSTEM_PROMPT"""
    global _giga, _system_prompt
    _giga = giga_instance
    _system_prompt = system_prompt_dict

async def ask_gigachat(message, query):
    """Функция для ответа через GigaChat (не зависит от aibot)"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        messages = [_system_prompt]
        messages.extend(conversation_history.get_history(chat_id, user_id))
        messages.append({"role": "user", "content": query})

        response = _giga.invoke(messages)
        answer = response.content

        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        if len(answer) > 4000:
            answer = answer[:4000] + "..."

        await message.reply(answer)
    except Exception as e:
        logging.error(f"Ошибка в ask_gigachat: {e}")
        await message.reply("❌ Ошибка при запросе.")