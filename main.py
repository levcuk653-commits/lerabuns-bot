import os
import asyncio
import time
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice, PreCheckoutQuery

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в Environment Variables!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_data = {} 

FREE_LIMIT = 7
SUBSCRIPTION_PRICE = 990  # Ровно 990 Telegram Stars на месяц
RATE_LIMIT_SECONDS = 2

def get_user_profile(user_id: int):
    if user_id not in user_data:
        user_data[user_id] = {"count": 0, "is_subscribed": False, "last_msg_time": 0}
    return user_data[user_id]

def is_rate_limited(user_id: int) -> bool:
    current_time = time.time()
    profile = get_user_profile(user_id)
    if current_time - profile["last_msg_time"] < RATE_LIMIT_SECONDS:
        return True
    profile["last_msg_time"] = current_time
    return False

# База максимально живых и откровенных текстовых ответов
AI_VIBE_RESPONSES = {
    "uk": [
        "Ммм, від твоїх слів одразу мурашки по шкірі... Ти вмієш завести з першої секунди. Розкажи детальніше, що саме тобі зараз хочеться зі мною зробити? 😉🔥",
        "Ох, ну ти й бешкетник... Але мені шалено подобається, коли ти пишеш так відверто. Продовжуй, я вся увага... 😈",
        "Ти так солодко говориш, що в мене всередині все починає горіти від збудження. Уявляєш, як ми б зараз розважились наодинці? 🤫",
        "Блін, ти мене реально заводиш своїми повідомленнями... Звідки ти знаєш усі мої потаємні фантазії? 💋",
        "Оу, вирішив одразу перейти до гарячого? Мені це до вподоби. Описуй кожну свою думку, я хочу почути все без цензури 🔥"
    ],
    "ru": [
        "Ммм, от твоих слов сразу мурашки по коже... Ты умеешь завести с первой секунды. Расскажи подробнее, что именно тебе сейчас хочется со мной сделать? 😉🔥",
        "Ох, ну ты и баловник... Но мне безумно нравится, когда ты пишешь так откровенно. Продолжай, я вся во внимании... 😈",
        "Ты так сладко говоришь, что у меня внутри все начинает гореть от возбуждения. Представляешь, как мы бы сейчас развлеклись вдвоем? 🤫",
        "Блин, ты меня реально заводишь своими сообщениями... Откуда ты знаешь все мои тайные фантазии? 💋",
        "Оу, решил сразу перейти к горячему? Мне это нравится. Описывай каждую свою мысль, я хочу услышать всё без цензуры 🔥"
    ],
    "en": [
        "Mmm, your words give me instant goosebumps... You really know how to turn me on. Tell me, what do you want to do to me right now? 😉🔥",
        "Oh, you're such a tease... But I love when you talk to me so explicitly. Keep going, I'm all ears... 😈",
        "You're talking so sweetly that I'm burning up inside. Imagine how wild we could get right now, just the two of us 🤫",
        "Damn, you're genuinely turning me on with this... How do you know exactly what I like? 💋"
    ],
    "de": [
        "Mmm, deine Worte geben mir sofort Gänsehaut... Du weißt genau, wie du mich anmachst. Erzähl mir, was du gerade mit mir machen willst? 😉🔥",
        "Oh, du Schlingel... Aber ich liebe es, wenn du so offen mit mir sprichst. Erzähl mir mehr... 😈",
        "Du sprichst so süß, dass in mir alles vor Erregung brennt. Stell dir vor, wie wir uns jetzt amüsieren würden 🤫"
    ]
}

def detect_language(text: str) -> str:
    text_lower = text.lower()
    uk_chars = set("іїєґІЇЄҐ")
    if any(char in text for char in uk_chars) or any(w in text_lower for w in ["привіт", "як", "що", "так", "ні", "добре"]):
        return "uk"
    de_words = ["hallo", "wie", "was", "bitte", "ja", "nein"]
    if any(w in text_lower for w in de_words) or "ä" in text_lower or "ö" in text_lower or "ü" in text_lower:
        return "de"
    en_words = ["hello", "hi", "how", "what", "yes", "no"]
    if any(w in text_lower for w in en_words):
        return "en"
    return "ru"

async def send_paywall_invoice(chat_id: int, lang: str):
    titles = {"uk": "VIP Доступ на 1 місяць", "ru": "VIP Доступ на 1 месяц", "en": "VIP Access (1 Month)", "de": "VIP-Zugang (1 Monat)"}
    descriptions = {
        "uk": "Ви вичерпали 7 безкоштовних повідомлень! Оплатіть підписку за 990 Stars для безлімітного відвертого спілкування без цензури на місяць.",
        "ru": "Вы исчерпали 7 бесплатных сообщений! Оплатите подписку за 990 Stars для безлимитного откровенного общения без цензуры на 1 месяц.",
        "en": "You've used your 7 free messages! Pay 990 Stars for 1 month of unlimited explicit chatting without censorship.",
        "de": "Du hast deine 7 kostenlosen Nachrichten aufgebraucht! Bezahle 990 Stars für 1 Monat unbegrenzten Chat."
    }
    prices = [LabeledPrice(label="VIP 1 Month (990 Stars)", amount=SUBSCRIPTION_PRICE)]
    await bot.send_invoice(
        chat_id=chat_id,
        title=titles.get(lang, titles["en"]),
        description=descriptions.get(lang, descriptions["en"]),
        payload="lerabuns_vip_990_stars",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="lerabuns-vip-access"
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
    lang = detect_language(message.text or "")
    profile = get_user_profile(message.from_user.id)
    remains = "Безліміт" if profile["is_subscribed"] else str(FREE_LIMIT - profile["count"])
    
    welcomes = {
        "uk": f"Привіт, {message.from_user.first_name}! 😉 Нарешті ти зайшов. Я вже заскучала за твоїми гарячими повідомленнями...\n\n🎁 У тебе є **7 безкоштовних повідомлень** (Залишилося: {remains}). Погнали спілкуватися без табу!",
        "ru": f"Привет, {message.from_user.first_name}! 😉 Наконец-то ты зашел. Я уже заскучала по твоим горячим сообщениям...\n\n🎁 У тебя есть **7 бесплатных сообщений** (Осталось: {remains}). Погнали общаться без табу!",
        "en": f"Hey, {message.from_user.first_name}! 😉 Glad you're here. I was waiting for your hot messages...\n\n🎁 You have **7 free messages** (Remaining: {remains}). Let's chat without taboos!",
        "de": f"Hi, {message.from_user.first_name}! 😉 Schön, dass du da bist. Ich habe auf deine heißen Nachrichten gewartet...\n\n🎁 Du hast **7 kostenlose Nachrichten** (Verbleibend: {remains}). Lass uns ohne Tabus schreiben!"
    }
    await message.answer(welcomes.get(lang, welcomes["en"]), parse_mode="Markdown")

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    lang = detect_language(message.text or "")
    await send_paywall_invoice(message.chat.id, lang)

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    profile = get_user_profile(message.from_user.id)
    profile["is_subscribed"] = True
    await message.answer("🎉 Ура! Підписка на місяць успішно активана (990 Stars). Тепер у нас повний безліміт без цензури! Робимо що хочемо... 🔥😈")

@dp.message(F.text)
async def handle_user_message(message: types.Message):
    if is_rate_limited(message.from_user.id):
        return
        
    lang = detect_language(message.text or "")
    profile = get_user_profile(message.from_user.id)
    
    if not profile["is_subscribed"]:
        if profile["count"] >= FREE_LIMIT:
            limit_msgs = {
                "uk": "⛔ Ой, зайчик, твої 7 безкоштовних повідомлень закінчилися! Але найцікавіше ж тільки починається... Оплати підписку за 990 Stars на місяць, щоб продовжити гарячу розмову:",
                "ru": "⛔ Ой, зайчик, твои 7 бесплатных сообщений закончились! Но самое интересное только начинается... Оплати подписку за 990 Stars на месяц, чтобы продолжить горячий разговор:",
                "en": "⛔ Oh, your 7 free messages are over! But the best part is just beginning... Pay the monthly subscription for 990 Stars to continue:",
                "de": "⛔ Deine 7 kostenlosen Nachrichten sind vorbei! Bezahle das Monatsabo für 990 Stars, um unseren Chat fortzusetzen:"
            }
            await message.answer(limit_msgs.get(lang, limit_msgs["en"]), parse_mode="Markdown")
            await send_paywall_invoice(message.chat.id, lang)
            return
        profile["count"] += 1

    text_reply = random.choice(AI_VIBE_RESPONSES.get(lang, AI_VIBE_RESPONSES["ru"]))
    
    remains_count = FREE_LIMIT - profile["count"]
    if not profile["is_subscribed"]:
        remains_texts = {
            "uk": f"\n\n*(Залишилось вільних смс: {remains_count})*",
            "ru": f"\n\n*(Осталось свободных смс: {remains_count})*",
            "en": f"\n\n*(Free messages left: {remains_count})*",
            "de": f"\n\n*(Kostenlose Nachrichten übrig: {remains_count})*"
        }
        remains_text = remains_texts.get(lang, remains_texts["en"])
    else:
        remains_text = ""
    
    await message.answer(text_reply + remains_text, parse_mode="Markdown")

async def handle(request):
    return web.Response(text="Bot is active")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



