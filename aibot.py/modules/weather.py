import os
import aiohttp
import logging
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command

# Создаём роутер для команд погоды
router = Router()

# API ключ из переменных окружения
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# ID чата для ограничения (если нужно)
TARGET_CHAT_ID = int(os.getenv("RANK_CHAT_ID", "0"))


async def get_weather(city: str):
    """
    Получает погоду для указанного города через OpenWeatherMap API
    Возвращает словарь с данными или None при ошибке
    """
    if not WEATHER_API_KEY:
        logging.error("❌ WEATHER_API_KEY не задан в переменных окружения")
        return None

    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WEATHER_API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    weather_data = {
                        'city': data['name'],
                        'country': data['sys']['country'],
                        'temp': round(data['main']['temp']),
                        'feels_like': round(data['main']['feels_like']),
                        'description': data['weather'][0]['description'].capitalize(),
                        'humidity': data['main']['humidity'],
                        'wind_speed': round(data['wind']['speed'], 1),
                        'pressure': round(data['main']['pressure'] * 0.75006),  # в мм рт. ст.
                        'icon': data['weather'][0]['icon']
                    }
                    return weather_data
                elif response.status == 404:
                    return {"error": "not_found"}
                else:
                    logging.error(f"Ошибка API погоды: {response.status}")
                    return {"error": "api_error"}
    except Exception as e:
        logging.error(f"Ошибка при запросе погоды: {e}")
        return {"error": "connection_error"}


def get_weather_emoji(icon_code: str) -> str:
    """Конвертирует код иконки OpenWeather в эмодзи"""
    icon_map = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '☁️',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️',
        '10d': '🌦️', '10n': '🌧️',
        '11d': '⛈️', '11n': '⛈️',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫️'
    }
    return icon_map.get(icon_code, '🌡️')


def get_temp_emoji(temp: int) -> str:
    """Возвращает эмодзи в зависимости от температуры"""
    if temp < -10:
        return "🥶"
    elif temp < 0:
        return "❄️"
    elif temp < 10:
        return "🌡️"
    elif temp < 20:
        return "😊"
    elif temp < 30:
        return "🌞"
    else:
        return "🔥"


# Команда /weather
@router.message(Command("weather"))
async def cmd_weather(message: types.Message):
    """Показывает погоду: /weather Москва или !погода Москва"""

    if TARGET_CHAT_ID and message.chat.id != TARGET_CHAT_ID:
        return

    # Проверяем, не вызвана ли команда через !
    text = message.text
    if text.startswith('!'):
        # Преобразуем !погода в /weather
        text = text.replace('!погода', '/weather', 1)

    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "🌍 **Погода**\n\n"
            "Использование:\n"
            "• `/weather Москва`\n"
            "• `!погода Новосибирск`\n\n"
            "Можно писать на русском или английском.",
            parse_mode="Markdown"
        )
        return

    city = parts[1].strip()

    status_msg = await message.answer(f"🔍 Ищу погоду в *{city}*...", parse_mode="Markdown")

    weather_data = await get_weather(city)

    if not weather_data:
        await status_msg.edit_text("❌ Не удалось получить данные о погоде. Попробуй позже.")
        return

    if isinstance(weather_data, dict) and weather_data.get("error") == "not_found":
        await status_msg.edit_text(f"❌ Город *{city}* не найден. Проверь название.", parse_mode="Markdown")
        return
    elif isinstance(weather_data, dict) and weather_data.get("error"):
        await status_msg.edit_text("❌ Ошибка при запросе погоды. Попробуй позже.")
        return

    emoji = get_weather_emoji(weather_data['icon'])
    temp_emoji = get_temp_emoji(weather_data['temp'])

    weather_text = (
        f"╭─────── {emoji} **ПОГОДА** {emoji} ───────╮\n\n"
        f"📍 **{weather_data['city']}, {weather_data['country']}**\n\n"
        f"{temp_emoji} Температура: **{weather_data['temp']}°C**\n"
        f"🤔 Ощущается как: **{weather_data['feels_like']}°C**\n"
        f"📝 Описание: *{weather_data['description']}*\n\n"
        f"💧 Влажность: **{weather_data['humidity']}%**\n"
        f"💨 Ветер: **{weather_data['wind_speed']} м/с**\n"
        f"📊 Давление: **{weather_data['pressure']} мм рт. ст.**\n\n"
        f"╰────────────────────────────╯"
    )

    await status_msg.edit_text(weather_text, parse_mode="Markdown")


# Поддержка !погода (обрабатывается отдельно)
@router.message()
async def handle_weather_exclamation(message: types.Message):
    """Обрабатывает !погода как альтернативу /weather"""
    if message.text and message.text.startswith('!погода'):
        # Просто вызываем команду weather с тем же сообщением
        await cmd_weather(message)