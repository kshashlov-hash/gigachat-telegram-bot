import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

COMPLIMENTS = [
    "Ты такая красивая! 🌟",
    "С тобой я часто улыбаюсь! 😄",
    "С тобой так хорошо общаться! 💬",
    "Твоя улыбка поднимает настроение и не только! ☀️",
    "У тебя прикольные волосы! 🎨",
    "Твоя атмосфера умиляет! ✨",
    "У тебя прекрасный вкус! 👌",
    "Ты умнее, чем думаешь! 🧠",
    "С тобой хочется стать лучше! 💫",
    "Твоё присутствие делает мир ярче! 🌈",
    "И все таки у тебя такая красивая грудь, вот бы разглядеть получше! (скидывать в лс создателю💖)"
]

active_compliments = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 Привет! Я бот для Лизы от milk!\n\n"
        "Госпожа, ваши команды для меня:\n"
        "/start - начало моей работы\n"
        "/compliments - начать отправку сообщений\n"
        "/compliments_off - остановить отправку\n"
        "/settings - настройки\n\n"
        "Просто напиши мне что-нибудь, и я отвечу, пока что правда только одним соо! 💖"
    )
    await update.message.reply_text(welcome_text)


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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if context.user_data.get('waiting_for_interval'):
        try:
            interval = int(text)
            if interval < 2:
                await update.message.reply_text("❌ Дурашка, интервал должен быть не менее 2 секунд!")
                return

            context.user_data['waiting_for_interval'] = False
            await update.message.reply_text(f"✅ Рассылка запущена с интервалом {interval} сек!")

            task = asyncio.create_task(send_compliments(chat_id, interval, context.application))
            active_compliments[chat_id] = {'task': task, 'interval': interval}

        except ValueError:
            await update.message.reply_text("❌ Введи число!")
        return

    await update.message.reply_text(f"Госпожа написала: '{text}'\n\nИспользуй команды из меню! 📋")


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
        await update.message.reply_text("🛑 Госпожа, молчу по вашему приказу!")
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


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")


def main():
    print("🚀 Запуск бота...")
    print(f"🤖 Количество комплиментов: {len(COMPLIMENTS)}")
    print("⏳ Для остановки нажми Ctrl+C\n")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("compliments", start_compliments))
    app.add_handler(CommandHandler("compliments_off", stop_compliments))
    app.add_handler(CommandHandler("list", list_compliments))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters=None, callback=handle_message))

    app.add_error_handler(error_handler)

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()