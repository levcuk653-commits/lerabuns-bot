import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Настройка логирования
logging.basicConfig(level=logging.INFO)

RAW_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_TOKEN = RAW_BOT_TOKEN.strip().replace(" ", "").replace("\n", "").replace("\r", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Я Лера 💫 Рада тебе бачити! Про що поспілкуємось?")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    # Тестова відповідь, щоб перевірити роботу самого бота
    await message.answer(f"Ти написав: «{message.text}». Я тебе чудово чую! 🔥")

async def handle_health_check(request):
    return web.Response(text="Bot is live!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logging.info(f"Web server active on port {port}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())











