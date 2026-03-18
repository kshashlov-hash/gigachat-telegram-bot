import uuid
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Твоя ссылка на GitHub
GAME_URL = "https://kshashlov-hash.github.io/snake-game-for-gtb/"

# 1. Команда /snake для личных сообщений
@router.message(Command("snake"))
async def cmd_snake(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🐍 Запустить Змейку",
        web_app=WebAppInfo(url=GAME_URL)
    ))

    await message.answer(
        "Нажми на кнопку ниже, чтобы начать игру прямо в Telegram!",
        reply_markup=builder.as_markup()
    )

# 2. Инлайн-режим (вызов через @DeadPIHTOaibot в любом чате)
@router.inline_query()
async def inline_snake(query: types.InlineQuery):
    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="🐍 Поиграть в Змейку",
            description="Отправить приглашение в игру в этот чат",
            thumbnail_url="https://img.icons8.com/color/48/snake.png",
            input_message_content=InputTextMessageContent(
                message_text="🕹 **Я вызываю всех на дуэль в Змейку!**\nКто сможет побить мой рекорд?"
            ),
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🎮 Играть", web_app=WebAppInfo(url=GAME_URL))]
            ])
        )
    ]
    await query.answer(results, cache_time=1)

# 3. Обработка данных из Mini App (когда игра шлет счет)
@router.message(F.web_app_data)
async def handle_game_data(message: types.Message):
    # Эта функция сработает, когда JS в игре вызовет tg.sendData(score)
    data = message.web_app_data.data
    await message.answer(f"🏁 Игра окончена! Твой результат: **{data}** очков. \nНеплохо для начала! 🐍")