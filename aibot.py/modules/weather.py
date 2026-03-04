import os
import aiohttp
import logging
from aiogram import Router, types
from aiogram.filters import Command
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

router = Router()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

async def get_weather(city: str):
    if not WEATHER_API_KEY:
        logging.error("❌ WEATHER_API_KEY не задан")
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
                    return {
                        'city': data['name'],
                        'country': data['sys']['country'],
                        'temp': round(data['main']['temp']),
                        'feels_like': round(data['main']['feels_like']),
                        'description': data['weather'][0]['description'].capitalize(),
                        'humidity': data['main']['humidity'],
                        'wind_speed': round(data['wind']['speed'], 1),
                        'pressure': round(data['main']['pressure'] * 0.75006),
                        'icon': data['weather'][0]['icon']
                    }
                elif response.status == 404:
                    return {"error": "not_found"}
                else:
                    return {"error": "api_error"}
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return {"error": "connection_error"}

def get_weather_emoji(icon_code: str) -> str:
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
    if temp < -10: return "🥶"
    elif temp < 0: return "❄️"
    elif temp < 10: return "🌡️"
    elif temp < 20: return "😊"
    elif temp < 30: return "🌞"
    else: return "🔥"


@router.message(Command("weather"))
async def cmd_weather(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "🌍 **Погода**\n\n"
            "Использование: `/weather Москва`",
            parse_mode="Markdown"
        )
        return

    city = parts[1].strip()
    status_msg = await message.answer(f"🔍 Ищу погоду в *{city}*...", parse_mode="Markdown")

    # Получаем данные
    weather_data = await get_weather(city)

    # ОТЛАДКА: выводим в логи
    print(f"🌤️ Данные для {city}: {weather_data}")

    if not weather_data:
        await status_msg.edit_text("❌ Не удалось получить данные о погоде.")
        return

    if isinstance(weather_data, dict) and "error" in weather_data:
        if weather_data["error"] == "not_found":
            await status_msg.edit_text(f"❌ Город *{city}* не найден.", parse_mode="Markdown")
        else:
            await status_msg.edit_text("❌ Ошибка при запросе погоды.")
        return

    # Если данные есть — показываем
    emoji = get_weather_emoji(weather_data['icon'])
    temp_emoji = get_temp_emoji(weather_data['temp'])

    weather_text = (
        f"╭─── {emoji} **ПОГОДА** {emoji} ───╮\n\n"
        f"📍 **{weather_data['city']}, {weather_data['country']}**\n\n"
        f"{temp_emoji} Температура: **{weather_data['temp']}°C**\n"
        f"🤔 Ощущается: **{weather_data['feels_like']}°C**\n"
        f"📝 {weather_data['description']}\n\n"
        f"💧 Влажность: **{weather_data['humidity']}%**\n"
        f"💨 Ветер: **{weather_data['wind_speed']} м/с**\n"
        f"📊 Давление: **{weather_data['pressure']} мм рт. ст.**\n\n"
        f"╰──────────────────╯"
    )

    await status_msg.edit_text(weather_text, parse_mode="Markdown")