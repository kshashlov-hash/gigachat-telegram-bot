import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from const.compliments import COMPLIMENTS
from const.prompt import send_prompt
from gigachat import GigaChat

load_dotenv()

TOKEN = os.getenv("TOKEN")
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")

giga = GigaChat(
    credentials=GIGACHAT_API_KEY,
    verify_ssl_certs=False,
    model="GigaChat",
    scope="GIGACHAT_API_PERS"
)

active_compliments = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 Привет! Я бот для Лизы от milk!\n\n"
        "Госпожа, ваши команды для меня:\n"
        "/start - начало моей работы\n"
        "/compliments - начать отправку сообщений\n"
        "/compliments_off - остановить отправку\n"
        "/list - список комплиментов\n"
        "/settings - настройки\n\n"
        "Просто напиши мне что-нибудь, и я отвечу! 💖"
    )
    await update.message.reply_text(welcome_text)


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ИИ-чата через GigaChat"""
    user_message = update.message.text
    username = update.message.from_user.username

    await update.message.chat.send_action(action="typing")

    try:
        # Получаем промпт
        system_prompt = send_prompt(username, user_message)

        # Формируем полный запрос
        full_prompt = f"{system_prompt}\n\nПользователь: {user_message}\nБот:"

        # Отправляем запрос в GigaChat
        response = giga.chat(full_prompt)

        # Извлекаем ответ
        ai_response = response.choices[0].message.content

        # Очищаем ответ (убираем возможные префиксы)
        if ai_response.startswith("Бот:"):
            ai_response = ai_response[4:].strip()

        await update.message.reply_text(ai_response[:4000])  # Ограничение Telegram

    except Exception as e:
        print(f"Ошибка GigaChat: {e}")

        # Фоллбэк ответы
        import random
        fallback_responses = [
            f"Привет, {username}! Как настроение? 💖",
            f"Рада тебя видеть, {username}! 🌟",
            f"{username}, ты сегодня прекрасна! ✨",
            "Как твой день проходит? 💫"
        ]
        await update.message.reply_text(random.choice(fallback_responses))

async def start_compliments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in active_compliments:
        await update.message.reply_text("⏳ Ц, рассылка уже запущена!")
        return

    await update.message.reply_text(
        "📝 Милая, введи интервал в секундах (например, 5):\n"
        "Или нажми /cancel для отмены"
    )
    context.user_data['waiting_for_interval'] = True


async def handle_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода интервала"""
    chat_id = update.effective_chat.id
    text = update.message.text

    # Проверяем, что мы действительно ждем интервал
    if not context.user_data.get('waiting_for_interval'):
        return False

    try:
        interval = int(text)
        if interval < 2:
            await update.message.reply_text("❌ Дурашка, интервал должен быть не менее 2 секунд!")
            return True

        context.user_data['waiting_for_interval'] = False
        await update.message.reply_text(f"✅ Рассылка запущена с интервалом {interval} сек!")

        task = asyncio.create_task(send_compliments(chat_id, interval, context.application))
        active_compliments[chat_id] = {'task': task, 'interval': interval}
        return True

    except ValueError:
        # Если ввели не число, но мы ждем интервал
        await update.message.reply_text("❌ Введи число, а не текст!")
        return True


async def send_compliments(chat_id: int, interval: int, app: Application):
    index = 0

    try:
        while chat_id in active_compliments:
            await app.bot.send_message(
                chat_id=chat_id,
                text=f"💖 Комплимент {index + 1}:\n{COMPLIMENTS[index]}"
            )
            index = (index + 1) % len(COMPLIMENTS)
            await asyncio.sleep(interval)

    except Exception as e:
        print(f"Ошибка в рассылке: {e}")
    finally:
        if chat_id in active_compliments:
            del active_compliments[chat_id]


async def stop_compliments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in active_compliments:
        active_compliments[chat_id]['task'].cancel()
        del active_compliments[chat_id]
        await update.message.reply_text("🛑 Молчу по вашему приказу!")
    else:
        await update.message.reply_text("ℹ️ Рассылка не была запущена.")


async def list_compliments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📜 Список всех комплиментов:\n\n"
    for i, compliment in enumerate(COMPLIMENTS, 1):
        text += f"{i}. {compliment}\n"
    await update.message.reply_text(text)


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in active_compliments:
        interval = active_compliments[chat_id]['interval']
        text = f"⚙️ Текущие настройки:\n\nИнтервал: {interval} сек\nСтатус: Активна ✅"
    else:
        text = "⚙️ Текущие настройки:\n\nСтатус: Неактивна ⏸️"

    text += f"\n\nВсего комплиментов: {len(COMPLIMENTS)}"
    await update.message.reply_text(text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_interval'):
        context.user_data['waiting_for_interval'] = False
        await update.message.reply_text("❌ Действие отменено")
    else:
        await update.message.reply_text("Нечего отменять 🤷‍♂️")


async def universal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик текстовых сообщений"""
    # 1. Сначала проверяем, не вводится ли интервал
    if context.user_data.get('waiting_for_interval'):
        await handle_interval(update, context)
    else:
        # 2. Если не интервал, то ИИ-чат
        await ai_chat(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")


def main():
    print("🚀 Запуск бота...")
    print(f"🤖 Количество комплиментов: {len(COMPLIMENTS)}")
    print("💬 ИИ чат активирован (DeepSeek)")
    print("⏳ Для остановки нажми Ctrl+C\n")

    app = Application.builder().token(TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("compliments", start_compliments))
    app.add_handler(CommandHandler("compliments_off", stop_compliments))
    app.add_handler(CommandHandler("list", list_compliments))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CommandHandler("cancel", cancel))

    # УНИВЕРСАЛЬНЫЙ обработчик всех текстовых сообщений
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        universal_handler
    ))

    app.add_error_handler(error_handler)

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()