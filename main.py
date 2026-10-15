import os
import asyncio
import logging
import requests
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримання токенів із змінних середовища Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Системний промпт для персонажа Lera Buns
SYSTEM_PROMPT = "Ти — Лера (Lera Buns), популярна блогерка та діджей. Відповідай дружньо, невимушено, з гумором та українською мовою."

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Я Лера 💫 Рада тебе бачити! Про що поспілкуємось?")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.text}
                ]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            await message.answer(reply)
        else:
            await message.answer("Ой, щось зв'язок підкачав... Спробуй ще раз трохи пізніше!")
            
    except Exception as e:
        logging.error(f"Error calling OpenRouter: {e}")
        await message.answer("Зараз трохи зайнята, напиши мені ще раз за хвилинку! ✨")

# Простий хендлер для Render, щоб тримати порт відкритим
async def handle_health_check(request):
    return web.Response(text="Bot is running!")

async def main():
    # Запуск вебсервера для Render
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logging.info(f"Web server started on port {port}")
    
    # Видалення застарілих вебхуків та запуск поллінгу
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())









