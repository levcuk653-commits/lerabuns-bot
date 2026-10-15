import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримання та очищення токенів від зайвих пробілів чи символів
RAW_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_TOKEN = RAW_BOT_TOKEN.strip().replace(" ", "").replace("\n", "").replace("\r", "")

RAW_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_KEY = RAW_OPENROUTER_KEY.strip().replace(" ", "").replace("\n", "").replace("\r", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = "Ти — Лера (Lera Buns), популярна блогерка та діджей. Відповідай дружньо, невимушено, з гумором та українською мовою."

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Я Лера 💫 Рада тебе бачити! Про що поспілкуємось?")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message.text}
        ]
    }

    try:
        async with web.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"]
                    await message.answer(reply)
                else:
                    await message.answer("Ой, щось зв'язок підкачав... Спробуй ще раз трохи пізніше!")
    except Exception as e:
        logging.error(f"Error calling OpenRouter: {e}")
        await message.answer("Зараз трохи зайнята, напиши мені ще раз за хвилинку! ✨")

async def handle_health_check(request):
    return web.Response(text="OK")

async def main():
    # Запуск веб-сервера під порт Render, щоб уникнути помилки портів
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Server started on port {port}")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())










