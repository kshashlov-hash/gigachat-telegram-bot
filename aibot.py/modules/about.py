from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

router = Router()


@router.message(Command("resume"))
async def cmd_resume(message: Message):
    # Твоя будущая ссылка (например, на GitHub Pages или Vercel)
    # Пока сайта нет, можешь временно поставить туда google.com для теста
    site_url = "https://kshashlov-hash.github.io/resume"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            # WebApp откроет сайт прямо внутри интерфейса Telegram красивой шторкой
            InlineKeyboardButton(text="✨ Открыть резюме в ТГ", web_app=WebAppInfo(url=site_url))
        ],
        [
            # Обычная ссылка на случай, если кто-то захочет открыть в полноценном браузере
            InlineKeyboardButton(text="🌐 Открыть в браузере", url=site_url)
        ]
    ])

    await message.answer(
        "🚀 <b>milk | Backend Developer and Creator</b>\n\n"
        "Привет! Рад, что ты здесь. Моё веб-портфолио — это интерактивная карта "
        "моих навыков, архитектурных решений и реализованных систем.\n\n"
        "<b>Что там внутри:</b>\n"
        "• 🛠 <b>Стек:</b> Разработка на Python (Asyncio/Aiogram) и C#\n"
        "• 📊 <b>Базы данных:</b> Проектирование и оптимизация SQL\n"
        "• 🖥 <b>Проекты:</b> От AI-ассистентов до сложных систем мониторинга\n\n"
        "Круто, что ты сюда кликнул, веб-визитка откроется красивой шторкой прямо внутри Telegram! ⎯⎯⎯👇",
        parse_mode="HTML",
        reply_markup=kb
    )