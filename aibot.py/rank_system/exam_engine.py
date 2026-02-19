import random
import re

# --- Экзамен на ранг (Four) Начало пути ---
EXAM_FOUR = [
    {"question": "Столица Франции?", "answer": "париж"},
    {"question": "2 + 2 * 2? (ответ числом)", "answer": "6"},
    {"question": "Цвет неба в ясный день?", "answer": "голубой"}
]

# --- Экзамен на ранг (Three) Пытливый ---
EXAM_THREE = [
    {"question": "Самый большой океан на Земле?", "answer": "тихий"},
    {"question": "Сколько дней в високосном году? (число)", "answer": "366"},
    {"question": "Автор романа 'Война и мир'?", "answer": "толстой"},
    {"question": "Какой газ мы вдыхаем?", "answer": "кислород"},
    {"question": "Результат 15 - 3 * 2? (число)", "answer": "9"}
]

# --- Экзамен на ранг (Two) Искусный ---
EXAM_TWO = [
    {"question": "Кто написал 'Преступление и наказание'?", "answer": "достоевский"},
    {"question": "Сколько планет в Солнечной системе? (число)", "answer": "8"},
    {"question": "Формула воды?", "answer": "h2o"},
    {"question": "Самая высокая гора в мире?", "answer": "эверест"},
    {"question": "Результат (8 + 4) / 3 * 2? (число)", "answer": "8"},
    {"question": "Кто изобрел телефон?", "answer": "белл"},
    {"question": "Какой химический символ у золота?", "answer": "au"},
    {"question": "Сколько лет в одном веке? (число)", "answer": "100"},
    {"question": "Результат 7 * 7 - 7? (число)", "answer": "42"}
]

# --- Экзамен на ранг (One) Бесконечность ---
EXAM_ONE_QUESTIONS = [
    {"question": "Сколько материков на Земле? (число)", "answer": "6"},
    {"question": "Кто написал 'Евгений Онегин'?", "answer": "пушкин"},
    {"question": "Какой газ самый распространенный в атмосфере?", "answer": "азот"}
]

EXAM_ONE_MATH = [
    {"question": "2 + 100 * 39 / 10 + 999 + 5", "answer": str(int(2 + 100 * 39 / 10 + 999 + 5))},
    {"question": "15 * 3 - 24 / 2 + 7", "answer": str(int(15 * 3 - 24 / 2 + 7))},
    {"question": "144 / 12 + 8 * 3 - 5", "answer": str(int(144 / 12 + 8 * 3 - 5))},
    {"question": "50 - 2 * (15 + 5) / 4", "answer": str(int(50 - 2 * (15 + 5) / 4))},
    {"question": "7 + 8 * 9 - 30 / 2", "answer": str(int(7 + 8 * 9 - 30 / 2))},
    {"question": "200 / 4 * 3 - 45 + 12", "answer": str(int(200 / 4 * 3 - 45 + 12))},
    {"question": "3 * 3 * 3 - 9 + 5 / 1", "answer": str(int(3 * 3 * 3 - 9 + 5))}
]


def get_exam_for_rank(target_rank):
    """Возвращает список вопросов для экзамена"""
    if target_rank == "Four":
        return random.sample(EXAM_FOUR, len(EXAM_FOUR))
    elif target_rank == "Three":
        return random.sample(EXAM_THREE, len(EXAM_THREE))
    elif target_rank == "Two":
        return random.sample(EXAM_TWO, len(EXAM_TWO))
    elif target_rank == "One":
        questions = random.sample(EXAM_ONE_QUESTIONS, len(EXAM_ONE_QUESTIONS))
        math_problems = random.sample(EXAM_ONE_MATH, len(EXAM_ONE_MATH))
        return questions + math_problems
    return []


def check_answer(user_answer, correct_answer):
    """
    Проверяет ответ пользователя.
    Возвращает True, если ответ совпадает с правильным.
    """
    if not user_answer or not correct_answer:
        return False

    # Приводим к нижнему регистру и убираем лишние пробелы
    user_clean = user_answer.strip().lower()
    correct_clean = correct_answer.strip().lower()

    # Для числовых ответов пробуем сравнивать как числа
    try:
        user_num = float(user_clean)
        correct_num = float(correct_clean)
        if abs(user_num - correct_num) < 0.001:
            return True
    except ValueError:
        pass

    # Убираем все пробелы и знаки препинания для текстовых ответов
    user_clean = re.sub(r'[^\w\s]', '', user_clean)
    correct_clean = re.sub(r'[^\w\s]', '', correct_clean)
    user_clean = re.sub(r'\s+', '', user_clean)
    correct_clean = re.sub(r'\s+', '', correct_clean)

    return user_clean == correct_clean