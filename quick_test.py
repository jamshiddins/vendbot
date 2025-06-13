import asyncio
from aiogram.client.bot import Bot  # 👈 обязательно из client.bot

TOKEN = "8108980727:AAEaLKa8PjjjLv_IoCGnJVGaIbyFV_6Qbhs"

async def main():
    bot = Bot(token=TOKEN)
    me = await bot.get_me()
    print(f"✅ Бот: @{me.username} | ID: {me.id}")
    await bot.session.close()  # 👈 вручную закрываем сессию

asyncio.run(main())