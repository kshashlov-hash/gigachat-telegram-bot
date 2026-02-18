import os
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Импортируем через абсолютные пути (как в aibot.py)
import database as db
import exam_engine as exam

# ID чата (из переменных окружения Render)
TARGET_CHAT_ID = int(os.getenv("RANK_CHAT_ID", "0"))

# Роутер
router = Router()
print("✅ rank_handler: роутер создан")

# -------------------- FSM для экзаменов --------------------
class ExamStates(StatesGroup):
    waiting_for_answer = State()
    exam_data = State()

# -------------------- Вспомогательная функция --------------------
def get_target_rank(total_questions):
    if 11 <= total_questions <= 60:
        return "Four"
    elif 61 <= total_questions <= 110:
        return "Three"
    elif 111 <= total_questions <= 200:
        return "Two"
    elif total_questions >= 201:
        return "One"
    return None

# -------------------- КОМАНДА /askrank --------------------
@router.message(Command("askrank"))
async def cmd_askrank(message: types.Message, state: FSMContext):
    print(f"🔥 /askrank получена в чате {message.chat.id}")

    # Проверка на целевой чат
    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        print(f"⛔ /askrank проигнорирована в чате {message.chat.id}")
        return

    # Выделяем текст вопроса
    query = message.text.replace("/askrank", "", 1).strip()
    if not query:
        await message.answer("❓ Напиши вопрос после команды /askrank")
        return

    user_id = message.from_user.id
    username = message.from_user.username or "no_username"
    first_name = message.from_user.first_name or "User"

    # Создаём пользователя, если нет
    db.create_user(user_id, username, first_name)

    # Получаем данные
    user_data = db.get_user_rank_and_counts(user_id)
    if not user_data:
        await message.answer("❌ Ошибка получения данных.")
        return

    today_q = user_data["today"]

    # Лимит 20 вопросов в день
    DAILY_LIMIT = 20
    if today_q >= DAILY_LIMIT:
        await message.answer(f"⏳ Ты сегодня уже задал {today_q} вопросов. Лимит исчерпан.")
        return

    # Проверка на экзамен
    current_state = await state.get_state()
    if current_state == ExamStates.waiting_for_answer:
        await message.answer("⚠️ Сначала заверши экзамен или отмени его: /exam_cancel")
        return

    # Увеличиваем счётчик вопросов
    new_total = db.increment_question_count(user_id)
    current_rank = user_data["rank"]
    target_rank = get_target_rank(new_total)

    # Если пора на экзамен
    if target_rank and target_rank != current_rank:
        exam_status = db.get_exam_status(user_id, target_rank)
        if not exam_status["passed"]:
            exam_questions = exam.get_exam_for_rank(target_rank)
            if exam_questions:
                await state.set_state(ExamStates.waiting_for_answer)
                await state.update_data(
                    exam_questions=exam_questions,
                    exam_index=0,
                    target_rank=target_rank,
                    correct_count=0
                )
                await message.answer(
                    f"🌟 **ЭКЗАМЕН на ранг {target_rank}!**\n\n"
                    f"Вопрос 1 из {len(exam_questions)}:\n{exam_questions[0]['question']}\n\n"
                    f"Ответь одним словом или числом.",
                    parse_mode="Markdown"
                )
                return

    # Если экзамен не нужен — просто подтверждаем приём вопроса
    await message.answer(f"✅ Вопрос принят! (Всего: {new_total}, сегодня: {today_q + 1})")

# -------------------- КОМАНДА /myrank --------------------
@router.message(Command("myrank"))
async def cmd_myrank(message: types.Message):
    print(f"📊 /myrank получена в чате {message.chat.id}")

    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        print(f"⛔ /myrank проигнорирована в чате {message.chat.id}")
        return

    user_data = db.get_user_rank_and_counts(message.from_user.id)
    if not user_data:
        await message.answer("❓ Ты ещё не в системе.\nНапиши `/askrank вопрос` чтобы начать.")
        return

    rank = user_data["rank"]
    total = user_data["total"]
    today = user_data["today"]
    name = message.from_user.first_name or "Аноним"

    # Описания рангов
    rank_desc = {
        "Five": "Невежа",
        "Four": "Начало пути",
        "Three": "Пытливый",
        "Two": "Искусный",
        "One": "Бесконечность",
        "Zero": "Неизбежность"
    }

    # Эмодзи для рангов
    rank_emoji = {
        "Five": "🪵",
        "Four": "🌱",
        "Three": "🔥",
        "Two": "⚡",
        "One": "✨",
        "Zero": "💀"
    }

    emoji = rank_emoji.get(rank, "🎖")
    desc = rank_desc.get(rank, rank)

    # Пороги для следующего ранга
    thresholds = [(11, "Four", "🌱"), (61, "Three", "🔥"), (111, "Two", "⚡"), (201, "One", "✨")]
    next_data = next(((v, r, e) for v, r, e in thresholds if total < v), (None, None, None))

    progress_bar = ""
    progress_text = ""

    if next_data[0]:
        next_val, next_rank, next_emoji = next_data
        percent = (total / next_val) * 100
        filled = int((total / next_val) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        progress_bar = f"{bar} `{total}/{next_val}`"
        progress_text = f"\n📈 До ранга {next_emoji} **{next_rank}**:\n   └─ {progress_bar}"
    elif rank != "Zero" and rank != "One":
        # Если уже максимальный ранг (кроме Zero)
        progress_text = f"\n✨ **Максимальный ранг!** ✨"

    # Собираем ответ
    text = (
        f"╭────────────────────────╮\n"
        f"│        🎖 **ПРОФИЛЬ**    │\n"
        f"╰────────────────────────╯\n\n"
        f"👤 **{name}**\n"
        f"{emoji} **Ранг:** {rank} ({desc})\n"
        f"📊 **Статистика:**\n"
        f"   └─ Всего вопросов: `{total}`\n"
        f"   └─ Сегодня: `{today}`"
        f"{progress_text}"
    )

    await message.answer(text, parse_mode="Markdown")

# -------------------- КОМАНДА /exam --------------------
@router.message(Command("exam"))
async def cmd_exam(message: types.Message, state: FSMContext):
    print(f"📝 /exam получена в чате {message.chat.id}")

    user_id = message.from_user.id
    user_data = db.get_user_rank_and_counts(user_id)
    if not user_data:
        await message.answer("Сначала задай вопрос через /askrank.")
        return

    total_q = user_data["total"]
    target_rank = get_target_rank(total_q)

    if not target_rank or target_rank == user_data["rank"]:
        await message.answer("Сейчас нет доступных экзаменов для повышения.")
        return

    exam_status = db.get_exam_status(user_id, target_rank)
    if exam_status["passed"]:
        await message.answer("Ты уже сдал этот экзамен.")
        return

    exam_questions = exam.get_exam_for_rank(target_rank)
    await state.set_state(ExamStates.waiting_for_answer)
    await state.update_data(
        exam_questions=exam_questions,
        exam_index=0,
        target_rank=target_rank,
        correct_count=0
    )
    await message.answer(
        f"🌟 **Экзамен на ранг {target_rank}!**\n\n"
        f"Вопрос 1 из {len(exam_questions)}:\n{exam_questions[0]['question']}\n\n"
        f"Ответь одним словом или числом.",
        parse_mode="Markdown"
    )

# -------------------- ОБРАБОТКА ОТВЕТОВ НА ЭКЗАМЕНЕ --------------------
@router.message(ExamStates.waiting_for_answer)
async def handle_exam_answer(message: types.Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    exam_questions = data['exam_questions']
    current_index = data['exam_index']
    target_rank = data['target_rank']
    correct_count = data['correct_count']

    correct = exam.check_answer(user_answer, exam_questions[current_index]['answer'])
    if correct:
        correct_count += 1
        await message.answer("✅ Верно!")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {exam_questions[current_index]['answer']}")

    current_index += 1
    if current_index < len(exam_questions):
        await state.update_data(exam_index=current_index, correct_count=correct_count)
        await message.answer(
            f"Вопрос {current_index + 1} из {len(exam_questions)}:\n{exam_questions[current_index]['question']}"
        )
    else:
        required = len(exam_questions)
        if correct_count >= required:
            db.update_user_rank(message.from_user.id, target_rank)
            db.update_exam_attempt(message.from_user.id, target_rank, passed=True)
            await message.answer(f"🎉 **Поздравляю!** Ты получил ранг **{target_rank}**!")
        else:
            db.update_exam_attempt(message.from_user.id, target_rank, passed=False)
            await message.answer(f"😞 Экзамен не сдан. Правильных ответов: {correct_count} из {required}.")
        await state.clear()

# -------------------- КОМАНДА /exam_cancel --------------------
@router.message(Command("exam_cancel"))
async def cmd_exam_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Экзамен прерван.")