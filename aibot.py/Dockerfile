FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем всё содержимое текущей папки в /app
COPY . .

# Пробуем установить зависимости из корня ИЛИ из подпапки
# Эта команда найдет файл, даже если он провалился вглубь
RUN pip install --no-cache-dir -r $(find . -name requirements.txt | head -n 1)

# Запускаем поиск главного файла и его выполнение
# Мы используем shell-форму, чтобы python нашел файл сам
CMD python $(find . -name chat_aibot.py | head -n 1)