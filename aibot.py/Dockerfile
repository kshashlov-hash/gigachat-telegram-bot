FROM python:3.11-slim

# 1. Ставим общую рабочую директорию
WORKDIR /app

# 2. Настройки для логов в реальном времени
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Копируем requirements (путь должен быть правильным!)
# Если файл в корне проекта:
COPY aibot.py/requirements.txt .
# Если файл уже в корне PythonProject, то просто: COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем ВЕСЬ проект в /app
COPY . .

# 5. КРИТИЧЕСКИЙ МОМЕНТ: переходим именно туда, где лежит главный файл
WORKDIR /app/aibot.py

# 6. Запускаем без указания папки (так как мы уже в ней)
CMD ["python", "chat_aibot.py"]