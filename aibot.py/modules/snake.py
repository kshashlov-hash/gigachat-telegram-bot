import uuid
import sys
from pathlib import Path
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db_game.database import update_snake_score, get_snake_top, create_user

router = Router()
GAME_URL = "https://kshashlov-hash.github.io/snake-game-for-gtb/"


@router.message(Command("snake"))
async def cmd_snake(message: types.Message):
    if message.chat.type == "private":
        # Кнопка в личке
        kb = [[KeyboardButton(text="🐍 Начать игру", web_app=WebAppInfo(url=GAME_URL))]]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("🐍 Нажми на кнопку ниже, чтобы играть со счетом!", reply_markup=keyboard)
    else:
        # Кнопка в группе
        builder = InlineKeyboardBuilder()
        bot_user = await message.bot.get_me()
        builder.row(InlineKeyboardButton(
            text="🕹 Играть (сохранить счёт)",
            url=f"https://t.me/{bot_user.username}?start=play_snake")
        )
        await message.answer(
            "🐍 В чате игра доступна в режиме тренировки.\nПерейди в личку, чтобы сохранить результат:",
            reply_markup=builder.as_markup()
        )


# ВОТ ЭТОТ ХЕНДЛЕР ТЕПЕРЬ БУДЕТ ОТВЕЧАТЬ В ЧАТ
@router.message(F.content_type == types.ContentType.WEB_APP_DATA)
async def handle_game_data(message: types.Message):
    try:
        score = int(message.web_app_data.data)
    except ValueError:
        score = 0

    user = message.from_user

    # Сначала создаем/обновляем юзера в общей таблице
    create_user(user.id, user.username, user.first_name)

    # Пытаемся обновить рекорд в таблице змейки
    is_new_record = update_snake_score(
        user_id=user.id,
        username=user.username or "Аноним",
        first_name=user.first_name,
        new_score=score
    )

    text = f"🏁 <b>Игра окончена!</b>\n\nТвой результат: <b>{score}</b> очков. 🐍\n"

    if is_new_record and score > 0:
        text += "🔥 <b>Это новый личный рекорд!</b>"

    await message.answer(text, parse_mode="HTML")

@router.inline_query()
async def inline_handler(query: types.InlineQuery):
    # Текст, который увидит пользователь в подсказке
    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="🐍 Запустить Змейку",
            description="Нажми, чтобы отправить приглашение в этот чат",
            thumbnail_url="https://img.icons8.com/color/48/snake.png",
            input_message_content=InputTextMessageContent(
                message_text="🕹 **Вызываю всех на дуэль в Змейку!**\n\nЧтобы играть и сохранять счёт, нажми на кнопку ниже или напиши /snake мне в личку."
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🐍 Играть", url=f"https://t.me/{(await query.bot.get_me()).username}?start=play_snake")]
            ])
        )
    ]
    # cache_time=0 ВАЖНО, чтобы убрать ту самую крутилку и кэш
    await query.answer(results=results, cache_time=0, is_personal=True)


@router.message(Command("topsnake"))
async def cmd_topsnake(message: types.Message):
    top_players = get_snake_top(15)

    if not top_players:
        await message.answer("🏆 Таблица лидеров пока пуста. Стань первым!")
        return

    # Формируем сообщение
    header = "🏆 <b>ТОП-15 ИГРОКОВ В ЗМЕЙКУ</b> 🏆\n"
    line = "⎯" * 15 + "\n"

    leaderboard_rows = []
    for i, (name, username, score) in enumerate(top_players, 1):
        # Добавляем медали для первых трех мест
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")

        user_display = f"@{username}" if username != "Аноним" else f"<b>{name}</b>"
        leaderboard_rows.append(f"{medal} {user_display} — <code>{score}</code>")

    full_text = header + line + "\n".join(leaderboard_rows) + f"\n\n{line}<i>Играй чаще, чтобы попасть в топ!</i>"

    await message.answer(full_text, parse_mode="HTML")