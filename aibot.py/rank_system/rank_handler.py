from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import logging
from . import database as db
from . import exam_engine as exam

import os
# ID чата, в котором работает ранговая система (задаётся в переменной окружения RANK_CHAT_ID)
# Если не задано или 0, система будет работать во всех чатах (для отладки)
TARGET_CHAT_ID = int(os.getenv("RANK_CHAT_ID", "0"))

# Создаем роутер для команд этой системы
router = Router()


# --- FSM для экзаменов (состояния) ---
class ExamStates(StatesGroup):
    waiting_for_answer = State()
    exam_data = State()  # храним список вопросов, индекс, целевой ранг


# --- Вспомогательная функция для определения следующего ранга ---
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


# --- Команда для задания вопроса в системе рангов ---

@router.message(Command("askrank"))
async def cmd_askrank(message: types.Message, state: FSMContext):
    print(f"🔥 /askrank получена в чате {message.chat.id}")
    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        # Можно просто игнорировать или ответить один раз
        # await message.answer("❌ Эта команда работает только в специальном чате.")
        return  # игнорируем
    user_id = message.from_user.id
    username = message.from_user.username or "no_username"
    first_name = message.from_user.first_name or "User"

    # Создаем пользователя, если его нет
    db.create_user(user_id, username, first_name)

    # Получаем данные о пользователе
    user_data = db.get_user_rank_and_counts(user_id)
    if not user_data:
        await message.answer("❌ Ошибка получения данных.")
        return

    total_q = user_data["total"]
    today_q = user_data["today"]
    current_rank = user_data["rank"]

    # Проверка суточного лимита (например, 20 вопросов в день)
    DAILY_LIMIT = 20
    if today_q >= DAILY_LIMIT:
        await message.answer(
            f"⏳ Ты сегодня уже задал {today_q} вопросов. Лимит на сегодня исчерпан. Возвращайся завтра!")
        return

    # Если пользователь в процессе экзамена, не даем задавать вопросы
    current_state = await state.get_state()
    if current_state is not None:
        await message.answer("Сначала заверши экзамен! Используй /exam_cancel, если хочешь прервать.")
        return

    # Увеличиваем счетчик вопросов и получаем новое общее количество
    new_total = db.increment_question_count(user_id)

    # Определяем, нужно ли начать экзамен для перехода на новый ранг
    target_rank = get_target_rank(new_total)

    if target_rank and target_rank != current_rank:
        # Проверяем, не сдавал ли он уже этот экзамен
        exam_status = db.get_exam_status(user_id, target_rank)
        if exam_status["passed"]:
            # Уже сдал, просто повышаем ранг (на всякий случай, если база не обновилась)
            db.update_user_rank(user_id, target_rank)
            await message.answer(f"🎉 Поздравляю! Ты достиг ранга **{target_rank}** (подтверждено ранее).")
        else:
            # Начинаем экзамен
            exam_questions = exam.get_exam_for_rank(target_rank)
            if exam_questions:
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
                return
    else:
        # Обычный вопрос, просто отвечаем через GigaChat (интеграция с ask_gigachat)
        # Здесь тебе нужно вызвать твою функцию ask_gigachat
        # Так как это отдельный модуль, мы просто отправим сообщение, что вопрос принят
        await message.answer(f"✅ Вопрос принят! (Всего: {new_total}, сегодня: {today_q + 1})")
        # Тут нужно будет вызвать ask_gigachat из основного файла, это обсуждаемо


# --- Команда для просмотра своего ранга ---
@router.message(Command("myrank"))
async def cmd_myrank(message: types.Message):
    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        # Можно просто игнорировать или ответить один раз
        # await message.answer("❌ Эта команда работает только в специальном чате.")
        return  # игнорируем
    user_id = message.from_user.id
    user_data = db.get_user_rank_and_counts(user_id)

    if not user_data:
        await message.answer("Ты еще не задавал вопросов через /askrank. Начни, чтобы получить ранг!")
        return

    rank = user_data["rank"]
    total = user_data["total"]
    today = user_data["today"]

    # Описание рангов
    rank_descriptions = {
        "Five": "Невежа",
        "Four": "Начало пути",
        "Three": "Пытливый",
        "Two": "Искусный",
        "One": "Бесконечность"
    }

    next_rank_info = ""
    if rank == "Five":
        next_rank_info = "Следующий ранг (Four): 11 вопросов (нужно сдать экзамен из 2 вопросов)"
    elif rank == "Four":
        next_rank_info = "Следующий ранг (Three): 61 вопрос (экзамен из 5 вопросов)"
    elif rank == "Three":
        next_rank_info = "Следующий ранг (Two): 111 вопросов (экзамен из 9 вопросов)"
    elif rank == "Two":
        next_rank_info = "Следующий ранг (One): 201 вопрос (экзамен из 10 заданий: 3 вопроса + 7 примеров)"

    text = (
        f"📊 **Твой профиль:**\n"
        f"Ранг: **{rank}** ({rank_descriptions.get(rank, rank)})\n"
        f"Всего вопросов: {total}\n"
        f"Сегодня: {today}\n\n"
        f"{next_rank_info}"
    )
    await message.answer(text)


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