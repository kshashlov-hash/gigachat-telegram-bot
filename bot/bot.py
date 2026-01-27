import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Безопасное получение токена
TOKEN = os.environ.get("8516268528:AAEmg97xyDyWtLE0fi4pu-2ITXkNBFuSr-0")

if not TOKEN:
    print("❌ Ошибка: TOKEN не найден! Установите переменную окружения TOKEN в Render")
    exit(1)

COMPLIMENTS = [
    "Лиз, ты сегодня невероятно выглядишь! 🌟",
    "У тебя отличное чувство юмора! 😄",
    "С тобой всегда приятно общаться! 💬",
    "Твоя улыбка поднимает настроение! ☀️",
    "Ты очень талантливый человек! 🎨",
    "Твоя энергия вдохновляет! ✨",
    "У тебя классная грудь!)",
    "Сегодня не поддавайся плохим событиям, будь выше."
]

compliments_active = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я сам напишу тебе всё, что надо! Я бот для Лизы от milk.\n"
        "Доступные команды:\n"
        "/start - начало работы\n"
        "/compliments - начать отправку комплиментов\n"
        "/compliments_off - остановить отправку комплиментов"
    )


async def start_compliments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global compliments_active
    if compliments_active:
        await update.message.reply_text("Рассылка уже запущена!")
        return

    compliments_active = True
    await update.message.reply_text("Запускаю все свои мысли в этого бота! ❤️")

    # Запускаем асинхронную задачу
    context.application.create_task(send_compliments(update.effective_chat.id, context.application))


async def send_compliments(chat_id: int, app: Application):
    global compliments_active
    index = 0

    while compliments_active:
        try:
            # Отправляем комплимент через существующее приложение
            await app.bot.send_message(chat_id=chat_id, text=COMPLIMENTS[index])

            index = (index + 1) % len(COMPLIMENTS)
            await asyncio.sleep(5)

        except Exception as e:
            print(f"Ошибка в send_compliments: {e}")
            compliments_active = False
            break


async def stop_compliments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global compliments_active
    if compliments_active:
        compliments_active = False
        await update.message.reply_text("Так и быть, замолчуgit --version. 😊")
    else:
        await update.message.reply_text("Рассылка не была запущена.")


def main():
    # Создаем приложение с увеличенными таймаутами для Render
    application = Application.builder() \
        .token(TOKEN) \
        .read_timeout(30) \
        .write_timeout(30) \
        .pool_timeout(30) \
        .connect_timeout(30) \
        .build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("compliments", start_compliments))
    application.add_handler(CommandHandler("compliments_off", stop_compliments))

    print("✅ Бот запущен на Render!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False
    )


if __name__ == "__main__":
    main()