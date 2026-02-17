import random
import re

# --- Экзамен на ранг (Four) Начало пути ---
EXAM_FOUR = [
    {"question": "Столица Франции?", "answer": "париж"},
    {"question": "2 + 2 * 2?", "answer": "6"},
    {"question": "Цвет неба в ясный день?", "answer": "голубой"}
]

# --- Экзамен на ранг (Three) Пытливый ---
EXAM_THREE = [
    {"question": "Самый большой океан на Земле?", "answer": "тихий"},
    {"question": "Сколько дней в високосном году?", "answer": "366"},
    {"question": "Автор романа 'Война и мир'?", "answer": "толстой"},
    {"question": "Какой газ мы вдыхаем?", "answer": "кислород"},
    {"question": "Результат 15 - 3 * 2?", "answer": "9"}
]

# --- Экзамен на ранг (Two) Искусный ---
EXAM_TWO = [
    {"question": "Кто написал 'Преступление и наказание'?", "answer": "достоевский"},
    {"question": "Сколько планет в Солнечной системе?", "answer": "8"},
    {"question": "Формула воды?", "answer": "h2o"},
    {"question": "Самая высокая гора в мире?", "answer": "эверест"},
    {"question": "Результат (8 + 4) / 3 * 2?", "answer": "8"},
    {"question": "Кто изобрел телефон?", "answer": "белл"},
    {"question": "Какой химический символ у золота?", "answer": "au"},
    {"question": "Сколько лет в одном веке?", "answer": "100"},
    {"question": "Результат 7 * 7 - 7?", "answer": "42"}
]

# --- Экзамен на ранг (One) Бесконечность ---
EXAM_ONE_QUESTIONS = [
    {"question": "Сколько материков на Земле?", "answer": "6"},
    {"question": "Кто написал 'Евгений Онегин'?", "answer": "пушкин"},
    {"question": "Какой газ самый распространенный в атмосфере?", "answer": "азот"}
]

EXAM_ONE_MATH = [
    {"question": "2+100*39/10+999+5", "answer": str(int(2 + 100*39/10 + 999 + 5))},
    {"question": "15 * 3 - 24 / 2 + 7", "answer": str(int(15*3 - 24/2 + 7))},
    {"question": "144 / 12 + 8 * 3 - 5", "answer": str(int(144/12 + 8*3 - 5))},
    {"question": "50 - 2 * (15 + 5) / 4", "answer": str(int(50 - 2*(15+5)/4))},
    {"question": "7 + 8 * 9 - 30 / 2", "answer": str(int(7 + 8*9 - 30/2))},
    {"question": "200 / 4 * 3 - 45 + 12", "answer": str(int(200/4*3 - 45 + 12))},
    {"question": "3 * 3 * 3 - 9 + 5 / 1", "answer": str(int(3*3*3 - 9 + 5))}
]

def get_exam_for_rank(target_rank):
    if target_rank == "Four":
        return random.sample(EXAM_FOUR, len(EXAM_FOUR))
    elif target_rank == "Three":
        return random.sample(EXAM_THREE, len(EXAM_THREE))
    elif target_rank == "Two":
        return random.sample(EXAM_TWO, len(EXAM_TWO))
    elif target_rank == "One":
        questions = random.sample(EXAM_ONE_QUESTIONS, len(EXAM_ONE_QUESTIONS))
        math_problems = random.sample(EXAM_ONE_MATH, 7)
        return questions + math_problems
    return []

def check_answer(user_answer, correct_answer):
    """Простая проверка: сравниваем строки без учета регистра и пробелов"""
    user_clean = re.sub(r'\s+', '', user_answer.strip().lower())
    correct_clean = re.sub(r'\s+', '', correct_answer.strip().lower())
    return user_clean == correct_clean