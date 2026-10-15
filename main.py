
import os
import asyncio
import logging
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Настройка логирования
logging.basicConfig(level=logging.INFO)

RAW_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_TOKEN = RAW_BOT_TOKEN.strip().replace(" ", "").replace("\n", "").replace("\r", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# База крутих живих відповідей Лери
LERI_RESPONSES = [
    "Оу, привітик! Я якраз новий трек зводжу в студії, але для тебе завжди знайду хвилину ✨",
    "Та все гуд! Що нового в тебе? Як настрій?",
    "Ахах, ти вмієш підняти настрій! Слухай, я тут готуюся до сету на вихідних, ти як, плануєш бути?",
    "Мене якраз відволікли від TikTok-зйомки, але з тобою погомоніти — залюбки! 💫",
    "Ну ти й засипаєш питаннями! Давай краще розкажи, яка музика зараз на повторі в твоїх навушниках?",
    "Я тут заварбую каву і думаю про нові сторіс... А ти чим зайнятий?",
    "Аж мурашки від таких розмов! 🔥 Розповідай, що цікавого?",
    "Сонце, я зараз трохи за пультом, але я тебе чую і обіймаю! Хвилинку — і я повністю твоя 😉"
]

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Я Лера 💫 Рада тебе бачити! Про що поспілкуємось?")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    # Невелика імітація природної затримки на «друк» (1 секунда)
    await asyncio.sleep(1)
    
    # Вибираємо випадкову фразу з бази
    reply = random.choice(LERI_RESPONSES)
    await message.answer(reply)

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












