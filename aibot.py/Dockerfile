FROM python:3.11-slim

# Устанавливаем базовую директорию
WORKDIR /app

# Настройки для логов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Копируем ВЕСЬ проект
COPY . .

# 2. Маленькая хитрость: выведем список файлов, чтобы в логах Render
# мы увидели, где лежит requirements.txt
RUN ls -R

# 3. Устанавливаем зависимости.
# Мы укажем путь ОТ КОРНЯ /app, чтобы Pip его точно нашел.
RUN pip install --no-cache-dir -r aibot.py/requirements.txt

# 4. Переходим в папку с ботом
WORKDIR /app/aibot.py

# 5. Запускаем бота
CMD ["python", "chat_aibot.py"]