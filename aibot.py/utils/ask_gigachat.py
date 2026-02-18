from langchain_gigachat.chat_models import GigaChat
from utils.history import conversation_history

# Единый экземпляр GigaChat (будет инициализирован из main)
giga_instance = None
system_prompt = None

def init_gigachat(giga, sys_prompt):
    """Инициализация клиента GigaChat (вызывается из aibot.py)"""
    global giga_instance, system_prompt
    giga_instance = giga
    system_prompt = sys_prompt

async def ask_gigachat(message, query):
    """Универсальная функция для ответа через GigaChat"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    await message.bot.send_chat_action(chat_id, "typing")

    try:
        # Собираем сообщения
        messages = [system_prompt]
        messages.extend(conversation_history.get_history(chat_id, user_id))
        messages.append({"role": "user", "content": query})

        # Запрос к GigaChat
        response = giga_instance.invoke(messages)
        answer = response.content

        # Сохраняем в историю
        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        # Обрезаем длинные ответы
        if len(answer) > 4000:
            answer = answer[:4000] + "...\n\n(ответ обрезан из-за лимита)"

        await message.reply(answer)

    except Exception as e:
        logging.error(f"Ошибка в ask_gigachat: {e}")
        await message.reply("❌ Ошибка при запросе. Попробуй позже.")