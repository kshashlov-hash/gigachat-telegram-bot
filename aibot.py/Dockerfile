FROM python:3.11-slim

# Устанавливаем базовую директорию
WORKDIR /app

# Настройки для логов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем ВЕСЬ проект (вместе с папкой aibot.py и всем содержимым)
COPY . .

# Теперь переходим в папку, где лежит файл зависимостей и сам бот
WORKDIR /app/aibot.py

# Устанавливаем библиотеки (теперь путь "." указывает прямо на aibot.py внутри контейнера)
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "chat_aibot.py"]