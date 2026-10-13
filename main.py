import os
import asyncio
import time
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice, PreCheckoutQuery

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в Environment Variables!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_last_message_time = {}
RATE_LIMIT_SECONDS = 2

def is_rate_limited(user_id: int) -> bool:
    current_time = time.time()
    last_time = user_last_message_time.get(user_id, 0)
    if current_time - last_time < RATE_LIMIT_SECONDS:
        return True
    user_last_message_time[user_id] = current_time
    return False

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
    welcome_text = (
        f"Привіт, {message.from_user.first_name}!\n\n"
        f"Вітаємо у **@Lerabuns18bot**! 🚀\n"
        f"Використовуйте команду /buy, щоб придбати доступ за Telegram Stars."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
    prices = [LabeledPrice(label="Преміум доступ", amount=10)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Підписка Lerabuns",
        description="Оплата доступу за допомогою Telegram Stars ⭐",
        payload="lerabuns_stars_payment",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="lerabuns-stars-subscription"
    )

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    await message.answer(
        f"Дякуємо за оплату!\n\n"
        f"Отримано: **{payment_info.total_amount} Stars** ⭐.\n"
        f"Ваш доступ успішно активовано!",
        parse_mode="Markdown"
    )

# Простий вебсервер для того, щоб Render не закривав порт
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Вебсервер запущено на порті {port}")

async def main():
    # Запускаємо і вебсервер, і бота одночасно
    await web_server()
    print("Бот @Lerabuns18bot успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

