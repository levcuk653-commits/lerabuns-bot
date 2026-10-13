import os
import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice, PreCheckoutQuery

# Отримання токена з змінних оточення (Environment Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в Environment Variables!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простий rate-limiter: пам'ять останніх повідомлень
user_last_message_time = {}
RATE_LIMIT_SECONDS = 2  # Пауза між повідомленнями (в секундах)

def is_rate_limited(user_id: int) -> bool:
    current_time = time.time()
    last_time = user_last_message_time.get(user_id, 0)
    if current_time - last_time < RATE_LIMIT_SECONDS:
        return True
    user_last_message_time[user_id] = current_time
    return False

# Обробник команди /start
@dp.message(CommandStart())
def cmd_start(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
    
    welcome_text = (
        f"Привіт, {message.from_user.first_name}!\n\n"
        f"Вітаємо у **@Lerabuns18bot**! 🚀\n"
        f"Використовуйте команду /buy, щоб придбати доступ за Telegram Stars."
    )
    message.answer(welcome_text, parse_mode="Markdown")

# Команда /buy для створення рахунку в Telegram Stars
@dp.message(Command("buy"))
def cmd_buy(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return

    prices = [LabeledPrice(label="Преміум доступ", amount=10)]  # 10 Stars

    bot.send_invoice(
        chat_id=message.chat.id,
        title="Підписка Lerabuns",
        description="Оплата доступу за допомогою Telegram Stars ⭐",
        payload="lerabuns_stars_payment",
        provider_token="",  # Для Telegram Stars provider_token залишається порожнім!
        currency="XTR",     # Код валюти Telegram Stars
        prices=prices,
        start_parameter="lerabuns-stars-subscription"
    )

# Обробка PreCheckoutQuery (обов'язковий підтверджувальний крок Telegram)
@dp.pre_checkout_query()
def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обробка успішної оплати
@dp.message(F.successful_payment)
def process_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    message.answer(
        f" Дякуємо за оплату!\n\n"
        f"Отримано: **{payment_info.total_amount} Stars** ⭐.\n"
        f"Ваш доступ успішно активовано!",
        parse_mode="Markdown"
    )

# Головна функція запуску
async def main():
    print("Бот @Lerabuns18bot успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
