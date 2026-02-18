import os
import sys
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- ХАК ДЛЯ ИМПОРТОВ ---
# Добавляем корень проекта в пути поиска, чтобы папка utils была видна
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ------------------------

# Теперь импорты должны работать без ошибок
from . import database as db
from . import exam_engine as exam

# Параметры чата
TARGET_CHAT_ID = int(os.getenv("RANK_CHAT_ID", "0"))
router = Router()

class ExamStates(StatesGroup):
    waiting_for_answer = State()
    exam_data = State()


def get_target_rank(total_questions):
    if 11 <= total_questions <= 60: return "Four"
    if 61 <= total_questions <= 110: return "Three"
    if 111 <= total_questions <= 200: return "Two"
    if total_questions >= 201: return "One"
    return None


@router.message(Command("askrank"))
async def cmd_askrank(message: types.Message, state: FSMContext, giga: any, sys_prompt: dict):
    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        return

    query = message.text.replace("/askrank", "").replace(f"@{message.bot.username}", "").strip()
    if not query:
        await message.answer("❓ **Вы не ввели вопрос!**\nИспользование: `/askrank ваш вопрос`", parse_mode="Markdown")
        return

    user_id = message.from_user.id
    db.create_user(user_id, message.from_user.username or "user", message.from_user.first_name)
    user_data = db.get_user_rank_and_counts(user_id)

    if user_data["today"] >= 20:
        await message.answer(f"⏳ Лимит 20 вопросов в день исчерпан. (За сегодня: {user_data['today']})")
        return

    if await state.get_state() == ExamStates.waiting_for_answer:
        await message.answer("⚠️ Сначала заверши экзамен или отмени его: /exam_cancel")
        return

    new_total = db.increment_question_count(user_id)
    current_rank = user_data["rank"]
    target_rank = get_target_rank(new_total)

    # Проверка на экзамен
    if target_rank and target_rank != current_rank:
        exam_status = db.get_exam_status(user_id, target_rank)
        if not exam_status["passed"]:
            exam_questions = exam.get_exam_for_rank(target_rank)
            if exam_questions:
                await state.set_state(ExamStates.waiting_for_answer)
                await state.update_data(exam_questions=exam_questions, exam_index=0, target_rank=target_rank,
                                        correct_count=0)
                await message.answer(
                    f"🌟 **ЭКЗАМЕН на ранг {target_rank}!**\nПрогресс: {new_total} вопр.\n\nВопрос 1:\n`{exam_questions[0]['question']}`",
                    parse_mode="Markdown")
                return

    # ОТВЕТ GIGACHAT
    await message.bot.send_chat_action(message.chat.id, "typing")
    chat_id = message.chat.id

    # Берем историю из импортированного объекта conversation_history
    history = conversation_history.get_history(chat_id, user_id)
    messages = [sys_prompt] + history + [{"role": "user", "content": query}]

    try:
        response = giga.invoke(messages)
        answer = response.content

        # Сохраняем в историю
        conversation_history.add_message(chat_id, user_id, "user", query)
        conversation_history.add_message(chat_id, user_id, "assistant", answer)

        await message.reply(f"{answer}\n\n💠 _Засчитано в ранг (Всего: {new_total})_", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"GigaChat Error: {e}")
        await message.reply("❌ Ошибка нейросети при ответе.")


@router.message(Command("myrank"))
async def cmd_myrank(message: types.Message):
    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        return

    user_data = db.get_user_rank_and_counts(message.from_user.id)
    if not user_data:
        await message.answer("🧐 Ты еще не в системе. Напиши `/askrank [вопрос]`")
        return

    rank = user_data["rank"]
    total = user_data["total"]
    today = user_data["today"]

    rank_descriptions = {
        "Zero": "Неизбежность", "Five": "Невежа", "Four": "Начало пути",
        "Three": "Пытливый", "Two": "Искусный", "One": "Бесконечность"
    }

    # Пороги для баров
    thresholds = [(11, "Four"), (61, "Three"), (111, "Two"), (201, "One")]
    next_val, n_rank = next(((v, r) for v, r in thresholds if total < v), (None, None))

    progress_str = ""
    if next_val:
        filled = int((total / next_val) * 10)
        bar = "🟢" * filled + "⚪" * (10 - filled)
        progress_str = f"\n\n**Прогресс до ранга {n_rank}:**\n`{bar}` {total}/{next_val}"

    text = (
        f"👤 **Профиль: {message.from_user.first_name}**\n"
        f"───\n"
        f"🎖 Ранг: **{rank}** ({rank_descriptions.get(rank, 'Странник')})\n"
        f"📊 Всего вопросов: `{total}`\n"
        f"📅 За сегодня: `{today}`\n"
        f"───{progress_str}"
    )
    await message.answer(text, parse_mode="Markdown")


# --- Команда для принудительного начала экзамена (если хочешь) ---
@router.message(Command("exam"))
async def cmd_exam(message: types.Message, state: FSMContext):
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

    # Начинаем экзамен
    exam_questions = exam.get_exam_for_rank(target_rank)
    await state.set_state(ExamStates.waiting_for_answer)
    await state.update_data(
        exam_questions=exam_questions,
        exam_index=0,
        target_rank=target_rank,
        correct_count=0
    )
    first_q = exam_questions[0]
    await message.answer(
        f"🌟 **Экзамен на ранг {target_rank}!**\n\n"
        f"Вопрос 1 из {len(exam_questions)}:\n"
        f"{first_q['question']}\n\n"
        f"Ответь одним словом или числом."
    )


# --- Обработка ответов на экзамене ---
@router.message(ExamStates.waiting_for_answer)
async def handle_exam_answer(message: types.Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    exam_questions = data['exam_questions']
    current_index = data['exam_index']
    target_rank = data['target_rank']
    correct_count = data['correct_count']

    # Проверяем ответ
    correct = exam.check_answer(user_answer, exam_questions[current_index]['answer'])
    if correct:
        correct_count += 1
        await message.answer("✅ Верно!")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {exam_questions[current_index]['answer']}")

    # Переходим к следующему вопросу
    current_index += 1
    if current_index < len(exam_questions):
        # Следующий вопрос
        await state.update_data(exam_index=current_index, correct_count=correct_count)
        next_q = exam_questions[current_index]
        await message.answer(
            f"Вопрос {current_index + 1} из {len(exam_questions)}:\n"
            f"{next_q['question']}"
        )
    else:
        # Экзамен окончен
        required_correct = len(exam_questions)  # Для простоты нужно ответить на все правильно
        if correct_count >= required_correct:
            # Повышаем ранг
            db.update_user_rank(message.from_user.id, target_rank)
            db.update_exam_attempt(message.from_user.id, target_rank, passed=True)
            await message.answer(
                f"🎉 **Поздравляю!** Ты успешно сдал экзамен и получил ранг **{target_rank}**!"
            )
        else:
            db.update_exam_attempt(message.from_user.id, target_rank, passed=False)
            await message.answer(
                f"😞 Экзамен не сдан. Правильных ответов: {correct_count} из {len(exam_questions)}.\n"
                f"Попробуй снова через /exam."
            )
        await state.clear()


# --- Команда для отмены экзамена ---
@router.message(Command("exam_cancel"))
async def cmd_exam_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Экзамен прерван.")