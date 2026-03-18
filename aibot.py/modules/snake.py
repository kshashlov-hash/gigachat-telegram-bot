import uuid
from aiogram import Router, types, F  # Добавили F
from aiogram.filters import Command  # Добавили Command
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder # Добавили InlineKeyboardBuilder

router = Router()

# Твоя ссылка на GitHub
GAME_URL = "https://kshashlov-hash.github.io/snake-game-for-gtb/"

# 1. Команда /snake для личных сообщений
@router.message(Command("snake"))
async def cmd_snake(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Используем InlineKeyboardButton напрямую из types для консистентности
    builder.row(InlineKeyboardButton(
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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Играть в Змейку", web_app=WebAppInfo(url=GAME_URL))]
    ])

    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="🐍 Змейка: Вызвать на дуэль",
        description="Нажми, чтобы отправить игру в чат",
        thumbnail_url="https://img.icons8.com/color/48/snake.png",
        input_message_content=InputTextMessageContent(
            message_text="🕹 **Я вызываю тебя на дуэль в Змейку!**\nСможешь набрать больше очков?"
        ),
        reply_markup=keyboard
    )

    try:
        # Важно: используем именованный аргумент results=[result]
        await query.answer(results=[result], cache_time=1)
    except Exception as e:
        print(f"Ошибка инлайна: {e}")

# 3. Обработка данных из Mini App (когда игра шлет счет)
@router.message(F.web_app_data)
async def handle_game_data(message: types.Message):
    data = message.web_app_data.data
    await message.answer(f"🏁 Игра окончена! Твой результат: **{data}** очков. \nНеплохо для начала! 🐍")