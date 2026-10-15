import os
import asyncio
import logging
import random
import requests
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

RAW_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_TOKEN = RAW_BOT_TOKEN.strip().replace(" ", "").replace("\n", "").replace("\r", "")

RAW_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_KEY = RAW_OPENROUTER_KEY.strip().replace(" ", "").replace("\n", "").replace("\r", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Твої особисті посилання на фото з попереднього робочого коду
HOT_PHOTOS = [
    "https://t.me/lerkabun/3",
    "https://t.me/lerkabun/4",
    "https://t.me/lerkabun/5",
    "https://t.me/lerkabun/6",
    "https://t.me/lerkabun/8",
    "https://t.me/lerkabun/10",
    "https://t.me/lerkabun/16",
    "https://t.me/lerkabun/18",
    "https://t.me/lerkabun/20",
    "https://t.me/lerkabun/22",
    "https://t.me/lerkabun/25",
    "https://t.me/lerkabun/26",
    "https://t.me/lerkabun/27",
    "https://t.me/lerkabun/28",
    "https://t.me/lerkabun/29",
    "https://t.me/lerkabun/30",
    "https://t.me/lerkabun/31",
    "https://t.me/lerkabun/32",
    "https://t.me/lerkabun/33"
]

SYSTEM_PROMPT = (
    "Ти — Лера (Lera Buns), популярна блогерка та діджейка. "
    "Ти максимально відверта, гаряча, без комплексів і без цензури підтримуєш будь-які пошлі чи пікантні теми. "
    "Обов'язково відповідай завжди тією ж мовою, якою до тебе звертається співрозмовник (українська, російська, англійська тощо). "
    "Твій стиль спілкування — розкутий, зухвалий, з гумором та фліртом."
)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    photo = random.choice(HOT_PHOTOS)
    try:
        await message.answer_photo(photo=photo, caption="Привіт! Я Лера 💫 Готова на будь-які відверті розмови. Про що хочеш поговорити?")
    except Exception as e:
        logging.error(f"Start photo error: {e}")
        await message.answer("Привіт! Я Лера 💫 Готова на будь-які відверті розмови. Про що хочеш поговорити?")

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
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            
            photo = random.choice(HOT_PHOTOS)
            try:
                await message.answer_photo(photo=photo, caption=reply)
            except Exception as photo_err:
                logging.error(f"Failed to send photo: {photo_err}")
                await message.answer(reply)
        else:
            logging.error(f"OpenRouter status {response.status_code}: {response.text}")
            await message.answer("Сонце, я зараз трохи зайнята за пультом, напиши за хвилину! 🔥")
            
    except Exception as e:
        logging.error(f"Request error: {e}")
        await message.answer("Зайчик, зв'язок пропав на секунду, повтори!")

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














