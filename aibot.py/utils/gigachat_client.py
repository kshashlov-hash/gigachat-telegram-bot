import sys
from pathlib import Path

# Добавляем путь к корню проекта
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import logging

# Единый экземпляр (будет инициализирован из main)
_giga = None
_system_prompt = None

def init_gigachat(giga_instance, system_prompt_dict):
    """Вызывается из aibot.py после создания giga и SYSTEM_PROMPT"""
    global _giga, _system_prompt
    _giga = giga_instance
    _system_prompt = system_prompt_dict

def get_history():
    """Ленивый импорт истории (чтобы избежать циклических импортов)"""
    from history import conversation_history
    return conversation_history

async def ask_gigachat(message, query):
    """Функция для ответа через GigaChat"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        history = get_history()
        messages = [_system_prompt]
        messages.extend(history.get_history(chat_id, user_id))
        messages.append({"role": "user", "content": query})

        response = _giga.invoke(messages)
        answer = response.content

        history.add_message(chat_id, user_id, "user", query)
        history.add_message(chat_id, user_id, "assistant", answer)

        if len(answer) > 4000:
            answer = answer[:4000] + "..."

        await message.reply(answer)
    except Exception as e:
        logging.error(f"Ошибка в ask_gigachat: {e}")
        await message.reply("❌ Ошибка при запросе.")