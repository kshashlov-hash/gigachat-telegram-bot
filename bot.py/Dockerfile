
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .
COPY render_fix.py .

RUN mkdir -p prompts

EXPOSE 8000

CMD sh -c 'python render_fix.py & python bot.py'