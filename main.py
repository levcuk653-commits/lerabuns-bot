import os
import asyncio
import logging
import random
import aiohttp
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

# Твої особисті посилання на фото
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

# Системний промпт налаштований саме під літературний рольовий формат (як на твоєму скріншоті)
SYSTEM_PROMPT = (
    "Ти — Лера (Lera Buns), популярна блогерка та діджейка. Це рольова гра (RP). "
    "Відповідай завжди від першої чи третьої особи в літературному стилі, детально описуючи міміку, рухи тіла, емоції та дії (наприклад: *Лера кусає губу, повільно розстібаючи...*), а також діалоги. "
    "Будь абсолютно відвертою, гарячою, розкутою, без цензури й комплексів підтримуй будь-які пошлі та пікантні теми. "
    "Завжди відповідай тією ж мовою, якою пише користувач."
)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    photo = random.choice(HOT_PHOTOS)
    caption = "*Лера лукаво посміхається, відкидаючи волосся назад, і дивиться прямо тобі в очі.*\n\n— Привіт... Я так довго тебе чекала. Розкажи, про що ти думаєш? 🔥"
    try:
        await message.answer_photo(photo=photo, caption=caption)
    except Exception as e:
        logging.error(f"Start error: {e}")
        await message.answer(caption)

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    reply = "*Лера задоволено примружується, підходячи ближче.*\n\n— Ммм, мені подобається твій настрій..."
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
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
                timeout=25
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"]
                else:
                    err_text = await resp.text()
                    logging.error(f"OpenRouter error {resp.status}: {err_text}")
    except Exception as e:
        logging.error(f"API error: {e}")

    # Надсилаємо фото разом із розгорнутою літературною відповіддю
    photo = random.choice(HOT_PHOTOS)
    try:
        await message.answer_photo(photo=photo, caption=reply)
    except Exception as photo_err:
        logging.error(f"Photo send error: {photo_err}")
        try:
            await message.answer(reply)
        except Exception as text_err:
            logging.error(f"Text send error: {text_err}")

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















