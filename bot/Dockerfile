FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt.txt
COPY . .
COPY render_fix.py .

# Запускаем и бота, и фиктивный сервер
CMD sh -c 'python render_fix.py & python bot.py'