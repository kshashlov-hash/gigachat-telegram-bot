FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем буферизацию логов (чтобы видеть принты в консоли Docker сразу)
# и создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Сначала копируем только requirements для использования кэша слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта
COPY . .

# Переходим в папку, где лежит основной скрипт
WORKDIR /app/aibot.py

# Запускаем бота
CMD ["python", "chat_aibot.py"]