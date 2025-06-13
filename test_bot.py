import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()  # Загружает токен из .env

TOKEN = os.getenv("BOT_TOKEN")

async def main():
    if not TOKEN:
        print("❌ Токен не найден. Проверь .env файл.")
        return
    bot = Bot(token=TOKEN)
    me = await bot.get_me()
    print(f"🤖 Бот успешно подключен: {me.username} (ID: {me.id})")

asyncio.run(main())
